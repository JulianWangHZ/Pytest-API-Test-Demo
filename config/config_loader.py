import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigLoader:
    
    def __init__(self):
        self.config_dir = Path(__file__).parent
        self.environment = os.getenv("TEST_ENV", "staging")
        self._cache = {}
        
        if self.environment not in ["staging", "prod"]:
            print(f"Invalid environment '{self.environment}', automatically switch to staging")
            self.environment = "staging"
        
        print(f"Current environment: {self.environment}")
        
        self._load_all_configs()
    
    def _load_all_configs(self):
        try:
            # Load environment configuration
            with open(self.config_dir / "environments.json", 'r', encoding='utf-8') as f:
                self._environments = json.load(f)
            
            # Load endpoints configuration
            with open(self.config_dir / "endpoints.json", 'r', encoding='utf-8') as f:
                self._endpoints = json.load(f)
            
            # Load test settings
            with open(self.config_dir / "test_settings.json", 'r', encoding='utf-8') as f:
                self._test_settings = json.load(f)
                
            print("Successfully loaded all configuration files")
            
        except FileNotFoundError as e:
            print(f"Failed to load configuration files: {e}")
            self._load_default_configs()
        except json.JSONDecodeError as e:
            print(f"JSON format error: {e}")
            self._load_default_configs()
    
    def _load_default_configs(self):
        self._environments = {
            "staging": {
                "base_url": "https://fakestoreapi.com",
                "timeout": 30,
                "retry_count": 3,
                "retry_delay": 2,
                "headers": {
                    "Content-Type": "application/json",
                    "User-Agent": "FakeStore-API-Test-Suite/1.0-staging"
                },
                "logging": {
                    "level": "INFO"
                },
                "performance": {
                    "max_response_time": 5.0
                },
                "test_execution": {
                    "parallel_workers": 4
                }
            },
            "prod": {
                "base_url": "https://fakestoreapi.com",
                "timeout": 20,
                "retry_count": 5,
                "retry_delay": 3,
                "headers": {
                    "Content-Type": "application/json",
                    "User-Agent": "FakeStore-API-Test-Suite/1.0-prod"
                },
                "logging": {
                    "level": "WARNING"
                },
                "performance": {
                    "max_response_time": 2.0
                },
                "test_execution": {
                    "parallel_workers": 6
                }
            }
        }
        
        self._endpoints = {
            "products": {
                "get_all": "/products",
                "get_by_id": "/products/{id}",
                "create": "/products"
            },
            "users": {
                "get_all": "/users",
                "get_by_id": "/users/{id}",
                "create": "/users"
            },
            "carts": {
                "get_all": "/carts",
                "get_by_id": "/carts/{id}",
                "create": "/carts"
            },
            "auth": {
                "login": "/auth/login"
            }
        }
        
        self._test_settings = {
            "data_generation": {
                "faker": {
                    "locale": "zh_TW",
                    "seed": 12345
                }
            },
            "auth": {
                "test_credentials": {
                    "username": "mor_2314",
                    "password": "83r5^_"
                }
            },
            "validation": {
                "strict_schema": True,
                "status_code_validation": True
            },
            "reporting": {
                "allure_enabled": True,
                "html_report": True
            }
        }
    
    def get_environment_config(self) -> Dict[str, Any]:
        env_config = self._environments.get(self.environment)
        if not env_config:
            print(f"Can't find the configuration of '{self.environment}', use 'staging' environment")
            env_config = self._environments.get("staging", {})
        
        return env_config
    
    def get_available_environments(self) -> list:
        return list(self._environments.keys())
    
    def is_production_environment(self) -> bool:
        return self.environment == "prod"
    
    def is_staging_environment(self) -> bool:
        return self.environment == "staging"
    
    def get_base_url(self) -> str:
        return self.get_environment_config().get("base_url", "https://fakestoreapi.com")
    
    def get_timeout(self) -> int:
        return self.get_environment_config().get("timeout", 30)
    
    def get_headers(self) -> Dict[str, str]:
        return self.get_environment_config().get("headers", {
            "Content-Type": "application/json"
        })
    
    def get_retry_config(self) -> Dict[str, Any]:
        env_config = self.get_environment_config()
        return {
            "retry_count": env_config.get("retry_count", 2),
            "retry_delay": env_config.get("retry_delay", 1)
        }
    
    def get_logging_config(self) -> Dict[str, Any]:
        return self.get_environment_config().get("logging", {
            "level": "INFO",
            "console_enabled": True,
            "file_enabled": True
        })
    
    def get_performance_config(self) -> Dict[str, Any]:
        return self.get_environment_config().get("performance", {
            "max_response_time": 5.0,
            "concurrent_requests": 10
        })
    
    def get_test_execution_config(self) -> Dict[str, Any]:
        return self.get_environment_config().get("test_execution", {
            "parallel_workers": 4,
            "max_retries": 2,
            "timeout_per_test": 60
        })
    
    def get_endpoints(self) -> Dict[str, Dict[str, str]]:
        return self._endpoints
    
    def get_faker_config(self) -> Dict[str, Any]:
        return self._test_settings.get("data_generation", {}).get("faker", {
            "locale": "zh_TW",
            "seed": 12345
        })
    
    def get_auth_config(self) -> Dict[str, Any]:
        return self._test_settings.get("auth", {
            "test_credentials": {
                "username": "mor_2314",
                "password": "83r5^_"
            }
        })
    
    def get_validation_config(self) -> Dict[str, Any]:
        return self._test_settings.get("validation", {
            "strict_schema": True,
            "status_code_validation": True
        })
    
    def get_reporting_config(self) -> Dict[str, Any]:
        return self._test_settings.get("reporting", {
            "allure_enabled": True,
            "html_report": True
        })
    
    def get_environment_summary(self) -> Dict[str, Any]:
        env_config = self.get_environment_config()
        return {
            "environment": self.environment,
            "available_environments": self.get_available_environments(),
            "is_production": self.is_production_environment(),
            "base_url": self.get_base_url(),
            "timeout": self.get_timeout(),
            "log_level": env_config.get("logging", {}).get("level", "INFO"),
            "parallel_workers": env_config.get("test_execution", {}).get("parallel_workers", 4),
            "max_response_time": env_config.get("performance", {}).get("max_response_time", 5.0)
        }
    
    def get_all_config(self) -> Dict[str, Any]:
        return {
            "environment": self.environment,
            "base_url": self.get_base_url(),
            "timeout": self.get_timeout(),
            "headers": self.get_headers(),
            "retry": self.get_retry_config(),
            "logging": self.get_logging_config(),
            "performance": self.get_performance_config(),
            "test_execution": self.get_test_execution_config(),
            "endpoints": self.get_endpoints(),
            "faker": self.get_faker_config(),
            "auth": self.get_auth_config(),
            "validation": self.get_validation_config(),
            "reporting": self.get_reporting_config()
        }
    
    def switch_environment(self, env: str):
        valid_envs = ["staging", "prod"]
        if env in valid_envs:
            self.environment = env
            os.environ["TEST_ENV"] = env
            print(f"Switched to environment: {env}")
        else:
            print(f"Invalid environment '{env}', only support: {valid_envs}")

# Global configuration instance
_config_loader = ConfigLoader()

def get_config() -> Dict[str, Any]:
    return _config_loader.get_all_config()

def get_environment_info() -> Dict[str, Any]:
    return _config_loader.get_environment_summary()

def switch_environment(env: str):
    _config_loader.switch_environment(env)

def is_production() -> bool:
    return _config_loader.is_production_environment()

def is_staging() -> bool:
    return _config_loader.is_staging_environment()

