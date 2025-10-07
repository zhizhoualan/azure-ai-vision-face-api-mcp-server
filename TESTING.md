# Testing Guide

This document provides detailed information about testing the Azure AI Vision Face API MCP Server.

## Test Structure

The test suite is organized into two main categories:

### Unit Tests (No Azure Credentials Required)

These tests can run without any Azure credentials and are executed in CI/CD:

1. **`tests/test_prompt_parser.py`** - 19 tests
   - Tests the prompt parsing logic for detect, compare, and enroll operations
   - Validates URL and local file path extraction
   - Tests various image file formats (jpg, jpeg, png, bmp, gif, webp)
   - Validates error handling for invalid prompts

2. **`tests/test_imports.py`** - 5 tests
   - Smoke tests to verify all modules can be imported
   - Catches import errors and missing dependencies early
   - Tests tool modules, prompt utilities, and storage tools

### Integration Tests (Require Azure Credentials)

These tests require valid Azure Face API credentials and are skipped in CI unless credentials are provided:

1. **`tests/test_prompt_live_enroll_face.py`** - 5 tests
   - Tests face enrollment from local files and URLs
   - Tests listing persons in a group
   - Tests deleting persons and faces from groups
   
2. **`tests/test_prompt_live_compare_two_images.py`** - 1 test
   - Tests comparing faces between two images
   
3. **`tests/test_prompt_live_detect_mask_glasses.py`** - 2 tests
   - Tests face attribute detection from local files and URLs

## Running Tests

### Prerequisites

```bash
# Install test dependencies
pip install pytest python-dotenv

# Install project dependencies
pip install azure-ai-vision-face fastmcp openai opencv-python azure-storage-blob
```

### Run All Tests

```bash
# Run all tests (unit + integration)
pytest

# Run with verbose output
pytest -v

# Run with detailed output on failures
pytest -vv --tb=long
```

### Run Only Unit Tests

```bash
# Fast tests that don't require credentials
pytest tests/test_prompt_parser.py tests/test_imports.py -v
```

### Run Only Integration Tests

```bash
# First, set up your .env file with Azure credentials
cp .env.example .env
# Edit .env and add your credentials

# Run integration tests
pytest tests/test_prompt_live_*.py -v
```

### Run Specific Test File

```bash
pytest tests/test_prompt_parser.py -v
```

### Run Specific Test Function

```bash
pytest tests/test_prompt_parser.py::TestParsePromptForDetect::test_parse_local_image_with_mask_and_glasses -v
```

## Setting Up Azure Credentials for Integration Tests

Integration tests require the following environment variables:

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and fill in your Azure credentials:
   ```bash
   AZURE_FACE_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
   AZURE_FACE_API_KEY=your-api-key-here
   ```

3. Optional credentials for additional features:
   ```bash
   AZURE_OPENAI_ENDPOINT=https://your-openai.openai.azure.com/
   AZURE_OPENAI_API_KEY=your-openai-key
   AZURE_STORAGE_ACCOUNT=your-storage-account
   AZURE_STORAGE_CONTAINER=your-container
   AZURE_STORAGE_SAS_TOKEN=your-sas-token
   ```

## Continuous Integration

The GitHub Actions CI pipeline (`.github/workflows/ci.yml`) automatically:

1. **Test Job**:
   - Runs on Python 3.10, 3.11, and 3.12
   - Installs all dependencies
   - Runs unit tests (always pass)
   - Runs integration tests if credentials are configured (skip if no credentials)

2. **Lint Job**:
   - Runs ruff to check code quality
   - Provides suggestions for code improvements

### CI Triggers

The CI pipeline runs on:
- Push to `main` or `develop` branches
- Pull requests targeting `main` or `develop` branches

### Configuring CI Credentials

To enable integration tests in CI, configure the following GitHub Secrets in your repository settings:

**Required for live tests:**
- `AZURE_FACE_ENDPOINT` - Your Azure Face API endpoint URL
- `AZURE_FACE_API_KEY` - Your Azure Face API key

**Optional (for additional features):**
- `AZURE_OPENAI_ENDPOINT` - Azure OpenAI endpoint for open-set attribute detection
- `AZURE_OPENAI_API_KEY` - Azure OpenAI API key
- `AZURE_STORAGE_ACCOUNT` - Azure Storage account name
- `AZURE_STORAGE_CONTAINER` - Azure Storage container name
- `AZURE_STORAGE_SAS_TOKEN` - Azure Storage SAS token

To add secrets:
1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret with its corresponding value

When these secrets are configured, the CI pipeline will run the integration tests instead of skipping them.

## Test Coverage Summary

| Category | Tests | Status | Credentials Required |
|----------|-------|--------|---------------------|
| Unit Tests | 24 | ✅ Passing | No |
| Integration Tests | 8 | ⏭️ Skipped (without credentials) | Yes |
| **Total** | **32** | - | - |

## Adding New Tests

### Adding Unit Tests

1. Create or edit test files in `tests/` directory
2. Follow the naming convention: `test_*.py`
3. Use descriptive test function names: `test_<what>_<scenario>()`
4. Add `sys.path.insert()` if importing from `src/`

Example:
```python
import pathlib
import sys
import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from your_module import your_function

def test_your_function_success():
    """Test that your_function works correctly."""
    result = your_function("input")
    assert result == "expected_output"
```

### Adding Integration Tests

1. Add tests to appropriate `test_prompt_live_*.py` file
2. Use the `@LIVE` decorator to skip tests when credentials are missing
3. Clean up resources after tests (delete test groups, persons, etc.)

Example:
```python
@LIVE
def test_live_new_feature():
    """Test new feature with live API."""
    # Setup
    group_id = "test-group-feature"
    create_large_person_group(group_id)
    
    # Test
    result = your_function(group_id)
    
    # Assert
    assert "expected" in str(result)
    
    # Cleanup
    delete_large_person_group(group_id)
```

## Troubleshooting

### Import Errors

If you see `ModuleNotFoundError`:
```bash
# Make sure you're in the project root
cd /path/to/azure-ai-vision-face-api-mcp-server

# Install dependencies
pip install -e .
# or
pip install azure-ai-vision-face fastmcp openai opencv-python azure-storage-blob
```

### Test Collection Errors

If pytest can't collect tests:
```bash
# Check pytest configuration
pytest --collect-only

# Clear pytest cache
rm -rf .pytest_cache
pytest --cache-clear
```

### Integration Tests Failing

If integration tests fail:
1. Verify your `.env` file has correct credentials
2. Check that your Azure Face API resource is active
3. Verify your API key hasn't expired
4. Check that you're using the correct endpoint URL

## Best Practices

1. **Keep unit tests fast**: Unit tests should complete in < 1 second each
2. **Isolate integration tests**: Each test should be independent
3. **Clean up resources**: Always delete test data after integration tests
4. **Use descriptive names**: Test names should explain what they test
5. **Test edge cases**: Include tests for error conditions and edge cases
6. **Mock external calls**: Unit tests shouldn't make real API calls

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [Azure Face API Documentation](https://learn.microsoft.com/en-us/rest/api/face/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
