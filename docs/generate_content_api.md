# Generate Content API Documentation

This document provides comprehensive API documentation for the presentation generation system, including curl examples and sample responses.

## Base URL
```
http://127.0.0.1:8000/api/generate/
```

## Overview

The Generate Content API provides endpoints for:
- **Presentation Generation**: Create PowerPoint presentations with AI or user-provided content
- **Template Management**: Browse and select presentation templates
- **System Monitoring**: Health checks, performance metrics, and cache management
- **Rate Limiting**: Built-in protection against abuse

## Authentication

Most endpoints are **publicly accessible** for testing. Rate limiting is applied per IP address.

---

## 🎯 Core Endpoints

### 1. Generate Presentation

**Endpoint:** `POST /api/generate/presentation/`  
**Rate Limit:** 3 requests per minute per IP  
**Description:** Generate a PowerPoint presentation with AI or user-provided content

#### Request Body
```json
{
  "prompt": "string",                    // Main topic (required, max 500 chars)
  "num_slides": integer,                 // Number of slides (1-20)
  "layout": ["slide_type", ...],         // Slide types for each slide
  "font": "string",                      // Font name (optional, default: Arial)
  "color": "#RRGGBB",                    // Theme color (optional, default: #112233)
  "content": [{}, ...],                  // Optional content for each slide
  "include_citations": boolean,          // Include citations (optional, default: true)
  "template_id": "string",               // Template ID (optional, default: default_16_9)
  "aspect_ratio": "16:9"                 // Aspect ratio (optional)
}
```

#### Slide Types
- `title`: Title slide with main heading
- `bullet`: Bullet points slide with heading and list
- `two-column`: Two-column layout with heading
- `content-image`: Content with image placeholder

#### Content Structure by Slide Type

**Title Slide:**
```json
{
  "title_text": "Main Title"
}
```

**Bullet Slide:**
```json
{
  "heading_text": "Section Heading",
  "bullet_points": ["Point 1", "Point 2", "Point 3"]
}
```

**Two-Column Slide:**
```json
{
  "heading_text": "Section Heading",
  "left_content": ["Left item 1", "Left item 2"],
  "right_content": ["Right item 1", "Right item 2"]
}
```

**Content-Image Slide:**
```json
{
  "heading_text": "Main Heading",
  "sub_heading": "Sub heading text"
}
```

#### curl Example - User-Provided Content
```bash
curl -X POST http://127.0.0.1:8000/api/generate/presentation/ \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "API Documentation Guide",
    "num_slides": 3,
    "layout": ["title", "bullet", "two-column"],
    "font": "Arial",
    "color": "#1f4e79",
    "content": [
      {
        "title_text": "API Documentation Guide"
      },
      {
        "heading_text": "Key Features",
        "bullet_points": [
          "Comprehensive API endpoints",
          "Rate limiting protection", 
          "Advanced caching system",
          "Real-time monitoring"
        ]
      },
      {
        "heading_text": "Implementation Details",
        "left_content": [
          "Django REST Framework",
          "JWT Authentication",
          "Custom Exception Handling"
        ],
        "right_content": [
          "Gemini AI Integration",
          "Multi-level Caching",
          "Template Management"
        ]
      }
    ]
  }'
```

#### Success Response (201 Created)
```json
{
  "success": true,
  "message": "Presentation generated successfully",
  "filename": "api_documentation_guide_81b7163a.pptx",
  "file_url": "http://127.0.0.1:8000/media/api_documentation_guide_81b7163a.pptx",
  "slides": [
    {
      "slide_index": 0,
      "slide_type": "title",
      "content_source": "provided",
      "content": {
        "title_text": "API Documentation Guide"
      }
    },
    {
      "slide_index": 1,
      "slide_type": "bullet",
      "content_source": "provided",
      "content": {
        "heading_text": "Key Features",
        "bullet_points": [
          "Comprehensive API endpoints",
          "Rate limiting protection",
          "Advanced caching system",
          "Real-time monitoring"
        ]
      }
    },
    {
      "slide_index": 2,
      "slide_type": "two-column",
      "content_source": "provided",
      "content": {
        "heading_text": "Implementation Details",
        "left_content": [
          "Django REST Framework",
          "JWT Authentication",
          "Custom Exception Handling"
        ],
        "right_content": [
          "Gemini AI Integration",
          "Multi-level Caching",
          "Template Management"
        ]
      }
    }
  ],
  "metadata": {
    "total_slides": 3,
    "generated_slides": 0,
    "provided_slides": 3,
    "font": "Arial",
    "color": "#1f4e79",
    "generation_time": null
  },
  "errors": null
}
```

