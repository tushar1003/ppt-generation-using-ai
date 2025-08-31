"""
Custom exceptions for the PPT generation API
"""
from rest_framework import status
from rest_framework.views import exception_handler
from rest_framework.response import Response
import logging

logger = logging.getLogger(__name__)


class PPTGenerationError(Exception):
    """Base exception for PPT generation errors"""
    def __init__(self, message, code=None, details=None):
        self.message = message
        self.code = code or 'PPT_GENERATION_ERROR'
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(PPTGenerationError):
    """Raised when input validation fails"""
    def __init__(self, message, field=None, details=None):
        self.field = field
        super().__init__(message, 'VALIDATION_ERROR', details)


class GeminiServiceError(PPTGenerationError):
    """Raised when Gemini AI service fails"""
    def __init__(self, message, details=None):
        super().__init__(message, 'GEMINI_SERVICE_ERROR', details)


class FileGenerationError(PPTGenerationError):
    """Raised when PPT file generation fails"""
    def __init__(self, message, details=None):
        super().__init__(message, 'FILE_GENERATION_ERROR', details)


class RateLimitExceededError(PPTGenerationError):
    """Raised when rate limit is exceeded"""
    def __init__(self, message="Rate limit exceeded", retry_after=None):
        self.retry_after = retry_after
        super().__init__(message, 'RATE_LIMIT_EXCEEDED', {'retry_after': retry_after})


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides consistent error responses
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    # Handle our custom exceptions
    if isinstance(exc, PPTGenerationError):
        error_response = {
            'success': False,
            'error': {
                'code': exc.code,
                'message': exc.message,
                'details': exc.details
            },
            'timestamp': context['request'].META.get('HTTP_X_REQUEST_ID', 'unknown')
        }
        
        # Determine HTTP status code based on exception type
        if isinstance(exc, ValidationError):
            status_code = status.HTTP_400_BAD_REQUEST
        elif isinstance(exc, RateLimitExceededError):
            status_code = status.HTTP_429_TOO_MANY_REQUESTS
            if exc.retry_after:
                error_response['retry_after'] = exc.retry_after
        elif isinstance(exc, GeminiServiceError):
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        elif isinstance(exc, FileGenerationError):
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        else:
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        
        # Log the error
        logger.error(f"PPT API Error: {exc.code} - {exc.message}", extra={
            'exception_type': type(exc).__name__,
            'details': exc.details,
            'request_path': context['request'].path,
            'request_method': context['request'].method
        })
        
        return Response(error_response, status=status_code)
    
    # Handle standard DRF validation errors
    if response is not None:
        custom_response_data = {
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Invalid input data',
                'details': response.data
            }
        }
        response.data = custom_response_data
    
    return response


def validate_slide_layout(layout, num_slides):
    """Validate slide layout configuration"""
    valid_slide_types = ['title', 'bullet', 'two-column', 'content-image']
    
    if len(layout) != num_slides:
        raise ValidationError(
            f"Layout array length ({len(layout)}) must match num_slides ({num_slides})",
            field='layout'
        )
    
    for i, slide_type in enumerate(layout):
        if slide_type not in valid_slide_types:
            raise ValidationError(
                f"Invalid slide type '{slide_type}' at position {i}",
                field='layout',
                details={'valid_types': valid_slide_types, 'position': i}
            )


def validate_content_array(content, layout):
    """Validate content array structure"""
    if content is None:
        return  # Content is optional
    
    if len(content) != len(layout):
        raise ValidationError(
            f"Content array length ({len(content)}) must match layout length ({len(layout)})",
            field='content'
        )
    
    for i, (slide_content, slide_type) in enumerate(zip(content, layout)):
        if slide_content is None:
            continue  # Empty content is allowed
        
        if not isinstance(slide_content, dict):
            raise ValidationError(
                f"Content at position {i} must be a dictionary",
                field='content',
                details={'position': i, 'received_type': type(slide_content).__name__}
            )


def validate_presentation_limits(num_slides, prompt):
    """Validate presentation size and content limits"""
    if num_slides > 50:
        raise ValidationError(
            "Maximum 50 slides allowed per presentation",
            field='num_slides',
            details={'max_allowed': 50, 'requested': num_slides}
        )
    
    if len(prompt) > 1000:
        raise ValidationError(
            "Prompt too long. Maximum 1000 characters allowed",
            field='prompt',
            details={'max_length': 1000, 'current_length': len(prompt)}
        )
