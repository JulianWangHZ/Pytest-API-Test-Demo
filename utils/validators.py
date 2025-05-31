import json
import jsonschema
from typing import Dict, Any, List, Optional, Union
from requests import Response
from pathlib import Path
from config import get_config

class ResponseValidator:
    """Response validation utility class"""
    
    def __init__(self):
        """Initialize response validator"""
        self.config = get_config()
        self.validation_config = self.config["validation"]
        self.schema_dir = Path(__file__).parent.parent / "test_data" / "schemas"
        
        print(f"Response validator initialized")
    
    def validate_status_code(self, response: Response, expected_code: Union[int, List[int]]) -> bool:
        """
        Validate response status code
        
        Args:
            response: HTTP response object
            expected_code: Expected status code(s)
            
        Returns:
            True if valid, False otherwise
        """
        if isinstance(expected_code, int):
            expected_codes = [expected_code]
        else:
            expected_codes = expected_code
        
        actual_code = response.status_code
        is_valid = actual_code in expected_codes
        
        if not is_valid:
            print(f"Status code validation failed: expected {expected_codes}, got {actual_code}")
        else:
            print(f"Status code validation passed: {actual_code}")
        
        return is_valid
    
    def validate_content_type(self, response: Response, expected_type: str = "application/json") -> bool:
        """
        Validate response content type
        
        Args:
            response: HTTP response object
            expected_type: Expected content type
            
        Returns:
            True if valid, False otherwise
        """
        if not self.validation_config.get("content_type_validation", True):
            return True
        
        actual_type = response.headers.get("content-type", "").split(";")[0]
        is_valid = actual_type == expected_type
        
        if not is_valid:
            print(f"Content type validation failed: expected {expected_type}, got {actual_type}")
        else:
            print(f"Content type validation passed: {actual_type}")
        
        return is_valid
    
    def validate_response_time(self, response: Response, max_time: Optional[float] = None) -> bool:
        """
        Validate response time
        
        Args:
            response: HTTP response object
            max_time: Maximum allowed response time in seconds
            
        Returns:
            True if valid, False otherwise
        """
        if max_time is None:
            max_time = self.config["performance"]["max_response_time"]
        
        response_time = response.elapsed.total_seconds()
        is_valid = response_time <= max_time
        
        if not is_valid:
            print(f"Response time validation failed: {response_time:.3f}s > {max_time}s")
        else:
            print(f"Response time validation passed: {response_time:.3f}s")
        
        return is_valid
    
    def validate_json_schema(self, response: Response, schema_name: str) -> bool:
        """
        Validate response JSON against schema
        
        Args:
            response: HTTP response object
            schema_name: Schema file name (without .json extension)
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Load JSON response
            response_json = response.json()
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON response: {e}")
            return False
        
        # Load schema
        schema = self._load_schema(schema_name)
        if not schema:
            print(f"Schema not found: {schema_name}")
            return False
        
        try:
            # Validate against schema
            jsonschema.validate(
                instance=response_json,
                schema=schema,
                format_checker=jsonschema.FormatChecker()
            )
            print(f"JSON schema validation passed: {schema_name}")
            return True
            
        except jsonschema.ValidationError as e:
            print(f"JSON schema validation failed: {e.message}")
            print(f"   Failed at path: {' -> '.join(str(p) for p in e.absolute_path)}")
            return False
        except jsonschema.SchemaError as e:
            print(f"Invalid schema: {e.message}")
            return False
    
    def validate_required_fields(self, response: Response, required_fields: List[str]) -> bool:
        """
        Validate that response contains required fields
        
        Args:
            response: HTTP response object
            required_fields: List of required field names
            
        Returns:
            True if all required fields present, False otherwise
        """
        try:
            response_json = response.json()
        except json.JSONDecodeError:
            print("Cannot validate fields: response is not valid JSON")
            return False
        
        missing_fields = []
        for field in required_fields:
            if self._is_field_missing(response_json, field):
                missing_fields.append(field)
        
        if missing_fields:
            print(f"Missing required fields: {missing_fields}")
            return False
        else:
            print(f"All required fields present: {required_fields}")
            return True
    
    def validate_field_types(self, response: Response, field_types: Dict[str, type]) -> bool:
        """
        Validate field data types in response
        
        Args:
            response: HTTP response object
            field_types: Dictionary mapping field names to expected types
            
        Returns:
            True if all field types are correct, False otherwise
        """
        try:
            response_json = response.json()
        except json.JSONDecodeError:
            print("Cannot validate field types: response is not valid JSON")
            return False
        
        invalid_fields = []
        for field_name, expected_type in field_types.items():
            field_value = self._get_nested_field(response_json, field_name)
            
            if field_value is not None and not isinstance(field_value, expected_type):
                actual_type = type(field_value).__name__
                expected_type_name = expected_type.__name__
                invalid_fields.append(f"{field_name} (expected {expected_type_name}, got {actual_type})")
        
        if invalid_fields:
            print(f"Invalid field types: {invalid_fields}")
            return False
        else:
            print(f"All field types are correct")
            return True
    
    def validate_array_length(self, response: Response, field_name: str, 
                            min_length: Optional[int] = None, 
                            max_length: Optional[int] = None) -> bool:
        """
        Validate array field length
        
        Args:
            response: HTTP response object
            field_name: Name of the array field
            min_length: Minimum array length
            max_length: Maximum array length
            
        Returns:
            True if array length is valid, False otherwise
        """
        try:
            response_json = response.json()
        except json.JSONDecodeError:
            print("Cannot validate array length: response is not valid JSON")
            return False
        
        array_value = self._get_nested_field(response_json, field_name)
        
        if not isinstance(array_value, list):
            print(f"Field '{field_name}' is not an array")
            return False
        
        array_length = len(array_value)
        
        if min_length is not None and array_length < min_length:
            print(f"Array length validation failed: {array_length} < {min_length}")
            return False
        
        if max_length is not None and array_length > max_length:
            print(f"Array length validation failed: {array_length} > {max_length}")
            return False
        
        print(f"Array length validation passed: {array_length}")
        return True
    
    def validate_numeric_range(self, response: Response, field_name: str,
                             min_value: Optional[Union[int, float]] = None,
                             max_value: Optional[Union[int, float]] = None) -> bool:
        """
        Validate numeric field value range
        
        Args:
            response: HTTP response object
            field_name: Name of the numeric field
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            
        Returns:
            True if value is within range, False otherwise
        """
        try:
            response_json = response.json()
        except json.JSONDecodeError:
            print("Cannot validate numeric range: response is not valid JSON")
            return False
        
        field_value = self._get_nested_field(response_json, field_name)
        
        if not isinstance(field_value, (int, float)):
            print(f"Field '{field_name}' is not numeric")
            return False
        
        if min_value is not None and field_value < min_value:
            print(f"Numeric range validation failed: {field_value} < {min_value}")
            return False
        
        if max_value is not None and field_value > max_value:
            print(f"Numeric range validation failed: {field_value} > {max_value}")
            return False
        
        print(f"Numeric range validation passed: {field_value}")
        return True
    
    def validate_complete_response(self, response: Response, 
                                 expected_status: Union[int, List[int]] = 200,
                                 schema_name: Optional[str] = None,
                                 required_fields: Optional[List[str]] = None) -> bool:
        """
        Perform complete response validation
        
        Args:
            response: HTTP response object
            expected_status: Expected status code(s)
            schema_name: Schema name for JSON validation
            required_fields: List of required fields
            
        Returns:
            True if all validations pass, False otherwise
        """
        validations = []
        
        # Status code validation
        validations.append(self.validate_status_code(response, expected_status))
        
        # Content type validation
        validations.append(self.validate_content_type(response))
        
        # Response time validation
        validations.append(self.validate_response_time(response))
        
        # Schema validation (if provided)
        if schema_name:
            validations.append(self.validate_json_schema(response, schema_name))
        
        # Required fields validation (if provided)
        if required_fields:
            validations.append(self.validate_required_fields(response, required_fields))
        
        all_valid = all(validations)
        
        if all_valid:
            print("Complete response validation passed")
        else:
            print("Complete response validation failed")
        
        return all_valid
    
    def _load_schema(self, schema_name: str) -> Optional[Dict[str, Any]]:
        """Load JSON schema from file"""
        schema_file = self.schema_dir / f"{schema_name}.json"
        
        if not schema_file.exists():
            return None
        
        try:
            with open(schema_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Failed to load schema {schema_name}: {e}")
            return None
    
    def _is_field_missing(self, data: Dict[str, Any], field_path: str) -> bool:
        """Check if nested field is missing"""
        return self._get_nested_field(data, field_path) is None
    
    def _get_nested_field(self, data: Dict[str, Any], field_path: str) -> Any:
        """Get value of nested field using dot notation"""
        keys = field_path.split('.')
        current = data
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        
        return current 