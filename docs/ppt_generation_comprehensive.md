# 🎯 PPT Generation - Comprehensive API & Code Documentation

## Overview

This document provides complete documentation for the PowerPoint presentation generation system, covering all generation methods, templates, customization options, and advanced features.

---

## 🎨 PPT Generation Methods

### 1. User-Provided Content Only

Generate presentations with completely user-defined content.

#### Basic Title Slide
```bash
curl -X POST http://127.0.0.1:8000/api/generate/presentation/ \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Company Overview",
    "num_slides": 1,
    "layout": ["title"],
    "font": "Calibri",
    "color": "#1f4e79",
    "content": [
      {
        "title_text": "TechCorp Solutions",
        "subtitle_text": "Innovating the Future of Technology"
      }
    ]
  }'
```

#### Bullet Points Presentation
```bash
curl -X POST http://127.0.0.1:8000/api/generate/presentation/ \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Project Management Best Practices",
    "num_slides": 3,
    "layout": ["title", "bullet", "bullet"],
    "font": "Arial",
    "color": "#2e7d32",
    "content": [
      {
        "title_text": "Project Management Best Practices",
        "subtitle_text": "Delivering Success Through Structured Approach"
      },
      {
        "heading_text": "Planning Phase",
        "bullet_points": [
          "Define clear project objectives",
          "Identify stakeholders and requirements",
          "Create detailed project timeline",
          "Allocate resources effectively",
          "Establish communication protocols"
        ]
      },
      {
        "heading_text": "Execution Phase",
        "bullet_points": [
          "Monitor progress against milestones",
          "Maintain regular team communication",
          "Manage risks proactively",
          "Ensure quality standards",
          "Document lessons learned"
        ]
      }
    ]
  }'
```

#### Two-Column Layout
```bash
curl -X POST http://127.0.0.1:8000/api/generate/presentation/ \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Technology Comparison",
    "num_slides": 2,
    "layout": ["title", "two-column"],
    "font": "Segoe UI",
    "color": "#8e44ad",
    "content": [
      {
        "title_text": "Frontend vs Backend Technologies"
      },
      {
        "heading_text": "Development Stack Comparison",
        "left_column": "Frontend Technologies:\n• React.js\n• Vue.js\n• Angular\n• HTML5/CSS3\n• TypeScript\n• Webpack",
        "right_column": "Backend Technologies:\n• Node.js\n• Python Django\n• Java Spring\n• PostgreSQL\n• Redis\n• Docker"
      }
    ]
  }'
```

#### Content-Image Layout
```bash
curl -X POST http://127.0.0.1:8000/api/generate/presentation/ \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Data Analytics Dashboard",
    "num_slides": 2,
    "layout": ["title", "content-image"],
    "font": "Calibri",
    "color": "#d32f2f",
    "content": [
      {
        "title_text": "Data Analytics Dashboard"
      },
      {
        "main_heading": "Real-time Performance Metrics",
        "sub_heading": "Monitor key performance indicators with interactive visualizations and automated reporting capabilities"
      }
    ]
  }'
```

### 2. AI-Generated Content Only

Let the AI generate all slide content based on the prompt.

#### Complete AI Generation
```bash
curl -X POST http://127.0.0.1:8000/api/generate/presentation/ \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Artificial Intelligence in Healthcare",
    "num_slides": 5,
    "layout": ["title", "bullet", "two-column", "content-image", "bullet"],
    "font": "Times New Roman",
    "color": "#1565c0",
    "include_citations": true,
    "citation_style": "apa",
    "content": [{}, {}, {}, {}, {}]
  }'
```

#### AI with Specific Topic Focus
```bash
curl -X POST http://127.0.0.1:8000/api/generate/presentation/ \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Blockchain Technology and Cryptocurrency",
    "num_slides": 4,
    "layout": ["title", "bullet", "two-column", "content-image"],
    "font": "Arial",
    "color": "#ff6f00",
    "include_citations": true,
    "citation_style": "ieee",
    "content": [{}, {}, {}, {}]
  }'
```

