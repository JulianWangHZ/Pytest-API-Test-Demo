import requests
import time

from typing import Dict, Any, Optional, Union
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from config import get_config

class APIClient:

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize API client
        
        Args:
            config: Configuration dictionary (optional)
        """
        self.config = config or get_config()
        self.base_url = self.config["base_url"]
        self.timeout = self.config["timeout"]
        
        # Create and configure session
        self.session = self._create_session()
        
        # Initialize API services
        self.products = ProductsAPI(self)
        self.users = UsersAPI(self)
        self.carts = CartsAPI(self)
        self.auth = AuthAPI(self)
    
    def _create_session(self) -> requests.Session:
        """Create and configure requests session"""
        session = requests.Session()
        
        # Set default headers
        session.headers.update(self.config["headers"])
        
        # Configure retry strategy
        retry_config = self.config["retry"]
        retry_strategy = Retry(
            total=retry_config["retry_count"],
            backoff_factor=retry_config["retry_delay"],
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """
        Send HTTP request
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            **kwargs: Additional request parameters
            
        Returns:
            Response object
        """
        url = f"{self.base_url}{endpoint}"
        kwargs.setdefault("timeout", self.timeout)
        
        # Record request start time
        start_time = time.time()
        
        try:
            response = self.session.request(method, url, **kwargs)
            
            # Calculate response time
            response_time = time.time() - start_time
            
            # Check response time threshold
            max_response_time = self.config["performance"]["max_response_time"]
            if response_time > max_response_time:
                print(f"Response time exceeded threshold: {response_time:.3f}s > {max_response_time}s")
            
            return response
            
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            raise
    
    def get(self, endpoint: str, **kwargs) -> requests.Response:
        """GET request"""
        return self.request("GET", endpoint, **kwargs)
    
    def post(self, endpoint: str, **kwargs) -> requests.Response:
        """POST request"""
        return self.request("POST", endpoint, **kwargs)
    
    def put(self, endpoint: str, **kwargs) -> requests.Response:
        """PUT request"""
        return self.request("PUT", endpoint, **kwargs)
    
    def patch(self, endpoint: str, **kwargs) -> requests.Response:
        """PATCH request"""
        return self.request("PATCH", endpoint, **kwargs)
    
    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        """DELETE request"""
        return self.request("DELETE", endpoint, **kwargs)
    
    def close(self):
        """Close session"""
        if self.session:
            self.session.close()

class BaseAPI:
    """Base class for API services"""
    
    def __init__(self, client: APIClient):
        """
        Initialize API service
        
        Args:
            client: API client instance
        """
        self.client = client
        self.endpoints = client.config["endpoints"]

class ProductsAPI(BaseAPI):
    """Products API service"""
    
    def get_all(self, limit: Optional[int] = None, sort: Optional[str] = None) -> requests.Response:
        """
        Get all products
        
        Args:
            limit: Limit number of products
            sort: Sort order (asc|desc)
            
        Returns:
            Response object
        """
        if limit and sort:
            endpoint = self.endpoints["products"]["limit_sort"].format(limit=limit, sort=sort)
        elif limit:
            endpoint = self.endpoints["products"]["limit"].format(limit=limit)
        elif sort:
            endpoint = self.endpoints["products"]["sort"].format(sort=sort)
        else:
            endpoint = self.endpoints["products"]["get_all"]
        
        return self.client.get(endpoint)
    
    def get_by_id(self, product_id: Union[int, str]) -> requests.Response:
        """
        Get product by ID
        
        Args:
            product_id: Product ID
            
        Returns:
            Response object
        """
        endpoint = self.endpoints["products"]["get_by_id"].format(id=product_id)
        return self.client.get(endpoint)
    
    def create(self, product_data: Dict[str, Any]) -> requests.Response:
        """
        Create product
        
        Args:
            product_data: Product data
            
        Returns:
            Response object
        """
        endpoint = self.endpoints["products"]["create"]
        return self.client.post(endpoint, json=product_data)
    
    def update(self, product_id: Union[int, str], product_data: Dict[str, Any]) -> requests.Response:
        """
        Update product (PUT)
        
        Args:
            product_id: Product ID
            product_data: Product data
            
        Returns:
            Response object
        """
        endpoint = self.endpoints["products"]["update"].format(id=product_id)
        return self.client.put(endpoint, json=product_data)
    
    def patch(self, product_id: Union[int, str], product_data: Dict[str, Any]) -> requests.Response:
        """
        Partially update product (PATCH)
        
        Args:
            product_id: Product ID
            product_data: Fields to update
            
        Returns:
            Response object
        """
        endpoint = self.endpoints["products"]["patch"].format(id=product_id)
        return self.client.patch(endpoint, json=product_data)
    
    def delete(self, product_id: Union[int, str]) -> requests.Response:
        """
        Delete product
        
        Args:
            product_id: Product ID
            
        Returns:
            Response object
        """
        endpoint = self.endpoints["products"]["delete"].format(id=product_id)
        return self.client.delete(endpoint)
    
    def get_categories(self) -> requests.Response:
        """
        Get all product categories
        
        Returns:
            Response object
        """
        endpoint = self.endpoints["products"]["categories"]
        return self.client.get(endpoint)
    
    def get_by_category(self, category: str) -> requests.Response:
        """
        Get products by category
        
        Args:
            category: Category name
            
        Returns:
            Response object
        """
        endpoint = self.endpoints["products"]["by_category"].format(category=category)
        return self.client.get(endpoint)

class UsersAPI(BaseAPI):
    """Users API service"""
    
    def get_all(self, limit: Optional[int] = None, sort: Optional[str] = None) -> requests.Response:
        """Get all users"""
        if limit and sort:
            endpoint = self.endpoints["users"]["limit_sort"].format(limit=limit, sort=sort)
        elif limit:
            endpoint = self.endpoints["users"]["limit"].format(limit=limit)
        elif sort:
            endpoint = self.endpoints["users"]["sort"].format(sort=sort)
        else:
            endpoint = self.endpoints["users"]["get_all"]
        
        return self.client.get(endpoint)
    
    def get_by_id(self, user_id: Union[int, str]) -> requests.Response:
        """Get user by ID"""
        endpoint = self.endpoints["users"]["get_by_id"].format(id=user_id)
        return self.client.get(endpoint)
    
    def create(self, user_data: Dict[str, Any]) -> requests.Response:
        """Create user"""
        endpoint = self.endpoints["users"]["create"]
        return self.client.post(endpoint, json=user_data)
    
    def update(self, user_id: Union[int, str], user_data: Dict[str, Any]) -> requests.Response:
        """Update user"""
        endpoint = self.endpoints["users"]["update"].format(id=user_id)
        return self.client.put(endpoint, json=user_data)
    
    def patch(self, user_id: Union[int, str], user_data: Dict[str, Any]) -> requests.Response:
        """Partially update user"""
        endpoint = self.endpoints["users"]["patch"].format(id=user_id)
        return self.client.patch(endpoint, json=user_data)
    
    def delete(self, user_id: Union[int, str]) -> requests.Response:
        """Delete user"""
        endpoint = self.endpoints["users"]["delete"].format(id=user_id)
        return self.client.delete(endpoint)

class CartsAPI(BaseAPI):
    """Carts API service"""
    
    def get_all(self, limit: Optional[int] = None, sort: Optional[str] = None) -> requests.Response:
        """Get all carts"""
        if limit:
            endpoint = self.endpoints["carts"]["limit"].format(limit=limit)
        elif sort:
            endpoint = self.endpoints["carts"]["sort"].format(sort=sort)
        else:
            endpoint = self.endpoints["carts"]["get_all"]
        
        return self.client.get(endpoint)
    
    def get_by_id(self, cart_id: Union[int, str]) -> requests.Response:
        """Get cart by ID"""
        endpoint = self.endpoints["carts"]["get_by_id"].format(id=cart_id)
        return self.client.get(endpoint)
    
    def create(self, cart_data: Dict[str, Any]) -> requests.Response:
        """Create cart"""
        endpoint = self.endpoints["carts"]["create"]
        return self.client.post(endpoint, json=cart_data)
    
    def update(self, cart_id: Union[int, str], cart_data: Dict[str, Any]) -> requests.Response:
        """Update cart"""
        endpoint = self.endpoints["carts"]["update"].format(id=cart_id)
        return self.client.put(endpoint, json=cart_data)
    
    def patch(self, cart_id: Union[int, str], cart_data: Dict[str, Any]) -> requests.Response:
        """Partially update cart"""
        endpoint = self.endpoints["carts"]["patch"].format(id=cart_id)
        return self.client.patch(endpoint, json=cart_data)
    
    def delete(self, cart_id: Union[int, str]) -> requests.Response:
        """Delete cart"""
        endpoint = self.endpoints["carts"]["delete"].format(id=cart_id)
        return self.client.delete(endpoint)
    
    def get_user_carts(self, user_id: Union[int, str]) -> requests.Response:
        """Get user's carts"""
        endpoint = self.endpoints["carts"]["user_carts"].format(user_id=user_id)
        return self.client.get(endpoint)
    
    def get_by_date_range(self, start_date: str, end_date: str) -> requests.Response:
        """Get carts by date range"""
        endpoint = self.endpoints["carts"]["date_range"].format(start=start_date, end=end_date)
        return self.client.get(endpoint)

class AuthAPI(BaseAPI):
    """Authentication API service"""
    
    def login(self, credentials: Dict[str, str]) -> requests.Response:
        """
        User login
        
        Args:
            credentials: Authentication credentials {"username": "xxx", "password": "xxx"}
            
        Returns:
            Response object containing authentication token
        """
        endpoint = self.endpoints["auth"]["login"]
        return self.client.post(endpoint, json=credentials) 