#### curl Example - AI-Generated Content
```bash
curl -X POST http://127.0.0.1:8000/api/generate/presentation/ \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Machine Learning Fundamentals",
    "num_slides": 4,
    "layout": ["title", "bullet", "two-column", "content-image"],
    "font": "Calibri",
    "color": "#2e7d32",
    "content": [
      {},
      {},
      {},
      {}
    ]
  }'
```

#### AI-Generated Success Response
```json
{
  "success": true,
  "message": "Presentation generated successfully",
  "filename": "machine_learning_fundamentals_a1b2c3d4.pptx",
  "file_url": "http://127.0.0.1:8000/media/machine_learning_fundamentals_a1b2c3d4.pptx",
  "slides": [
    {
      "slide_index": 0,
      "slide_type": "title",
      "content_source": "generated",
      "content": {
        "title_text": "Machine Learning Fundamentals"
      }
    },
    {
      "slide_index": 1,
      "slide_type": "bullet",
      "content_source": "generated",
      "content": {
        "heading_text": "Core Concepts",
        "bullet_points": [
          "Supervised Learning",
          "Unsupervised Learning",
          "Neural Networks",
          "Data Preprocessing"
        ]
      }
    }
  ],
  "metadata": {
    "total_slides": 4,
    "generated_slides": 4,
    "provided_slides": 0,
    "font": "Calibri",
    "color": "#2e7d32",
    "generation_time": 3.45
  }
}
```

#### Rate Limit Response (429 Too Many Requests)
```json
{
  "detail": "Request was throttled. Expected available in 45 seconds."
}
```