### 3. Mixed Content (User + AI)

Combine user-provided content with AI-generated content.

#### Strategic Mix
```bash
curl -X POST http://127.0.0.1:8000/api/generate/presentation/ \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Digital Marketing Strategy 2024",
    "num_slides": 6,
    "layout": ["title", "bullet", "two-column", "content-image", "bullet", "bullet"],
    "font": "Calibri",
    "color": "#e91e63",
    "include_citations": true,
    "citation_style": "mla",
    "content": [
      {
        "title_text": "Digital Marketing Strategy 2024",
        "subtitle_text": "Comprehensive Guide to Modern Marketing"
      },
      {
        "heading_text": "Core Objectives",
        "bullet_points": [
          "Increase brand awareness by 40%",
          "Generate 25% more qualified leads",
          "Improve customer retention rate",
          "Expand into new market segments"
        ]
      },
      {},
      {},
      {},
      {
        "heading_text": "Success Metrics",
        "bullet_points": [
          "ROI measurement and tracking",
          "Customer acquisition cost (CAC)",
          "Lifetime value (LTV) analysis",
          "Conversion rate optimization"
        ]
      }
    ]
  }'
```

---

## 🎨 Template System

### Available Templates

#### 1. Default Business Template (default_16_9)
Professional business presentation template with clean design.

```bash
curl -X POST http://127.0.0.1:8000/api/generate/presentation/ \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Quarterly Business Review",
    "num_slides": 4,
    "layout": ["title", "bullet", "two-column", "content-image"],
    "template_id": "default_16_9",
    "aspect_ratio": "16:9",
    "font": "Calibri",
    "color": "#1f4e79",
    "content": [
      {
        "title_text": "Q3 2024 Business Review",
        "subtitle_text": "Performance Analysis and Strategic Outlook"
      },
      {
        "heading_text": "Key Achievements",
        "bullet_points": [
          "Revenue growth of 15% YoY",
          "Successful product launch",
          "Market expansion in Asia",
          "Team growth by 25%"
        ]
      },
      {
        "heading_text": "Financial Performance",
        "left_column": "Revenue:\n• Q3: $2.5M\n• Growth: +15%\n• Target: $2.3M",
        "right_column": "Expenses:\n• OpEx: $1.8M\n• Savings: 8%\n• Efficiency: +12%"
      },
      {
        "main_heading": "Strategic Initiatives",
        "sub_heading": "Focus areas for Q4 and beyond"
      }
    ]
  }'
```

#### 2. Frost Academic Template (frost_16_9)
Academic and research-focused template with professional styling.

```bash
curl -X POST http://127.0.0.1:8000/api/generate/presentation/ \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Research Methodology in Computer Science",
    "num_slides": 5,
    "layout": ["title", "bullet", "two-column", "content-image", "bullet"],
    "template_id": "frost_16_9",
    "aspect_ratio": "16:9",
    "font": "Times New Roman",
    "color": "#2c3e50",
    "include_citations": true,
    "citation_style": "ieee",
    "content": [
      {
        "title_text": "Research Methodology in Computer Science",
        "subtitle_text": "Systematic Approaches to Scientific Investigation"
      },
      {
        "heading_text": "Research Paradigms",
        "bullet_points": [
          "Quantitative research methods",
          "Qualitative analysis techniques",
          "Mixed-method approaches",
          "Experimental design principles"
        ]
      },
      {
        "heading_text": "Data Collection vs Analysis",
        "left_column": "Data Collection:\n• Surveys and questionnaires\n• Interviews and focus groups\n• Observational studies\n• Controlled experiments",
        "right_column": "Data Analysis:\n• Statistical analysis\n• Machine learning algorithms\n• Pattern recognition\n• Visualization techniques"
      },
      {
        "main_heading": "Validation Methods",
        "sub_heading": "Ensuring reliability and validity in computer science research"
      },
      {
        "heading_text": "Publication Standards",
        "bullet_points": [
          "Peer review process",
          "Reproducibility requirements",
          "Ethical considerations",
          "Open science practices"
        ]
      }
    ]
  }'
```

