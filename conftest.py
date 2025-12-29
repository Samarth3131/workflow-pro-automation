import pytest
import json
from pathlib import Path

TEST_DATA_PATH = Path(__file__).parent / "tests" / "data" / "test_data.json"
with open(TEST_DATA_PATH) as f:
    TEST_DATA = json.load(f)


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
