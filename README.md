# FakeStore API Automation Testing Framework

A professional, comprehensive API automation testing architecture specifically designed for testing the [FakeStore API](https://fakestoreapi.com/docs).

## 📋 Project Overview

This is a Python-based API testing framework that uses pytest as the test runner and integrates with the Allure reporting system. The framework supports multi-environment configuration, data-driven testing, parameterized testing, and provides a complete CI/CD integration solution.

![Test Results Demo](assets/test_results.gif)

[🔗 View Latest Test Report](https://julianwanghz.github.io/Pytest-API-Test-Demo/allure-report/)

## 📋 Key Features

- **Modular Design**: Clear architectural separation for easy maintenance and scalability
- **Data-Driven Testing**: Support for JSON format test data
- **Allure Reporting**: Beautiful test reports with detailed test steps
- **Environment Management**: Multi-environment configuration support (staging/production)
- **Robust Validation**: Multi-layer response validation (status codes, response time, JSON Schema)
- **Complete HTTP Support**: GET, POST, PUT, PATCH, DELETE methods
- **Auto Retry Mechanism**: Intelligent retry for network errors
- **Parallel Execution**: Support for pytest-xdist parallel testing
- **Docker Support**: Containerized testing environment for consistency

## 🏗️ Project Architecture

```
pytest-api-demo/
├── config/                     # Configuration files
│   ├── __init__.py
│   ├── config_loader.py        # Configuration loader
│   ├── environments.json       # Environment configurations
│   ├── test_settings.json      # Test settings
│   └── endpoints.json          # API endpoint configurations
├── utils/                      # Utility modules
│   ├── __init__.py
│   ├── api_client.py          # HTTP client
│   ├── validators.py          # Response validators
│   ├── helpers.py             # Test helper utilities
│   └── data_provider.py       # Test data provider
├── tests/                      # Test cases
│   ├── __init__.py
│   ├── test_products.py       # Products API tests
│   ├── test_users.py          # Users API tests
│   ├── test_carts.py          # Carts API tests
│   └── test_auth.py           # Authentication API tests
├── test_data/                  # Test data
│   ├── products_test_data.json
│   ├── users_test_data.json
│   ├── carts_test_data.json
│   └── schemas/               # JSON Schemas
│       ├── product_schema.json
│       ├── user_schema.json
│       └── cart_schema.json
├── reports/                    # Test reports
│   ├── allure/
│   ├── html/
│   ├── coverage/
│   └── logs/
├── conftest.py                # pytest global configuration
├── pytest.ini                # pytest settings
├── requirements.txt           # Dependencies
└── README.md                  # Project documentation
```

## 🚀 Quick Start Guide

### 1. Clone Repository

```bash
git clone <your-repo-url>
cd pytest-api-demo
```

### 2. Choose Execution Method

#### Option A: Docker (Recommended)

```bash
# One-click test execution
make docker-test

# View test reports
ls -la reports/
```

#### Option B: Local Development

```bash
# Install dependencies (requires virtual environment on macOS)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run tests
pytest -m smoke
```

## 🐳 Docker Usage (Recommended)

### Why Use Docker?

- ✅ **Environment Consistency**: Ensures all developers use the same testing environment
- ✅ **No Local Dependencies**: No need to install Python dependencies locally
- ✅ **Quick Deployment**: One-click build and run
- ✅ **Isolated Environment**: Won't pollute your local development environment

### Build Docker Image

```bash
# Build Docker image
docker build -t fakestore-api-tests .

# Or use Makefile (simpler)
make docker-build
```

### Running Tests

#### 1. Using Makefile (Recommended)

```bash
# Build and run all tests
make docker-test

# Build image only
make docker-build
```

#### 2. Using Docker Commands

```bash
# Run all tests
docker run --rm -v $(pwd)/reports:/app/reports fakestore-api-tests

# Run smoke tests
docker run --rm -v $(pwd)/reports:/app/reports fakestore-api-tests pytest -m smoke -v

# Run specific test file
docker run --rm -v $(pwd)/reports:/app/reports fakestore-api-tests pytest tests/test_products.py -v

# Run specific test case
docker run --rm -v $(pwd)/reports:/app/reports fakestore-api-tests pytest tests/test_products.py::TestGetProducts::test_get_all_products -v

# Run tests with specific markers
docker run --rm -v $(pwd)/reports:/app/reports fakestore-api-tests pytest -m "products and positive" -v
```

### Common Test Commands

```bash
# 1. Quick Smoke Tests (Basic functionality verification)
docker run --rm -v $(pwd)/reports:/app/reports fakestore-api-tests pytest -m smoke -v

# 2. Complete Product API Tests
docker run --rm -v $(pwd)/reports:/app/reports fakestore-api-tests pytest tests/test_products.py -v

# 3. Positive Test Cases
docker run --rm -v $(pwd)/reports:/app/reports fakestore-api-tests pytest -m positive -v

# 4. Negative Test Cases
docker run --rm -v $(pwd)/reports:/app/reports fakestore-api-tests pytest -m negative -v

# 5. Specific Test Method
docker run --rm -v $(pwd)/reports:/app/reports fakestore-api-tests pytest tests/test_products.py::TestGetProducts::test_get_product_invalid_id -v
```

### Viewing Reports

After test completion, reports are automatically saved to the `./reports` directory:

```bash
# View generated reports
ls -la reports/

# Reports directory structure
reports/
├── allure/          # Allure test reports
├── html/            # HTML test reports
├── coverage/        # Code coverage reports
└── logs/            # Test logs
```

### Docker Environment Variables

```bash
# Specify test environment
docker run --rm \
  -e ENVIRONMENT=staging \
  -v $(pwd)/reports:/app/reports \
  fakestore-api-tests pytest -m smoke -v

# Specify base URL
docker run --rm \
  -e BASE_URL=https://fakestoreapi.com \
  -v $(pwd)/reports:/app/reports \
  fakestore-api-tests
```

## 🛠️ Environment Setup Options

### Option 1: Docker (Recommended)

- **Use Cases**: Production environment, CI/CD, team collaboration
- **Benefits**: Environment consistency, quick deployment, no dependency conflicts
- **Commands**: `make docker-test` or `docker run ...`

### Option 2: Local Development

- **Use Cases**: Development debugging, IDE integration, quick testing
- **Prerequisites**: Need to install dependencies first `pip install -r requirements.txt`
- **Commands**: `pytest -m smoke`

### ❗ Important Notes

**Docker and Local are Independent Environments**:

- Docker installs dependencies **inside the container** during build
- Local environment needs to **separately install** dependencies to run pytest
- Docker is recommended for environment consistency

## 🧑🏻‍🎤 Test Types

### Pytest Markers

- `@pytest.mark.smoke`: Smoke tests
- `@pytest.mark.regression`: Regression tests
- `@pytest.mark.positive`: Positive test cases
- `@pytest.mark.negative`: Negative test cases
- `@pytest.mark.boundary`: Boundary value tests
- `@pytest.mark.products`: Products API related
- `@pytest.mark.users`: Users API related
- `@pytest.mark.carts`: Carts API related
- `@pytest.mark.auth`: Authentication API related

### Run Specific Test Types

```bash
# Run smoke tests
pytest -m smoke -v

# Run positive test cases
pytest -m positive -v

# Run product and user related tests
pytest -m "products or users" -v

# Exclude specific tests
pytest -m "not slow" -v
```

## 📊 Test Reports

### Allure Reports

```bash
# Generate and serve Allure report
pytest --alluredir=reports/allure/results
allure serve reports/allure/results
```

### HTML Reports

```bash
# Generate HTML report
pytest --html=reports/html/report.html --self-contained-html
```

### Coverage Reports

```bash
# Generate coverage report
pytest --cov=utils --cov=config --cov-report=html:reports/coverage
```

## 🔧 API Client Usage

```python
from utils import APIClient

# Initialize client
client = APIClient()

# Products API
response = client.products.get_all()
response = client.products.get_by_id(1)
response = client.products.create(product_data)

# Users API
response = client.users.get_all()
response = client.users.create(user_data)

# Carts API
response = client.carts.get_all()
response = client.carts.get_user_carts(1)

# Authentication API
response = client.auth.login(credentials)
```

## 📝 Test Data Management

### Loading Test Data

```python
from utils import DataProvider

data_provider = DataProvider()

# Load product test data
product_data = data_provider.get_positive_test_data("products")

# Generate random test data
random_product = data_provider.get_random_test_data("products", count=1)

# Get invalid data variations
invalid_data = data_provider.get_invalid_data_variations("products")
```

### Custom Test Data

Create JSON files in the `test_data/` directory:

```json
{
  "test_cases": [
    {
      "test_type": "positive",
      "name": "valid_data",
      "data": {...},
      "expected_fields": ["id", "name"]
    }
  ]
}
```

## 🔍 Response Validation

```python
from utils import ResponseValidator

validator = ResponseValidator()

# Basic validation
assert validator.validate_status_code(response, 200)
assert validator.validate_content_type(response, "application/json")
assert validator.validate_response_time(response, max_time=5.0)

# Field validation
assert validator.validate_required_fields(response, ["id", "title", "price"])

# JSON Schema validation
assert validator.validate_json_schema(response, "product_schema")
```

## 🛠️ Development Tools

### Code Formatting

```bash
black .
```

### Static Analysis

```bash
flake8
mypy .
```

### Pre-commit Hooks

```bash
pre-commit install
pre-commit run --all-files
```

## 📈 Continuous Integration

This framework supports integration with CI/CD tools:

```bash
# Jenkins/GitHub Actions
pytest -m "smoke" --alluredir=allure-results
```

## 🎯 Using Makefile Commands

This project includes a Makefile for convenient command execution:

```bash
# Show all available commands
make help

# Quick setup and install
make install

# Run different test types
make smoke          # Run smoke tests
make regression     # Run regression tests
make products       # Run product API tests
make parallel       # Run tests in parallel

# Generate reports
make allure         # Generate and serve Allure report
make html-report    # Generate HTML report
make coverage       # Generate coverage report

# Development tasks
make format         # Format code with black
make lint           # Run linting checks
make clean          # Clean generated files

# Combined tasks
make quick-check    # Format + lint + smoke tests
make full-check     # Format + lint + all tests + coverage
```

## 📚 Additional Resources

- [FakeStore API Documentation](https://fakestoreapi.com/docs)
- [Pytest Official Documentation](https://docs.pytest.org/)
- [Allure Report Documentation](https://docs.qameta.io/allure/)
- [Requests Documentation](https://requests.readthedocs.io/)

## 📋 Project Status

This is a complete, production-ready API testing framework that includes:

✅ **Core Components**

- Configuration management with JSON
- HTTP client with retry mechanisms
- Response validators with multi-layer validation
- Test data providers with data-driven support
- Test helpers for common operations

✅ **Test Infrastructure**

- Comprehensive pytest configuration
- Allure reporting integration
- Parallel test execution support
- Custom markers and fixtures
- Environment management

✅ **Documentation & Tools**

- Complete README with usage examples
- Makefile for common operations
- Proper project structure
- JSON schemas for validation

✅ **Ready for Extension**

- Easy to add new API endpoints
- Scalable test data management
- Modular design for maintainability
- CI/CD integration ready

## 📊 Test Markers and Usage

```bash
# Test type markers
pytest -m smoke      # Smoke tests (basic functionality verification)
pytest -m regression # Regression tests
pytest -m positive   # Positive test cases
pytest -m negative   # Negative test cases

# API functionality markers
pytest -m products   # Product-related APIs
pytest -m users      # User-related APIs
pytest -m carts      # Cart-related APIs
pytest -m auth       # Authentication-related APIs
```
