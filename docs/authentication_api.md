# Authentication API Documentation

This document provides comprehensive API documentation for the authentication system, including curl examples and sample responses.

## Base URL
```
http://127.0.0.1:8000/api/auth/
```

## Authentication Overview

The API uses **JWT (JSON Web Tokens)** for authentication with the following token types:
- **Access Token**: Short-lived token (2 hours) for API access
- **Refresh Token**: Long-lived token (7 days) for obtaining new access tokens

## Endpoints

### 1. User Registration

**Endpoint:** `POST /api/auth/register/`  
**Authentication:** Not required  
**Description:** Register a new user account

#### Request Body
```json
{
  "username": "string",
  "email": "string",
  "first_name": "string",
  "last_name": "string", 
  "password": "string",
  "password_confirm": "string"
}
```

#### Validation Rules
- `username`: Required, unique
- `email`: Required, valid email format
- `password`: Required, minimum 8 characters
- `password_confirm`: Must match password
- `first_name`, `last_name`: Optional

#### curl Example
```bash
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "newuser@example.com", 
    "first_name": "New",
    "last_name": "User",
    "password": "securepass123",
    "password_confirm": "securepass123"
  }'
```

#### Success Response (201 Created)
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 3,
    "username": "newuser",
    "email": "newuser@example.com",
    "first_name": "New",
    "last_name": "User",
    "date_joined": "2025-08-31T14:55:57.856427Z",
    "is_active": true
  },
  "tokens": {
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

#### Error Response (400 Bad Request)
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "username": [
        "A user with that username already exists."
      ]
    }
  }
}
```

---

### 2. User Login

**Endpoint:** `POST /api/auth/login/`  
**Authentication:** Not required  
**Description:** Authenticate user and receive JWT tokens

#### Request Body
```json
{
  "username": "string",
  "password": "string"
}
```

#### curl Example
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "password": "securepass123"
  }'
```

#### Success Response (200 OK)
```json
{
  "message": "Login successful",
  "user": {
    "id": 3,
    "username": "newuser",
    "email": "newuser@example.com",
    "first_name": "New",
    "last_name": "User",
    "date_joined": "2025-08-31T14:55:57.856427Z",
    "is_active": true
  },
  "tokens": {
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

#### Error Response (400 Bad Request)
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "non_field_errors": [
        "Invalid credentials"
      ]
    }
  }
}
```

---

### 3. Token Refresh

**Endpoint:** `POST /api/auth/token/refresh/`  
**Authentication:** Not required (uses refresh token)  
**Description:** Get a new access token using refresh token

#### Request Body
```json
{
  "refresh": "string"
}
```

#### curl Example
```bash
curl -X POST http://127.0.0.1:8000/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'
```

#### Success Response (200 OK)
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### Error Response (401 Unauthorized)
```json
{
  "detail": "Token is invalid or expired",
  "code": "token_not_valid"
}
```

---

### 4. User Profile

**Endpoint:** `GET /api/auth/profile/`  
**Authentication:** Required (Bearer token)  
**Description:** Get current user's profile information

#### curl Example
```bash
curl -X GET http://127.0.0.1:8000/api/auth/profile/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

#### Success Response (200 OK)
```json
{
  "id": 3,
  "username": "newuser",
  "email": "newuser@example.com",
  "first_name": "New",
  "last_name": "User",
  "date_joined": "2025-08-31T14:55:57.856427Z",
  "is_active": true
}
```

---

### 5. Update Profile

**Endpoint:** `PUT /api/auth/profile/`  
**Authentication:** Required (Bearer token)  
**Description:** Update current user's profile information

#### Request Body
```json
{
  "email": "string",
  "first_name": "string",
  "last_name": "string"
}
```

#### curl Example
```bash
curl -X PUT http://127.0.0.1:8000/api/auth/profile/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "email": "updated@example.com",
    "first_name": "Updated",
    "last_name": "Name"
  }'
```

#### Success Response (200 OK)
```json
{
  "id": 3,
  "username": "newuser",
  "email": "updated@example.com",
  "first_name": "Updated",
  "last_name": "Name",
  "date_joined": "2025-08-31T14:55:57.856427Z",
  "is_active": true
}
```

---

### 6. Change Password

**Endpoint:** `POST /api/auth/change-password/`  
**Authentication:** Required (Bearer token)  
**Description:** Change current user's password

#### Request Body
```json
{
  "old_password": "string",
  "new_password": "string",
  "new_password_confirm": "string"
}
```

#### Validation Rules
- `old_password`: Must match current password
- `new_password`: Minimum 8 characters
- `new_password_confirm`: Must match new_password

#### curl Example
```bash
curl -X POST http://127.0.0.1:8000/api/auth/change-password/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "old_password": "oldpass123",
    "new_password": "newpass123",
    "new_password_confirm": "newpass123"
  }'
```

#### Success Response (200 OK)
```json
{
  "message": "Password changed successfully"
}
```

#### Error Response (400 Bad Request)
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "old_password": [
        "Old password is incorrect"
      ]
    }
  }
}
```

---

### 7. User Logout

**Endpoint:** `POST /api/auth/logout/`  
**Authentication:** Required (Bearer token)  
**Description:** Logout user and blacklist refresh token

#### Request Body
```json
{
  "refresh": "string"
}
```

#### curl Example
```bash
curl -X POST http://127.0.0.1:8000/api/auth/logout/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'
```

#### Success Response (200 OK)
```json
{
  "message": "Logout successful"
}
```

#### Error Response (400 Bad Request)
```json
{
  "error": "Invalid token"
}
```

---

## Authentication Headers

For protected endpoints, include the access token in the Authorization header:

```
Authorization: Bearer <access_token>
```

## Error Handling

The API uses consistent error response format:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message",
    "details": {
      "field_name": ["Specific error message"]
    }
  }
}
```

### Common Error Codes
- `VALIDATION_ERROR`: Input validation failed
- `AUTHENTICATION_ERROR`: Invalid or missing authentication
- `PERMISSION_ERROR`: Insufficient permissions
- `NOT_FOUND_ERROR`: Resource not found

## Token Lifecycle

1. **Registration/Login**: Receive both access and refresh tokens
2. **API Calls**: Use access token in Authorization header
3. **Token Expiry**: When access token expires (2 hours), use refresh token to get new access token
4. **Refresh Token Expiry**: When refresh token expires (7 days), user must login again
5. **Logout**: Blacklist refresh token to prevent further use

## Security Considerations

- Access tokens are short-lived (2 hours) for security
- Refresh tokens are long-lived (7 days) but can be blacklisted
- All passwords are hashed using Django's built-in password hashing
- CORS is configured for allowed origins
- JWT tokens include user ID and expiration claims