#### Validation Error Response (400 Bad Request)
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data provided",
    "details": {
      "prompt": [
        "This field may not be blank."
      ],
      "num_slides": [
        "Ensure this value is less than or equal to 20."
      ],
      "color": [
        "This value does not match the required pattern."
      ],
      "layout": {
        "0": [
          "\"invalid_type\" is not a valid choice."
        ]
      }
    }
  },
  "timestamp": "2025-08-31T15:30:45Z"
}
```

---

## 🎨 Template Management

### 2. Get Available Templates

**Endpoint:** `GET /api/generate/templates/`  
**Authentication:** Not required  
**Description:** List all available presentation templates

#### curl Example
```bash
curl -X GET http://127.0.0.1:8000/api/generate/templates/
```

#### Success Response (200 OK)
```json
{
  "templates": {
    "default_16_9": {
      "name": "Default Business Template",
      "category": "business",
      "aspect_ratio": "16:9",
      "description": "Standard business presentation template with clean design",
      "author": "System",
      "version": "1.0",
      "slide_layouts": [
        "title",
        "bullet",
        "two-column",
        "content-image"
      ],
      "color_scheme": {
        "primary": "#1f4e79",
        "secondary": "#70ad47",
        "accent": "#ffc000"
      },
      "font_recommendations": [
        "Calibri",
        "Arial",
        "Segoe UI"
      ]
    }
  },
  "total_count": 1
}
```

### 3. Get Templates by Category

**Endpoint:** `GET /api/generate/templates/category/{category}/`  
**Authentication:** Not required  
**Description:** Filter templates by category

#### Available Categories
- `business`: Business presentations (default_16_9)
- `academic`: Academic/educational presentations (frost_16_9)
- `creative`: Creative/artistic presentations (galaxy_16_9)
- `minimal`: Minimal design presentations

#### curl Example
```bash
curl -X GET http://127.0.0.1:8000/api/generate/templates/category/business/
```

#### Success Response (200 OK)
```json
{
  "category": "business",
  "templates": {
    "default_16_9": {
      "name": "Default Business Template",
      "aspect_ratio": "16:9",
      "description": "Standard business presentation template with clean design",
      "author": "System",
      "version": "1.0"
    }
  },
  "count": 1
}
```

### 4. Get Templates by Aspect Ratio

**Endpoint:** `GET /api/generate/templates/aspect-ratio/{aspect_ratio}/`  
**Authentication:** Not required  
**Description:** Filter templates by aspect ratio

#### Available Aspect Ratios
- `16:9`: Widescreen (1920x1080)
- `4:3`: Standard (1024x768)
- `16:10`: Widescreen (1920x1200)

#### curl Example
```bash
curl -X GET http://127.0.0.1:8000/api/generate/templates/aspect-ratio/16:9/
```

### 5. Get Template Details

**Endpoint:** `GET /api/generate/templates/{template_id}/`  
**Authentication:** Not required  
**Description:** Get detailed information about a specific template

#### curl Example
```bash
curl -X GET http://127.0.0.1:8000/api/generate/templates/default_16_9/
```

---

## 📊 System Monitoring

### 6. Health Check

**Endpoint:** `GET /api/generate/health/`  
**Authentication:** Not required  
**Description:** Check system health and service status

#### curl Example
```bash
curl -X GET http://127.0.0.1:8000/api/generate/health/
```

#### Success Response (200 OK)
```json
{
  "status": "healthy",
  "timestamp": "2025-08-31T15:30:45Z",
  "services": {
    "cache": "ok",
    "media_storage": "ok",
    "gemini_service": "available"
  },
  "version": "1.0.0",
  "rate_limits": {
    "presentation_generation": "3/minute",
    "api_calls": "100/hour",
    "validation": "50/hour"
  }
}
```

### 7. Performance Statistics

**Endpoint:** `GET /api/generate/performance/`  
**Authentication:** Not required  
**Description:** Get detailed performance metrics and cache statistics

#### curl Example
```bash
curl -X GET http://127.0.0.1:8000/api/generate/performance/
```

#### Success Response (200 OK)
```json
{
  "cache_statistics": {
    "hits": 156,
    "misses": 23,
    "memory_hits": 89,
    "django_hits": 45,
    "file_hits": 22,
    "evictions": 3,
    "hit_rate_percent": 87.2,
    "memory_cache_size": 2048576,
    "memory_cache_entries": 45,
    "memory_usage_percent": 12.5
  },
  "system_metrics": {
    "memory_usage_mb": 245.67,
    "memory_percent": 1.35,
    "cpu_percent": 8.2,
    "process_id": 4575,
    "thread_count": 8
  },
  "gunicorn_workers": {
    "current_worker_pid": 4575
  },
  "template_cache": {
    "loaded_templates": 3,
    "metadata_cache_size": 1
  }
}
```

### 8. Rate Limit Status

**Endpoint:** `GET /api/generate/rate-limits/`  
**Authentication:** Required (JWT)  
**Description:** Get current rate limit status for authenticated user

#### curl Example
```bash
curl -X GET http://127.0.0.1:8000/api/generate/rate-limits/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 🔧 Cache Management

### 9. Clear Cache

**Endpoint:** `POST /api/generate/cache/clear/`  
**Authentication:** Required (JWT)  
**Description:** Clear specific cache namespaces or all caches

#### Request Body
```json
{
  "namespaces": ["gemini", "templates"],  // Optional: specific namespaces
  "clear_all": false                      // Optional: clear all caches
}
```

#### curl Example
```bash
curl -X POST http://127.0.0.1:8000/api/generate/cache/clear/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "namespaces": ["gemini", "templates"]
  }'
```

### 10. Cleanup Expired Cache

**Endpoint:** `POST /api/generate/cache/cleanup/`  
**Authentication:** Not required  
**Description:** Remove expired cache entries

#### curl Example
```bash
curl -X POST http://127.0.0.1:8000/api/generate/cache/cleanup/
```

---

## 🚦 Rate Limiting

The API implements rate limiting to prevent abuse:

| Endpoint | Rate Limit | Scope |
|----------|------------|-------|
| `/presentation/` | 3/minute | Per IP |
| Other endpoints | 100/hour | Per IP |

### Rate Limit Headers
```
X-RateLimit-Limit: 3
X-RateLimit-Remaining: 2
X-RateLimit-Reset: 1630000000
```

### Rate Limit Exceeded Response
```json
{
  "detail": "Request was throttled. Expected available in 45 seconds."
}
```

