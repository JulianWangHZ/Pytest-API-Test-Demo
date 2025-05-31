import pytest
import allure
from typing import Dict, Any


@allure.feature("Products API")
@allure.story("Get Products")
class TestGetProducts:
    """Test cases for getting products"""
    
    @pytest.mark.smoke
    @pytest.mark.products
    @pytest.mark.positive
    @allure.title("Get all products successfully")
    @allure.description("Test getting all products from the API")
    def test_get_all_products(self, api_client, validator, capture_request_response):
        """Test getting all products"""
        with allure.step("Send GET request to get all products"):
            response = api_client.products.get_all()
            capture_request_response(response, "Get All Products")
        
        with allure.step("Validate response"):
            assert validator.validate_status_code(response, 200)
            assert validator.validate_content_type(response, "application/json")
            assert validator.validate_response_time(response, max_time=5.0)
            
            data = response.json()
            assert isinstance(data, list)
            assert len(data) > 0
    
    @pytest.mark.smoke
    @pytest.mark.products
    @pytest.mark.positive
    @allure.title("Get products with limit")
    @allure.description("Test getting limited number of products")
    @pytest.mark.parametrize("limit", [1, 5, 10])
    def test_get_products_with_limit(self, api_client, validator, capture_request_response, limit):
        """Test getting products with limit"""
        with allure.step(f"Send GET request to get {limit} products"):
            response = api_client.products.get_all(limit=limit)
            capture_request_response(response, f"Get {limit} Products")
        
        with allure.step("Validate response"):
            assert validator.validate_status_code(response, 200)
            data = response.json()
            assert len(data) <= limit
    
    @pytest.mark.products
    @pytest.mark.positive
    @allure.title("Get product by ID")
    @allure.description("Test getting a specific product by ID")
    @pytest.mark.parametrize("product_id", [1, 2, 5, 10])
    def test_get_product_by_id(self, api_client, validator, capture_request_response, product_id):
        """Test getting product by ID"""
        with allure.step(f"Send GET request to get product {product_id}"):
            response = api_client.products.get_by_id(product_id)
            capture_request_response(response, f"Get Product {product_id}")
        
        with allure.step("Validate response"):
            assert validator.validate_status_code(response, 200)
            assert validator.validate_required_fields(response, ["id", "title", "price", "category"])
            
            data = response.json()
            assert data["id"] == product_id
    
    @pytest.mark.products
    @pytest.mark.negative
    @allure.title("Get product with invalid ID")
    @allure.description("Test getting product with invalid ID should return 404")
    @pytest.mark.parametrize("invalid_id", [999999, -1, "invalid"])
    def test_get_product_invalid_id(self, api_client, validator, capture_request_response, invalid_id):
        """Test getting product with invalid ID"""
        with allure.step(f"Send GET request with invalid ID: {invalid_id}"):
            response = api_client.products.get_by_id(invalid_id)
            capture_request_response(response, f"Get Product Invalid ID {invalid_id}")
        
        with allure.step("Validate error response"):
            # FakeStore API may return different status codes for invalid IDs
            assert response.status_code in [404, 400]


@allure.feature("Products API")
@allure.story("Product Categories")
class TestProductCategories:
    """Test cases for product categories"""
    
    @pytest.mark.smoke
    @pytest.mark.products
    @pytest.mark.positive
    @allure.title("Get all categories")
    @allure.description("Test getting all product categories")
    def test_get_all_categories(self, api_client, validator, capture_request_response):
        """Test getting all categories"""
        with allure.step("Send GET request to get all categories"):
            response = api_client.products.get_categories()
            capture_request_response(response, "Get All Categories")
        
        with allure.step("Validate response"):
            assert validator.validate_status_code(response, 200)
            data = response.json()
            assert isinstance(data, list)
            assert len(data) > 0
    
    @pytest.mark.products
    @pytest.mark.positive
    @allure.title("Get products by category")
    @allure.description("Test getting products from a specific category")
    def test_get_products_by_category(self, api_client, validator, capture_request_response):
        """Test getting products by category"""
        # First get categories
        categories_response = api_client.products.get_categories()
        categories = categories_response.json()
        
        if categories:
            category = categories[0]
            
            with allure.step(f"Send GET request to get products from category: {category}"):
                response = api_client.products.get_by_category(category)
                capture_request_response(response, f"Get Products from {category}")
            
            with allure.step("Validate response"):
                assert validator.validate_status_code(response, 200)
                data = response.json()
                assert isinstance(data, list)
                
                # Verify all products belong to the requested category
                for product in data:
                    assert product["category"] == category