#### 3. Galaxy Creative Template (galaxy_16_9)
Modern, creative template for artistic and innovative presentations.

```bash
curl -X POST http://127.0.0.1:8000/api/generate/presentation/ \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Creative Design Workshop",
    "num_slides": 4,
    "layout": ["title", "bullet", "two-column", "content-image"],
    "template_id": "galaxy_16_9",
    "aspect_ratio": "16:9",
    "font": "Arial",
    "color": "#8e44ad",
    "content": [
      {
        "title_text": "Creative Design Workshop",
        "subtitle_text": "Unleashing Innovation Through Design Thinking"
      },
      {
        "heading_text": "Design Principles",
        "bullet_points": [
          "User-centered design approach",
          "Visual hierarchy and balance",
          "Color theory and psychology",
          "Typography and readability",
          "Accessibility considerations"
        ]
      },
      {
        "heading_text": "Process vs Tools",
        "left_column": "Design Process:\n• Research and discovery\n• Ideation and brainstorming\n• Prototyping and testing\n• Iteration and refinement",
        "right_column": "Design Tools:\n• Adobe Creative Suite\n• Figma and Sketch\n• Prototyping tools\n• Collaboration platforms"
      },
      {
        "main_heading": "Innovation Framework",
        "sub_heading": "Structured approach to creative problem-solving"
      }
    ]
  }'
```

---

## 🎨 Custom Fonts and Colors

### Font Options
Supported fonts with examples:

#### Arial Font
```bash
curl -X POST http://127.0.0.1:8000/api/generate/presentation/ \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Modern Technology Trends",
    "num_slides": 2,
    "layout": ["title", "bullet"],
    "font": "Arial",
    "color": "#1976d2",
    "content": [
      {"title_text": "Technology Trends 2024"},
      {"heading_text": "Emerging Technologies", "bullet_points": ["AI and Machine Learning", "Quantum Computing", "Edge Computing"]}
    ]
  }'
```

#### Calibri Font
```bash
curl -X POST http://127.0.0.1:8000/api/generate/presentation/ \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Business Strategy",
    "num_slides": 2,
    "layout": ["title", "bullet"],
    "font": "Calibri",
    "color": "#388e3c",
    "content": [
      {"title_text": "Strategic Planning"},
      {"heading_text": "Key Focus Areas", "bullet_points": ["Market Analysis", "Competitive Positioning", "Growth Strategies"]}
    ]
  }'
```

#### Times New Roman Font
```bash
curl -X POST http://127.0.0.1:8000/api/generate/presentation/ \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Academic Research",
    "num_slides": 2,
    "layout": ["title", "bullet"],
    "font": "Times New Roman",
    "color": "#5d4037",
    "content": [
      {"title_text": "Research Findings"},
      {"heading_text": "Methodology", "bullet_points": ["Literature Review", "Data Collection", "Statistical Analysis"]}
    ]
  }'
```

#### Segoe UI Font
```bash
curl -X POST http://127.0.0.1:8000/api/generate/presentation/ \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "User Interface Design",
    "num_slides": 2,
    "layout": ["title", "bullet"],
    "font": "Segoe UI",
    "color": "#7b1fa2",
    "content": [
      {"title_text": "UI/UX Best Practices"},
      {"heading_text": "Design Principles", "bullet_points": ["Consistency", "Simplicity", "Accessibility"]}
    ]
  }'
```

### Color Schemes

#### Professional Blue Theme
```bash
curl -X POST http://127.0.0.1:8000/api/generate/presentation/ \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Corporate Presentation",
    "num_slides": 1,
    "layout": ["title"],
    "font": "Calibri",
    "color": "#1f4e79",
    "content": [{"title_text": "Professional Blue Theme"}]
  }'
```

