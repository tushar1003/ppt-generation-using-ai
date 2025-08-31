# Documentation Index

This directory contains comprehensive documentation for the PPT Generation API project.

## Generate Content Documentation

### 1. [API Documentation](generate_content_api.md)
Complete API reference with curl examples and sample responses for all presentation generation endpoints:
- Presentation Generation (with AI and user content)
- Template Management (browse, filter, details)
- System Monitoring (health, performance, cache stats)
- Rate Limiting and Error Handling

**Features:**
- ✅ Complete curl examples for all 10+ endpoints
- ✅ Real sample request/response payloads
- ✅ Rate limiting examples and troubleshooting
- ✅ Advanced usage patterns (mixed content, custom templates)
- ✅ Comprehensive error handling scenarios

### 2. [Code Documentation](generate_content_code.md)
In-depth technical documentation covering the entire presentation generation system:
- PPT Generation Logic and slide type implementations
- Multi-level Caching System (Memory → Django → File)
- Gemini AI Service integration and prompt engineering
- Rate Limiting implementation and strategies
- Exception Handling hierarchy and custom error responses
- Template Management system with metadata
- Performance optimizations and concurrent processing

**Key Topics:**
- ✅ Architecture overview and design principles
- ✅ Detailed explanation of 4 slide types (Title, Bullet, Two-Column, Content-Image)
- ✅ Multi-tier caching strategy with LRU eviction
- ✅ Gemini AI integration with intelligent response parsing
- ✅ Rate limiting: django-ratelimit vs custom implementation
- ✅ Custom exception hierarchy and global error handling
- ✅ Template system with aspect ratio support
- ✅ Security considerations and performance optimizations

## Authentication Documentation

### 1. [API Documentation](authentication_api.md)
Complete API reference with curl examples and sample responses for all authentication endpoints:
- User Registration
- User Login  
- Token Refresh
- User Profile (GET/UPDATE)
- Change Password
- User Logout

**Features:**
- ✅ Complete curl examples for all endpoints
- ✅ Sample request/response payloads
- ✅ Error handling examples
- ✅ Authentication header formats
- ✅ Token lifecycle explanation

### 2. [Code Documentation](authentication_code.md)
In-depth technical documentation explaining design decisions and implementation:
- JWT implementation and configuration
- View inheritance patterns and rationale
- Serializer design decisions
- Security considerations
- Architecture overview

**Key Topics:**
- ✅ Why JWT was chosen for authentication
- ✅ Why `UserRegistrationView` inherits from `CreateAPIView`
- ✅ Why other views use `APIView` vs generic views
- ✅ Token lifecycle and security measures
- ✅ Error handling strategy
- ✅ Future enhancement considerations

## Quick Start

### Generate Content API
1. **For API Users**: Start with [generate_content_api.md](generate_content_api.md) for complete API reference
2. **For Developers**: Read [generate_content_code.md](generate_content_code.md) to understand the implementation
3. **Quick Test**: Use the health check endpoint: `curl -X GET http://127.0.0.1:8000/api/generate/health/`

### Authentication API  
1. **For API Users**: Start with [authentication_api.md](authentication_api.md) for complete API reference
2. **For Developers**: Read [authentication_code.md](authentication_code.md) to understand the implementation

## Testing the APIs

All curl examples in the API documentation have been tested and include real sample responses. The server should be running on `http://127.0.0.1:8000` for the examples to work.

### Automated Testing Script

For comprehensive API testing, use the provided test script:

```bash
# Make sure Django server is running first
python manage.py runserver 8000

# In another terminal, run the test script
./docs/test_generate_content_api.sh
```

The test script covers:
- ✅ All 15+ API endpoints
- ✅ Health checks and system monitoring
- ✅ Template management operations
- ✅ Presentation generation (user content, AI content, mixed)
- ✅ Error handling scenarios
- ✅ Rate limiting verification
- ✅ Cache management operations

## Authentication Flow Summary

```
1. Register/Login → Get JWT tokens (access + refresh)
2. API Calls → Use access token in Authorization header
3. Token Expires → Use refresh token to get new access token  
4. Logout → Blacklist refresh token
```

## Security Features

- ✅ JWT-based stateless authentication
- ✅ Token blacklisting on logout
- ✅ Password hashing with Django's built-in system
- ✅ Input validation and sanitization
- ✅ Consistent error handling
- ✅ Permission-based access control
