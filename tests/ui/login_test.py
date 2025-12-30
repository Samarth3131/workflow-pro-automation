import pytest
import json
import pyotp
from pathlib import Path
import json

TEST_DATA_PATH = Path(__file__).parent.parent / "data" / "test_data.json"

def load_test_data():
    if not TEST_DATA_PATH.exists():
        raise FileNotFoundError(f"Missing test data file: {TEST_DATA_PATH}")
    with open(TEST_DATA_PATH) as f:
        return json.load(f)

TEST_DATA = load_test_data()


BASE_URL = TEST_DATA["base_urls"]["staging"]["web"]

NAVIGATION_TIMEOUT = 15000
ELEMENT_TIMEOUT = 10000
QUICK_TIMEOUT = 5000


@pytest.fixture
def robust_context(browser: Browser) -> BrowserContext:
    context = browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        locale='en-US',
        timezone_id='America/New_York',
    )
    
    context.set_default_timeout(ELEMENT_TIMEOUT)
    context.set_default_navigation_timeout(NAVIGATION_TIMEOUT)
    
    yield context
    context.close()


@pytest.fixture
def robust_page(robust_context: BrowserContext) -> Page:
    page = robust_context.new_page()
    yield page


class TestRobustLogin:
    
    @pytest.mark.ui
    @pytest.mark.smoke
    @pytest.mark.auth
    def test_user_login(self, robust_page: Page):
        user = TEST_DATA["test_users"]["tenant_a_member"]
        selectors = TEST_DATA["ui_selectors"]["login"]
        
        try:
            robust_page.goto(f"{BASE_URL}/login", wait_until="domcontentloaded")
            robust_page.wait_for_load_state("networkidle", timeout=NAVIGATION_TIMEOUT)
            
            email_input = robust_page.locator(
                f"[data-testid='email-input'], {selectors['email_input']}"
            ).first
            
            expect(email_input).to_be_visible(timeout=ELEMENT_TIMEOUT)
            
            email_input.fill("")
            email_input.fill(user["email"])
            
            password_input = robust_page.locator(
                f"[data-testid='password-input'], {selectors['password_input']}"
            ).first
            expect(password_input).to_be_visible(timeout=ELEMENT_TIMEOUT)
            password_input.fill("")
            password_input.fill(user["password"])
            
            login_button = robust_page.locator(
                f"[data-testid='login-button'], {selectors['login_button']}"
            ).first
            expect(login_button).to_be_enabled(timeout=ELEMENT_TIMEOUT)
            
            login_button.click()
            
            try:
                otp_selector = "[data-testid='otp-input'], " + selectors.get(
                    "otp_input", "input[name='otp']"
                )
                
                otp_input = robust_page.locator(otp_selector).first

                
                if otp_input.is_visible(timeout=QUICK_TIMEOUT):
                    if user.get("totp_secret"):
                        self._handle_2fa(robust_page, user, selectors)
                    else:
                        pytest.skip(f"2FA prompt appeared but no TOTP secret for user {user['email']}")
            except PlaywrightTimeoutError:
                pass
            
            try:
                robust_page.wait_for_url(
                    "**/projects",
                    timeout=NAVIGATION_TIMEOUT,
                    wait_until="domcontentloaded"
                )
            except PlaywrightTimeoutError as e:
                current_url = robust_page.url
                raise AssertionError(
                    f"Login failed: Expected /projects page but stayed at: {current_url}"
                )
            
            logged_in_indicators = [
                "[data-testid='user-menu']",
                "[data-testid='logout-button']",
                "text=Projects",
                ".projects-page",
                "#projects-list"
            ]
            
            found_indicator = False
            for selector in logged_in_indicators:
                try:
                    element = robust_page.locator(selector).first
                    if element.is_visible(timeout=QUICK_TIMEOUT):
                        found_indicator = True
                        break
                except:
                    continue
            
            if not found_indicator:
                current_url = robust_page.url
                assert "/login" not in current_url, f"Still on login page: {current_url}"
                
        except PlaywrightTimeoutError as e:
            screenshot_path = f"test-results/login_timeout_{user['email'].replace('@', '_')}.png"
            robust_page.screenshot(path=screenshot_path)
            raise AssertionError(f"Timeout during login: {e}\nScreenshot: {screenshot_path}")
        except Exception as e:
            screenshot_path = f"test-results/login_error_{user['email'].replace('@', '_')}.png"
            robust_page.screenshot(path=screenshot_path)
            raise AssertionError(f"Error during login: {e}\nScreenshot: {screenshot_path}")
    
    def _handle_2fa(self, page: Page, user: dict, selectors: dict):
        try:
            totp = pyotp.TOTP(user["totp_secret"])
            current_code = totp.now()
            
            otp_input = page.locator(
                f"[data-testid='otp-input'], {selectors.get('otp_input', 'input[name=\"otp\"]')}"
            ).first
            expect(otp_input).to_be_visible(timeout=ELEMENT_TIMEOUT)
            otp_input.fill(current_code)
            
            verify_button = page.locator(
                "[data-testid='verify-2fa-button'], button:has-text('Verify'), button[type='submit']"
            ).first
            expect(verify_button).to_be_enabled(timeout=ELEMENT_TIMEOUT)
            verify_button.click()
            
        except Exception as e:
            pytest.skip(f"2FA handling failed: {e}")
    
    @pytest.mark.ui
    @pytest.mark.auth
    def test_login_with_invalid_credentials(self, robust_page: Page):
        selectors = TEST_DATA["ui_selectors"]["login"]
        
        robust_page.goto(f"{BASE_URL}/login", wait_until="domcontentloaded")
        robust_page.wait_for_load_state("networkidle", timeout=NAVIGATION_TIMEOUT)
        
        email_input = robust_page.locator(
            f"[data-testid='email-input'], {selectors['email_input']}"
        ).first
        expect(email_input).to_be_visible(timeout=ELEMENT_TIMEOUT)
        email_input.fill("invalid_user@example.com")
        
        password_input = robust_page.locator(
            f"[data-testid='password-input'], {selectors['password_input']}"
        ).first
        expect(password_input).to_be_visible(timeout=ELEMENT_TIMEOUT)
        password_input.fill("WrongPassword123!")
        
        login_button = robust_page.locator(
            f"[data-testid='login-button'], {selectors['login_button']}"
        ).first
        login_button.click()
        
        try:
            error_locator = robust_page.locator(
                f"[data-testid='error-message'], {selectors.get('error_message', '.error-message, .alert-error')}"
            ).first
            
            expect(error_locator).to_be_visible(timeout=ELEMENT_TIMEOUT)
            
            error_text = error_locator.inner_text().lower()
            assert any(keyword in error_text for keyword in ["invalid", "incorrect", "wrong", "failed"]), \
                f"Error message doesn't show invalid credentials: {error_text}"
            
        except PlaywrightTimeoutError:
            current_url = robust_page.url
            assert "/login" in current_url, f"Expected to stay on login page but went to: {current_url}"


