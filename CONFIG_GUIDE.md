# IHACPA Configuration System Guide

## 📋 Overview

The IHACPA standalone application now includes a comprehensive configuration system that allows you to customize all aspects of the automation process. The configuration is managed through YAML files and environment variables.

## 🔧 Configuration Files

### Main Configuration File: `config.yaml`

This is the primary configuration file that contains all settings for the application. It includes:

- **Application Settings**: Name, version, description
- **Azure OpenAI Configuration**: API keys, endpoints, models
- **File Processing Settings**: Default paths, backup options
- **Processing Options**: Batch sizes, timeouts, concurrent limits
- **Vulnerability Scanning Settings**: Database enable/disable, timeouts
- **GUI Settings**: Window size, themes, fonts
- **Logging Configuration**: Log levels, file settings
- **Network Settings**: Proxies, timeouts, headers
- **Security Settings**: SSL verification, file size limits
- **Performance Settings**: Memory limits, monitoring
- **Advanced Settings**: Custom endpoints, rate limits

### GUI Settings File: `ihacpa_settings.json`

This file stores GUI-specific settings that are saved automatically when you use the application:

- Last used file paths
- Azure OpenAI credentials (encrypted)
- Processing options
- Window preferences

## 🎯 Configuration Priority

Settings are applied in this order (later overrides earlier):

1. **Default Configuration** (built into the application)
2. **config.yaml File** (if exists)
3. **Environment Variables** (highest priority)
4. **GUI Settings** (for GUI-specific values only)

## 🌍 Environment Variables

You can override any configuration setting using environment variables:

### Azure OpenAI Settings
```bash
AZURE_OPENAI_KEY=your-api-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_MODEL=gpt-4
AZURE_OPENAI_API_VERSION=2024-02-01
```

### File Settings
```bash
IHACPA_INPUT_FILE=C:\path\to\input.xlsx
IHACPA_OUTPUT_FILE=C:\path\to\output.xlsx
```

### Processing Settings
```bash
IHACPA_BATCH_SIZE=10
IHACPA_API_DELAY=0.5
IHACPA_MAX_CONCURRENT=5
```

### Network Settings
```bash
HTTP_PROXY=http://proxy.company.com:8080
HTTPS_PROXY=https://proxy.company.com:8080
```

### Debug Settings
```bash
IHACPA_DEBUG=true
IHACPA_TEST_MODE=true
IHACPA_LOG_LEVEL=DEBUG
```

## 📝 Configuration Examples

### Basic Azure OpenAI Setup

```yaml
azure_openai:
  api_key: "your-secret-api-key"
  endpoint: "https://your-company.openai.azure.com/"
  model: "gpt-4"
  api_version: "2024-02-01"
  timeout: 30
  max_retries: 3
```

### File Processing Configuration

```yaml
files:
  default_input_path: "C:\\data\\python_packages.xlsx"
  default_output_path: "C:\\output\\updated_packages.xlsx"
  create_backup: true
  backup_suffix: "_backup"
  auto_generate_output: true
  output_suffix: "_updated"
```

### Performance Optimization

```yaml
processing:
  batch_size: 20          # Process 20 packages at a time
  api_delay: 0.3          # 300ms delay between API calls
  max_concurrent: 8       # Up to 8 concurrent requests
  skip_complete: true     # Skip already processed packages
```

### Corporate Proxy Setup

```yaml
network:
  proxy:
    http: "http://proxy.company.com:8080"
    https: "https://proxy.company.com:8080"
  headers:
    User-Agent: "IHACPA-Automation/1.5.0 (Company-Name)"
```

### Debugging Configuration

```yaml
logging:
  level: "DEBUG"
  log_to_file: true
  log_file: "ihacpa_debug.log"
  max_log_size: 50    # 50MB log files

development:
  debug_mode: true
  test_mode: true
  test_package_limit: 5  # Only process first 5 packages
```

## 🔧 Using the Configuration Editor

The standalone application includes a built-in configuration editor:

1. **Open the application**
2. **Click "Edit Configuration"** in the Processing Options section
3. **Edit the YAML configuration** directly in the text editor
4. **Click "Save"** to apply changes immediately
5. **Use "Reset to Default"** to restore original settings

### Configuration Editor Features:

- **Real-time YAML validation**: Prevents saving invalid configurations
- **Syntax highlighting**: Makes editing easier
- **Default reset**: Quickly restore default settings
- **Live reload**: Changes take effect immediately

## 🛡️ Security Best Practices

### API Key Management

1. **Never commit API keys to version control**
2. **Use environment variables for production**:
   ```bash
   set AZURE_OPENAI_KEY=your-secret-key
   ```
