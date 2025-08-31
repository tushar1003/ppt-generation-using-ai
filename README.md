# PPT Generation Using AI 🎯

An advanced PowerPoint presentation generation system powered by Google Gemini AI, built with Django REST Framework. This system allows users to create professional presentations with a mix of user-provided content and AI-generated content.

## 🚀 Features

### Core Features
- **AI-Powered Content Generation**: Uses Google Gemini AI for intelligent slide content creation
- **Mixed Content Support**: Combine user-provided content with AI-generated content
- **Multiple Slide Types**: Title, Bullet Points, Two-Column, and Content-Image slides
- **Template System**: Advanced templating with multiple aspect ratios (16:9, 4:3, 16:10, 1:1)
- **Citation Support**: Academic citations in APA, MLA, Chicago, and IEEE formats

### Advanced Features
- **Multi-Level Caching**: Memory, Django cache, and file-based caching for optimal performance
- **Concurrent Processing**: Gunicorn-based multi-worker setup for handling concurrent requests
- **Rate Limiting**: Configurable rate limiting with local caching
- **Performance Monitoring**: Real-time performance metrics and cache statistics
- **JWT Authentication**: Secure API access with JWT tokens
- **Field Name Flexibility**: Supports multiple field name variations for user convenience

### Performance Optimizations
- **96% Speed Improvement** on cached requests
- **Multi-Worker Architecture**: Up to 65+ concurrent workers
- **Intelligent Cache Management**: LRU eviction with automatic cleanup
- **Template Caching**: Optimized template loading and caching

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Django REST    │    │   Google        │
│   (API Client)  │◄──►│   Framework      │◄──►│   Gemini AI     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   Multi-Level    │
                    │   Caching        │
                    │   System         │
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   Template       │
                    │   Management     │
                    │   System         │
                    └──────────────────┘
```

## 📋 Prerequisites

- Python 3.8+
- Django 4.2+
- Google Cloud Project with Vertex AI enabled
- Git

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/tushar1003/ppt-generation-using-ai.git
   cd ppt-generation-using-ai
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

## 🚀 Usage

### Development Server
```bash
python manage.py runserver
```

### Production Server (Gunicorn)
```bash
# Start with multiple workers
gunicorn --config gunicorn.conf.py core.wsgi:application

# Or use the provided script
./start_server.sh --production --workers 32
```

## 📡 API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/token/refresh/` - Refresh JWT token

### Presentation Generation
- `POST /api/generate/presentation/` - Generate presentation
- `GET /api/generate/templates/` - List available templates
- `GET /api/generate/templates/{template_id}/` - Get template details

### System Monitoring
- `GET /api/generate/health/` - Health check
- `GET /api/generate/performance/` - Performance statistics
- `GET /api/generate/rate-limits/` - Rate limit status

## 🎯 API Usage Examples

### Generate Cricket Presentation
```bash
curl -X POST http://localhost:8000/api/generate/presentation/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "prompt": "Cricket World Cup Final 2024",
    "num_slides": 4,
    "font": "Calibri",
    "template_id": "default_16_9",
    "layout": ["title", "bullet", "two-column", "content-image"],
    "include_citations": true,
    "citation_style": "apa",
    "content": [
      {
        "title_text": "Cricket World Cup Final 2024"
      },
      {
        "heading_text": "Match Highlights",
        "bullet_points": ["Epic battle", "Record attendance", "Thrilling finish"]
      },
      {
        "heading_text": "Team Statistics",
        "left_column": "Team A:\n• Runs: 347/8\n• Top Scorer: 89",
        "right_column": "Team B:\n• Runs: 342/9\n• Top Scorer: 76"
      },
      {}
    ]
  }'
```

### Response Format
```json
{
  "success": true,
  "message": "Presentation generated successfully",
  "filename": "cricket_world_cup_final_2024_abc123.pptx",
  "file_url": "http://localhost:8000/media/cricket_world_cup_final_2024_abc123.pptx",
  "slides": [...],
  "metadata": {
    "total_slides": 4,
    "generated_slides": 1,
    "provided_slides": 3,
    "font": "Calibri",
    "generation_time": null
  }
}
```

## 🎨 Supported Slide Types

### 1. Title Slide
```json
{
  "title_text": "Main Title",
  "subtitle_text": "Optional Subtitle"
}
```

### 2. Bullet Points Slide
```json
{
  "heading_text": "Slide Heading",
  "bullet_points": ["Point 1", "Point 2", "Point 3"]
}
```

### 3. Two-Column Slide
```json
{
  "heading_text": "Comparison Title",
  "left_column": "Left content\n• Point 1\n• Point 2",
  "right_column": "Right content\n• Point A\n• Point B"
}
```

### 4. Content-Image Slide
```json
{
  "main_heading": "Main Topic",
  "sub_heading": "Detailed description"
}
```

## 🔧 Configuration

### Environment Variables
```env
# Django Settings
DEBUG=False
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1

# Google Cloud
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_REGION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json

# Database (optional)
DATABASE_URL=sqlite:///db.sqlite3

# JWT Settings
JWT_SECRET_KEY=your-jwt-secret
JWT_ALGORITHM=HS256
```

### Gunicorn Configuration
The project includes a comprehensive `gunicorn.conf.py` with optimized settings for production deployment.

## 📊 Performance Metrics

- **Cache Hit Rate**: Up to 96% speed improvement on repeated requests
- **Concurrent Workers**: Supports 65+ workers on 32-core machines
- **Rate Limiting**: Configurable limits (default: 3 requests/minute for testing)
- **Memory Usage**: Intelligent caching with LRU eviction
- **Response Time**: Sub-second response for cached content

## 🔒 Security Features

- JWT-based authentication
- Rate limiting with IP-based tracking
- Input validation and sanitization
- CORS configuration
- Secure file handling

## 🧪 Testing

### Run Tests
```bash
python manage.py test
```

### Test Rate Limiting
```bash
# Multiple requests to test rate limiting
for i in {1..5}; do
  curl -X POST http://localhost:8000/api/generate/presentation/ \
    -H "Content-Type: application/json" \
    -d '{"prompt": "Test '$i'", "num_slides": 1, "layout": ["title"], "content": [{}]}'
done
```

## 📈 Monitoring

### Performance Dashboard
Access real-time performance metrics:
```bash
curl http://localhost:8000/api/generate/performance/
```

### Cache Statistics
```json
{
  "cache_statistics": {
    "hits": 15,
    "misses": 5,
    "hit_rate_percent": 75.0,
    "memory_cache_entries": 8
  },
  "system_metrics": {
    "memory_usage_mb": 64.48,
    "cpu_percent": 15.2,
    "process_id": 12345
  }
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Tushar Bhatia**
- Email: tusharbhatia1003@gmail.com
- GitHub: [@tushar1003](https://github.com/tushar1003)

## 🙏 Acknowledgments

- Google Gemini AI for content generation
- Django REST Framework community
- Python-pptx library contributors
- All contributors and testers

## 📞 Support

If you encounter any issues or have questions, please:
1. Check the [Issues](https://github.com/tushar1003/ppt-generation-using-ai/issues) page
2. Create a new issue with detailed information
3. Contact: tusharbhatia1003@gmail.com

---

**Made with ❤️ by Tushar Bhatia**