#### Success Green Theme
```bash
curl -X POST http://127.0.0.1:8000/api/generate/presentation/ \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Growth Report",
    "num_slides": 1,
    "layout": ["title"],
    "font": "Arial",
    "color": "#2e7d32",
    "content": [{"title_text": "Success Green Theme"}]
  }'
```

#### Creative Purple Theme
```bash
curl -X POST http://127.0.0.1:8000/api/generate/presentation/ \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Innovation Workshop",
    "num_slides": 1,
    "layout": ["title"],
    "font": "Arial",
    "color": "#8e44ad",
    "content": [{"title_text": "Creative Purple Theme"}]
  }'
```

#### Warning Orange Theme
```bash
curl -X POST http://127.0.0.1:8000/api/generate/presentation/ \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Risk Assessment",
    "num_slides": 1,
    "layout": ["title"],
    "font": "Calibri",
    "color": "#ff6f00",
    "content": [{"title_text": "Warning Orange Theme"}]
  }'
```

#### Elegant Red Theme
```bash
curl -X POST http://127.0.0.1:8000/api/generate/presentation/ \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Important Announcement",
    "num_slides": 1,
    "layout": ["title"],
    "font": "Times New Roman",
    "color": "#d32f2f",
    "content": [{"title_text": "Elegant Red Theme"}]
  }'
```

---

## 📚 Citation Styles

### APA Citation Style
```bash
curl -X POST http://127.0.0.1:8000/api/generate/presentation/ \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Psychology Research Methods",
    "num_slides": 3,
    "layout": ["title", "bullet", "content-image"],
    "font": "Times New Roman",
    "color": "#1f4e79",
    "include_citations": true,
    "citation_style": "apa",
    "content": [
      {"title_text": "Psychology Research Methods"},
      {},
      {}
    ]
  }'
```

### IEEE Citation Style
```bash
curl -X POST http://127.0.0.1:8000/api/generate/presentation/ \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Machine Learning Algorithms",
    "num_slides": 3,
    "layout": ["title", "bullet", "two-column"],
    "font": "Arial",
    "color": "#2e7d32",
    "include_citations": true,
    "citation_style": "ieee",
    "content": [
      {"title_text": "Machine Learning Algorithms"},
      {},
      {}
    ]
  }'
```

### MLA Citation Style
```bash
curl -X POST http://127.0.0.1:8000/api/generate/presentation/ \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Literature Analysis",
    "num_slides": 3,
    "layout": ["title", "bullet", "content-image"],
    "font": "Times New Roman",
    "color": "#8e44ad",
    "include_citations": true,
    "citation_style": "mla",
    "content": [
      {"title_text": "Literature Analysis"},
      {},
      {}
    ]
  }'
```

### Chicago Citation Style
```bash
curl -X POST http://127.0.0.1:8000/api/generate/presentation/ \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Historical Research",
    "num_slides": 3,
    "layout": ["title", "bullet", "two-column"],
    "font": "Times New Roman",
    "color": "#5d4037",
    "include_citations": true,
    "citation_style": "chicago",
    "content": [
      {"title_text": "Historical Research"},
      {},
      {}
    ]
  }'
```

### Without Citations
```bash
curl -X POST http://127.0.0.1:8000/api/generate/presentation/ \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Business Presentation",
    "num_slides": 3,
    "layout": ["title", "bullet", "two-column"],
    "font": "Calibri",
    "color": "#1f4e79",
    "include_citations": false,
    "content": [
      {"title_text": "Business Presentation"},
      {},
      {}
    ]
  }'
```

---

## 🎯 Aspect Ratios