@allure.feature("Products API")
@allure.story("Create Product")
class TestCreateProduct:
    """Test cases for creating products"""
    
    @pytest.mark.products
    @pytest.mark.positive
    @allure.title("Create product successfully")
    @allure.description("Test creating a new product")
    def test_create_product(self, api_client, validator, capture_request_response, random_product_data):
        """Test creating a product"""
        with allure.step("Send POST request to create product"):
            response = api_client.products.create(random_product_data)
            capture_request_response(response, "Create Product")
        
        with allure.step("Validate response"):
            assert validator.validate_status_code(response, 200)  # FakeStore returns 200 instead of 201
            assert validator.validate_required_fields(response, ["id"])
    
    @pytest.mark.products
    @pytest.mark.negative
    @allure.title("Create product with invalid data")
    @allure.description("Test creating product with invalid data")
    def test_create_product_invalid_data(self, api_client, validator, capture_request_response, data_provider):
        """Test creating product with invalid data"""
        invalid_variations = data_provider.get_invalid_data_variations("products")
        
        for invalid_data in invalid_variations[:3]:  # Test first 3 variations
            with allure.step(f"Send POST request with invalid data: {invalid_data}"):
                response = api_client.products.create(invalid_data)
                capture_request_response(response, "Create Product Invalid Data")
            
            with allure.step("Validate error response"):
                # Note: FakeStore API might not validate data properly
                # This is more for demonstrating test structure
                assert response.status_code in [200, 400, 422]


@allure.feature("Products API")
@allure.story("Update Product")
class TestUpdateProduct:
    """Test cases for updating products"""
    
    @pytest.mark.products
    @pytest.mark.positive
    @allure.title("Update product successfully")
    @allure.description("Test updating an existing product")
    def test_update_product(self, api_client, validator, capture_request_response, random_product_data):
        """Test updating a product"""
        product_id = 1
        
        with allure.step(f"Send PUT request to update product {product_id}"):
            response = api_client.products.update(product_id, random_product_data)
            capture_request_response(response, f"Update Product {product_id}")
        
        with allure.step("Validate response"):
            assert validator.validate_status_code(response, 200)
            assert validator.validate_required_fields(response, ["id"])
    
    @pytest.mark.products
    @pytest.mark.positive
    @allure.title("Partially update product")
    @allure.description("Test partially updating a product using PATCH")
    def test_patch_product(self, api_client, validator, capture_request_response):
        """Test patching a product"""
        product_id = 1
        partial_data = {"title": "Updated Test Product"}
        
        with allure.step(f"Send PATCH request to update product {product_id}"):
            response = api_client.products.patch(product_id, partial_data)
            capture_request_response(response, f"Patch Product {product_id}")
        
        with allure.step("Validate response"):
            assert validator.validate_status_code(response, 200)


@allure.feature("Products API")
@allure.story("Delete Product")
class TestDeleteProduct:
    """Test cases for deleting products"""
    
    @pytest.mark.products
    @pytest.mark.positive
    @allure.title("Delete product successfully")
    @allure.description("Test deleting a product")
    def test_delete_product(self, api_client, validator, capture_request_response):
        """Test deleting a product"""
        product_id = 1
        
        with allure.step(f"Send DELETE request to delete product {product_id}"):
            response = api_client.products.delete(product_id)
            capture_request_response(response, f"Delete Product {product_id}")
        
        with allure.step("Validate response"):
            assert validator.validate_status_code(response, 200)
    
    @pytest.mark.products
    @pytest.mark.negative
    @allure.title("Delete non-existent product")
    @allure.description("Test deleting a non-existent product")
    def test_delete_nonexistent_product(self, api_client, validator, capture_request_response):
        """Test deleting non-existent product"""
        product_id = 999999
        
        with allure.step(f"Send DELETE request to delete non-existent product {product_id}"):
            response = api_client.products.delete(product_id)
            capture_request_response(response, f"Delete Non-existent Product {product_id}")
        
        with allure.step("Validate response"):
            # FakeStore API behavior for non-existent resources
            assert response.status_code in [200, 404] 