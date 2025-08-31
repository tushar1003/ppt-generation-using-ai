"""
Rate limiting utilities for PPT generation API
"""
from django.core.cache import cache
from django.conf import settings
from django_ratelimit.decorators import ratelimit
from django_ratelimit.core import is_ratelimited
from functools import wraps
import time
import hashlib
import json
from typing import Dict, Any, Optional
import logging

from .exceptions import RateLimitExceededError

logger = logging.getLogger(__name__)


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_rate_limit_key(request, group='default'):
    """Generate rate limit cache key"""
    ip = get_client_ip(request)
    user_id = getattr(request.user, 'id', None) if hasattr(request.user, 'id') and request.user.is_authenticated else 'anonymous'
    return f"ratelimit:{group}:{user_id}:{ip}"


class RateLimitConfig:
    """Rate limiting configuration"""
    
    # Different rate limits for different operations
    LIMITS = {
        'presentation_generation': {
            'rate': '3/m',  # 3 presentations per minute for easy testing
            'block': True,
            'methods': ['POST']
        },
        'api_calls': {
            'rate': '10/m',  # 10 API calls per minute for easy testing
            'block': True,
            'methods': ['GET', 'POST']
        },
        'validation': {
            'rate': '50/h',  # 50 validations per hour
            'block': True,
            'methods': ['POST']
        }
    }


def enhanced_ratelimit(group='default', key=None, rate=None, method=None, block=True):
    """
    Enhanced rate limiting decorator with custom error handling
    """
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            # Get rate limit configuration
            config = RateLimitConfig.LIMITS.get(group, {
                'rate': rate or '60/h',
                'block': block,
                'methods': method or ['GET', 'POST']
            })
            
            # Check if method is rate limited
            if request.method not in config['methods']:
                return func(request, *args, **kwargs)
            
            # Generate cache key
            cache_key = key(request) if callable(key) else get_rate_limit_key(request, group)
            
            # Check rate limit
            if is_ratelimited(request, group=group, fn=func, key=cache_key, 
                             rate=config['rate'], method=request.method):
                
                # Calculate retry after time
                retry_after = calculate_retry_after(cache_key, config['rate'])
                
                # Log rate limit hit
                logger.warning(f"Rate limit exceeded for {cache_key}", extra={
                    'group': group,
                    'rate': config['rate'],
                    'ip': get_client_ip(request),
                    'user': getattr(request.user, 'username', 'anonymous'),
                    'retry_after': retry_after
                })
                
                if config['block']:
                    raise RateLimitExceededError(
                        f"Rate limit exceeded. Try again in {retry_after} seconds.",
                        retry_after=retry_after
                    )
            
            return func(request, *args, **kwargs)
        
        return wrapper
    return decorator


def calculate_retry_after(cache_key: str, rate: str) -> int:
    """Calculate seconds until rate limit resets"""
    try:
        # Parse rate (e.g., "10/h" -> 10 requests per hour)
        count, period = rate.split('/')
        
        # Convert period to seconds
        period_seconds = {
            's': 1,
            'm': 60,
            'h': 3600,
            'd': 86400
        }.get(period, 3600)
        
        # Get current usage from cache
        current_usage = cache.get(cache_key, 0)
        
        # Calculate time until reset (simplified)
        return period_seconds // int(count)
        
    except Exception:
        return 3600  # Default to 1 hour


class PresentationCache:
    """Cache for presentation generation to avoid duplicate work"""
    
    CACHE_PREFIX = 'ppt_generation'
    DEFAULT_TIMEOUT = 3600  # 1 hour
    
    @staticmethod
    def generate_cache_key(prompt: str, layout: list, content: list, 
                          font: str = 'Arial', color: str = '#000000') -> str:
        """Generate cache key for presentation parameters"""
        # Create a hash of the input parameters
        cache_data = {
            'prompt': prompt,
            'layout': layout,
            'content': content,
            'font': font,
            'color': color
        }
        
        # Convert to JSON string and hash
        cache_string = json.dumps(cache_data, sort_keys=True)
        cache_hash = hashlib.md5(cache_string.encode()).hexdigest()
        
        return f"{PresentationCache.CACHE_PREFIX}:{cache_hash}"
    
    @staticmethod
    def get_cached_presentation(cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached presentation result"""
        try:
            cached_data = cache.get(cache_key)
            if cached_data:
                logger.info(f"Cache hit for presentation: {cache_key}")
                return cached_data
        except Exception as e:
            logger.error(f"Error retrieving from cache: {e}")
        
        return None
    
    @staticmethod
    def cache_presentation(cache_key: str, presentation_data: Dict[str, Any], 
                          timeout: int = None) -> bool:
        """Cache presentation generation result"""
        try:
            timeout = timeout or PresentationCache.DEFAULT_TIMEOUT
            cache.set(cache_key, presentation_data, timeout)
            logger.info(f"Cached presentation result: {cache_key}")
            return True
        except Exception as e:
            logger.error(f"Error caching presentation: {e}")
            return False
    
    @staticmethod
    def invalidate_cache(cache_key: str) -> bool:
        """Invalidate cached presentation"""
        try:
            cache.delete(cache_key)
            logger.info(f"Invalidated cache: {cache_key}")
            return True
        except Exception as e:
            logger.error(f"Error invalidating cache: {e}")
            return False


def cache_presentation_result(timeout: int = 3600):
    """
    Decorator to cache presentation generation results
    """
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            # Only cache for GET requests or specific conditions
            if request.method != 'POST':
                return func(request, *args, **kwargs)
            
            try:
                # Extract parameters for cache key
                data = request.data
                cache_key = PresentationCache.generate_cache_key(
                    prompt=data.get('prompt', ''),
                    layout=data.get('layout', []),
                    content=data.get('content', []),
                    font=data.get('font', 'Arial'),
                    color=data.get('color', '#000000')
                )
                
                # Check cache first
                cached_result = PresentationCache.get_cached_presentation(cache_key)
                if cached_result:
                    # Return cached result with cache indicator
                    cached_result['cached'] = True
                    cached_result['cache_key'] = cache_key
                    return cached_result
                
                # Execute function if not cached
                result = func(request, *args, **kwargs)
                
                # Cache successful results
                if hasattr(result, 'data') and result.data.get('success'):
                    PresentationCache.cache_presentation(
                        cache_key, result.data, timeout
                    )
                
                return result
                
            except Exception as e:
                logger.error(f"Error in cache decorator: {e}")
                # Fall back to normal execution
                return func(request, *args, **kwargs)
        
        return wrapper
    return decorator


# Rate limiting decorators for different endpoints
presentation_rate_limit = enhanced_ratelimit(
    group='presentation_generation',
    rate='10/h',
    method=['POST']
)

api_rate_limit = enhanced_ratelimit(
    group='api_calls',
    rate='100/h',
    method=['GET', 'POST']
)

validation_rate_limit = enhanced_ratelimit(
    group='validation',
    rate='50/h',
    method=['POST']
)
