from django.urls import path
from . import views

app_name = 'generate_content'

urlpatterns = [
    # PPT generation endpoints
    path('presentation/', views.generate_presentation, name='generate_presentation'),
    
    # Template management endpoints
    path('templates/', views.get_available_templates, name='available_templates'),
    path('templates/category/<str:category>/', views.get_templates_by_category, name='templates_by_category'),
    path('templates/aspect-ratio/<str:aspect_ratio>/', views.get_templates_by_aspect_ratio, name='templates_by_aspect_ratio'),
    path('templates/<str:template_id>/', views.get_template_info, name='template_info'),
    
    # System endpoints
    path('health/', views.health_check, name='health_check'),
    path('rate-limits/', views.get_rate_limit_status, name='rate_limit_status'),
    path('performance/', views.get_performance_stats, name='performance_stats'),
    path('cache/clear/', views.clear_cache, name='clear_cache'),
    path('cache/cleanup/', views.cleanup_expired_cache, name='cleanup_cache'),
]
