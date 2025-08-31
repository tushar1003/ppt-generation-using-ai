import os
import uuid
from typing import Dict, Any, List
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.conf import settings
from django.urls import reverse
import logging

from .serializers import (
    PresentationInputSerializer,
    validate_slide_content,
    is_slide_content_complete
)
from .ppt_generator import PPTGenerator
from .gemini_service import GeminiContentGenerator
from .template_manager import template_manager, AspectRatio, TemplateCategory
from .performance_cache import performance_cache
from .exceptions import (
    ValidationError,
    GeminiServiceError,
    FileGenerationError,
    validate_slide_layout,
    validate_content_array,
    validate_presentation_limits
)
from django_ratelimit.decorators import ratelimit

logger = logging.getLogger(__name__)

@ratelimit(key='ip', rate='3/m', method='POST', block=True)
@api_view(['POST'])
@permission_classes([])
def generate_presentation(request):
    """
    Generate a presentation based on input prompt and specifications
    Enhanced with validation, error handling, rate limiting, and caching
    """
    try:
        # Enhanced input validation
        serializer = PresentationInputSerializer(data=request.data)
        if not serializer.is_valid():
            raise ValidationError(
                "Invalid input data provided",
                details=serializer.errors
            )
        
        input_data = serializer.validated_data
        
        # Additional custom validations
        validate_presentation_limits(
            input_data['num_slides'], 
            input_data['prompt']
        )
        
        validate_slide_layout(
            input_data['layout'], 
            input_data['num_slides']
        )
        
        validate_content_array(
            input_data.get('content'), 
            input_data['layout']
        )
        
        # Generate unique filename
        filename = f"{input_data['prompt'].lower().replace(' ', '_')}_{uuid.uuid4().hex[:8]}.pptx"
        
        # Create full path in media directory
        media_path = os.path.join(settings.MEDIA_ROOT, filename)
        
        # Initialize PPT generator with error handling
        try:
            # Get aspect ratio enum if provided
            aspect_ratio = None
            if input_data.get('aspect_ratio_enum'):
                aspect_ratio = input_data['aspect_ratio_enum']
            
            ppt_generator = PPTGenerator(
                output_filename=media_path,
                font_name=input_data.get('font', 'Arial'),
                template_id=input_data.get('template_id', 'default_16_9'),
                aspect_ratio=aspect_ratio
            )
        except Exception as e:
            raise FileGenerationError(
                f"Failed to initialize PPT generator: {str(e)}",
                details={
                    'filename': filename, 
                    'font': input_data.get('font'),
                    'template_id': input_data.get('template_id'),
                    'aspect_ratio': input_data.get('aspect_ratio')
                }
            )
        
        # Prepare content array for Gemini inference
        content_for_inference = []
        slides_needing_generation = []
        
        for i, slide_type in enumerate(input_data['layout']):
            # Get provided content for this slide (if any)
            provided_content = {}
            if input_data.get('content') and i < len(input_data['content']):
                provided_content = input_data['content'][i] or {}
            
            # Validate and normalize content
            validated_content = validate_slide_content(slide_type, provided_content)
            
            # Check if we need to generate content
            needs_generation = not is_slide_content_complete(slide_type, validated_content)
            
            
            if needs_generation:
                content_for_inference.append({})  # Empty object for Gemini to fill
                slides_needing_generation.append(i)
            else:
                content_for_inference.append(validated_content)  # Use provided content
        
        # Single Gemini inference call if needed
        if slides_needing_generation:
            try:
                gemini_service = GeminiContentGenerator(
                    project_id=os.getenv("GOOGLE_CLOUD_PROJECT"),
                    location=os.getenv("GOOGLE_CLOUD_REGION", "us-central1")
                )
                
                generated_response = gemini_service.generate_presentation_content(
                    prompt=input_data['prompt'],
                    layout=input_data['layout'],
                    content=content_for_inference,
                    filename=filename,
                    include_citations=input_data.get('include_citations', True),
                    citation_style=input_data.get('citation_style', 'apa')
                )
                
                # Merge generated content with user-provided content
                if generated_response and 'content' in generated_response:
                    generated_content = generated_response['content']
                    
                    # Only update slides that needed generation, preserve user-provided content
                    for slide_idx in slides_needing_generation:
                        if slide_idx < len(generated_content) and generated_content[slide_idx]:
                            content_for_inference[slide_idx] = generated_content[slide_idx]
                            logger.info(f"Updated slide {slide_idx} with AI-generated content")
                        else:
                            logger.warning(f"No generated content available for slide {slide_idx}")
                else:
                    raise GeminiServiceError("Invalid response from Gemini service")
                    
            except GeminiServiceError:
                raise  # Re-raise Gemini-specific errors
            except Exception as e:
                logger.warning(f"Gemini generation failed, using fallback: {str(e)}")
                # Fallback to simple generation if Gemini fails
                try:
                    content_for_inference = generate_fallback_content(
                        input_data['prompt'], 
                        input_data['layout'], 
                        content_for_inference
                    )
                except Exception as fallback_error:
                    raise GeminiServiceError(
                        f"Both Gemini and fallback generation failed: {str(fallback_error)}",
                        details={'original_error': str(e), 'fallback_error': str(fallback_error)}
                    )
        
        # Process each slide and add to presentation
        slides_results = []
        errors = []
        
        for i, slide_type in enumerate(input_data['layout']):
            try:
                final_content = content_for_inference[i]
                content_source = "provided" if i not in slides_needing_generation else "generated"
                
                # Add slide to presentation
                add_slide_to_presentation(ppt_generator, slide_type, final_content)
                
                # Record result
                slides_results.append({
                    'slide_index': i,
                    'slide_type': slide_type,
                    'content_source': content_source,
                    'content': final_content
                })
                
            except Exception as e:
                error_msg = f"Error processing slide {i} ({slide_type}): {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)
        
        # Save presentation with error handling
        try:
            ppt_generator.save()
        except Exception as e:
            raise FileGenerationError(
                f"Failed to save presentation file: {str(e)}",
                details={'filename': filename, 'media_path': media_path}
            )
        
        # Generate file URL
        file_url = request.build_absolute_uri(settings.MEDIA_URL + filename)
        
        # Prepare enhanced response
        response_data = {
            'success': len(errors) == 0,
            'message': "Presentation generated successfully" if len(errors) == 0 else f"Presentation generated with {len(errors)} errors",
            'filename': filename,
            'file_url': file_url,
            'slides': slides_results,
            'metadata': {
                'total_slides': len(slides_results),
                'generated_slides': len(slides_needing_generation),
                'provided_slides': len(slides_results) - len(slides_needing_generation),
                'font': input_data.get('font', 'Arial'),
                'color': input_data.get('color', '#000000'),
                'generation_time': None  # Could add timing if needed
            },
            'errors': errors if errors else None
        }
        
        # Log successful generation
        logger.info(f"Successfully generated presentation: {filename}", extra={
            'user': getattr(request.user, 'username', 'anonymous'),
            'slides_count': len(slides_results),
            'prompt_length': len(input_data['prompt'])
        })
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except (ValidationError, GeminiServiceError, FileGenerationError):
        # These will be handled by custom exception handler
        raise
    except Exception as e:
        # Catch any unexpected errors
        logger.error(f"Unexpected error in presentation generation: {str(e)}", extra={
            'user': getattr(request.user, 'username', 'anonymous'),
            'request_data': request.data
        })
        raise FileGenerationError(
            f"Unexpected error during presentation generation: {str(e)}",
            details={'error_type': type(e).__name__}
        )