### 16:9 Widescreen (Default)
```bash
curl -X POST http://127.0.0.1:8000/api/generate/presentation/ \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Widescreen Presentation",
    "num_slides": 2,
    "layout": ["title", "bullet"],
    "aspect_ratio": "16:9",
    "template_id": "default_16_9",
    "content": [
      {"title_text": "16:9 Widescreen Format"},
      {"heading_text": "Benefits", "bullet_points": ["Modern display compatibility", "Cinematic viewing experience", "Professional appearance"]}
    ]
  }'
```

### 4:3 Standard
```bash
curl -X POST http://127.0.0.1:8000/api/generate/presentation/ \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Standard Presentation",
    "num_slides": 2,
    "layout": ["title", "bullet"],
    "aspect_ratio": "4:3",
    "content": [
      {"title_text": "4:3 Standard Format"},
      {"heading_text": "Use Cases", "bullet_points": ["Legacy projectors", "Print compatibility", "Traditional formats"]}
    ]
  }'
```

### 16:10 Widescreen
```bash
curl -X POST http://127.0.0.1:8000/api/generate/presentation/ \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Extended Widescreen",
    "num_slides": 2,
    "layout": ["title", "bullet"],
    "aspect_ratio": "16:10",
    "content": [
      {"title_text": "16:10 Extended Format"},
      {"heading_text": "Advantages", "bullet_points": ["Extra vertical space", "Laptop screen compatibility", "Professional displays"]}
    ]
  }'
```

---

## 📊 Maximum Slides Example (20 slides)

```bash
curl -X POST http://127.0.0.1:8000/api/generate/presentation/ \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Complete Software Development Lifecycle",
    "num_slides": 20,
    "layout": [
      "title", "bullet", "two-column", "content-image", "bullet",
      "two-column", "content-image", "bullet", "two-column", "content-image",
      "bullet", "two-column", "content-image", "bullet", "two-column",
      "content-image", "bullet", "two-column", "content-image", "bullet"
    ],
    "font": "Calibri",
    "color": "#1f4e79",
    "template_id": "default_16_9",
    "include_citations": true,
    "citation_style": "ieee",
    "content": [
      {"title_text": "Complete Software Development Lifecycle"},
      {"heading_text": "Planning Phase", "bullet_points": ["Requirements gathering", "Project scope definition", "Timeline estimation", "Resource allocation"]},
      {"heading_text": "Design vs Development", "left_column": "Design Phase:\n• System architecture\n• UI/UX design\n• Database design\n• API specifications", "right_column": "Development Phase:\n• Code implementation\n• Unit testing\n• Integration\n• Code reviews"},
      {"main_heading": "Testing Strategies", "sub_heading": "Comprehensive quality assurance approach"},
      {"heading_text": "Testing Types", "bullet_points": ["Unit testing", "Integration testing", "System testing", "User acceptance testing"]},
      {},
      {},
      {},
      {},
      {},
      {},
      {},
      {},
      {},
      {},
      {},
      {},
      {},
      {},
      {}
    ]
  }'
```

---

## 🔍 Template Information Endpoints

### Get All Templates
```bash
curl -X GET http://127.0.0.1:8000/api/generate/templates/
```

### Get Template by ID
```bash
curl -X GET http://127.0.0.1:8000/api/generate/templates/default_16_9/
```

```bash
curl -X GET http://127.0.0.1:8000/api/generate/templates/frost_16_9/
```

```bash
curl -X GET http://127.0.0.1:8000/api/generate/templates/galaxy_16_9/
```

### Get Templates by Category
```bash
curl -X GET http://127.0.0.1:8000/api/generate/templates/category/business/
```

```bash
curl -X GET http://127.0.0.1:8000/api/generate/templates/category/academic/
```

```bash
curl -X GET http://127.0.0.1:8000/api/generate/templates/category/creative/
```

### Get Templates by Aspect Ratio
```bash
curl -X GET http://127.0.0.1:8000/api/generate/templates/aspect-ratio/16:9/
```

```bash
curl -X GET http://127.0.0.1:8000/api/generate/templates/aspect-ratio/4:3/
```

