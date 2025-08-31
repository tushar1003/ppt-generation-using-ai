"""
Advanced Multi-Level Caching System for PPT Generation
Implements memory, file-based, and Redis caching with intelligent cache strategies
"""
import os
import json
import pickle
import hashlib
import time
import logging
from typing import Any, Optional, Dict, List, Union
from pathlib import Path
from django.conf import settings
from django.core.cache import cache
from django.core.cache.backends.base import DEFAULT_TIMEOUT
import threading
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from functools import wraps

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    data: Any
    created_at: datetime
    accessed_at: datetime
    access_count: int = 0
    ttl: int = 3600  # Time to live in seconds
    size_bytes: int = 0
    cache_key: str = ""
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        return datetime.now() > self.created_at + timedelta(seconds=self.ttl)
    
    def update_access(self):
        """Update access statistics"""
        self.accessed_at = datetime.now()
        self.access_count += 1


class PerformanceCache:
    """
    Multi-level caching system with intelligent cache strategies
    Level 1: Memory cache (fastest)
    Level 2: Django cache (Redis/Memcached if configured)
    Level 3: File-based cache (persistent)
    """
    
    def __init__(self):
        self.memory_cache = {}
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'memory_hits': 0,
            'django_hits': 0,
            'file_hits': 0,
            'evictions': 0
        }
        self.max_memory_size = 100 * 1024 * 1024  # 100MB
        self.current_memory_size = 0
        self.cache_dir = Path(settings.BASE_DIR) / "cache" / "performance"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        
        # Cache configuration
        self.cache_config = {
            'gemini_responses': {'ttl': 3600, 'max_size': 50 * 1024 * 1024},  # 1 hour, 50MB
            'template_data': {'ttl': 86400, 'max_size': 10 * 1024 * 1024},   # 24 hours, 10MB
            'presentation_metadata': {'ttl': 7200, 'max_size': 5 * 1024 * 1024},  # 2 hours, 5MB
            'user_preferences': {'ttl': 3600, 'max_size': 1 * 1024 * 1024},   # 1 hour, 1MB
            'font_validation': {'ttl': 86400, 'max_size': 1024 * 1024},       # 24 hours, 1MB
        }
    
    def _generate_cache_key(self, namespace: str, key_data: Union[str, Dict, List]) -> str:
        """Generate a consistent cache key"""
        if isinstance(key_data, str):
            key_string = key_data
        else:
            key_string = json.dumps(key_data, sort_keys=True)
        
        key_hash = hashlib.sha256(key_string.encode()).hexdigest()[:16]
        return f"{namespace}:{key_hash}"
    
    def _calculate_size(self, data: Any) -> int:
        """Calculate approximate size of data in bytes"""
        try:
            return len(pickle.dumps(data))
        except:
            return len(str(data).encode('utf-8'))
    
    def _evict_memory_cache(self, required_size: int):
        """Evict items from memory cache using LRU strategy"""
        with self._lock:
            if not self.memory_cache:
                return
            
            # Sort by last accessed time (LRU)
            sorted_items = sorted(
                self.memory_cache.items(),
                key=lambda x: x[1].accessed_at
            )
            
            freed_size = 0
            for cache_key, entry in sorted_items:
                if freed_size >= required_size:
                    break
                
                freed_size += entry.size_bytes
                self.current_memory_size -= entry.size_bytes
                del self.memory_cache[cache_key]
                self.cache_stats['evictions'] += 1
                
                logger.debug(f"Evicted cache entry: {cache_key}, size: {entry.size_bytes}")
    
    def get(self, namespace: str, key_data: Union[str, Dict, List], default: Any = None) -> Any:
        """
        Get data from cache with multi-level fallback
        """
        cache_key = self._generate_cache_key(namespace, key_data)
        
        # Level 1: Memory cache
        with self._lock:
            if cache_key in self.memory_cache:
                entry = self.memory_cache[cache_key]
                if not entry.is_expired():
                    entry.update_access()
                    self.cache_stats['hits'] += 1
                    self.cache_stats['memory_hits'] += 1
                    logger.debug(f"Memory cache hit: {cache_key}")
                    return entry.data
                else:
                    # Remove expired entry
                    self.current_memory_size -= entry.size_bytes
                    del self.memory_cache[cache_key]
        
        # Level 2: Django cache (Redis/Memcached)
        try:
            django_data = cache.get(cache_key)
            if django_data is not None:
                # Promote to memory cache
                self._set_memory_cache(cache_key, django_data, namespace)
                self.cache_stats['hits'] += 1
                self.cache_stats['django_hits'] += 1
                logger.debug(f"Django cache hit: {cache_key}")
                return django_data
        except Exception as e:
            logger.warning(f"Django cache error: {e}")
        
        # Level 3: File-based cache
        file_path = self.cache_dir / f"{cache_key}.pkl"
        if file_path.exists():
            try:
                with open(file_path, 'rb') as f:
                    cached_entry = pickle.load(f)
                
                if not cached_entry.is_expired():
                    # Promote to higher levels
                    self._set_django_cache(cache_key, cached_entry.data, namespace)
                    self._set_memory_cache(cache_key, cached_entry.data, namespace)
                    
                    self.cache_stats['hits'] += 1
                    self.cache_stats['file_hits'] += 1
                    logger.debug(f"File cache hit: {cache_key}")
                    return cached_entry.data
                else:
                    # Remove expired file
                    file_path.unlink()
            except Exception as e:
                logger.warning(f"File cache error: {e}")
                if file_path.exists():
                    file_path.unlink()
        
        # Cache miss
        self.cache_stats['misses'] += 1
        logger.debug(f"Cache miss: {cache_key}")
        return default
    
    def set(self, namespace: str, key_data: Union[str, Dict, List], data: Any, ttl: Optional[int] = None) -> bool:
        """
        Set data in all cache levels
        """
        cache_key = self._generate_cache_key(namespace, key_data)
        
        # Get TTL from config or use provided
        config = self.cache_config.get(namespace, {})
        if ttl is None:
            ttl = config.get('ttl', 3600)
        
        success = True
        
        # Set in all levels
        success &= self._set_memory_cache(cache_key, data, namespace, ttl)
        success &= self._set_django_cache(cache_key, data, namespace, ttl)
        success &= self._set_file_cache(cache_key, data, namespace, ttl)
        
        return success
    
    def _set_memory_cache(self, cache_key: str, data: Any, namespace: str, ttl: int = 3600) -> bool:
        """Set data in memory cache"""
        try:
            data_size = self._calculate_size(data)
            config = self.cache_config.get(namespace, {})
            max_size = config.get('max_size', 10 * 1024 * 1024)
            
            # Check if data is too large
            if data_size > max_size:
                logger.warning(f"Data too large for memory cache: {data_size} > {max_size}")
                return False
            
            with self._lock:
                # Evict if necessary
                if self.current_memory_size + data_size > self.max_memory_size:
                    self._evict_memory_cache(data_size)
                
                entry = CacheEntry(
                    data=data,
                    created_at=datetime.now(),
                    accessed_at=datetime.now(),
                    ttl=ttl,
                    size_bytes=data_size,
                    cache_key=cache_key
                )
                
                self.memory_cache[cache_key] = entry
                self.current_memory_size += data_size
                
            logger.debug(f"Set memory cache: {cache_key}, size: {data_size}")
            return True
            
        except Exception as e:
            logger.error(f"Memory cache set error: {e}")
            return False
    
    def _set_django_cache(self, cache_key: str, data: Any, namespace: str, ttl: int = 3600) -> bool:
        """Set data in Django cache"""
        try:
            cache.set(cache_key, data, ttl)
            logger.debug(f"Set Django cache: {cache_key}")
            return True
        except Exception as e:
            logger.error(f"Django cache set error: {e}")
            return False
    
    def _set_file_cache(self, cache_key: str, data: Any, namespace: str, ttl: int = 3600) -> bool:
        """Set data in file cache"""
        try:
            entry = CacheEntry(
                data=data,
                created_at=datetime.now(),
                accessed_at=datetime.now(),
                ttl=ttl,
                cache_key=cache_key
            )
            
            file_path = self.cache_dir / f"{cache_key}.pkl"
            with open(file_path, 'wb') as f:
                pickle.dump(entry, f)
            
            logger.debug(f"Set file cache: {cache_key}")
            return True
            
        except Exception as e:
            logger.error(f"File cache set error: {e}")
            return False
    
    def delete(self, namespace: str, key_data: Union[str, Dict, List]) -> bool:
        """Delete from all cache levels"""
        cache_key = self._generate_cache_key(namespace, key_data)
        
        success = True
        
        # Delete from memory cache
        with self._lock:
            if cache_key in self.memory_cache:
                entry = self.memory_cache[cache_key]
                self.current_memory_size -= entry.size_bytes
                del self.memory_cache[cache_key]
        
        # Delete from Django cache
        try:
            cache.delete(cache_key)
        except Exception as e:
            logger.error(f"Django cache delete error: {e}")
            success = False
        
        # Delete from file cache
        file_path = self.cache_dir / f"{cache_key}.pkl"
        if file_path.exists():
            try:
                file_path.unlink()
            except Exception as e:
                logger.error(f"File cache delete error: {e}")
                success = False
        
        return success
    
    def clear_namespace(self, namespace: str):
        """Clear all cache entries for a namespace"""
        # This is a simplified implementation
        # In production, you'd want more sophisticated namespace tracking
        with self._lock:
            keys_to_delete = [k for k in self.memory_cache.keys() if k.startswith(f"{namespace}:")]
            for key in keys_to_delete:
                entry = self.memory_cache[key]
                self.current_memory_size -= entry.size_bytes
                del self.memory_cache[key]
        
        # Clear file cache for namespace
        for file_path in self.cache_dir.glob(f"{namespace}_*.pkl"):
            try:
                file_path.unlink()
            except Exception as e:
                logger.error(f"Error clearing file cache: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
        hit_rate = (self.cache_stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            **self.cache_stats,
            'hit_rate_percent': round(hit_rate, 2),
            'memory_cache_size': self.current_memory_size,
            'memory_cache_entries': len(self.memory_cache),
            'memory_usage_percent': round((self.current_memory_size / self.max_memory_size) * 100, 2)
        }
    
    def cleanup_expired(self):
        """Clean up expired entries from all cache levels"""
        with self._lock:
            expired_keys = []
            for key, entry in self.memory_cache.items():
                if entry.is_expired():
                    expired_keys.append(key)
            
            for key in expired_keys:
                entry = self.memory_cache[key]
                self.current_memory_size -= entry.size_bytes
                del self.memory_cache[key]
        
        # Clean up file cache
        for file_path in self.cache_dir.glob("*.pkl"):
            try:
                with open(file_path, 'rb') as f:
                    entry = pickle.load(f)
                if entry.is_expired():
                    file_path.unlink()
            except Exception as e:
                logger.error(f"Error cleaning up file cache: {e}")


# Global cache instance
performance_cache = PerformanceCache()


def cached(namespace: str, ttl: Optional[int] = None, key_func: Optional[callable] = None):
    """
    Decorator for caching function results
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key_data = key_func(*args, **kwargs)
            else:
                cache_key_data = {
                    'func': func.__name__,
                    'args': str(args),
                    'kwargs': str(sorted(kwargs.items()))
                }
            
            # Try to get from cache
            cached_result = performance_cache.get(namespace, cache_key_data)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            performance_cache.set(namespace, cache_key_data, result, ttl)
            
            return result
        return wrapper
    return decorator


def cache_gemini_response(prompt_data: Dict) -> str:
    """Generate cache key for Gemini responses"""
    return f"gemini_{hashlib.md5(json.dumps(prompt_data, sort_keys=True).encode()).hexdigest()}"


def cache_template_data(template_id: str) -> str:
    """Generate cache key for template data"""
    return f"template_{template_id}"


def cache_presentation_config(config: Dict) -> str:
    """Generate cache key for presentation configuration"""
    return f"ppt_config_{hashlib.md5(json.dumps(config, sort_keys=True).encode()).hexdigest()}"