def generate_fallback_content(prompt: str, layout: List[str], content_array: List[Dict]) -> List[Dict]:
    """Generate fallback content when Gemini is not available"""
    
    for i, slide_type in enumerate(layout):
        if not content_array[i]:  # Empty content needs generation
            if slide_type == 'title':
                content_array[i] = {"title_text": f"{prompt.title()}"}
            elif slide_type == 'bullet':
                headings = {
                    0: f"Introduction to {prompt}",
                    1: f"What is {prompt}?",
                    2: f"{prompt} Overview",
                    3: f"Key Concepts in {prompt}",
                    4: f"Applications of {prompt}",
                }
                content_array[i] = {
                    "heading_text": headings.get(i, f"{prompt} - Topic {i + 1}"),
                    "bullet_points": [f"Key aspect of {prompt}", f"Important {prompt} concept", f"Core {prompt} principle"]
                }
            elif slide_type == 'two-column':
                content_array[i] = {
                    "heading_text": f"{prompt} Comparison",
                    "left_content": [f"{prompt} Benefits:", f"• Improved efficiency", f"• Better outcomes"],
                    "right_content": [f"{prompt} Challenges:", f"• Implementation complexity", f"• Resource requirements"]
                }
            elif slide_type == 'content-image':
                content_array[i] = {
                    "main_heading": f"{prompt} Overview",
                    "sub_heading": f"Understanding the fundamentals of {prompt} and its core principles"
                }
    
    return content_array


