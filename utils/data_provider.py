import json
import random
from typing import Dict, Any, List, Optional, Iterator, Union
from pathlib import Path
from itertools import product
from config import get_config
from .helpers import TestHelper

class DataProvider:
    def __init__(self, data_dir: str = "test_data"):
        """
        Initialize data provider
        
        Args:
            data_dir: Directory containing test data files
        """
        self.config = get_config()
        self.data_dir = Path(data_dir)
        self.data_cache = {}
        self.helper = TestHelper()
        
        # Ensure data directory exists
        self.data_dir.mkdir(exist_ok=True)
        
        print(f"Data provider initialized - Data directory: {self.data_dir}")
    
    def load_json_data(self, filename: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        Load test data from JSON file
        
        Args:
            filename: JSON filename (with or without .json extension)
            use_cache: Whether to use cached data
            
        Returns:
            Loaded test data dictionary
        """
        # Ensure .json extension
        if not filename.endswith('.json'):
            filename += '.json'
        
        # Check cache first
        if use_cache and filename in self.data_cache:
            print(f"Loading cached data: {filename}")
            return self.data_cache[filename]
        
        file_path = self.data_dir / filename
        
        if not file_path.exists():
            raise FileNotFoundError(f"Test data file not found: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Cache the data
            if use_cache:
                self.data_cache[filename] = data
            
            print(f"Loaded test data: {filename} ({len(data)} items)")
            return data
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in file {filename}: {e}")
        except Exception as e:
            raise IOError(f"Failed to load test data from {filename}: {e}")
    
    def get_test_cases(self, test_suite: str, test_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get test cases for a specific test suite
        
        Args:
            test_suite: Test suite name (e.g., 'products', 'users')
            test_type: Specific test type filter (optional)
            
        Returns:
            List of test case dictionaries
        """
        filename = f"{test_suite}_test_data.json"
        data = self.load_json_data(filename)
        
        if test_type:
            # Filter by test type
            filtered_cases = []
            for case in data.get('test_cases', []):
                if case.get('test_type') == test_type:
                    filtered_cases.append(case)
            return filtered_cases
        
        return data.get('test_cases', [])
    
    def get_positive_test_data(self, resource: str) -> List[Dict[str, Any]]:
        """
        Get positive test data for a resource
        
        Args:
            resource: Resource name (products, users, carts)
            
        Returns:
            List of positive test data
        """
        return self.get_test_cases(resource, 'positive')
    
    def get_negative_test_data(self, resource: str) -> List[Dict[str, Any]]:
        """
        Get negative test data for a resource
        
        Args:
            resource: Resource name (products, users, carts)
            
        Returns:
            List of negative test data
        """
        return self.get_test_cases(resource, 'negative')
    
    def get_boundary_test_data(self, resource: str) -> List[Dict[str, Any]]:
        """
        Get boundary test data for a resource
        
        Args:
            resource: Resource name (products, users, carts)
            
        Returns:
            List of boundary test data
        """
        return self.get_test_cases(resource, 'boundary')
    
    def get_parametrized_data(self, test_suite: str, parameter_combinations: bool = True) -> Iterator[Dict[str, Any]]:
        """
        Get parametrized test data for pytest parametrize
        
        Args:
            test_suite: Test suite name
            parameter_combinations: Whether to generate parameter combinations
            
        Yields:
            Test case data dictionaries
        """
        test_cases = self.get_test_cases(test_suite)
        
        if parameter_combinations:
            # Generate combinations of parameters if specified
            for case in test_cases:
                if 'parameters' in case and isinstance(case['parameters'], dict):
                    param_keys = list(case['parameters'].keys())
                    param_values = [case['parameters'][key] if isinstance(case['parameters'][key], list) 
                                   else [case['parameters'][key]] for key in param_keys]
                    
                    for combination in product(*param_values):
                        yield dict(zip(param_keys, combination))
                else:
                    yield case
        else:
            for case in test_cases:
                yield case
    
    def get_random_test_data(self, resource: str, count: int = 1) -> List[Dict[str, Any]]:
        """
        Get random test data for a resource
        
        Args:
            resource: Resource name
            count: Number of random test data items to generate
            
        Returns:
            List of randomly generated test data
        """
        random_data = []
        
        for _ in range(count):
            if resource == 'products':
                data = self.helper.generate_product_data()
            elif resource == 'users':
                data = self.helper.generate_user_data()
            elif resource == 'carts':
                user_id = random.randint(1, 10)
                data = self.helper.generate_cart_data(user_id)
            else:
                raise ValueError(f"Unsupported resource for random data generation: {resource}")
            
            random_data.append(data)
        
        return random_data
    
    def create_test_data_combinations(self, base_data: Dict[str, Any], 
                                    field_variations: Dict[str, List[Any]]) -> List[Dict[str, Any]]:
        """
        Create test data combinations by varying specific fields
        
        Args:
            base_data: Base test data dictionary
            field_variations: Dictionary mapping field names to lists of values
            
        Returns:
            List of test data combinations
        """
        combinations = []
        field_names = list(field_variations.keys())
        field_value_lists = list(field_variations.values())
        
        for value_combination in product(*field_value_lists):
            test_data = base_data.copy()
            
            # Apply field variations
            for field_name, field_value in zip(field_names, value_combination):
                if '.' in field_name:
                    # Handle nested fields
                    self._set_nested_field(test_data, field_name, field_value)
                else:
                    test_data[field_name] = field_value
            
            combinations.append(test_data)
        
        return combinations
    
    def get_invalid_data_variations(self, resource: str) -> List[Dict[str, Any]]:
        """
        Get common invalid data variations for testing
        
        Args:
            resource: Resource name
            
        Returns:
            List of invalid data variations
        """
        if resource == 'products':
            return self._get_invalid_product_variations()
        elif resource == 'users':
            return self._get_invalid_user_variations()
        elif resource == 'carts':
            return self._get_invalid_cart_variations()
        else:
            return []
    
    def save_test_results(self, filename: str, results: List[Dict[str, Any]]) -> str:
        """
        Save test results to JSON file
        
        Args:
            filename: Output filename
            results: Test results data
            
        Returns:
            Full path of saved file
        """
        if not filename.endswith('.json'):
            filename += '.json'
        
        output_path = self.data_dir / "results" / filename
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"Test results saved: {output_path}")
        return str(output_path)
    
    def load_schema_data(self, schema_name: str) -> Dict[str, Any]:
        """
        Load JSON schema for validation
        
        Args:
            schema_name: Schema filename (without .json extension)
            
        Returns:
            JSON schema dictionary
        """
        schema_dir = self.data_dir / "schemas"
        schema_file = schema_dir / f"{schema_name}.json"
        
        if not schema_file.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_file}")
        
        with open(schema_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def clear_cache(self):
        """Clear cached test data"""
        self.data_cache.clear()
        print("Test data cache cleared")
    
    def _get_invalid_product_variations(self) -> List[Dict[str, Any]]:
        """Get invalid product data variations"""
        base_product = self.helper.generate_product_data()
        
        variations = [
            # Invalid title variations
            {**base_product, "title": ""},  # Empty title
            {**base_product, "title": None},  # Null title
            {**base_product, "title": 123},  # Non-string title
            
            # Invalid price variations
            {**base_product, "price": -10},  # Negative price
            {**base_product, "price": "invalid"},  # Non-numeric price
            {**base_product, "price": None},  # Null price
            
            # Invalid category variations
            {**base_product, "category": "invalid_category"},  # Invalid category
            {**base_product, "category": ""},  # Empty category
            {**base_product, "category": None},  # Null category
            
            # Missing required fields
            {k: v for k, v in base_product.items() if k != "title"},  # Missing title
            {k: v for k, v in base_product.items() if k != "price"},  # Missing price
        ]
        
        return variations
    
    def _get_invalid_user_variations(self) -> List[Dict[str, Any]]:
        """Get invalid user data variations"""
        base_user = self.helper.generate_user_data()
        
        variations = [
            # Invalid email variations
            {**base_user, "email": "invalid-email"},  # Invalid email format
            {**base_user, "email": ""},  # Empty email
            {**base_user, "email": None},  # Null email
            
            # Invalid username variations
            {**base_user, "username": ""},  # Empty username
            {**base_user, "username": None},  # Null username
            {**base_user, "username": "a"},  # Too short username
            
            # Invalid password variations
            {**base_user, "password": "123"},  # Too short password
            {**base_user, "password": ""},  # Empty password
            {**base_user, "password": None},  # Null password
            
            # Missing required fields
            {k: v for k, v in base_user.items() if k != "email"},  # Missing email
            {k: v for k, v in base_user.items() if k != "username"},  # Missing username
        ]
        
        return variations
    
    def _get_invalid_cart_variations(self) -> List[Dict[str, Any]]:
        """Get invalid cart data variations"""
        base_cart = self.helper.generate_cart_data(1)
        
        variations = [
            # Invalid userId variations
            {**base_cart, "userId": -1},  # Negative userId
            {**base_cart, "userId": "invalid"},  # Non-numeric userId
            {**base_cart, "userId": None},  # Null userId
            
            # Invalid products variations
            {**base_cart, "products": []},  # Empty products array
            {**base_cart, "products": None},  # Null products
            {**base_cart, "products": "invalid"},  # Non-array products
            
            # Invalid date variations
            {**base_cart, "date": "invalid-date"},  # Invalid date format
            {**base_cart, "date": None},  # Null date
            
            # Missing required fields
            {k: v for k, v in base_cart.items() if k != "userId"},  # Missing userId
            {k: v for k, v in base_cart.items() if k != "products"},  # Missing products
        ]
        
        return variations
    
    def _set_nested_field(self, data: Dict[str, Any], field_path: str, value: Any):
        """Set value of nested field using dot notation"""
        keys = field_path.split('.')
        current = data
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value 