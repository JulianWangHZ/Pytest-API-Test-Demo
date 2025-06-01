import pytest
import allure
import json
from typing import Dict, Any, Generator
from utils import APIClient, DataProvider, ResponseValidator, TestHelper
from config import get_config

# Configure pytest
def pytest_configure(config):
    # Add custom markers
    config.addinivalue_line("markers", "smoke: mark test as smoke test")
    config.addinivalue_line("markers", "regression: mark test as regression test")
    config.addinivalue_line("markers", "positive: mark test as positive test case")
    config.addinivalue_line("markers", "negative: mark test as negative test case")
    config.addinivalue_line("markers", "boundary: mark test as boundary test case")
    config.addinivalue_line("markers", "products: mark test as products related")
    config.addinivalue_line("markers", "users: mark test as users related")
    config.addinivalue_line("markers", "carts: mark test as carts related")
    config.addinivalue_line("markers", "auth: mark test as authentication related")

def pytest_runtest_setup(item):
    """Setup for each test item"""
    # Add allure labels based on markers
    if hasattr(item, 'get_closest_marker'):
        # Add test type labels
        if item.get_closest_marker('smoke'):
            allure.dynamic.label('test_type', 'smoke')
        elif item.get_closest_marker('regression'):
            allure.dynamic.label('test_type', 'regression')
        
        # Add test category labels
        if item.get_closest_marker('positive'):
            allure.dynamic.label('test_category', 'positive')
        elif item.get_closest_marker('negative'):
            allure.dynamic.label('test_category', 'negative')
        elif item.get_closest_marker('boundary'):
            allure.dynamic.label('test_category', 'boundary')
        
        # Add feature labels
        if item.get_closest_marker('products'):
            allure.dynamic.feature('Products API')
        elif item.get_closest_marker('users'):
            allure.dynamic.feature('Users API')
        elif item.get_closest_marker('carts'):
            allure.dynamic.feature('Carts API')
        elif item.get_closest_marker('auth'):
            allure.dynamic.feature('Authentication API')

@pytest.fixture(scope="session")
def config() -> Dict[str, Any]:
    """
    Provide test configuration
    
    Returns:
        Configuration dictionary
    """
    return get_config()

@pytest.fixture(scope="session")
def api_client(config) -> Generator[APIClient, None, None]:
    """
    Provide API client instance
    
    Args:
        config: Test configuration
        
    Yields:
        API client instance
    """
    client = APIClient(config)
    yield client
    client.close()

@pytest.fixture(scope="session")
def data_provider() -> DataProvider:
    """
    Provide data provider instance
    
    Returns:
        Data provider instance
    """
    return DataProvider()

@pytest.fixture(scope="session")
def validator() -> ResponseValidator:
    """
    Provide response validator instance
    
    Returns:
        Response validator instance
    """
    return ResponseValidator()

@pytest.fixture(scope="session")
def test_helper() -> TestHelper:
    """
    Provide test helper instance
    
    Returns:
        Test helper instance
    """
    return TestHelper()

@pytest.fixture
def random_product_data(test_helper) -> Dict[str, Any]:
    """
    Provide random product test data
    
    Args:
        test_helper: Test helper instance
        
    Returns:
        Random product data
    """
    return test_helper.generate_product_data()

@pytest.fixture
def random_user_data(test_helper) -> Dict[str, Any]:
    """
    Provide random user test data
    
    Args:
        test_helper: Test helper instance
        
    Returns:
        Random user data
    """
    return test_helper.generate_user_data()

@pytest.fixture
def random_cart_data(test_helper) -> Dict[str, Any]:
    """
    Provide random cart test data
    
    Args:
        test_helper: Test helper instance
        
    Returns:
        Random cart data
    """
    return test_helper.generate_cart_data(user_id=1)

@pytest.fixture
def auth_credentials() -> Dict[str, str]:
    """
    Provide authentication credentials for testing
    
    Returns:
        Authentication credentials
    """
    return {
        "username": "mor_2314",
        "password": "83r5^_"
    }

@pytest.fixture
def authenticated_headers(api_client, auth_credentials) -> Dict[str, str]:
    """
    Provide authenticated headers for API requests
    
    Args:
        api_client: API client instance
        auth_credentials: Authentication credentials
        
    Returns:
        Headers with authentication token
    """
    response = api_client.auth.login(auth_credentials)
    
    if response.status_code == 200:
        token = response.json().get('token')
        return {"Authorization": f"Bearer {token}"}
    else:
        pytest.skip("Authentication failed, skipping test requiring auth")

@pytest.fixture(autouse=True)
def add_allure_environment_info(config):
    """
    Add environment information to Allure report
    
    Args:
        config: Test configuration
    """
    allure.dynamic.label('environment', config['environment'])
    allure.dynamic.label('base_url', config['base_url'])

