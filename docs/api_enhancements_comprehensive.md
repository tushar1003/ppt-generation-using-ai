# 🛡️ API Enhancements - Comprehensive Documentation

## Overview

This document covers the advanced API enhancements implemented in the PPT Generation system, including request/response validation, comprehensive error handling, and rate limiting with practical curl examples and code documentation.

---

## 🔍 Request & Response Validation

### Input Validation System

The API implements comprehensive input validation using Django REST Framework serializers with custom validation logic.

#### Core Validation Components

1. **PresentationInputSerializer** - Main request validation
2. **Custom Validators** - Business logic validation
3. **Field Validation** - Individual field constraints
4. **Cross-field Validation** - Relationships between fields

### Validation Testing Examples

#### 1. Valid Request (Baseline)
```bash
curl -X POST http://127.0.0.1:8000/api/generate/presentation/ \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Valid Presentation",
    "num_slides": 3,
    "layout": ["title", "bullet", "two-column"],
    "font": "Arial",
    "color": "#1f4e79",
    "content": [
      {"title_text": "Valid Title"},
      {"heading_text": "Valid Heading", "bullet_points": ["Point 1", "Point 2"]},
      {"heading_text": "Valid Two Column", "left_column": "Left", "right_column": "Right"}
    ]
  }'
```

**Expected Response (201 Created):**
```json
{
  "success": true,
  "message": "Presentation generated successfully",
  "filename": "valid_presentation_abc123.pptx",
  "file_url": "http://127.0.0.1:8000/media/valid_presentation_abc123.pptx",
  "metadata": {
    "total_slides": 3,
    "generated_slides": 0,
    "provided_slides": 3
  }
}
```

#### 2. Empty Prompt Validation
```bash
curl -X POST http://127.0.0.1:8000/api/generate/presentation/ \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "",
    "num_slides": 2,
    "layout": ["title", "bullet"],
    "content": [{}, {}]
  }'
```

**Expected Response (400 Bad Request):**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data provided",
    "details": {
      "prompt": [
        "This field may not be blank."
      ]
    }
  },
  "timestamp": "2024-01-15T10:30:45Z"
}
```

#### 3. Prompt Length Validation
```bash
curl -X POST http://127.0.0.1:8000/api/generate/presentation/ \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "'"$(python3 -c "print('A' * 501)")"'",
    "num_slides": 1,
    "layout": ["title"],
    "content": [{}]
  }'
```

**Expected Response (400 Bad Request):**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data provided",
    "details": {
      "prompt": [
        "Ensure this field has no more than 500 characters."
      ]
    }
  },
  "timestamp": "2024-01-15T10:30:45Z"
}
```

#### 4. Slide Count Validation (Minimum)
```bash
curl -X POST http://127.0.0.1:8000/api/generate/presentation/ \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Test Presentation",
    "num_slides": 0,
    "layout": [],
    "content": []
  }'
```

**Expected Response (400 Bad Request):**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data provided",
    "details": {
      "num_slides": [
        "Ensure this value is greater than or equal to 1."
      ]
    }
  },
  "timestamp": "2024-01-15T10:30:45Z"
}
```

#### 5. Slide Count Validation (Maximum)
```bash
curl -X POST http://127.0.0.1:8000/api/generate/presentation/ \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Test Presentation",
    "num_slides": 25,
    "layout": ["title"],
    "content": [{}]
  }'
```

**Expected Response (400 Bad Request):**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data provided",
    "details": {
      "num_slides": [
        "Ensure this value is less than or equal to 20."
      ]
    }
  },
  "timestamp": "2024-01-15T10:30:45Z"
}
```

#### 6. Invalid Layout Type
```bash
curl -X POST http://127.0.0.1:8000/api/generate/presentation/ \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Test Presentation",
    "num_slides": 2,
    "layout": ["title", "invalid_layout"],
    "content": [{}, {}]
  }'
```

**Expected Response (400 Bad Request):**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data provided",
    "details": {
      "layout": {
        "1": [
          "\"invalid_layout\" is not a valid choice."
        ]
      }
    }
  },
  "timestamp": "2024-01-15T10:30:45Z"
}
```

#### 7. Layout-Slides Count Mismatch
```bash
curl -X POST http://127.0.0.1:8000/api/generate/presentation/ \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Test Presentation",
    "num_slides": 3,
    "layout": ["title", "bullet"],
    "content": [{}, {}, {}]
  }'
