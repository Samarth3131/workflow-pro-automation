import pytest
import json
import requests
import time
import os
from pathlib import Path
from playwright.sync_api import Page, Browser, expect, TimeoutError as PlaywrightTimeoutError

TEST_DATA_PATH = Path(__file__).parent.parent / "data" / "test_data.json"
with open(TEST_DATA_PATH) as f:
    TEST_DATA = json.load(f)

BASE_URL = os.getenv("BASE_URL", TEST_DATA["base_urls"]["staging"]["web"])
API_BASE_URL = os.getenv("API_BASE_URL", TEST_DATA["base_urls"]["staging"]["api"])
AUTH_TOKEN = os.getenv("AUTH_TOKEN", "fake_token_replace_with_real")
TENANT_A_ID = os.getenv("TENANT_A_ID", TEST_DATA["test_users"]["tenant_a_admin"]["tenant_id"])
TENANT_B_ID = os.getenv("TENANT_B_ID", TEST_DATA["test_users"]["tenant_b_admin"]["tenant_id"])

API_TIMEOUT = 30
UI_TIMEOUT = 15000
ELEMENT_TIMEOUT = 10000


class TestProjectCreationFlow:
    
    @pytest.mark.integration
    @pytest.mark.smoke
    def test_api_create_ui_verify_with_mobile(self, browser: Browser):
        project_id = None
        
        try:
            project_name = f"IntegrationTest_{int(time.time())}"
            project_data = {
                "name": project_name,
                "description": "Integration test project",
                "status": "active"
            }
            
            create_response = requests.post(
                f"{API_BASE_URL}/api/v1/projects",
                json=project_data,
                headers={
                    "Authorization": f"Bearer {AUTH_TOKEN}",
                    "X-Tenant-ID": TENANT_A_ID,
                    "Content-Type": "application/json"
                },
                timeout=API_TIMEOUT
            )
            
            assert create_response.status_code == 201, f"Project creation failed: {create_response.status_code}"
            
            project_response = create_response.json()
            project_id = project_response.get("id") or project_response.get("project_id")
            
            assert project_id, f"No project ID in response: {project_response}"
            
            time.sleep(2)
            
            desktop_context = browser.new_context(
                viewport={'width': 1920, 'height': 1080}
            )
            desktop_page = desktop_context.new_page()
            
            try:
                self._login(desktop_page, TENANT_A_ID)
                
                desktop_page.goto(f"{BASE_URL}/projects", wait_until="domcontentloaded")
                desktop_page.wait_for_load_state("networkidle", timeout=UI_TIMEOUT)
                desktop_page.wait_for_timeout(2000)
                
                project_selectors = [
                    f"[data-testid='project-{project_id}']",
                    f"text={project_name}",
                    f".project-card:has-text('{project_name}')"
                ]
                
                project_found = False
                for selector in project_selectors:
                    try:
                        element = desktop_page.locator(selector).first
                        if element.is_visible(timeout=5000):
                            project_found = True
                            break
                    except PlaywrightTimeoutError:
                        continue
                
                assert project_found, f"Project '{project_name}' not found in Desktop UI"
                
            finally:
                desktop_context.close()
            
            mobile_context = browser.new_context(**browser.devices['iPhone 12'])
            mobile_page = mobile_context.new_page()
            
            try:
                self._login(mobile_page, TENANT_A_ID)
                
                mobile_page.goto(f"{BASE_URL}/projects", wait_until="domcontentloaded")
                mobile_page.wait_for_load_state("networkidle", timeout=UI_TIMEOUT)
                mobile_page.wait_for_timeout(2000)
                
                mobile_project_found = False
                for selector in project_selectors:
                    try:
                        element = mobile_page.locator(selector).first
                        if element.is_visible(timeout=5000):
                            mobile_project_found = True
                            break
                    except PlaywrightTimeoutError:
                        continue
                
                assert mobile_project_found, f"Project not visible on mobile"
                
            finally:
                mobile_context.close()
            
            tenant_b_context = browser.new_context(viewport={'width': 1920, 'height': 1080})
            tenant_b_page = tenant_b_context.new_page()
            
            try:
                self._login(tenant_b_page, TENANT_B_ID)
                
                tenant_b_page.goto(f"{BASE_URL}/projects", wait_until="domcontentloaded")
                tenant_b_page.wait_for_load_state("networkidle", timeout=UI_TIMEOUT)
                tenant_b_page.wait_for_timeout(2000)
                
                project_visible_in_tenant_b = False
                for selector in project_selectors:
                    try:
                        element = tenant_b_page.locator(selector).first
                        if element.is_visible(timeout=3000):
                            project_visible_in_tenant_b = True
                            break
                    except PlaywrightTimeoutError:
                        continue
                
                tenant_b_api_response = requests.get(
                    f"{API_BASE_URL}/api/v1/projects",
                    headers={
                        "Authorization": f"Bearer {AUTH_TOKEN}",
                        "X-Tenant-ID": TENANT_B_ID
                    },
                    timeout=API_TIMEOUT
                )
                
                if tenant_b_api_response.status_code == 200:
                    tenant_b_projects = tenant_b_api_response.json()
                    tenant_b_project_ids = [p.get("id") or p.get("project_id") for p in tenant_b_projects]
                    
                    api_isolation_violated = project_id in tenant_b_project_ids
                    
                    assert not project_visible_in_tenant_b and not api_isolation_violated, \
                        f"Tenant isolation violated! Project visible in Tenant B"
                
            finally:
                tenant_b_context.close()
            
        finally:
            if project_id:
                try:
                    delete_response = requests.delete(
                        f"{API_BASE_URL}/api/v1/projects/{project_id}",
                        headers={
                            "Authorization": f"Bearer {AUTH_TOKEN}",
                            "X-Tenant-ID": TENANT_A_ID
                        },
                        timeout=API_TIMEOUT
                    )
                except Exception as e:
                    print(f"Cleanup error: {e}")
    
    @pytest.mark.integration
    def test_project_not_visible_across_tenants_api_only(self):
        project_id = None
        
        try:
            project_data = {
                "name": f"TenantIsolationTest_{int(time.time())}",
                "description": "Testing tenant isolation"
            }
            
            create_resp = requests.post(
                f"{API_BASE_URL}/api/v1/projects",
                json=project_data,
                headers={
                    "Authorization": f"Bearer {AUTH_TOKEN}",
                    "X-Tenant-ID": TENANT_A_ID
                },
                timeout=API_TIMEOUT
            )
            
            assert create_resp.status_code == 201
            project_id = create_resp.json().get("id") or create_resp.json().get("project_id")
            
            get_resp = requests.get(
                f"{API_BASE_URL}/api/v1/projects/{project_id}",
                headers={
                    "Authorization": f"Bearer {AUTH_TOKEN}",
                    "X-Tenant-ID": TENANT_B_ID
                },
                timeout=API_TIMEOUT
            )
            
            assert get_resp.status_code in [403, 404], \
                f"Tenant isolation violated! Expected 403/404, got {get_resp.status_code}"
            
        finally:
            if project_id:
                requests.delete(
                    f"{API_BASE_URL}/api/v1/projects/{project_id}",
                    headers={
                        "Authorization": f"Bearer {AUTH_TOKEN}",
                        "X-Tenant-ID": TENANT_A_ID
                    },
                    timeout=API_TIMEOUT
                )
    
    def _login(self, page: Page, tenant_id: str):
        user_email = os.getenv("TENANT_A_USER_EMAIL")
        user_password = os.getenv("TENANT_A_USER_PASSWORD")
        
        if not user_email or not user_password:
            if tenant_id == TENANT_A_ID:
                user = TEST_DATA["test_users"]["tenant_a_admin"]
            elif tenant_id == TENANT_B_ID:
                user = TEST_DATA["test_users"]["tenant_b_admin"]
            else:
                user = TEST_DATA["test_users"]["tenant_a_admin"]
            
            user_email = user["email"]
            user_password = user["password"]
        
        selectors = TEST_DATA["ui_selectors"]["login"]
        
        page.goto(f"{BASE_URL}/login", wait_until="domcontentloaded")
        page.wait_for_load_state("networkidle", timeout=UI_TIMEOUT)
        
        email_input = page.locator(
            f"[data-testid='email-input'], {selectors['email_input']}"
        ).first
        expect(email_input).to_be_visible(timeout=ELEMENT_TIMEOUT)
        email_input.fill(user_email)
        
        password_input = page.locator(
            f"[data-testid='password-input'], {selectors['password_input']}"
        ).first
        expect(password_input).to_be_visible(timeout=ELEMENT_TIMEOUT)
        password_input.fill(user_password)
        
        login_button = page.locator(
            f"[data-testid='login-button'], {selectors['login_button']}"
        ).first
        expect(login_button).to_be_enabled(timeout=ELEMENT_TIMEOUT)
        login_button.click()
        
        try:
            page.wait_for_url("**/projects", timeout=UI_TIMEOUT, wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle", timeout=UI_TIMEOUT)
        except PlaywrightTimeoutError:
            current_url = page.url
            if "/login" in current_url:
                raise AssertionError(f"Login failed - still on login page: {current_url}")
