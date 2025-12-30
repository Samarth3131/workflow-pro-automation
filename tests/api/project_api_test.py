import pytest
import requests
import json
from pathlib import Path

TEST_DATA_PATH = Path(__file__).parent.parent / "data" / "test_data.json"
with open(TEST_DATA_PATH) as f:
    TEST_DATA = json.load(f)

API_BASE_URL = TEST_DATA["base_urls"]["staging"]["api"]

# Timeout configuration
CONNECTION_TIMEOUT = 10  # seconds for initial connection
READ_TIMEOUT = 30  # seconds for reading response


class TestProjectAPI:
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.tenant_a_token = "fake_token_tenant_a"
        self.tenant_b_token = "fake_token_tenant_b"
        
        self.tenant_a_id = TEST_DATA["test_users"]["tenant_a_admin"]["tenant_id"]
        self.tenant_b_id = TEST_DATA["test_users"]["tenant_b_admin"]["tenant_id"]
        
        self.created_project_ids = []
        
        yield
        
        for project_id in self.created_project_ids:
            try:
                requests.delete(
                    f"{API_BASE_URL}/api/projects/{project_id}",
                    headers={"Authorization": f"Bearer {self.tenant_a_token}"},
                    timeout=(CONNECTION_TIMEOUT, READ_TIMEOUT)
                )
            except:
                pass
    
    @pytest.mark.api
    @pytest.mark.smoke
    def test_create_project_returns_201(self):
        project_data = {
            "name": "API Test Project",
            "description": "testing project creation"
        }
        
        response = requests.post(
            f"{API_BASE_URL}/api/projects",
            json=project_data,
            headers={
                "Authorization": f"Bearer {self.tenant_a_token}",
                "X-Tenant-ID": self.tenant_a_id
            },
            timeout=(CONNECTION_TIMEOUT, READ_TIMEOUT)
        )
        
        assert response.status_code == 201, f"Expected 201 but got {response.status_code}"
        
        response_data = response.json()
        assert "id" in response_data, "Response should contain project id"
        assert response_data["name"] == project_data["name"]
        
        self.created_project_ids.append(response_data["id"])
    
    @pytest.mark.api
    def test_list_projects_for_tenant(self):
        response = requests.get(
            f"{API_BASE_URL}/api/projects",
            headers={
                "Authorization": f"Bearer {self.tenant_a_token}",
                "X-Tenant-ID": self.tenant_a_id
            },
            timeout=(CONNECTION_TIMEOUT, READ_TIMEOUT)
        )
        
        assert response.status_code == 200
        projects = response.json()
        assert isinstance(projects, list), "Response should be list of projects"
    
    @pytest.mark.api
    @pytest.mark.tenant
    def test_tenant_isolation_at_api_level(self):
        project_data = {
            "name": "Tenant A Only Project",
            "description": "should not be visible to tenant B"
        }
        
        create_response = requests.post(
            f"{API_BASE_URL}/api/projects",
            json=project_data,
            headers={
                "Authorization": f"Bearer {self.tenant_a_token}",
                "X-Tenant-ID": self.tenant_a_id
            },
            timeout=(CONNECTION_TIMEOUT, READ_TIMEOUT)
        )
        
        assert create_response.status_code == 201
        project_id = create_response.json()["id"]
        self.created_project_ids.append(project_id)
        
        get_response = requests.get(
            f"{API_BASE_URL}/api/projects/{project_id}",
            headers={
                "Authorization": f"Bearer {self.tenant_b_token}",
                "X-Tenant-ID": self.tenant_b_id
            },
            timeout=(CONNECTION_TIMEOUT, READ_TIMEOUT)
        )
        
        assert get_response.status_code in [403, 404], \
            f"Tenant B should not access Tenant A's project. Got {get_response.status_code}"
    
    @pytest.mark.api
    def test_delete_project_as_admin(self):
        project_data = {"name": "To Delete", "description": "test deletion"}
        
        create_response = requests.post(
            f"{API_BASE_URL}/api/projects",
            json=project_data,
            headers={
                "Authorization": f"Bearer {self.tenant_a_token}",
                "X-Tenant-ID": self.tenant_a_id
            },
            timeout=(CONNECTION_TIMEOUT, READ_TIMEOUT)
        )
        
        project_id = create_response.json()["id"]
        
        delete_response = requests.delete(
            f"{API_BASE_URL}/api/projects/{project_id}",
            headers={
                "Authorization": f"Bearer {self.tenant_a_token}",
                "X-Tenant-ID": self.tenant_a_id
            },
            timeout=(CONNECTION_TIMEOUT, READ_TIMEOUT)
        )
        
        assert delete_response.status_code in [200, 204], \
            f"Delete failed with status {delete_response.status_code}"
        
        get_response = requests.get(
            f"{API_BASE_URL}/api/projects/{project_id}",
            headers={
                "Authorization": f"Bearer {self.tenant_a_token}",
                "X-Tenant-ID": self.tenant_a_id
            },
            timeout=(CONNECTION_TIMEOUT, READ_TIMEOUT)
        )
        
        assert get_response.status_code == 404, "Deleted project should return 404"
    
    @pytest.mark.api
    def test_create_project_without_auth_fails(self):
        project_data = {"name": "No Auth Test", "description": "should fail"}
        
        response = requests.post(
            f"{API_BASE_URL}/api/projects",
            json=project_data,
            timeout=(CONNECTION_TIMEOUT, READ_TIMEOUT)
        )
        
        assert response.status_code == 401, f"Expected 401 but got {response.status_code}"
    
    @pytest.mark.api
    def test_create_project_with_invalid_data(self):
        invalid_project = {}
        
        response = requests.post(
            f"{API_BASE_URL}/api/projects",
            json=invalid_project,
            headers={
                "Authorization": f"Bearer {self.tenant_a_token}",
                "X-Tenant-ID": self.tenant_a_id
            },
            timeout=(CONNECTION_TIMEOUT, READ_TIMEOUT)
        )
        
        assert response.status_code == 400, \
            f"Invalid data should return 400 but got {response.status_code}"
    
    @pytest.mark.api
    def test_get_non_existent_project(self):
        fake_id = "non_existent_project_99999"
        
        response = requests.get(
            f"{API_BASE_URL}/api/projects/{fake_id}",
            headers={
                "Authorization": f"Bearer {self.tenant_a_token}",
                "X-Tenant-ID": self.tenant_a_id
            },
            timeout=(CONNECTION_TIMEOUT, READ_TIMEOUT)
        )
        
        assert response.status_code == 404, \
            f"Non-existent project should return 404 but got {response.status_code}"