```

**Expected Response (400 Bad Request):**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Layout array length must match num_slides",
    "details": {
      "layout": [
        "Layout array must have exactly 3 items to match num_slides"
      ]
    }
  },
  "timestamp": "2024-01-15T10:30:45Z"
}
```

#### 8. Invalid Color Format
```bash
curl -X POST http://127.0.0.1:8000/api/generate/presentation/ \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Test Presentation",
    "num_slides": 1,
    "layout": ["title"],
    "color": "invalid_color",
    "content": [{}]
  }'
```

**Expected Response (400 Bad Request):**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data provided",
    "details": {
      "color": [
        "Color must be in hex format (e.g., #FF0000)"
      ]
    }
  },
  "timestamp": "2024-01-15T10:30:45Z"
}
```

#### 9. Invalid Template ID
```bash
curl -X POST http://127.0.0.1:8000/api/generate/presentation/ \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Test Presentation",
    "num_slides": 1,
    "layout": ["title"],
    "template_id": "nonexistent_template",
    "content": [{}]
  }'
```

**Expected Response (400 Bad Request):**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid template ID provided",
    "details": {
      "template_id": [
        "Template 'nonexistent_template' not found. Available templates: default_16_9, frost_16_9, galaxy_16_9"
      ]
    }
  },
  "timestamp": "2024-01-15T10:30:45Z"
}
```

#### 10. Content-Layout Mismatch Validation
```bash
curl -X POST http://127.0.0.1:8000/api/generate/presentation/ \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Test Presentation",
    "num_slides": 2,
    "layout": ["title", "bullet"],
    "content": [
      {"title_text": "Valid Title"},
      {"wrong_field": "This should be heading_text and bullet_points"}
    ]
  }'
```

**Expected Response (400 Bad Request):**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Content validation failed for slide layouts",
    "details": {
      "content": {
        "1": [
          "Bullet slide requires 'heading_text' and 'bullet_points' fields"
        ]
      }
    }
  },
  "timestamp": "2024-01-15T10:30:45Z"
}
```

#### 11. Multiple Validation Errors
```bash
curl -X POST http://127.0.0.1:8000/api/generate/presentation/ \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "",
    "num_slides": 25,
    "layout": ["invalid_type", "another_invalid"],
    "color": "not_a_color",
    "font": "",
    "content": []
  }'
```

**Expected Response (400 Bad Request):**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Multiple validation errors found",
    "details": {
      "prompt": [
        "This field may not be blank."
      ],
      "num_slides": [
        "Ensure this value is less than or equal to 20."
      ],
      "layout": {
        "0": [
          "\"invalid_type\" is not a valid choice."
        ],
        "1": [
          "\"another_invalid\" is not a valid choice."
        ]
      },
      "color": [
        "Color must be in hex format (e.g., #FF0000)"
      ]
    }
  },
  "timestamp": "2024-01-15T10:30:45Z"
}
```

---

## 🚨 Comprehensive Error Handling

### Error Categories and Examples

#### 1. Validation Errors (400 Bad Request)
Already covered in validation section above.

#### 2. Authentication Errors (401 Unauthorized)
```bash
curl -X GET http://127.0.0.1:8000/api/generate/rate-limits/ \
  -H "Authorization: Bearer invalid_token"
```

**Expected Response (401 Unauthorized):**
```json
{
  "detail": "Given token not valid for any token type",
  "code": "token_not_valid",
  "messages": [
    {
      "token_class": "AccessToken",
      "token_type": "access",
      "message": "Token is invalid or expired"
    }
  ]
}
```

#### 3. Permission Errors (403 Forbidden)
```bash
curl -X POST http://127.0.0.1:8000/api/generate/cache/clear/ \
  -H "Content-Type: application/json" \
  -d '{"clear_all": true}'
```

**Expected Response (403 Forbidden):**
```json
{
  "success": false,
  "error": {
    "code": "PERMISSION_ERROR",
    "message": "Authentication credentials were not provided",
    "details": {
      "authentication": [
        "This endpoint requires authentication"
      ]
    }
  },
  "timestamp": "2024-01-15T10:30:45Z"
}
```

#### 4. Not Found Errors (404 Not Found)
```bash
curl -X GET http://127.0.0.1:8000/api/generate/templates/nonexistent_template/
```

**Expected Response (404 Not Found):**
```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND_ERROR",
    "message": "Template not found",
    "details": {
      "template_id": "nonexistent_template",
      "available_templates": [
        "default_16_9",
        "frost_16_9", 
        "galaxy_16_9"
      ]
    }
  },
  "timestamp": "2024-01-15T10:30:45Z"
}
```