3. **Use the GUI to enter keys** (they're stored securely)

### Network Security

```yaml
security:
  verify_ssl: true                    # Always verify SSL certificates
  max_file_size: 100                  # Limit file size to 100MB
  allowed_extensions: [".xlsx", ".xls"] # Only allow Excel files
```

## 🔍 Validation and Troubleshooting

### Configuration Validation

The application automatically validates your configuration on startup:

- **Errors**: Critical issues that prevent operation
- **Warnings**: Non-critical issues that may affect functionality

### Common Issues

**"Azure OpenAI API key not configured"**
- Add your API key to the configuration or environment variables

**"Invalid log level"**
- Use one of: DEBUG, INFO, WARNING, ERROR, CRITICAL

**"Default input file not found"**
- Update the path or remove the default_input_path setting

**"Batch size should be between 1 and 100"**
- Adjust the batch_size value in processing configuration

### Debug Mode

Enable debug mode for detailed troubleshooting:

```yaml
development:
  debug_mode: true
logging:
  level: "DEBUG"
```

## 📋 Configuration Templates

### Minimal Configuration

```yaml
azure_openai:
  api_key: "your-api-key"
  endpoint: "https://your-resource.openai.azure.com/"
  
processing:
  format_check: true
  
files:
  create_backup: true
```

### High-Performance Configuration

```yaml
processing:
  batch_size: 50
  api_delay: 0.1
  max_concurrent: 10
  
network:
  http_timeout: 60
  max_redirects: 10
  
performance:
  memory_limit: 2048
```

### Corporate/Enterprise Configuration

```yaml
network:
  proxy:
    http: "http://proxy.company.com:8080"
    https: "https://proxy.company.com:8080"
  headers:
    User-Agent: "IHACPA-Automation/1.5.0 (Company-IT)"

security:
  verify_ssl: true
  max_file_size: 50

logging:
  level: "INFO"
  log_to_file: true
  log_file: "\\\\shared\\logs\\ihacpa_automation.log"
```

## 🎛️ Advanced Configuration

### Custom API Endpoints

```yaml
advanced:
  custom_endpoints:
    github_advisory: "https://api.github.com/advisories"
    nist_nvd: "https://services.nvd.nist.gov/rest/json/cves/1.0"
    
  api_timeouts:
    github_advisory: 45
    nist_nvd: 60
    
  rate_limits:
    github_advisory: 100  # requests per minute
    nist_nvd: 20
```

### Database-Specific Configuration

```yaml
scanning:
  enable_github_advisory: true
  enable_nist_nvd: true
  enable_mitre_cve: true
  enable_snyk: false          # Disable Snyk scanning
  enable_exploit_db: false    # Disable Exploit-DB scanning
  
  scan_timeout: 45
  enable_ai_analysis: true
  min_severity: "medium"      # Only report medium+ severity
```

## 💾 Backup and Migration

### Backing Up Configuration

1. **Copy config.yaml** to a safe location
2. **Export environment variables** if used
3. **Save ihacpa_settings.json** for GUI preferences

### Migrating Configuration

1. **Copy config.yaml** to new installation
2. **Set environment variables** on new system
3. **Run application** to verify configuration

## 📞 Support

For configuration issues:

1. **Check validation messages** on application startup
2. **Review the log file** for detailed error information
3. **Use the configuration editor** to validate YAML syntax
4. **Reset to defaults** if configuration becomes corrupted

## 📚 Reference

### Complete Configuration Schema

See `config.yaml` for the complete configuration schema with all available options and their default values.

### Environment Variable Reference

| Environment Variable | Configuration Path | Description |
|---------------------|-------------------|-------------|
| `AZURE_OPENAI_KEY` | `azure_openai.api_key` | Azure OpenAI API key |
| `AZURE_OPENAI_ENDPOINT` | `azure_openai.endpoint` | Azure OpenAI endpoint URL |
| `AZURE_OPENAI_MODEL` | `azure_openai.model` | Azure OpenAI model name |
| `IHACPA_INPUT_FILE` | `files.default_input_path` | Default input file path |
| `IHACPA_OUTPUT_FILE` | `files.default_output_path` | Default output file path |
| `IHACPA_BATCH_SIZE` | `processing.batch_size` | Processing batch size |
| `IHACPA_LOG_LEVEL` | `logging.level` | Logging level |
| `HTTP_PROXY` | `network.proxy.http` | HTTP proxy URL |
| `HTTPS_PROXY` | `network.proxy.https` | HTTPS proxy URL |
| `IHACPA_DEBUG` | `development.debug_mode` | Enable debug mode |

---

**Configuration Version**: 1.5.0  
**Last Updated**: July 2025  
**Status**: Production Ready