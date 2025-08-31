from rest_framework import serializers
from typing import List, Dict, Any
from .template_manager import AspectRatio, TemplateCategory, template_manager


class PresentationInputSerializer(serializers.Serializer):
    """Serializer for presentation generation input"""
    
    SLIDE_TYPE_CHOICES = [
        ('title', 'Title Slide'),
        ('bullet', 'Bullet Points Slide'),
        ('two-column', 'Two Column Slide'),
        ('content-image', 'Content with Image Slide'),
    ]
    
    prompt = serializers.CharField(
        max_length=500,
        help_text="Main topic/prompt for the presentation"
    )
    num_slides = serializers.IntegerField(
        min_value=1,
        max_value=20,
        help_text="Number of slides to generate"
    )
    font = serializers.CharField(
        max_length=100,
        default="Arial",
        required=False,
        help_text="Font name to use (defaults to Arial if not found)"
    )
    color = serializers.RegexField(
        regex=r'^#[0-9A-Fa-f]{6}$',
        default="#112233",
        required=False,
        help_text="Theme color in hex format"
    )
    layout = serializers.ListField(
        child=serializers.ChoiceField(choices=SLIDE_TYPE_CHOICES),
        help_text="List of slide types for each slide"
    )
    content = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        allow_null=True,
        help_text="Optional content for each slide"
    )
    include_citations = serializers.BooleanField(
        default=True,
        required=False,
        help_text="Whether to include citations and references in slides"
    )
    citation_style = serializers.ChoiceField(
        choices=[
            ('apa', 'APA Style'),
            ('mla', 'MLA Style'),
            ('chicago', 'Chicago Style'),
            ('ieee', 'IEEE Style')
        ],
        default='apa',
        required=False,
        help_text="Citation style to use"
    )
    template_id = serializers.CharField(
        max_length=100,
        default="default_16_9",
        required=False,
        help_text="Template ID to use for presentation"
    )
    aspect_ratio = serializers.ChoiceField(
        choices=[
            ('16:9', 'Widescreen 16:9'),
            ('4:3', 'Standard 4:3'),
            ('16:10', 'Widescreen 16:10'),
            ('1:1', 'Square 1:1')
        ],
        required=False,
        allow_null=True,
        help_text="Override aspect ratio (optional)"
    )
    template_category = serializers.ChoiceField(
        choices=[
            ('business', 'Business'),
            ('academic', 'Academic'),
            ('creative', 'Creative'),
            ('medical', 'Medical'),
            ('technology', 'Technology'),
            ('education', 'Education')
        ],
        required=False,
        allow_null=True,
        help_text="Filter templates by category (optional)"
    )
    
    def validate(self, data):
        """Custom validation for the entire input"""
        num_slides = data.get('num_slides')
        layout = data.get('layout', [])
        content = data.get('content')
        template_id = data.get('template_id', 'default_16_9')
        aspect_ratio = data.get('aspect_ratio')
        template_category = data.get('template_category')
        
        # Validate layout length
        if len(layout) != num_slides:
            raise serializers.ValidationError(
                f"Layout list length ({len(layout)}) must match num_slides ({num_slides})"
            )
        
        # Validate content length if provided
        if content is not None and len(content) != num_slides:
            raise serializers.ValidationError(
                f"Content list length ({len(content)}) must match num_slides ({num_slides})"
            )
        
        # Validate template exists
        if not template_manager.get_template_metadata(template_id):
            available_templates = list(template_manager.get_available_templates().keys())
            raise serializers.ValidationError(
                f"Template '{template_id}' not found. Available templates: {available_templates}"
            )
        
        # If template_category is specified, suggest templates
        if template_category:
            try:
                category_enum = TemplateCategory(template_category)
                category_templates = template_manager.get_templates_by_category(category_enum)
                if not category_templates:
                    raise serializers.ValidationError(
                        f"No templates found for category '{template_category}'"
                    )
                # If template_id is default but category is specified, suggest using category template
                if template_id == 'default_16_9' and category_templates:
                    data['suggested_templates'] = list(category_templates.keys())
            except ValueError:
                pass  # Invalid category, will be caught by choice field validation
        
        # Convert aspect_ratio string to enum if provided
        if aspect_ratio:
            try:
                data['aspect_ratio_enum'] = AspectRatio(aspect_ratio)
            except ValueError:
                raise serializers.ValidationError(f"Invalid aspect ratio: {aspect_ratio}")
        
        return data


class SlideContentSerializer(serializers.Serializer):
    """Base serializer for slide content validation"""
    pass


