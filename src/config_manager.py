#!/usr/bin/env python3
"""
Configuration Manager for IHACPA Python Package Review Automation
Handles loading and managing configuration from YAML files and environment variables
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional, Union
import logging

class ConfigManager:
    """Manages configuration for the IHACPA automation system"""
    
    def __init__(self, config_file: str = "config.yaml"):
        """
        Initialize configuration manager
        
        Args:
            config_file: Path to the YAML configuration file
        """
        self.config_file = config_file
        self.config = {}
        self.logger = logging.getLogger(__name__)
        
        # Load configuration
        self.load_config()
        
        # Apply environment variable overrides
        self.apply_env_overrides()
    
    def load_config(self) -> bool:
        """
        Load configuration from YAML file
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Check if config file exists
            if not os.path.exists(self.config_file):
                self.logger.warning(f"Config file {self.config_file} not found, using defaults")
                self.config = self.get_default_config()
                return False
            
            # Load YAML configuration
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f) or {}
            
            self.logger.info(f"Configuration loaded from {self.config_file}")
            return True
            
        except yaml.YAMLError as e:
            self.logger.error(f"Error parsing YAML config file: {e}")
            self.config = self.get_default_config()
            return False
        except Exception as e:
            self.logger.error(f"Error loading config file: {e}")
            self.config = self.get_default_config()
            return False
    
    def apply_env_overrides(self):
        """Apply environment variable overrides to configuration"""
        env_mappings = {
            # Azure OpenAI settings
            'AZURE_OPENAI_KEY': 'azure_openai.api_key',
            'AZURE_OPENAI_ENDPOINT': 'azure_openai.endpoint',
            'AZURE_OPENAI_MODEL': 'azure_openai.model',
            'AZURE_OPENAI_API_VERSION': 'azure_openai.api_version',
            
            # File settings
            'IHACPA_INPUT_FILE': 'files.default_input_path',
            'IHACPA_OUTPUT_FILE': 'files.default_output_path',
            
            # Processing settings
            'IHACPA_BATCH_SIZE': 'processing.batch_size',
            'IHACPA_API_DELAY': 'processing.api_delay',
            'IHACPA_MAX_CONCURRENT': 'processing.max_concurrent',
            
            # Logging settings
            'IHACPA_LOG_LEVEL': 'logging.level',
            'IHACPA_LOG_FILE': 'logging.log_file',
            
            # Network settings
            'HTTP_PROXY': 'network.proxy.http',
            'HTTPS_PROXY': 'network.proxy.https',
            
            # Debug settings
            'IHACPA_DEBUG': 'development.debug_mode',
            'IHACPA_TEST_MODE': 'development.test_mode',
        }
        
        for env_var, config_path in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                self.set_nested_value(config_path, env_value)
                self.logger.debug(f"Applied environment override: {env_var} -> {config_path}")
    
    def get_nested_value(self, path: str, default: Any = None) -> Any:
        """
        Get a nested configuration value using dot notation
        
        Args:
            path: Dot-separated path (e.g., 'azure_openai.api_key')
            default: Default value if path not found
            
        Returns:
            Configuration value or default
        """
        try:
            keys = path.split('.')
            value = self.config
            
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return default
            
            return value
        except Exception:
            return default
    
    def set_nested_value(self, path: str, value: Any):
        """
        Set a nested configuration value using dot notation
        
        Args:
            path: Dot-separated path (e.g., 'azure_openai.api_key')
            value: Value to set
        """
        keys = path.split('.')
        config = self.config
        
        # Navigate to the parent dictionary
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        # Set the final value
        final_key = keys[-1]
        
        # Convert string values to appropriate types
        if isinstance(value, str):
            if value.lower() in ['true', 'false']:
                value = value.lower() == 'true'
            elif value.isdigit():
                value = int(value)
            elif value.replace('.', '', 1).isdigit():
                value = float(value)
        
        config[final_key] = value
    
    def get_azure_openai_config(self) -> Dict[str, Any]:
        """Get Azure OpenAI configuration"""
        return self.get_nested_value('azure_openai', {})
    
    def get_processing_config(self) -> Dict[str, Any]:
        """Get processing configuration"""
        return self.get_nested_value('processing', {})
    
    def get_scanning_config(self) -> Dict[str, Any]:
        """Get vulnerability scanning configuration"""
        return self.get_nested_value('scanning', {})
    
    def get_gui_config(self) -> Dict[str, Any]:
        """Get GUI configuration"""
        return self.get_nested_value('gui', {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration"""
        return self.get_nested_value('logging', {})
    
    def get_network_config(self) -> Dict[str, Any]:
        """Get network configuration"""
        return self.get_nested_value('network', {})
    
    def get_files_config(self) -> Dict[str, Any]:
        """Get file processing configuration"""
        return self.get_nested_value('files', {})
    
    def is_debug_mode(self) -> bool:
        """Check if debug mode is enabled"""
        return self.get_nested_value('development.debug_mode', False)
    
    def is_test_mode(self) -> bool:
        """Check if test mode is enabled"""
        return self.get_nested_value('development.test_mode', False)
    
    def get_test_package_limit(self) -> int:
        """Get test mode package limit"""
        return self.get_nested_value('development.test_package_limit', 5)
    
    def save_config(self, output_file: Optional[str] = None) -> bool:
        """
        Save current configuration to YAML file
        
        Args:
            output_file: Optional output file path, defaults to current config file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            file_path = output_file or self.config_file
            
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, indent=2)
            
            self.logger.info(f"Configuration saved to {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")
            return False
    
    def export_env_vars(self) -> Dict[str, str]:
        """
        Export configuration as environment variables
        
        Returns:
            Dictionary of environment variable mappings
        """
        env_vars = {}
        
        # Azure OpenAI
        azure_config = self.get_azure_openai_config()
        if azure_config.get('api_key'):
            env_vars['AZURE_OPENAI_KEY'] = azure_config['api_key']
        if azure_config.get('endpoint'):
            env_vars['AZURE_OPENAI_ENDPOINT'] = azure_config['endpoint']
        if azure_config.get('model'):
            env_vars['AZURE_OPENAI_MODEL'] = azure_config['model']
        if azure_config.get('api_version'):
            env_vars['AZURE_OPENAI_API_VERSION'] = azure_config['api_version']
        
        # Network proxy
        network_config = self.get_network_config()
        proxy_config = network_config.get('proxy', {})
        if proxy_config.get('http'):
            env_vars['HTTP_PROXY'] = proxy_config['http']
        if proxy_config.get('https'):
            env_vars['HTTPS_PROXY'] = proxy_config['https']
        
        return env_vars
    
    def apply_to_environment(self):
        """Apply configuration to environment variables"""
        env_vars = self.export_env_vars()
        for key, value in env_vars.items():
            os.environ[key] = str(value)
        
        self.logger.debug(f"Applied {len(env_vars)} environment variables")
    
    def validate_config(self) -> Dict[str, list]:
        """
        Validate configuration and return any issues
        
        Returns:
            Dictionary with 'errors' and 'warnings' lists
        """
        errors = []
        warnings = []
        
        # Check Azure OpenAI configuration
        azure_config = self.get_azure_openai_config()
        if not azure_config.get('api_key'):
            warnings.append("Azure OpenAI API key not configured - AI analysis will be disabled")
        
        if azure_config.get('endpoint') and not azure_config['endpoint'].startswith('https://'):
            errors.append("Azure OpenAI endpoint must start with https://")
        
        # Check file settings
        files_config = self.get_files_config()
        input_path = files_config.get('default_input_path')
        if input_path and not os.path.exists(input_path):
            warnings.append(f"Default input file not found: {input_path}")
        
        # Check processing settings
        processing_config = self.get_processing_config()
        batch_size = processing_config.get('batch_size', 10)
        if batch_size < 1 or batch_size > 100:
            warnings.append("Batch size should be between 1 and 100")
        
        max_concurrent = processing_config.get('max_concurrent', 5)
        if max_concurrent < 1 or max_concurrent > 20:
            warnings.append("Max concurrent requests should be between 1 and 20")
        
        # Check logging settings
        logging_config = self.get_logging_config()
        log_level = logging_config.get('level', 'INFO')
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if log_level not in valid_levels:
            errors.append(f"Invalid log level: {log_level}. Must be one of {valid_levels}")
        
        return {'errors': errors, 'warnings': warnings}
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration values"""
        return {
            'app': {
                'name': 'IHACPA Python Package Review Automation',
                'version': '1.5.0',
                'description': 'Automated vulnerability scanning for 486 Python packages'
            },
            'azure_openai': {
                'api_key': '',
                'endpoint': 'https://your-resource-name.openai.azure.com/',
                'model': 'gpt-4',
                'api_version': '2024-02-01',
                'timeout': 30,
                'max_retries': 3
            },
            'files': {
                'default_input_path': '',
                'default_output_path': '',
                'create_backup': True,
                'backup_suffix': '_backup',
                'auto_generate_output': True,
                'output_suffix': '_updated'
            },
            'processing': {
                'format_check': True,
                'verbose_logging': True,
                'batch_size': 10,
                'api_delay': 0.5,
                'skip_complete': True,
                'max_concurrent': 5
            },
            'scanning': {
                'enable_github_advisory': True,
                'enable_nist_nvd': True,
                'enable_mitre_cve': True,
                'enable_snyk': True,
                'enable_exploit_db': True,
                'scan_timeout': 30,
                'enable_ai_analysis': True,
                'min_severity': 'low'
            },
            'gui': {
                'window_width': 900,
                'window_height': 700,
                'theme': 'default',
                'font_family': 'Arial',
                'font_size': 9,
                'auto_save_settings': True,
                'settings_file': 'ihacpa_settings.json',
                'progress_update_interval': 100
            },
            'logging': {
                'level': 'INFO',
                'log_to_file': True,
                'log_file': 'ihacpa_automation.log',
                'max_log_size': 10,
                'backup_count': 5,
                'format': '[%(asctime)s] %(levelname)s: %(message)s',
                'date_format': '%Y-%m-%d %H:%M:%S'
            },
            'network': {
                'http_timeout': 30,
                'connect_timeout': 10,
                'read_timeout': 30,
                'max_redirects': 5,
                'proxy': {'http': '', 'https': ''},
                'headers': {
                    'Accept': 'application/json',
                    'Accept-Encoding': 'gzip, deflate'
                }
            },
            'development': {
                'debug_mode': False,
                'mock_api': False,
                'test_mode': False,
                'test_package_limit': 5,
                'dry_run': False
            }
        }
    
    def __str__(self) -> str:
        """String representation of configuration"""
        return f"ConfigManager(config_file='{self.config_file}', loaded={bool(self.config)})"
    
    def __repr__(self) -> str:
        """Detailed string representation"""
        return f"ConfigManager(config_file='{self.config_file}', sections={list(self.config.keys())})"