#### 5. Rate Limit Errors (429 Too Many Requests)
```bash
# Make 4 rapid requests to trigger rate limiting
for i in {1..4}; do
  curl -X POST http://127.0.0.1:8000/api/generate/presentation/ \
    -H "Content-Type: application/json" \
    -d '{
      "prompt": "Rate Test '$i'",
      "num_slides": 1,
      "layout": ["title"],
      "content": [{"title_text": "Test '$i'"}]
    }'
  echo ""
done
```

**Expected Response for 4th request (429 Too Many Requests):**
```json
{
  "detail": "Request was throttled. Expected available in 45 seconds."
}
```

#### 6. Gemini Service Errors (503 Service Unavailable)
```bash
# This error occurs when Gemini AI service is unavailable
curl -X POST http://127.0.0.1:8000/api/generate/presentation/ \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "AI Generated Content",
    "num_slides": 2,
    "layout": ["title", "bullet"],
    "content": [{}, {}]
  }'
```

**Expected Response when Gemini is unavailable (503 Service Unavailable):**
```json
{
  "success": false,
  "error": {
    "code": "GEMINI_SERVICE_ERROR",
    "message": "AI content generation service is currently unavailable",
    "details": {
      "service": "Google Gemini AI",
      "status": "unavailable",
      "retry_after": 30,
      "fallback": "Please provide content manually or try again later"
    }
  },
  "timestamp": "2024-01-15T10:30:45Z"
}
```

#### 7. File Generation Errors (500 Internal Server Error)
```bash
# This might occur with corrupted templates or file system issues
curl -X POST http://127.0.0.1:8000/api/generate/presentation/ \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "File Generation Test",
    "num_slides": 1,
    "layout": ["title"],
    "content": [{"title_text": "Test"}]
  }'
```

**Expected Response when file generation fails (500 Internal Server Error):**
```json
{
  "success": false,
  "error": {
    "code": "FILE_GENERATION_ERROR",
    "message": "Failed to generate PowerPoint file",
    "details": {
      "stage": "ppt_creation",
      "template_id": "default_16_9",
      "error_type": "template_corruption",
      "suggestion": "Try using a different template or contact support"
    }
  },
  "timestamp": "2024-01-15T10:30:45Z"
}
```

#### 8. Template Loading Errors
```bash
curl -X POST http://127.0.0.1:8000/api/generate/presentation/ \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Template Test",
    "num_slides": 1,
    "layout": ["title"],
    "template_id": "corrupted_template",
    "content": [{}]
  }'
```

**Expected Response (500 Internal Server Error):**
```json
{
  "success": false,
  "error": {
    "code": "TEMPLATE_LOADING_ERROR",
    "message": "Failed to load presentation template",
    "details": {
      "template_id": "corrupted_template",
      "error_type": "file_corruption",
      "available_templates": [
        "default_16_9",
        "frost_16_9",
        "galaxy_16_9"
      ]
    }
  },
  "timestamp": "2024-01-15T10:30:45Z"
}
```

---

## ⏱️ Rate Limiting System

### Rate Limiting Configuration

The API implements IP-based rate limiting with the following limits:
- **Presentation Generation**: 3 requests per minute
- **General API calls**: 100 requests per hour
- **Authentication endpoints**: 10 requests per minute

### Rate Limiting Testing

#### 1. Check Rate Limit Status
```bash
curl -X GET http://127.0.0.1:8000/api/generate/rate-limits/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Expected Response (200 OK):**
```json
{
  "rate_limits": {
    "presentation_generation": {
      "limit": 3,
      "remaining": 3,
      "reset_time": "2024-01-15T10:31:00Z",
      "window": "1 minute"
    },
    "api_calls": {
      "limit": 100,
      "remaining": 98,
      "reset_time": "2024-01-15T11:30:00Z",
      "window": "1 hour"
    }
  },
  "current_ip": "127.0.0.1",
  "timestamp": "2024-01-15T10:30:45Z"
}
```

#### 2. Test Rate Limiting (Automated Script)
```bash
#!/bin/bash
echo "Testing Rate Limiting - Making 5 rapid requests"
for i in {1..5}; do
  echo "Request $i:"
  response=$(curl -s -w "%{http_code}" -X POST http://127.0.0.1:8000/api/generate/presentation/ \
    -H "Content-Type: application/json" \
    -d '{
      "prompt": "Rate Test '$i'",
      "num_slides": 1,
      "layout": ["title"],
      "content": [{"title_text": "Rate Test '$i'"}]
    }')
  
  http_code="${response: -3}"
  response_body="${response%???}"
  
  echo "HTTP Status: $http_code"
  if [ "$http_code" = "201" ]; then
    echo "✅ Request successful"
  elif [ "$http_code" = "429" ]; then
    echo "🚫 Rate limited"
    echo "$response_body" | jq .
  else
    echo "❌ Other error: $http_code"
  fi
  echo "---"
  sleep 1