---

## 🎯 Advanced Usage Examples

### Mixed Content Generation
Generate a presentation with both user-provided and AI-generated content:

```bash
curl -X POST http://127.0.0.1:8000/api/generate/presentation/ \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Data Science Workshop",
    "num_slides": 4,
    "layout": ["title", "bullet", "two-column", "content-image"],
    "content": [
      {
        "title_text": "Data Science Workshop"
      },
      {},
      {
        "heading_text": "Tools & Technologies",
        "left_content": ["Python", "Pandas", "NumPy"],
        "right_content": ["Jupyter", "Matplotlib", "Scikit-learn"]
      },
      {}
    ]
  }'
```

### Custom Template and Styling

#### Using Frost Template (Academic)
```bash
curl -X POST http://127.0.0.1:8000/api/generate/presentation/ \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Academic Research Presentation",
    "num_slides": 3,
    "layout": ["title", "bullet", "two-column"],
    "template_id": "frost_16_9",
    "aspect_ratio": "16:9",
    "font": "Calibri",
    "color": "#2c3e50",
    "include_citations": true,
    "content": [...]
  }'
```

#### Using Galaxy Template (Creative)
```bash
curl -X POST http://127.0.0.1:8000/api/generate/presentation/ \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Creative Design Workshop",
    "num_slides": 3,
    "layout": ["title", "bullet", "two-column"],
    "template_id": "galaxy_16_9",
    "aspect_ratio": "16:9",
    "font": "Arial",
    "color": "#8e44ad",
    "include_citations": true,
    "content": [...]
  }'
```

---

## 🔍 Error Handling

### Error Response Format
All errors follow a consistent format:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message",
    "details": {
      "field_name": ["Specific error message"]
    }
  },
  "timestamp": "2025-08-31T15:30:45Z"
}
```

### Common Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `VALIDATION_ERROR` | Input validation failed | 400 |
| `RATE_LIMIT_EXCEEDED` | Too many requests | 429 |
| `GEMINI_SERVICE_ERROR` | AI service unavailable | 503 |
| `FILE_GENERATION_ERROR` | PPT generation failed | 500 |
| `TEMPLATE_NOT_FOUND` | Invalid template ID | 404 |

### Validation Rules

- **prompt**: Required, 1-500 characters
- **num_slides**: Required, 1-20 slides
- **layout**: Required, must match num_slides length
- **color**: Optional, hex format (#RRGGBB)
- **font**: Optional, string (fallback to Arial)
- **content**: Optional, array matching num_slides length

---

## 📁 File Management

Generated presentations are stored in `/media/` directory and accessible via:
```
http://127.0.0.1:8000/media/{filename}.pptx
```

### File Naming Convention
```
{sanitized_prompt}_{random_uuid}.pptx
```

Example: `machine_learning_basics_a1b2c3d4.pptx`

---

## 🔒 Security Considerations

1. **Rate Limiting**: Prevents API abuse
2. **Input Validation**: All inputs are validated and sanitized
3. **File Security**: Generated files have unique names
4. **Error Handling**: No sensitive information in error messages
5. **CORS**: Configured for allowed origins only

---

## 🚀 Performance Tips

1. **Use Caching**: Identical requests are cached for faster responses
2. **Provide Content**: User-provided content is faster than AI generation
3. **Monitor Rate Limits**: Check headers to avoid throttling
4. **Template Selection**: Choose appropriate templates for better performance
5. **Batch Operations**: Generate multiple slides in one request when possible

---

## 📈 Monitoring and Debugging

### Check System Health
```bash
curl -X GET http://127.0.0.1:8000/api/generate/health/
```

### Monitor Performance
```bash
curl -X GET http://127.0.0.1:8000/api/generate/performance/
```

### Clear Cache if Issues
```bash
curl -X POST http://127.0.0.1:8000/api/generate/cache/clear/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"clear_all": true}'
```

---

## 🆘 Troubleshooting

### Common Issues

1. **Rate Limited**: Wait for reset time or use different IP
2. **Invalid Template**: Check available templates endpoint
3. **Generation Timeout**: Reduce slides or provide more content
4. **File Not Found**: Check file_url in response
5. **Validation Errors**: Review request format and required fields