def add_slide_to_presentation(ppt_generator: PPTGenerator, slide_type: str, content: Dict[str, Any]):
    """Add a slide to the presentation based on type and content"""
    
    # Extract citations if present
    citations = content.get('citations', [])
    
    if slide_type == 'title':
        ppt_generator.add_title_slide(
            title_text=content.get('title_text', 'Untitled'),
            citations=citations
        )
    
    elif slide_type == 'bullet':
        ppt_generator.add_bullet_slide(
            heading_text=content.get('heading_text', 'Heading'),
            bullet_points=content.get('bullet_points', ['Point 1', 'Point 2', 'Point 3']),
            citations=citations
        )
    
    elif slide_type == 'two-column':
        # Handle both field name variations (left_content/left_column, right_content/right_column)
        left_content = content.get('left_content') or content.get('left_column', ['Left content'])
        right_content = content.get('right_content') or content.get('right_column', ['Right content'])
        
        # Convert string to list if needed (for user-provided newline-separated content)
        if isinstance(left_content, str):
            left_content = left_content.split('\n')
        if isinstance(right_content, str):
            right_content = right_content.split('\n')
            
        ppt_generator.add_two_column_slide(
            heading_text=content.get('heading_text', 'Heading'),
            left_content=left_content,
            right_content=right_content,
            citations=citations
        )
    
    elif slide_type == 'content-image':
        ppt_generator.add_image_slide(
            main_heading=content.get('main_heading', 'Main Heading'),
            sub_heading=content.get('sub_heading', 'Sub heading'),
            citations=citations
        )