@pytest.fixture
def capture_request_response():
    """
    Fixture to capture and attach request/response data to Allure
    """
    def _capture(response, test_name: str = "API Request"):
        """
        Capture request and response data
        
        Args:
            response: HTTP response object
            test_name: Name for the test step
        """
        with allure.step(f"{test_name}: {response.request.method} {response.url}"):
            # Attach request details
            request_body = response.request.body
            # Convert bytes to string for JSON serialization
            if isinstance(request_body, bytes):
                try:
                    request_body = request_body.decode('utf-8')
                except UnicodeDecodeError:
                    request_body = str(request_body)
            
            request_data = {
                "method": response.request.method,
                "url": str(response.url),
                "headers": dict(response.request.headers),
                "body": request_body
            }
            
            allure.attach(
                json.dumps(request_data, indent=2),
                name="Request Details",
                attachment_type=allure.attachment_type.JSON
            )
            
            # Attach response details
            response_data = {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "response_time_seconds": response.elapsed.total_seconds()
            }
            
            try:
                response_data["body"] = response.json()
            except:
                response_data["body"] = response.text
            
            allure.attach(
                json.dumps(response_data, indent=2, default=str),
                name="Response Details",
                attachment_type=allure.attachment_type.JSON
            )
    
    return _capture

@pytest.fixture
def assert_response():
    """
    Fixture for enhanced response assertions with Allure reporting
    """
    def _assert_response(response, expected_status: int = 200, 
                        schema_name: str = None, 
                        required_fields: list = None):
        """
        Assert response with detailed reporting
        
        Args:
            response: HTTP response object
            expected_status: Expected status code
            schema_name: JSON schema name for validation
            required_fields: List of required fields
        """
        validator = ResponseValidator()
        
        with allure.step(f"Validate response status code: {expected_status}"):
            assert response.status_code == expected_status, \
                f"Expected status {expected_status}, got {response.status_code}"
        
        with allure.step("Validate response time"):
            max_time = 5.0  # 5 seconds default
            response_time = response.elapsed.total_seconds()
            assert response_time <= max_time, \
                f"Response time {response_time}s exceeded maximum {max_time}s"
        
        if response.status_code == 200 and response.headers.get('content-type', '').startswith('application/json'):
            with allure.step("Validate response content type"):
                assert 'application/json' in response.headers.get('content-type', '')
            
            if schema_name:
                with allure.step(f"Validate JSON schema: {schema_name}"):
                    assert validator.validate_json_schema(response, schema_name)
            
            if required_fields:
                with allure.step(f"Validate required fields: {required_fields}"):
                    assert validator.validate_required_fields(response, required_fields)
    
    return _assert_response

@pytest.fixture
def cleanup_created_resources():
    """
    Fixture to track and cleanup created resources
    """
    created_resources = {
        'products': [],
        'users': [],
        'carts': []
    }
    
    def _add_resource(resource_type: str, resource_id: int):
        """Add resource to cleanup list"""
        if resource_type in created_resources:
            created_resources[resource_type].append(resource_id)
    
    yield _add_resource
    
    for resource_type, ids in created_resources.items():
        if ids:
            allure.attach(
                f"Created {resource_type}: {ids}",
                name=f"Created Resources - {resource_type}",
                attachment_type=allure.attachment_type.TEXT
            )

# Pytest hooks for enhanced reporting
def pytest_runtest_makereport(item, call):
    """Generate test reports with additional information"""
    if call.when == "call":
        # Add test execution details to Allure
        if hasattr(item, 'rep_call'):
            item.rep_call = call
        
        # Add test duration
        if hasattr(call, 'duration'):
            allure.dynamic.label('duration', f"{call.duration:.2f}s")

def pytest_runtest_logreport(report):
    """Log test reports"""
    if report.when == "call":
        if report.outcome == "failed":
            # Add failure details to Allure
            failure_details = str(report.longrepr)
            allure.attach(
                failure_details,
                name="Failure Details",
                attachment_type=allure.attachment_type.TEXT
            )

# Custom pytest markers for data-driven tests
def pytest_generate_tests(metafunc):
    """Generate parametrized tests based on test data"""
    if "product_test_data" in metafunc.fixturenames:
        data_provider = DataProvider()
        test_data = data_provider.get_positive_test_data("products")
        metafunc.parametrize("product_test_data", test_data)
    
    elif "user_test_data" in metafunc.fixturenames:
        data_provider = DataProvider()
        test_data = data_provider.get_positive_test_data("users")
        metafunc.parametrize("user_test_data", test_data)
    
    elif "cart_test_data" in metafunc.fixturenames:
        data_provider = DataProvider()
        test_data = data_provider.get_positive_test_data("carts")
        metafunc.parametrize("cart_test_data", test_data)
