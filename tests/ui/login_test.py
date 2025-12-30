import pytest
import json
import pyotp
from pathlib import Path

from playwright.sync_api import Browser, BrowserContext, Page, expect
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


# -----------------------------
# Test data loading (SAFE)
# -----------------------------

TEST_DATA_PATH = Path(__file__).parent.parent / "data" / "test_data.json"


def load_test_data():
    if not TEST_DATA_PATH.exists():
        raise FileNotFoundError(f"Missing test data file: {TEST_DATA_PATH}")
    with open(TEST_DATA_PATH) as f:
        return json.load(f)


@pytest.fixture(scope="session")
def test_data():
    return load_test_data()


@pytest.fixture(scope="session")
def base_url(test_data):
    return test_data["base_urls"]["staging"]["web"]


@pytest.fixture(scope="session", autouse=True)
def check_web_health(test_data):
    """Check if web application is reachable before running UI tests"""
    import requests
    base_url = test_data["base_urls"]["staging"]["web"]
    
    try:
        # Try to connect to the web app with a short timeout
        response = requests.get(
            base_url,
            timeout=(5, 5)
        )
        # Even if we get an error status, the server is reachable
    except requests.exceptions.ConnectionError:
        pytest.skip(f"Web application is unreachable at {base_url} - skipping UI tests")
    except requests.exceptions.Timeout:
        pytest.skip(f"Web application health check timed out for {base_url} - skipping UI tests")
    except Exception:
        # For other exceptions, we'll continue as it might be a legitimate server response
        pass


# -----------------------------
# Timeouts
# -----------------------------

NAVIGATION_TIMEOUT = 15000
ELEMENT_TIMEOUT = 10000
QUICK_TIMEOUT = 5000


# -----------------------------
# Browser / Page fixtures
# -----------------------------

@pytest.fixture
def robust_context(browser: Browser) -> BrowserContext:
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        locale="en-US",
        timezone_id="America/New_York",
    )
    context.set_default_timeout(ELEMENT_TIMEOUT)
    context.set_default_navigation_timeout(NAVIGATION_TIMEOUT)

    yield context
    context.close()


@pytest.fixture
def robust_page(robust_context: BrowserContext) -> Page:
    page = robust_context.new_page()
    yield page


# -----------------------------
# LOGIN TESTS
# -----------------------------

class TestRobustLogin:

    @pytest.mark.ui
    @pytest.mark.smoke
    @pytest.mark.auth
    def test_user_login(self, robust_page: Page, test_data, base_url):
        user = test_data["test_users"]["tenant_a_member"]
        selectors = test_data["ui_selectors"]["login"]

        robust_page.goto(f"{base_url}/login", wait_until="domcontentloaded")
        robust_page.wait_for_load_state("networkidle", timeout=NAVIGATION_TIMEOUT)

        email_input = robust_page.locator(
            "[data-testid='email-input'], " + selectors["email_input"]
        ).first
        expect(email_input).to_be_visible(timeout=ELEMENT_TIMEOUT)
        email_input.fill(user["email"])

        password_input = robust_page.locator(
            "[data-testid='password-input'], " + selectors["password_input"]
        ).first
        expect(password_input).to_be_visible(timeout=ELEMENT_TIMEOUT)
        password_input.fill(user["password"])

        login_button = robust_page.locator(
            "[data-testid='login-button'], " + selectors["login_button"]
        ).first
        expect(login_button).to_be_enabled(timeout=ELEMENT_TIMEOUT)
        login_button.click()

        # Handle optional OTP
        try:
            otp_selector = "[data-testid='otp-input'], " + selectors.get(
                "otp_input", "input[name='otp']"
            )
            otp_input = robust_page.locator(otp_selector).first

            if otp_input.is_visible(timeout=QUICK_TIMEOUT):
                if user.get("totp_secret"):
                    self._handle_2fa(robust_page, user, selectors)
                else:
                    pytest.skip("2FA required but no TOTP secret provided")
        except PlaywrightTimeoutError:
            pass

        robust_page.wait_for_url("**/projects", timeout=NAVIGATION_TIMEOUT)
        assert "/projects" in robust_page.url


    def _handle_2fa(self, page: Page, user: dict, selectors: dict):
        totp = pyotp.TOTP(user["totp_secret"])
        otp_code = totp.now()

        otp_input = page.locator(
            "[data-testid='otp-input'], " + selectors.get(
                "otp_input", "input[name='otp']"
            )
        ).first
        expect(otp_input).to_be_visible(timeout=ELEMENT_TIMEOUT)
        otp_input.fill(otp_code)

        verify_button = page.locator(
            "[data-testid='verify-2fa-button'], button:has-text('Verify')"
        ).first
        expect(verify_button).to_be_enabled(timeout=ELEMENT_TIMEOUT)
        verify_button.click()


# -----------------------------
# INVALID LOGIN
# -----------------------------

class TestInvalidLogin:

    @pytest.mark.ui
    @pytest.mark.auth
    def test_login_with_invalid_credentials(self, robust_page: Page, test_data, base_url):
        selectors = test_data["ui_selectors"]["login"]

        robust_page.goto(f"{base_url}/login", wait_until="domcontentloaded")

        robust_page.locator(selectors["email_input"]).fill("invalid@example.com")
        robust_page.locator(selectors["password_input"]).fill("WrongPassword123!")
        robust_page.locator(selectors["login_button"]).click()

        error_locator = robust_page.locator(
            selectors.get("error_message", ".error-message")
        ).first

        expect(error_locator).to_be_visible(timeout=ELEMENT_TIMEOUT)


# -----------------------------
# MULTI-TENANT TESTS
# -----------------------------

class TestRobustMultiTenant:

    @pytest.mark.ui
    @pytest.mark.tenant
    def test_multi_tenant_access(self, robust_page: Page, test_data, base_url):
        user = test_data["test_users"]["tenant_a_admin"]
        self._login(robust_page, user, test_data, base_url)

        robust_page.goto(f"{base_url}/projects")
        expect(robust_page).to_have_url("**/projects")


    def _login(self, page: Page, user: dict, test_data, base_url):
        selectors = test_data["ui_selectors"]["login"]

        page.goto(f"{base_url}/login", wait_until="domcontentloaded")

        page.locator(selectors["email_input"]).fill(user["email"])
        page.locator(selectors["password_input"]).fill(user["password"])
        page.locator(selectors["login_button"]).click()

        if user.get("totp_secret"):
            totp = pyotp.TOTP(user["totp_secret"])
            otp_input = page.locator(
                selectors.get("otp_input", "input[name='otp']")
            ).first
            if otp_input.is_visible(timeout=QUICK_TIMEOUT):
                otp_input.fill(totp.now())
                page.locator("button:has-text('Verify')").click()

        page.wait_for_url("**/projects", timeout=NAVIGATION_TIMEOUT)


# -----------------------------
# LOGOUT
# -----------------------------

class TestLogout:

    @pytest.mark.ui
    @pytest.mark.auth
    def test_logout(self, robust_page: Page, test_data, base_url):
        user = test_data["test_users"]["tenant_a_member"]
        selectors = test_data["ui_selectors"]["navigation"]

        helper = TestRobustMultiTenant()
        helper._login(robust_page, user, test_data, base_url)

        logout_button = robust_page.locator(
            selectors.get("logout_button", "button:has-text('Logout')")
        ).first

        expect(logout_button).to_be_visible(timeout=ELEMENT_TIMEOUT)
        logout_button.click()

        robust_page.wait_for_url("**/login", timeout=NAVIGATION_TIMEOUT)