@api_view(['GET'])
@permission_classes([])
def health_check(request):
    """
    API health check endpoint with system status
    """
    try:
        from django.core.cache import cache
        
        # Test cache connectivity
        cache_key = 'health_check_test'
        cache.set(cache_key, 'ok', 30)
        cache_status = cache.get(cache_key) == 'ok'
        cache.delete(cache_key)
        
        # Check media directory
        media_accessible = os.path.exists(settings.MEDIA_ROOT) and os.access(settings.MEDIA_ROOT, os.W_OK)
        
        # System status
        status_data = {
            'status': 'healthy',
            'timestamp': request.META.get('HTTP_DATE', 'unknown'),
            'services': {
                'cache': 'ok' if cache_status else 'error',
                'media_storage': 'ok' if media_accessible else 'error',
                'gemini_service': 'available',  # Could add actual check
            },
            'version': '1.0.0',
            'rate_limits': {
                'presentation_generation': '10/hour',
                'api_calls': '100/hour',
                'validation': '50/hour'
            }
        }
        
        overall_status = status.HTTP_200_OK
        if not cache_status or not media_accessible:
            status_data['status'] = 'degraded'
            overall_status = status.HTTP_503_SERVICE_UNAVAILABLE
        
        return Response(status_data, status=overall_status)
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return Response({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': request.META.get('HTTP_DATE', 'unknown')
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(['GET'])
@permission_classes([])
def get_rate_limit_status(request):
    """
    Get current rate limit status for the user
    """
    try:
        from .rate_limiting import get_rate_limit_key
        
        # Get rate limit keys for different groups
        groups = ['presentation_generation', 'api_calls', 'validation']
        rate_limit_status = {}
        
        for group in groups:
            from .rate_limiting import RateLimitConfig
            from django.core.cache import cache
            cache_key = get_rate_limit_key(request, group)
            current_usage = cache.get(cache_key, 0)
            
            rate_limit_status[group] = {
                'current_usage': current_usage,
                'limit': RateLimitConfig.LIMITS.get(group, {}).get('rate', 'unknown'),
                'reset_time': 'varies'  # Could calculate actual reset time
            }
        
        return Response({
            'user': getattr(request.user, 'username', 'anonymous'),
            'rate_limits': rate_limit_status,
            'timestamp': request.META.get('HTTP_DATE', 'unknown')
        })
        
    except Exception as e:
        logger.error(f"Rate limit status check failed: {str(e)}")
        return Response({
            'error': 'Failed to retrieve rate limit status',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([])
def get_available_templates(request):
    """Get all available templates"""
    try:
        templates = template_manager.get_available_templates()
        
        # Convert to serializable format
        template_data = {}
        for template_id, metadata in templates.items():
            template_data[template_id] = {
                'name': metadata.name,
                'category': metadata.category.value,
                'aspect_ratio': metadata.aspect_ratio.value,
                'description': metadata.description,
                'author': metadata.author,
                'version': metadata.version,
                'slide_layouts': metadata.slide_layouts,
                'color_scheme': metadata.color_scheme,
                'font_recommendations': metadata.font_recommendations
            }
        
        return Response({
            'templates': template_data,
            'total_count': len(template_data)
        })
        
    except Exception as e:
        logger.error(f"Error retrieving templates: {str(e)}")
        return Response({
            'error': 'Failed to retrieve templates',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([])
def get_templates_by_category(request, category):
    """Get templates filtered by category"""
    try:
        category_enum = TemplateCategory(category)
        templates = template_manager.get_templates_by_category(category_enum)
        
        # Convert to serializable format
        template_data = {}
        for template_id, metadata in templates.items():
            template_data[template_id] = {
                'name': metadata.name,
                'aspect_ratio': metadata.aspect_ratio.value,
                'description': metadata.description,
                'author': metadata.author,
                'version': metadata.version
            }
        
        return Response({
            'category': category,
            'templates': template_data,
            'count': len(template_data)
        })
        
    except ValueError:
        return Response({
            'error': f'Invalid category: {category}',
            'valid_categories': [cat.value for cat in TemplateCategory]
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error retrieving templates by category: {str(e)}")
        return Response({
            'error': 'Failed to retrieve templates',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([])
def get_templates_by_aspect_ratio(request, aspect_ratio):
    """Get templates filtered by aspect ratio"""
    try:
        ratio_enum = AspectRatio(aspect_ratio)
        templates = template_manager.get_templates_by_aspect_ratio(ratio_enum)
        
        # Convert to serializable format
        template_data = {}
        for template_id, metadata in templates.items():
            template_data[template_id] = {
                'name': metadata.name,
                'category': metadata.category.value,
                'description': metadata.description,
                'author': metadata.author,
                'version': metadata.version
            }
        
        return Response({
            'aspect_ratio': aspect_ratio,
            'templates': template_data,
            'count': len(template_data)
        })
        
    except ValueError:
        return Response({
            'error': f'Invalid aspect ratio: {aspect_ratio}',
            'valid_ratios': [ratio.value for ratio in AspectRatio]
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error retrieving templates by aspect ratio: {str(e)}")
        return Response({
            'error': 'Failed to retrieve templates',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([])
def get_template_info(request, template_id):
    """Get detailed information about a specific template"""
    try:
        metadata = template_manager.get_template_metadata(template_id)
        if not metadata:
            return Response({
                'error': f'Template not found: {template_id}'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get template dimensions
        dimensions = template_manager.get_template_dimensions(template_id)
        
        template_info = {
            'template_id': template_id,
            'name': metadata.name,
            'category': metadata.category.value,
            'aspect_ratio': metadata.aspect_ratio.value,
            'description': metadata.description,
            'author': metadata.author,
            'version': metadata.version,
            'slide_layouts': metadata.slide_layouts,
            'color_scheme': metadata.color_scheme,
            'font_recommendations': metadata.font_recommendations,
            'dimensions': {
                'width': dimensions[0] if dimensions else None,
                'height': dimensions[1] if dimensions else None
            } if dimensions else None
        }
        
        return Response(template_info)
        
    except Exception as e:
        logger.error(f"Error retrieving template info: {str(e)}")
        return Response({
            'error': 'Failed to retrieve template information',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([])
def get_performance_stats(request):
    """Get performance and caching statistics"""
    try:
        cache_stats = performance_cache.get_stats()
        
        # Add system performance metrics
        try:
            import psutil
            import os
            
            # Memory usage
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            system_metrics = {
                'memory_usage_mb': round(memory_info.rss / 1024 / 1024, 2),
                'memory_percent': round(process.memory_percent(), 2),
                'cpu_percent': cpu_percent,
                'process_id': os.getpid(),
                'thread_count': process.num_threads()
            }
        except ImportError:
            system_metrics = {'error': 'psutil not available'}
        
        performance_stats = {
            'cache_statistics': cache_stats,
            'system_metrics': system_metrics,
            'gunicorn_workers': {
                'current_worker_pid': os.getpid(),
            },
            'template_cache': {
                'loaded_templates': len(template_manager._template_cache),
                'metadata_cache_size': len(template_manager._metadata_cache)
            }
        }
        
        return Response(performance_stats)
        
    except Exception as e:
        logger.error(f"Performance stats error: {str(e)}")
        return Response({
            'error': 'Failed to retrieve performance statistics',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def clear_cache(request):
    """Clear performance cache (admin only)"""
    try:
        namespace = request.data.get('namespace', 'all')
        
        if namespace == 'all':
            # Clear all cache namespaces
            for ns in ['gemini_responses', 'template_data', 'presentation_metadata', 'user_preferences', 'font_validation']:
                performance_cache.clear_namespace(ns)
            message = "All caches cleared"
        else:
            performance_cache.clear_namespace(namespace)
            message = f"Cache namespace '{namespace}' cleared"
        
        # Also clear template manager cache
        template_manager.clear_cache()
        
        return Response({
            'success': True,
            'message': message,
            'cache_stats': performance_cache.get_stats()
        })
        
    except Exception as e:
        logger.error(f"Cache clear error: {str(e)}")
        return Response({
            'error': 'Failed to clear cache',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([])
def cleanup_expired_cache(request):
    """Cleanup expired cache entries"""
    try:
        performance_cache.cleanup_expired()
        
        return Response({
            'success': True,
            'message': 'Expired cache entries cleaned up',
            'cache_stats': performance_cache.get_stats()
        })
        
    except Exception as e:
        logger.error(f"Cache cleanup error: {str(e)}")
        return Response({
            'error': 'Failed to cleanup cache',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