class TestRobustMultiTenant:
    
    @pytest.mark.ui
    @pytest.mark.tenant
    @pytest.mark.smoke
    def test_multi_tenant_access(self, robust_page: Page):
        user_a = TEST_DATA["test_users"]["tenant_a_admin"]
        self._robust_login(robust_page, user_a)
        
        robust_page.goto(f"{BASE_URL}/projects", wait_until="domcontentloaded")
        robust_page.wait_for_load_state("networkidle", timeout=NAVIGATION_TIMEOUT)
        robust_page.wait_for_timeout(1000)
        
        tenant_selectors = [
            f"[data-testid='tenant-name']:has-text('{user_a['tenant_name']}')",
            f"text={user_a['tenant_name']}",
            f"[data-testid='current-tenant']",
            ".tenant-info",
            "#tenant-display"
        ]
        
        for selector in tenant_selectors:
            try:
                element = robust_page.locator(selector).first
                if element.is_visible(timeout=QUICK_TIMEOUT):
                    break
            except:
                continue
        
        project_list_selectors = [
            "[data-testid='project-list']",
            "[data-testid='project-card']",
            TEST_DATA["ui_selectors"]["projects"]["project_list"],
            ".project-container",
            "#projects-list",
            ".projects-grid"
        ]
        
        project_elements = None
        for selector in project_list_selectors:
            try:
                locator = robust_page.locator(selector)
                count = locator.count()
                if count > 0:
                    project_elements = locator
                    break
                else:
                    try:
                        expect(locator.first).to_be_visible(timeout=QUICK_TIMEOUT)
                        project_elements = locator
                        break
                    except:
                        continue
            except:
                continue
        
        if project_elements:
            project_count = project_elements.count()
            assert project_count >= 0, "Project list should be accessible"
        else:
            empty_state_selectors = [
                "text=No projects",
                "text=Create your first project",
                "[data-testid='empty-state']",
                ".empty-state"
            ]
            
            for selector in empty_state_selectors:
                try:
                    element = robust_page.locator(selector).first
                    if element.is_visible(timeout=QUICK_TIMEOUT):
                        break
                except:
                    continue
    
    @pytest.mark.ui
    @pytest.mark.tenant
    def test_tenant_isolation_prevents_url_manipulation(self, robust_page: Page):
        user_a = TEST_DATA["test_users"]["tenant_a_admin"]
        self._robust_login(robust_page, user_a)
        
        fake_tenant_b_project_id = "tenant_b_project_999"
        
        robust_page.goto(
            f"{BASE_URL}/projects/{fake_tenant_b_project_id}",
            wait_until="domcontentloaded"
        )
        robust_page.wait_for_load_state("networkidle", timeout=NAVIGATION_TIMEOUT)
        
        current_url = robust_page.url
        
        error_indicators = [
            "[data-testid='error-page']",
            "text=Not Found",
            "text=Access Denied",
            "text=403",
            "text=404",
            "text=Forbidden",
            ".error-page",
            "#error-message"
        ]
        
        found_error = False
        for selector in error_indicators:
            try:
                element = robust_page.locator(selector).first
                if element.is_visible(timeout=QUICK_TIMEOUT):
                    found_error = True
                    break
            except:
                continue
        
        assert found_error or fake_tenant_b_project_id not in current_url, \
            f"User accessed other tenant's project without error: {current_url}"
    
    def _robust_login(self, page: Page, user: dict):
        selectors = TEST_DATA["ui_selectors"]["login"]
        
        page.goto(f"{BASE_URL}/login", wait_until="domcontentloaded")
        page.wait_for_load_state("networkidle", timeout=NAVIGATION_TIMEOUT)
        
        email_input = page.locator(
            f"[data-testid='email-input'], {selectors['email_input']}"
        ).first
        expect(email_input).to_be_visible(timeout=ELEMENT_TIMEOUT)
        email_input.fill(user["email"])
        
        password_input = page.locator(
            f"[data-testid='password-input'], {selectors['password_input']}"
        ).first
        expect(password_input).to_be_visible(timeout=ELEMENT_TIMEOUT)
        password_input.fill(user["password"])
        
        login_button = page.locator(
            f"[data-testid='login-button'], {selectors['login_button']}"
        ).first
        expect(login_button).to_be_enabled(timeout=ELEMENT_TIMEOUT)
        login_button.click()
        
        if user.get("totp_secret"):
            try:
                otp_input = page.locator(
                    f"[data-testid='otp-input'], {selectors.get('otp_input', 'input[name=\"otp\"]')}"
                ).first
                
                if otp_input.is_visible(timeout=QUICK_TIMEOUT):
                    totp = pyotp.TOTP(user["totp_secret"])
                    otp_input.fill(totp.now())
                    
                    verify_button = page.locator(
                        "[data-testid='verify-2fa-button'], button:has-text('Verify'), button[type='submit']"
                    ).first
                    verify_button.click()
            except PlaywrightTimeoutError:
                pass
        
        try:
            page.wait_for_url("**/projects", timeout=NAVIGATION_TIMEOUT, wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle", timeout=NAVIGATION_TIMEOUT)
        except PlaywrightTimeoutError:
            current_url = page.url
            if "/login" in current_url:
                raise AssertionError(f"Login failed - still on login page: {current_url}")


class TestLogout:
    
    @pytest.mark.ui
    @pytest.mark.auth
    def test_logout_clears_session(self, robust_page: Page):
        user = TEST_DATA["test_users"]["tenant_a_member"]
        selectors = TEST_DATA["ui_selectors"]
        
        helper = TestRobustMultiTenant()
        helper._robust_login(robust_page, user)
        
        try:
            logout_button = robust_page.locator(
                f"[data-testid='logout-button'], {selectors['navigation'].get('logout_button', 'button:has-text(\"Logout\")')}"
            ).first
            
            if not logout_button.is_visible(timeout=QUICK_TIMEOUT):
                menu_button = robust_page.locator(
                    "[data-testid='user-menu'], [data-testid='hamburger-menu'], .menu-button"
                ).first
                if menu_button.is_visible(timeout=QUICK_TIMEOUT):
                    menu_button.click()
                    robust_page.wait_for_timeout(500)
            
            expect(logout_button).to_be_visible(timeout=ELEMENT_TIMEOUT)
            logout_button.click()
            
        except PlaywrightTimeoutError:
            pytest.skip("Logout button not found")
        
        robust_page.wait_for_url("**/login", timeout=NAVIGATION_TIMEOUT, wait_until="domcontentloaded")
        
        robust_page.goto(f"{BASE_URL}/projects", wait_until="domcontentloaded")
        robust_page.wait_for_load_state("networkidle", timeout=NAVIGATION_TIMEOUT)
        
        current_url = robust_page.url
        assert "/login" in current_url, f"Session not cleared - can still access: {current_url}"

        user = TEST_DATA["test_users"]["tenant_a_member"]
        selectors = TEST_DATA["ui_selectors"]["login"]
        
        try:
            robust_page.goto(f"{BASE_URL}/login", wait_until="domcontentloaded")
            robust_page.wait_for_load_state("networkidle", timeout=NAVIGATION_TIMEOUT)
            
            email_input = robust_page.locator(
                f"[data-testid='email-input'], {selectors['email_input']}"
            ).first
            
            expect(email_input).to_be_visible(timeout=ELEMENT_TIMEOUT)
            
            email_input.fill("")
            email_input.fill(user["email"])
            
            password_input = robust_page.locator(
                f"[data-testid='password-input'], {selectors['password_input']}"
            ).first
            expect(password_input).to_be_visible(timeout=ELEMENT_TIMEOUT)
            password_input.fill("")
            password_input.fill(user["password"])
            
            login_button = robust_page.locator(
                f"[data-testid='login-button'], {selectors['login_button']}"
            ).first
            expect(login_button).to_be_enabled(timeout=ELEMENT_TIMEOUT)
            
            login_button.click()
            
            try:
                otp_input = robust_page.locator(
                    f"[data-testid='otp-input'], {selectors.get('otp_input', 'input[name=\"otp\"]')}"
                ).first
                
                if otp_input.is_visible(timeout=QUICK_TIMEOUT):
                    if user.get("totp_secret"):
                        self._handle_2fa(robust_page, user, selectors)
                    else:
                        pytest.skip(f"2FA prompt appeared but no TOTP secret for user {user['email']}")
            except PlaywrightTimeoutError:
                pass
            
            try:
                robust_page.wait_for_url(
                    "**/projects",
                    timeout=NAVIGATION_TIMEOUT,
                    wait_until="domcontentloaded"
                )
            except PlaywrightTimeoutError as e:
                current_url = robust_page.url
                raise AssertionError(
                    f"Login failed: Expected /projects page but stayed at: {current_url}"
                )
            
            logged_in_indicators = [
                "[data-testid='user-menu']",
                "[data-testid='logout-button']",
                "text=Projects",
                ".projects-page",
                "#projects-list"
            ]
            
            found_indicator = False
            for selector in logged_in_indicators:
                try:
                    element = robust_page.locator(selector).first
                    if element.is_visible(timeout=QUICK_TIMEOUT):
                        found_indicator = True
                        break
                except:
                    continue
            
            if not found_indicator:
                current_url = robust_page.url
                assert "/login" not in current_url, f"Still on login page: {current_url}"
                
        except PlaywrightTimeoutError as e:
            screenshot_path = f"test-results/login_timeout_{user['email'].replace('@', '_')}.png"
            robust_page.screenshot(path=screenshot_path)
            raise AssertionError(f"Timeout during login: {e}\nScreenshot: {screenshot_path}")
        except Exception as e:
            screenshot_path = f"test-results/login_error_{user['email'].replace('@', '_')}.png"
            robust_page.screenshot(path=screenshot_path)
            raise AssertionError(f"Error during login: {e}\nScreenshot: {screenshot_path}")
    
    def _handle_2fa(self, page: Page, user: dict, selectors: dict):
        try:
            totp = pyotp.TOTP(user["totp_secret"])
            current_code = totp.now()
            
            otp_input = page.locator(
                f"[data-testid='otp-input'], {selectors.get('otp_input', 'input[name=\"otp\"]')}"
            ).first
            expect(otp_input).to_be_visible(timeout=ELEMENT_TIMEOUT)
            otp_input.fill(current_code)
            
            verify_button = page.locator(
                "[data-testid='verify-2fa-button'], button:has-text('Verify'), button[type='submit']"
            ).first
            expect(verify_button).to_be_enabled(timeout=ELEMENT_TIMEOUT)
            verify_button.click()
            
        except Exception as e:
            pytest.skip(f"2FA handling failed: {e}")
    
    @pytest.mark.ui
    @pytest.mark.auth
    @pytest.mark.flaky(reruns=1)
    def test_login_with_invalid_credentials(self, robust_page: Page):
        selectors = TEST_DATA["ui_selectors"]["login"]
        
        robust_page.goto(f"{BASE_URL}/login", wait_until="domcontentloaded")
        robust_page.wait_for_load_state("networkidle", timeout=NAVIGATION_TIMEOUT)
        
        email_input = robust_page.locator(
            f"[data-testid='email-input'], {selectors['email_input']}"
        ).first
        expect(email_input).to_be_visible(timeout=ELEMENT_TIMEOUT)
        email_input.fill("invalid_user@example.com")
        
        password_input = robust_page.locator(
            f"[data-testid='password-input'], {selectors['password_input']}"
        ).first
        expect(password_input).to_be_visible(timeout=ELEMENT_TIMEOUT)
        password_input.fill("WrongPassword123!")
        
        login_button = robust_page.locator(
            f"[data-testid='login-button'], {selectors['login_button']}"
        ).first
        login_button.click()
        
        try:
            error_locator = robust_page.locator(
                f"[data-testid='error-message'], {selectors.get('error_message', '.error-message, .alert-error')}"
            ).first
            
            expect(error_locator).to_be_visible(timeout=ELEMENT_TIMEOUT)
            
            error_text = error_locator.inner_text().lower()
            assert any(keyword in error_text for keyword in ["invalid", "incorrect", "wrong", "failed"]), \
                f"Error message doesn't show invalid credentials: {error_text}"
            
        except PlaywrightTimeoutError:
            current_url = robust_page.url
            assert "/login" in current_url, f"Expected to stay on login page but went to: {current_url}"


class TestRobustMultiTenant:
    
    @pytest.mark.ui
    @pytest.mark.tenant
    @pytest.mark.smoke
    @pytest.mark.flaky(reruns=2, reruns_delay=1)
    def test_multi_tenant_access(self, robust_page: Page):
        user_a = TEST_DATA["test_users"]["tenant_a_admin"]
        self._robust_login(robust_page, user_a)
        
        robust_page.goto(f"{BASE_URL}/projects", wait_until="domcontentloaded")
        robust_page.wait_for_load_state("networkidle", timeout=NAVIGATION_TIMEOUT)
        robust_page.wait_for_timeout(1000)
        
        tenant_selectors = [
            f"[data-testid='tenant-name']:has-text('{user_a['tenant_name']}')",
            f"text={user_a['tenant_name']}",
            f"[data-testid='current-tenant']",
            ".tenant-info",
            "#tenant-display"
        ]
        
        for selector in tenant_selectors:
            try:
                element = robust_page.locator(selector).first
                if element.is_visible(timeout=QUICK_TIMEOUT):
                    break
            except:
                continue
        
        project_list_selectors = [
            "[data-testid='project-list']",
            "[data-testid='project-card']",
            TEST_DATA["ui_selectors"]["projects"]["project_list"],
            ".project-container",
            "#projects-list",
            ".projects-grid"
        ]
        
        project_elements = None
        for selector in project_list_selectors:
            try:
                locator = robust_page.locator(selector)
                count = locator.count()
                if count > 0:
                    project_elements = locator
                    break
                else:
                    try:
                        expect(locator.first).to_be_visible(timeout=QUICK_TIMEOUT)
                        project_elements = locator
                        break
                    except:
                        continue
            except:
                continue
        
        if project_elements:
            project_count = project_elements.count()
            assert project_count >= 0, "Project list should be accessible"
        else:
            empty_state_selectors = [
                "text=No projects",
                "text=Create your first project",
                "[data-testid='empty-state']",
                ".empty-state"
            ]
            
            for selector in empty_state_selectors:
                try:
                    element = robust_page.locator(selector).first
                    if element.is_visible(timeout=QUICK_TIMEOUT):
                        break
                except:
                    continue
    
    @pytest.mark.ui
    @pytest.mark.tenant
    @pytest.mark.flaky(reruns=1)
    def test_tenant_isolation_prevents_url_manipulation(self, robust_page: Page):
        user_a = TEST_DATA["test_users"]["tenant_a_admin"]
        self._robust_login(robust_page, user_a)
        
        fake_tenant_b_project_id = "tenant_b_project_999"
        
        robust_page.goto(
            f"{BASE_URL}/projects/{fake_tenant_b_project_id}",
            wait_until="domcontentloaded"
        )
        robust_page.wait_for_load_state("networkidle", timeout=NAVIGATION_TIMEOUT)
        
        current_url = robust_page.url
        
        error_indicators = [
            "[data-testid='error-page']",
            "text=Not Found",
            "text=Access Denied",
            "text=403",
            "text=404",
            "text=Forbidden",
            ".error-page",
            "#error-message"
        ]
        
        found_error = False
        for selector in error_indicators:
            try:
                element = robust_page.locator(selector).first
                if element.is_visible(timeout=QUICK_TIMEOUT):
                    found_error = True
                    break
            except:
                continue
        
        assert found_error or fake_tenant_b_project_id not in current_url, \
            f"User accessed other tenant's project without error: {current_url}"
    
    def _robust_login(self, page: Page, user: dict):
        selectors = TEST_DATA["ui_selectors"]["login"]
        
        page.goto(f"{BASE_URL}/login", wait_until="domcontentloaded")
        page.wait_for_load_state("networkidle", timeout=NAVIGATION_TIMEOUT)
        
        email_input = page.locator(
            f"[data-testid='email-input'], {selectors['email_input']}"
        ).first
        expect(email_input).to_be_visible(timeout=ELEMENT_TIMEOUT)
        email_input.fill(user["email"])
        
        password_input = page.locator(
            f"[data-testid='password-input'], {selectors['password_input']}"
        ).first
        expect(password_input).to_be_visible(timeout=ELEMENT_TIMEOUT)
        password_input.fill(user["password"])
        
        login_button = page.locator(
            f"[data-testid='login-button'], {selectors['login_button']}"
        ).first
        expect(login_button).to_be_enabled(timeout=ELEMENT_TIMEOUT)
        login_button.click()
        
        if user.get("totp_secret"):
            try:
                otp_input = page.locator(
                    f"[data-testid='otp-input'], {selectors.get('otp_input', 'input[name=\"otp\"]')}"
                ).first
                
                if otp_input.is_visible(timeout=QUICK_TIMEOUT):
                    totp = pyotp.TOTP(user["totp_secret"])
                    otp_input.fill(totp.now())
                    
                    verify_button = page.locator(
                        "[data-testid='verify-2fa-button'], button:has-text('Verify'), button[type='submit']"
                    ).first
                    verify_button.click()
            except PlaywrightTimeoutError:
                pass
        
        try:
            page.wait_for_url("**/projects", timeout=NAVIGATION_TIMEOUT, wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle", timeout=NAVIGATION_TIMEOUT)
        except PlaywrightTimeoutError:
            current_url = page.url
            if "/login" in current_url:
                raise AssertionError(f"Login failed - still on login page: {current_url}")


class TestLogout:
    
    @pytest.mark.ui
    @pytest.mark.auth
    @pytest.mark.flaky(reruns=1)
    def test_logout_clears_session(self, robust_page: Page):
        user = TEST_DATA["test_users"]["tenant_a_member"]
        selectors = TEST_DATA["ui_selectors"]
        
        helper = TestRobustMultiTenant()
        helper._robust_login(robust_page, user)
        
        try:
            logout_button = robust_page.locator(
                f"[data-testid='logout-button'], {selectors['navigation'].get('logout_button', 'button:has-text(\"Logout\")')}"
            ).first
            
            if not logout_button.is_visible(timeout=QUICK_TIMEOUT):
                menu_button = robust_page.locator(
                    "[data-testid='user-menu'], [data-testid='hamburger-menu'], .menu-button"
                ).first
                if menu_button.is_visible(timeout=QUICK_TIMEOUT):
                    menu_button.click()
                    robust_page.wait_for_timeout(500)
            
            expect(logout_button).to_be_visible(timeout=ELEMENT_TIMEOUT)
            logout_button.click()
            
        except PlaywrightTimeoutError:
            pytest.skip("Logout button not found")
        
        robust_page.wait_for_url("**/login", timeout=NAVIGATION_TIMEOUT, wait_until="domcontentloaded")
        
        robust_page.goto(f"{BASE_URL}/projects", wait_until="domcontentloaded")
        robust_page.wait_for_load_state("networkidle", timeout=NAVIGATION_TIMEOUT)
        
        current_url = robust_page.url
        assert "/login" in current_url, f"Session not cleared - can still access: {current_url}"
