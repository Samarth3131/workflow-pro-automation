import pytest
import json
import requests
from pathlib import Path
from requests.adapters import HTTPAdapter, Retry

TEST_DATA_PATH = Path(__file__).parent / "tests" / "data" / "test_data.json"
with open(TEST_DATA_PATH) as f:
    TEST_DATA = json.load(f)

# Timeout configuration constants
CONNECTION_TIMEOUT = 5  # seconds for initial connection (also used for health checks)
READ_TIMEOUT = 30  # seconds for reading response
HEALTH_CHECK_TIMEOUT = 5  # seconds for health check requests (both connection and read)


def pytest_configure(config):
    config.addinivalue_line("markers", "smoke: Critical path tests")
    config.addinivalue_line("markers", "api: API tests")
    config.addinivalue_line("markers", "ui: UI tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "auth: Authentication tests")
    config.addinivalue_line("markers", "tenant: Multi-tenant tests")
    config.addinivalue_line("markers", "slow: Tests that take longer")


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "viewport": {
            "width": 1920,
            "height": 1080,
        },
    }


@pytest.fixture(scope="function")
def context(context):
    yield context


@pytest.fixture(scope="session")
def test_data():
    return TEST_DATA


@pytest.fixture(scope="session")
def base_url():
    return TEST_DATA["base_urls"]["staging"]["web"]


@pytest.fixture(scope="session")
def api_base_url():
    return TEST_DATA["base_urls"]["staging"]["api"]


@pytest.fixture(scope="function", autouse=True)
def cleanup_after_test(request):
    yield
    pass


def create_retry_session(retries=3, backoff_factor=1):
    """
    Create a requests session with retry logic for handling transient network issues.
    
    This utility function is available for use in tests that need retry capabilities.
    It's not used in health checks (which should fail fast) but can be used in actual
    test requests to handle transient failures.
    
    Args:
        retries: Number of retry attempts for failed requests
        backoff_factor: Multiplier for exponential backoff between retries
        
    Returns:
        A configured requests.Session with retry logic
        
    Example:
        session = create_retry_session()
        response = session.get(url, timeout=(CONNECTION_TIMEOUT, READ_TIMEOUT))
    """
    session = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=(500, 502, 503, 504),
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


@pytest.fixture(scope="session", autouse=True)
def check_api_health():
    """Check if API is reachable before running tests."""
    api_base_url = TEST_DATA["base_urls"]["staging"]["api"]
    
    # Try to connect to the API base URL
    try:
        # Use short timeout for fast health check - we want to fail fast
        # if the API is down rather than wait for a long read timeout
        response = requests.get(
            api_base_url,
            timeout=(HEALTH_CHECK_TIMEOUT, HEALTH_CHECK_TIMEOUT)
        )
        # Even if we get a 404, that's better than a connection timeout
        # It means the server is reachable
    except requests.exceptions.ConnectionError:
        pytest.skip(f"API is unreachable at {api_base_url} - skipping all tests")
    except requests.exceptions.Timeout:
        pytest.skip(f"API health check timed out for {api_base_url} - skipping all tests")
    except Exception as e:
        # For other exceptions, we'll log but continue
        # as it might be a legitimate server response
        pass


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    
    if report.when == "call" and report.failed:
        if "page" in item.funcargs:
            page = item.funcargs["page"]
            screenshot_name = f"test-results/{item.name}.png"
            try:
                page.screenshot(path=screenshot_name)
            except:
                pass