done
```

#### 3. Rate Limit Headers
When making requests, check the response headers for rate limit information:

```bash
curl -I -X POST http://127.0.0.1:8000/api/generate/presentation/ \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Header Test",
    "num_slides": 1,
    "layout": ["title"],
    "content": [{}]
  }'
```

**Expected Headers:**
```
HTTP/1.1 201 Created
X-RateLimit-Limit: 3
X-RateLimit-Remaining: 2
X-RateLimit-Reset: 1705312260
Content-Type: application/json
```

#### 4. Rate Limit Exceeded Response
```bash
# After exceeding the limit
curl -X POST http://127.0.0.1:8000/api/generate/presentation/ \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Exceeded Test",
    "num_slides": 1,
    "layout": ["title"],
    "content": [{}]
  }'
```

**Expected Response (429 Too Many Requests):**
```json
{
  "detail": "Request was throttled. Expected available in 45 seconds.",
  "available_in": 45,
  "throttle_type": "presentation_generation",
  "limit": 3,
  "window": "1 minute"
}
```

#### 5. Rate Limit Reset Testing
```bash
# Wait for rate limit to reset, then test
echo "Waiting for rate limit reset..."
sleep 60
echo "Testing after reset:"

curl -X POST http://127.0.0.1:8000/api/generate/presentation/ \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Reset Test",
    "num_slides": 1,
    "layout": ["title"],
    "content": [{"title_text": "After Reset"}]
  }'
```

---

## 🔧 Code Implementation Details

### Validation Architecture

#### 1. Serializer-Based Validation
```python
# Location: generate_content/serializers.py
class PresentationInputSerializer(serializers.Serializer):
    prompt = serializers.CharField(
        max_length=500,
        min_length=1,
        help_text="Main topic for the presentation"
    )
    num_slides = serializers.IntegerField(
        min_value=1,
        max_value=20,
        help_text="Number of slides (1-20)"
    )
    layout = serializers.ListField(
        child=serializers.ChoiceField(choices=SLIDE_LAYOUT_CHOICES),
        help_text="Slide layout types"
    )
    
    def validate(self, data):
        """Cross-field validation"""
        if len(data['layout']) != data['num_slides']:
            raise serializers.ValidationError(
                "Layout array length must match num_slides"
            )
        return data
```

#### 2. Custom Exception Handling
```python
# Location: generate_content/exceptions.py
class CustomException(Exception):
    def __init__(self, message, code=None, details=None):
        self.message = message
        self.code = code or self.__class__.__name__.upper()
        self.details = details or {}
        super().__init__(self.message)

class ValidationError(CustomException):
    pass

class GeminiServiceError(CustomException):
    pass

def custom_exception_handler(exc, context):
    """Custom exception handler for consistent error responses"""
    if isinstance(exc, CustomException):
        return Response({
            'success': False,
            'error': {
                'code': exc.code,
                'message': exc.message,
                'details': exc.details
            },
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_400_BAD_REQUEST)
```

#### 3. Rate Limiting Implementation
```python
# Location: generate_content/views.py
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='3/m', method='POST', block=True)
@api_view(['POST'])
@permission_classes([])
def generate_presentation(request):
    """Rate-limited presentation generation endpoint"""
    try:
        # Validation and processing logic
        pass
    except RateLimitExceeded:
        return Response({
            'detail': 'Request was throttled. Expected available in 45 seconds.'
        }, status=status.HTTP_429_TOO_MANY_REQUESTS)
```

### Error Handling Pipeline

1. **Input Validation**: Serializer validation catches format errors
2. **Business Logic Validation**: Custom validators check business rules
3. **Service Integration**: Handle external service errors (Gemini AI)
4. **File Operations**: Manage file system and template errors
5. **Response Formation**: Consistent error response format

### Rate Limiting Strategy

1. **IP-Based Limiting**: Track requests per IP address
2. **Endpoint-Specific Limits**: Different limits for different endpoints
3. **Sliding Window**: Time-based request counting
4. **Graceful Degradation**: Informative error messages
5. **Header Information**: Rate limit status in response headers

This comprehensive error handling and validation system ensures robust API operation with clear feedback for developers and users.
