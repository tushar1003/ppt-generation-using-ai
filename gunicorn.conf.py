"""
Gunicorn configuration for PPT Generation API
Optimized for concurrent request handling and performance
"""
import multiprocessing
import os

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1  # Recommended formula
worker_class = "sync"  # Use sync workers for Python 3.13 compatibility
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50

# Timeout settings
timeout = 120  # Increased for PPT generation
keepalive = 2
graceful_timeout = 30

# Logging
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'ppt_generation_api'

# Server mechanics
daemon = False
pidfile = '/tmp/gunicorn.pid'
user = None
group = None
tmp_upload_dir = None

# SSL (if needed)
keyfile = None
certfile = None

# Application
wsgi_module = 'core.wsgi:application'

# Preload application for better memory usage
preload_app = True

# Worker process lifecycle
def when_ready(server):
    """Called just after the server is started."""
    server.log.info("PPT Generation API server is ready. Listening on: %s", server.address)

def worker_int(worker):
    """Called just after a worker has been killed by a signal."""
    worker.log.info("Worker received INT or QUIT signal")

def pre_fork(server, worker):
    """Called just before a worker is forked."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def worker_abort(worker):
    """Called when a worker receives the SIGABRT signal."""
    worker.log.info("Worker received SIGABRT signal")

# Environment variables
raw_env = [
    'DJANGO_SETTINGS_MODULE=core.settings',
]

# Memory and resource limits
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Performance tuning
enable_stdio_inheritance = True
reuse_port = True

# Development vs Production settings
if os.getenv('DJANGO_DEBUG', 'False').lower() == 'true':
    # Development settings
    reload = True
    reload_engine = 'auto'
    workers = 2  # Fewer workers for development
    loglevel = "debug"
else:
    # Production settings
    reload = False
    workers = multiprocessing.cpu_count() * 2 + 1
    loglevel = "info"
    
    # Security headers (can be handled by reverse proxy too)
    secure_headers = {
        'X-Frame-Options': 'DENY',
        'X-Content-Type-Options': 'nosniff',
        'X-XSS-Protection': '1; mode=block',
    }

# Custom application configuration
def post_worker_init(worker):
    """Initialize worker-specific resources"""
    # Clear template cache on worker start to ensure fresh state
    try:
        from generate_content.template_manager import template_manager
        template_manager.clear_cache()
        worker.log.info("Template cache cleared for worker %s", worker.pid)
    except ImportError:
        pass  # Template manager not available yet

# Graceful shutdown
def on_exit(server):
    """Called just before exiting."""
    server.log.info("PPT Generation API server is shutting down")

# Error handling
def worker_exit(server, worker):
    """Called just after a worker has been exited."""
    server.log.info("Worker %s exited", worker.pid)
