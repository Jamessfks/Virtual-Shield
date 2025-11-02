# Custom API Integration Guide

This guide provides detailed instructions for integrating your custom AI detection API into the application.

---

## Table of Contents
1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [API Requirements](#api-requirements)
4. [Implementation Steps](#implementation-steps)
5. [Testing](#testing)
6. [Examples](#examples)

---

## Overview

The application is designed with a modular architecture that supports multiple AI detection providers:

- **Reality Defender** (current default)
- **Custom API** (your implementation)
- **Mock Mode** (development/demo)

### Architecture

```
┌─────────────────┐
│   Next.js Web   │
│   Application   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Flask API     │
│   Server        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ DetectorService │  ◄── Abstraction Layer
└────────┬────────┘
         │
    ┌────┴────┬──────────┬──────────┐
    ▼         ▼          ▼          ▼
┌─────┐  ┌────────┐  ┌──────┐  ┌──────┐
│ RD  │  │Custom  │  │ Mock │  │Future│
│ API │  │  API   │  │ Mode │  │ APIs │
└─────┘  └────────┘  └──────┘  └──────┘
```

---

## Quick Start

### 1. Locate Integration Files

All custom API code goes in: `services/custom_api.py`

Key method to implement:
```python
def analyze_image(self, image_path: str | Path) -> Dict[str, Any]:
    # Your implementation here
```

### 2. Configure Environment

Add to `.env`:
```env
CUSTOM_API_KEY=your_api_key_here
CUSTOM_API_URL=https://api.yourservice.com
CUSTOM_API_TIMEOUT=30
```

### 3. Implement API Client

See [Implementation Steps](#implementation-steps) below.

### 4. Switch to Custom API

Edit `api_server_v2.py` (around line 120):
```python
detector = DetectorService(
    provider='custom',
    api_key=config_class.CUSTOM_API_KEY,
    api_url=config_class.CUSTOM_API_URL,
    timeout=config_class.CUSTOM_API_TIMEOUT
)
```

---

## API Requirements

### Request Format

Your API should accept image uploads via:
- **Method**: POST
- **Content-Type**: multipart/form-data
- **File Parameter**: Configurable (default: `file`)

### Response Format

Your API must return JSON with at least:

```json
{
  "is_ai": true,              // or false
  "confidence": 0.85,         // 0.0 to 1.0
  
  // Optional but recommended:
  "status": "MANIPULATED",    // or "AUTHENTIC"
  "model_version": "v2.1",
  "processing_time": 1234,    // milliseconds
  "metadata": {
    // Any additional data
  }
}
```

### Authentication

Support one of:
- Bearer token: `Authorization: Bearer <token>`
- API key header: `X-API-Key: <key>`
- Custom authentication (implement in your code)

### Error Handling

Return appropriate HTTP status codes:
- `200` - Success
- `400` - Bad request (invalid image)
- `401` - Unauthorized (bad API key)
- `413` - File too large
- `429` - Rate limit exceeded
- `500` - Internal server error

---

## Implementation Steps

### Step 1: Understand the Interface

The `CustomAPIService` class provides the interface:

```python
class CustomAPIService:
    def __init__(self, api_key: str, api_url: str, timeout: int = 30):
        # Initialize your API client
        
    def analyze_image(self, image_path: str | Path) -> Dict[str, Any]:
        # Implement image analysis
        # Return standardized format
        
    def health_check(self) -> Dict[str, Any]:
        # Optional: Check API health
```

### Step 2: Implement analyze_image()

Open `services/custom_api.py` and find the `analyze_image()` method:

```python
def analyze_image(self, image_path: str | Path) -> Dict[str, Any]:
    """
    Your implementation here
    """
    
    # 1. READ IMAGE FILE
    image_path = Path(image_path)
    if not image_path.exists():
        raise CustomAPIValidationError(f"Image not found: {image_path}")
    
    with open(image_path, 'rb') as f:
        image_data = f.read()
    
    # 2. PREPARE API REQUEST
    headers = {
        'Authorization': f'Bearer {self.api_key}',
        # Add any other headers your API needs
    }
    
    files = {
        'file': (image_path.name, image_data, 'image/jpeg')
    }
    
    # Optional: Add form data
    data = {
        'return_metadata': 'true',
        # Add parameters your API needs
    }
    
    # 3. SEND REQUEST
    try:
        response = requests.post(
            f'{self.api_url}/v1/detect',  # Your endpoint
            headers=headers,
            files=files,
            data=data,
            timeout=self.timeout,
            verify=self.verify_ssl
        )
        response.raise_for_status()
        
    except requests.Timeout:
        raise CustomAPINetworkError("Request timeout")
    except requests.ConnectionError as e:
        raise CustomAPINetworkError(f"Connection failed: {e}")
    except requests.HTTPError as e:
        if e.response.status_code == 401:
            raise CustomAPIAuthenticationError("Invalid API key")
        elif e.response.status_code == 400:
            raise CustomAPIValidationError("Invalid request")
        else:
            raise CustomAPIError(f"API error {e.response.status_code}: {e}")
    
    # 4. PARSE RESPONSE
    try:
        result = response.json()
    except ValueError:
        raise CustomAPIError("Invalid JSON response from API")
    
    # 5. VALIDATE RESPONSE
    if 'is_ai' not in result and 'status' not in result:
        raise CustomAPIError("Missing required fields in API response")
    
    # 6. NORMALIZE TO STANDARD FORMAT
    # Map your API's response to our standard format
    is_manipulated = result.get('is_ai', False) or result.get('status') == 'MANIPULATED'
    confidence_score = float(result.get('confidence', result.get('score', 0.0)))
    
    return {
        'status': 'MANIPULATED' if is_manipulated else 'AUTHENTIC',
        'score': confidence_score,
        'confidence': self._calculate_confidence(confidence_score),
        'metadata': {
            'model_version': result.get('model_version'),
            'processing_time': result.get('processing_time'),
            'raw_response': result  # Keep full response for debugging
        }
    }
```

### Step 3: Implement health_check() (Optional)

```python
def health_check(self) -> Dict[str, Any]:
    """Check if API is accessible"""
    try:
        response = requests.get(
            f'{self.api_url}/health',  # or /status, /ping, etc.
            headers={'Authorization': f'Bearer {self.api_key}'},
            timeout=5
        )
        
        return {
            'healthy': response.status_code == 200,
            'status_code': response.status_code,
            'endpoint': self.api_url
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            'healthy': False,
            'error': str(e),
            'endpoint': self.api_url
        }
```

### Step 4: Add Custom Error Handling (Optional)

If your API has specific error codes:

```python
def _handle_api_error(self, response: requests.Response):
    """Handle API-specific errors"""
    try:
        error_data = response.json()
        error_code = error_data.get('error_code')
        
        if error_code == 'INVALID_IMAGE':
            raise CustomAPIValidationError("Image format not supported")
        elif error_code == 'QUOTA_EXCEEDED':
            raise CustomAPIError("API quota exceeded")
        # Add more specific handling
        
    except ValueError:
        # Response is not JSON
        raise CustomAPIError(f"API error: {response.status_code}")
```

### Step 5: Configure the Server

Edit `api_server_v2.py`:

Find this section (around line 100-130):
```python
# ┌──────────────────────────────────────────────────────────────────┐
# │ API PROVIDER SELECTION                                           │
# └──────────────────────────────────────────────────────────────────┘

if config_class.ENABLE_MOCK_MODE:
    detector = DetectorService(provider='mock', mock_mode=True)
elif config_class.CUSTOM_API_KEY and config_class.CUSTOM_API_URL:
    # TODO: Uncomment when custom API is implemented
    detector = DetectorService(
        provider='custom',
        api_key=config_class.CUSTOM_API_KEY,
        api_url=config_class.CUSTOM_API_URL,
        timeout=config_class.CUSTOM_API_TIMEOUT
    )
else:
    detector = DetectorService(
        provider='reality_defender',
        api_key=config_class.REALITY_DEFENDER_API_KEY
    )
```

Uncomment the custom API section and update logic as needed.

---

## Testing

### Unit Tests

Create `tests/test_custom_api.py`:

```python
import pytest
from services.custom_api import CustomAPIService

def test_custom_api_initialization():
    """Test API client initialization"""
    service = CustomAPIService(
        api_key="test_key",
        api_url="https://api.example.com",
        timeout=30
    )
    assert service.api_key == "test_key"
    assert service.api_url == "https://api.example.com"

def test_analyze_image_success(tmp_path):
    """Test successful image analysis"""
    # Create test image
    test_image = tmp_path / "test.jpg"
    test_image.write_bytes(b"fake image data")
    
    # Mock the API response
    # ... implement with requests-mock or similar
    
def test_analyze_image_invalid_key():
    """Test authentication error"""
    service = CustomAPIService(
        api_key="invalid_key",
        api_url="https://api.example.com"
    )
    
    # Should raise CustomAPIAuthenticationError
    # ... implement test
```

### Integration Tests

Test with real API:

```bash
# Set test API credentials
export CUSTOM_API_KEY=your_test_key
export CUSTOM_API_URL=https://api.yourservice.com

# Run server
python api_server_v2.py

# Test endpoint
curl -X POST http://localhost:5001/api/analyze \
  -F "file=@test_images/authentic.jpg" \
  -v
```

### Manual Testing Checklist

- [ ] API initialization with valid credentials
- [ ] API initialization with invalid credentials (should fail gracefully)
- [ ] Image analysis with valid image
- [ ] Image analysis with invalid image (should return error)
- [ ] Large file handling (16MB+)
- [ ] Timeout handling
- [ ] Network error handling
- [ ] Rate limit handling
- [ ] Response parsing
- [ ] Metadata extraction

---

## Examples

### Example 1: Simple REST API

```python
def analyze_image(self, image_path: str | Path) -> Dict[str, Any]:
    with open(image_path, 'rb') as f:
        image_data = f.read()
    
    response = requests.post(
        f'{self.api_url}/detect',
        headers={'X-API-Key': self.api_key},
        files={'image': image_data},
        timeout=self.timeout
    )
    response.raise_for_status()
    
    data = response.json()
    
    return {
        'status': 'MANIPULATED' if data['is_fake'] else 'AUTHENTIC',
        'score': data['probability'],
        'confidence': self._calculate_confidence(data['probability']),
        'metadata': data
    }
```

### Example 2: GraphQL API

```python
def analyze_image(self, image_path: str | Path) -> Dict[str, Any]:
    # Read image and encode to base64
    import base64
    with open(image_path, 'rb') as f:
        image_b64 = base64.b64encode(f.read()).decode()
    
    # GraphQL mutation
    mutation = """
    mutation AnalyzeImage($imageData: String!) {
        analyzeImage(imageData: $imageData) {
            isAI
            confidence
            metadata
        }
    }
    """
    
    response = requests.post(
        self.api_url,
        headers={'Authorization': f'Bearer {self.api_key}'},
        json={
            'query': mutation,
            'variables': {'imageData': image_b64}
        },
        timeout=self.timeout
    )
    response.raise_for_status()
    
    result = response.json()['data']['analyzeImage']
    
    return {
        'status': 'MANIPULATED' if result['isAI'] else 'AUTHENTIC',
        'score': result['confidence'],
        'confidence': self._calculate_confidence(result['confidence']),
        'metadata': result.get('metadata', {})
    }
```

### Example 3: Streaming API

```python
def analyze_image(self, image_path: str | Path) -> Dict[str, Any]:
    with open(image_path, 'rb') as f:
        # Stream large files
        response = requests.post(
            f'{self.api_url}/analyze',
            headers={'Authorization': f'Bearer {self.api_key}'},
            data=f,  # Stream file
            timeout=self.timeout
        )
    
    response.raise_for_status()
    data = response.json()
    
    return {
        'status': data['result'],
        'score': data['score'],
        'confidence': self._calculate_confidence(data['score']),
        'metadata': data
    }
```

---

## Common Issues

### Issue: Import Errors

**Problem**: `ModuleNotFoundError: No module named 'services'`

**Solution**:
```bash
# Make sure you're in the project root
cd /path/to/project

# Verify services/ directory exists
ls -la services/

# Ensure __init__.py exists
ls -la services/__init__.py

# Run server from project root
python api_server_v2.py
```

### Issue: Authentication Fails

**Problem**: `CustomAPIAuthenticationError: Invalid API key`

**Solution**:
- Verify API key in `.env` is correct
- Check API key format (some APIs use prefixes)
- Ensure API key has correct permissions
- Check if API key is expired

### Issue: Timeout Errors

**Problem**: `CustomAPINetworkError: Request timeout`

**Solution**:
```env
# Increase timeout in .env
CUSTOM_API_TIMEOUT=60
```

### Issue: Response Format Mismatch

**Problem**: `CustomAPIError: Missing required fields`

**Solution**: Map your API's response correctly:
```python
# If your API returns different field names:
is_ai = result.get('ai_detected') or result.get('fake') or result.get('synthetic')
score = result.get('confidence') or result.get('probability') or result.get('score')
```

---

## Best Practices

1. **Error Handling**: Always handle all exception types
2. **Logging**: Log API calls and responses for debugging
3. **Retries**: Implement retry logic for transient failures
4. **Caching**: Cache results for identical images (optional)
5. **Validation**: Validate API responses before using
6. **Security**: Never log API keys or sensitive data
7. **Testing**: Write comprehensive tests
8. **Documentation**: Document your API integration

---

## Support

For integration help:
1. Check the example implementations in `services/custom_api.py`
2. Review error messages in server logs
3. Test with mock mode first: `ENABLE_MOCK_MODE=true`
4. Verify API documentation from your provider
5. Test API independently with curl/Postman first

---

## Next Steps

After implementing:
1. Test thoroughly with various images
2. Monitor API performance and costs
3. Implement caching if needed
4. Add custom error messages
5. Document any API-specific quirks
6. Setup monitoring and alerts