```bash
curl -X GET http://127.0.0.1:8000/api/generate/templates/aspect-ratio/16:10/
```

---

## 📈 Response Examples

### Successful Generation Response
```json
{
  "success": true,
  "message": "Presentation generated successfully",
  "filename": "technology_trends_a1b2c3d4.pptx",
  "file_url": "http://127.0.0.1:8000/media/technology_trends_a1b2c3d4.pptx",
  "slides": [
    {
      "slide_index": 0,
      "slide_type": "title",
      "content_source": "provided",
      "content": {
        "title_text": "Technology Trends 2024",
        "subtitle_text": "Emerging Technologies and Market Insights"
      }
    },
    {
      "slide_index": 1,
      "slide_type": "bullet",
      "content_source": "generated",
      "content": {
        "heading_text": "Key Technology Trends",
        "bullet_points": [
          "Artificial Intelligence and Machine Learning",
          "Quantum Computing Advances",
          "Edge Computing Solutions",
          "Sustainable Technology Initiatives"
        ]
      }
    }
  ],
  "metadata": {
    "total_slides": 2,
    "generated_slides": 1,
    "provided_slides": 1,
    "font": "Calibri",
    "color": "#1976d2",
    "template_id": "default_16_9",
    "aspect_ratio": "16:9",
    "generation_time": 2.34,
    "cache_hit": false
  },
  "citations": [
    {
      "slide_index": 1,
      "citation": "Smith, J. (2024). Emerging Technology Trends. Tech Journal, 15(3), 45-67."
    }
  ]
}
```

### Template Information Response
```json
{
  "template_id": "default_16_9",
  "name": "Default Business Template",
  "category": "business",
  "aspect_ratio": "16:9",
  "description": "Professional business presentation template with clean, modern design suitable for corporate presentations",
  "author": "System",
  "version": "1.0",
  "created_date": "2024-01-01",
  "slide_layouts": [
    "title",
    "bullet",
    "two-column", 
    "content-image"
  ],
  "color_scheme": {
    "primary": "#1f4e79",
    "secondary": "#70ad47",
    "accent": "#ffc000",
    "background": "#ffffff",
    "text": "#000000"
  },
  "font_recommendations": [
    "Calibri",
    "Arial",
    "Segoe UI"
  ],
  "dimensions": {
    "width": 1920,
    "height": 1080,
    "dpi": 96
  },
  "features": [
    "Professional styling",
    "Corporate color scheme",
    "Clean typography",
    "Consistent layouts"
  ]
}
```

---

## 🎯 Code Implementation Details

### Core Generation Logic
The presentation generation system is implemented in `generate_content/views.py` with the main function `generate_presentation()`. Key components:

1. **Input Validation**: Uses `PresentationInputSerializer` for comprehensive validation
2. **Content Processing**: Handles mixed user/AI content through `process_content_array()`
3. **AI Integration**: Leverages `GeminiContentGenerator` for AI-powered content
4. **Template Management**: Uses `TemplateManager` for template loading and caching
5. **PPT Generation**: Employs `PPTGenerator` for PowerPoint file creation

### Template System Architecture
Templates are managed through:
- **Template Files**: Physical .pptx files in `templates/presentations/`
- **Metadata**: JSON files describing template properties
- **Template Manager**: Centralized template loading and caching
- **Aspect Ratio Support**: Multiple format support (16:9, 4:3, 16:10)

### Content Generation Pipeline
1. **Request Validation**: Validate all input parameters
2. **Content Analysis**: Determine which slides need AI generation
3. **AI Processing**: Generate content for empty slides using Gemini
4. **Template Loading**: Load appropriate template based on ID
5. **Slide Creation**: Create slides with user/AI content
6. **File Generation**: Export to PowerPoint format
7. **Response Formation**: Return structured response with metadata

This comprehensive system provides maximum flexibility while maintaining high performance through intelligent caching and optimized processing pipelines.