class TitleSlideContentSerializer(SlideContentSerializer):
    """Serializer for title slide content"""
    title_text = serializers.CharField(max_length=200, required=False)
    citations = serializers.ListField(
        child=serializers.CharField(max_length=500),
        required=False,
        allow_empty=True,
        help_text="List of citations for this slide"
    )


class BulletSlideContentSerializer(SlideContentSerializer):
    """Serializer for bullet slide content"""
    heading_text = serializers.CharField(max_length=100, required=False)
    bullet_points = serializers.ListField(
        child=serializers.CharField(max_length=200),
        required=False
    )
    citations = serializers.ListField(
        child=serializers.CharField(max_length=500),
        required=False,
        allow_empty=True,
        help_text="List of citations for this slide"
    )


class TwoColumnSlideContentSerializer(SlideContentSerializer):
    """Serializer for two-column slide content"""
    heading_text = serializers.CharField(max_length=100, required=False)
    left_content = serializers.ListField(
        child=serializers.CharField(max_length=200),
        required=False
    )
    right_content = serializers.ListField(
        child=serializers.CharField(max_length=200),
        required=False
    )
    # Accept alternative field names
    left_column = serializers.CharField(max_length=1000, required=False, write_only=True)
    right_column = serializers.CharField(max_length=1000, required=False, write_only=True)
    citations = serializers.ListField(
        child=serializers.CharField(max_length=500),
        required=False,
        allow_empty=True,
        help_text="List of citations for this slide"
    )
    
    def validate(self, data):
        """Handle alternative field names and convert string to list"""
        # Handle left_column -> left_content conversion
        if 'left_column' in data and not data.get('left_content'):
            left_text = data.pop('left_column')
            if isinstance(left_text, str):
                data['left_content'] = [line.strip() for line in left_text.split('\n') if line.strip()]
        
        # Handle right_column -> right_content conversion  
        if 'right_column' in data and not data.get('right_content'):
            right_text = data.pop('right_column')
            if isinstance(right_text, str):
                data['right_content'] = [line.strip() for line in right_text.split('\n') if line.strip()]
        
        return data


class ContentImageSlideContentSerializer(SlideContentSerializer):
    """Serializer for content-image slide content"""
    main_heading = serializers.CharField(max_length=100, required=False)
    sub_heading = serializers.CharField(max_length=200, required=False)
    citations = serializers.ListField(
        child=serializers.CharField(max_length=500),
        required=False,
        allow_empty=True,
        help_text="List of citations for this slide"
    )


class SlideGenerationResultSerializer(serializers.Serializer):
    """Serializer for slide generation result"""
    slide_index = serializers.IntegerField()
    slide_type = serializers.ChoiceField(choices=PresentationInputSerializer.SLIDE_TYPE_CHOICES)
    content_source = serializers.ChoiceField(choices=[('provided', 'Provided'), ('generated', 'Generated')])
    content = serializers.DictField()


class PresentationGenerationResponseSerializer(serializers.Serializer):
    """Serializer for presentation generation response"""
    success = serializers.BooleanField()
    message = serializers.CharField()
    filename = serializers.CharField(required=False, allow_null=True)
    slides = SlideGenerationResultSerializer(many=True, required=False, allow_null=True)
    errors = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_null=True
    )


def validate_slide_content(slide_type: str, content: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and normalize slide content based on slide type"""
    if not content:
        return {}
    
    try:
        if slide_type == 'title':
            serializer = TitleSlideContentSerializer(data=content)
        elif slide_type == 'bullet':
            serializer = BulletSlideContentSerializer(data=content)
        elif slide_type == 'two-column':
            serializer = TwoColumnSlideContentSerializer(data=content)
        elif slide_type == 'content-image':
            serializer = ContentImageSlideContentSerializer(data=content)
        else:
            return {}
        
        if serializer.is_valid():
            return {k: v for k, v in serializer.validated_data.items() if v is not None}
        else:
            return {}
    except Exception:
        return {}


def is_slide_content_complete(slide_type: str, content: Dict[str, Any]) -> bool:
    """Check if slide content is complete enough to skip generation"""
    if not content:
        return False
    
    if slide_type == 'title':
        return bool(content.get('title_text'))
    elif slide_type == 'bullet':
        return bool(content.get('heading_text')) and bool(content.get('bullet_points'))
    elif slide_type == 'two-column':
        # Check for both possible field names (left_content/left_column, right_content/right_column)
        has_heading = bool(content.get('heading_text'))
        has_left = bool(content.get('left_content') or content.get('left_column'))
        has_right = bool(content.get('right_content') or content.get('right_column'))
        return has_heading and has_left and has_right
    elif slide_type == 'content-image':
        return bool(content.get('main_heading')) and bool(content.get('sub_heading'))
    
    return False
