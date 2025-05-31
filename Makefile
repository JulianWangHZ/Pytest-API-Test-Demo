.PHONY: install test smoke regression clean format lint setup-reports help docker-build docker-test docker-clean

# Default target
help:
	@echo "Available targets:"
	@echo "  install       - Install dependencies"
	@echo "  test          - Run all tests"
	@echo "  smoke         - Run smoke tests only"
	@echo "  regression    - Run regression tests only"
	@echo "  parallel      - Run tests in parallel"
	@echo "  allure        - Generate and serve Allure report"
	@echo "  html-report   - Generate HTML report"
	@echo "  coverage      - Generate coverage report"
	@echo "  format        - Format code with black"
	@echo "  lint          - Run linting checks"
	@echo "  clean         - Clean generated files"
	@echo "  setup-reports - Create reports directories"
	@echo ""
	@echo "Docker commands:"
	@echo "  docker-build  - Build Docker image"
	@echo "  docker-test   - Run tests in Docker container"
	@echo "  docker-up     - Start all services with docker-compose"
	@echo "  docker-down   - Stop all services"
	@echo "  docker-allure - View Allure reports in browser"
	@echo "  docker-clean  - Clean Docker images and containers"

# Install dependencies
install:
	pip install -r requirements.txt

# Setup report directories
setup-reports:
	mkdir -p reports/allure/results
	mkdir -p reports/allure/reports
	mkdir -p reports/html
	mkdir -p reports/coverage
	mkdir -p reports/logs

# Run all tests
test: setup-reports
	pytest

# Run smoke tests
smoke: setup-reports
	pytest -m smoke

# Run regression tests
regression: setup-reports
	pytest -m regression

# Run positive tests
positive: setup-reports
	pytest -m positive

# Run negative tests  
negative: setup-reports
	pytest -m negative

# Run tests for specific API
products: setup-reports
	pytest -m products

users: setup-reports
	pytest -m users

carts: setup-reports
	pytest -m carts

auth: setup-reports
	pytest -m auth

# Run tests in parallel
parallel: setup-reports
	pytest -n auto

# Generate and serve Allure report
allure: setup-reports
	pytest --alluredir=reports/allure/results
	allure serve reports/allure/results

# Generate Allure report without serving
allure-generate: setup-reports
	pytest --alluredir=reports/allure/results
	allure generate reports/allure/results -o reports/allure/reports --clean

# Generate HTML report
html-report: setup-reports
	pytest --html=reports/html/report.html --self-contained-html

# Generate coverage report
coverage: setup-reports
	pytest --cov=utils --cov=config --cov-report=html:reports/coverage --cov-report=term

# Format code
format:
	black .

# Run linting
lint:
	flake8 utils/ config/ tests/
	mypy utils/ config/

# Clean generated files
clean:
	rm -rf reports/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf allure-results/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Development setup
dev-setup: install setup-reports
	pre-commit install

# Run quick validation (smoke + format + lint)
quick-check: format lint smoke

# Run full validation
full-check: format lint test coverage

# Docker commands
docker-build:
	docker build -t fakestore-api-tests .

docker-test: docker-build setup-reports
	docker run --rm -v $(PWD)/reports:/app/reports fakestore-api-tests

docker-up: setup-reports
	docker-compose up --build -d

docker-down:
	docker-compose down

docker-allure: docker-up
	@echo "Allure reports will be available at: http://localhost:5050"
	@echo "Starting services..."
	sleep 10
	open http://localhost:5050 || xdg-open http://localhost:5050 || echo "Please open http://localhost:5050 in your browser"

docker-clean:
	docker-compose down -v
	docker rmi fakestore-api-tests 2>/dev/null || true
	docker system prune -f 