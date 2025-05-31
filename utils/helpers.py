import json
import random
import string
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from config import get_config

class TestHelper:
    
    def __init__(self):
        self.config = get_config()
    
    @staticmethod
    def generate_random_string(length: int = 10, include_digits: bool = True, include_symbols: bool = False) -> str:
        """ 
        Args:
            length: String length
            include_digits: Include digits in string
            include_symbols: Include symbols in string
            
        Returns:
            Random string
        """
        chars = string.ascii_letters
        
        if include_digits:
            chars += string.digits
        
        if include_symbols:
            chars += "!@#$%^&*"
        
        return ''.join(random.choice(chars) for _ in range(length))
    
    @staticmethod
    def generate_random_email(domain: str = "example.com") -> str:
        """
        Generate random email address
        
        Args:
            domain: Email domain
            
        Returns:
            Random email address
        """
        username = TestHelper.generate_random_string(8).lower()
        return f"{username}@{domain}"
    
    @staticmethod
    def generate_random_phone() -> str:
        """
        Generate random phone number
        
        Returns:
            Random phone number
        """
        return f"+1{random.randint(1000000000, 9999999999)}"
    
    @staticmethod
    def generate_random_price(min_price: float = 1.0, max_price: float = 1000.0) -> float:
        """
        Generate random price
        
        Args:
            min_price: Minimum price
            max_price: Maximum price
            
        Returns:
            Random price rounded to 2 decimal places
        """
        return round(random.uniform(min_price, max_price), 2)
    
    @staticmethod
    def generate_random_date(start_date: Optional[datetime] = None, 
                           end_date: Optional[datetime] = None) -> str:
        """
        Generate random date in ISO format
        
        Args:
            start_date: Start date range
            end_date: End date range
            
        Returns:
            Random date string in ISO format
        """
        if start_date is None:
            start_date = datetime.now() - timedelta(days=365)
        
        if end_date is None:
            end_date = datetime.now()
        
        time_between = end_date - start_date
        random_days = random.randint(0, time_between.days)
        random_date = start_date + timedelta(days=random_days)
        
        return random_date.isoformat()
    
    @staticmethod
    def generate_user_data(custom_fields: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate test user data
        
        Args:
            custom_fields: Custom fields to override defaults
            
        Returns:
            User data dictionary
        """
        user_data = {
            "email": TestHelper.generate_random_email(),
            "username": TestHelper.generate_random_string(8).lower(),
            "password": TestHelper.generate_random_string(12, include_symbols=True),
            "name": {
                "firstname": random.choice(["John", "Jane", "Bob", "Alice", "Mike", "Sarah"]),
                "lastname": random.choice(["Doe", "Smith", "Johnson", "Brown", "Davis", "Wilson"])
            },
            "address": {
                "city": random.choice(["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"]),
                "street": f"{random.randint(1, 999)} {random.choice(['Main', 'Oak', 'Pine', 'Elm'])} St",
                "number": random.randint(1, 999),
                "zipcode": f"{random.randint(10000, 99999)}",
                "geolocation": {
                    "lat": f"{random.uniform(-90, 90):.6f}",
                    "long": f"{random.uniform(-180, 180):.6f}"
                }
            },
            "phone": TestHelper.generate_random_phone()
        }
        
        if custom_fields:
            user_data.update(custom_fields)
        
        return user_data
    
    @staticmethod
    def generate_product_data(custom_fields: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate test product data
        
        Args:
            custom_fields: Custom fields to override defaults
            
        Returns:
            Product data dictionary
        """
        categories = ["electronics", "jewelery", "men's clothing", "women's clothing"]
        
        product_data = {
            "title": f"Test Product {TestHelper.generate_random_string(5)}",
            "price": TestHelper.generate_random_price(),
            "description": f"Test product description {TestHelper.generate_random_string(20)}",
            "image": "https://fakestoreapi.com/img/placeholder.jpg",
            "category": random.choice(categories)
        }
        
        if custom_fields:
            product_data.update(custom_fields)
        
        return product_data
    
    @staticmethod
    def generate_cart_data(user_id: int, custom_fields: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate test cart data
        
        Args:
            user_id: User ID for the cart
            custom_fields: Custom fields to override defaults
            
        Returns:
            Cart data dictionary
        """
        num_products = random.randint(1, 5)
        products = []
        
        for _ in range(num_products):
            products.append({
                "productId": random.randint(1, 20),
                "quantity": random.randint(1, 5)
            })
        
        cart_data = {
            "userId": user_id,
            "date": TestHelper.generate_random_date(),
            "products": products
        }
        
        if custom_fields:
            cart_data.update(custom_fields)
        
        return cart_data
    
    @staticmethod
    def wait_for_condition(condition_func, timeout: int = 30, interval: float = 1.0) -> bool:
        """
        Wait for a condition to be true
        
        Args:
            condition_func: Function that returns True when condition is met
            timeout: Maximum wait time in seconds
            interval: Check interval in seconds
            
        Returns:
            True if condition met within timeout, False otherwise
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if condition_func():
                return True
            time.sleep(interval)
        
        return False
    
    @staticmethod
    def extract_ids_from_response(response_data: Union[Dict, List], id_field: str = "id") -> List[int]:
        """
        Extract IDs from API response
        
        Args:
            response_data: Response data (dict or list)
            id_field: Name of the ID field
            
        Returns:
            List of extracted IDs
        """
        ids = []
        
        if isinstance(response_data, list):
            for item in response_data:
                if isinstance(item, dict) and id_field in item:
                    ids.append(item[id_field])
        elif isinstance(response_data, dict) and id_field in response_data:
            ids.append(response_data[id_field])
        
        return ids
    
    @staticmethod
    def compare_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any], 
                     ignore_keys: Optional[List[str]] = None) -> List[str]:
        """
        Compare two dictionaries and return differences
        
        Args:
            dict1: First dictionary
            dict2: Second dictionary
            ignore_keys: Keys to ignore in comparison
            
        Returns:
            List of differences
        """
        if ignore_keys is None:
            ignore_keys = []
        
        differences = []
        
        # Filter out ignored keys
        filtered_dict1 = {k: v for k, v in dict1.items() if k not in ignore_keys}
        filtered_dict2 = {k: v for k, v in dict2.items() if k not in ignore_keys}
        
        # Check for different values
        all_keys = set(filtered_dict1.keys()) | set(filtered_dict2.keys())
        
        for key in all_keys:
            if key not in filtered_dict1:
                differences.append(f"Key '{key}' missing in first dict")
            elif key not in filtered_dict2:
                differences.append(f"Key '{key}' missing in second dict")
            elif filtered_dict1[key] != filtered_dict2[key]:
                differences.append(f"Key '{key}': {filtered_dict1[key]} != {filtered_dict2[key]}")
        
        return differences
    
    @staticmethod
    def format_json_response(response_data: Dict[str, Any], indent: int = 2) -> str:
        """
        Format JSON response for logging
        
        Args:
            response_data: JSON response data
            indent: JSON indentation
            
        Returns:
            Formatted JSON string
        """
        return json.dumps(response_data, indent=indent, ensure_ascii=False)
    
    @staticmethod
    def save_response_to_file(response_data: Dict[str, Any], filename: str, 
                            output_dir: str = "test_output") -> str:
        """
        Save response data to file
        
        Args:
            response_data: Response data to save
            filename: Output filename
            output_dir: Output directory
            
        Returns:
            Full path of saved file
        """
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        file_path = output_path / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(response_data, f, indent=2, ensure_ascii=False)
        
        return str(file_path)
    
    @staticmethod
    def load_test_data(filename: str, data_dir: str = "test_data") -> Dict[str, Any]:
        """
        Load test data from JSON file
        
        Args:
            filename: Test data filename
            data_dir: Test data directory
            
        Returns:
            Loaded test data
        """
        data_path = Path(data_dir) / filename
        
        if not data_path.exists():
            raise FileNotFoundError(f"Test data file not found: {data_path}")
        
        with open(data_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @staticmethod
    def mask_sensitive_data(data: Dict[str, Any], sensitive_fields: List[str]) -> Dict[str, Any]:
        """
        Mask sensitive data in dictionary
        
        Args:
            data: Data dictionary
            sensitive_fields: List of sensitive field names
            
        Returns:
            Dictionary with masked sensitive data
        """
        masked_data = data.copy()
        
        for field in sensitive_fields:
            if field in masked_data:
                if isinstance(masked_data[field], str):
                    masked_data[field] = "*" * len(str(masked_data[field]))
                else:
                    masked_data[field] = "***"
        
        return masked_data
    
    @staticmethod
    def get_current_timestamp() -> str:
        """
        Get current timestamp in ISO format
        
        Returns:
            Current timestamp string
        """
        return datetime.now().isoformat()
    
    @staticmethod
    def parse_response_headers(headers: Dict[str, str]) -> Dict[str, Any]:
        """
        Parse and extract useful information from response headers
        
        Args:
            headers: Response headers dictionary
            
        Returns:
            Parsed header information
        """
        parsed_headers = {
            "content_type": headers.get("content-type", ""),
            "content_length": headers.get("content-length", "0"),
            "server": headers.get("server", ""),
            "date": headers.get("date", ""),
            "cache_control": headers.get("cache-control", ""),
            "x_ratelimit_limit": headers.get("x-ratelimit-limit", ""),
            "x_ratelimit_remaining": headers.get("x-ratelimit-remaining", "")
        }
        
        return {k: v for k, v in parsed_headers.items() if v} 