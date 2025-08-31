import os
import logging
import asyncio
import concurrent.futures
import time
import json
from typing import List, Dict, Any, Optional
import vertexai
from google.oauth2 import service_account
from google.cloud import aiplatform
from vertexai.generative_models import GenerativeModel
from .performance_cache import performance_cache, cached, cache_gemini_response

logger = logging.getLogger(__name__)

service = None

class GeminiContentGenerator:

    def __init__(self, project_id: str = None, location: str = None):
        global service
        if service is not None:
            return service
        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
        self.location = location or os.getenv("GOOGLE_CLOUD_REGION", "us-central1")
        self.credentials = None
        self.model = None

        self._initialize_vertex_ai()

        service = self

    def _initialize_vertex_ai(self):
        """Initialize Vertex AI with service account credentials"""
        try:
            # Try to load service account credentials
            service_account_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            if service_account_path and os.path.exists(service_account_path):
                self.credentials = (
                    service_account.Credentials.from_service_account_file(
                        service_account_path
                    )
                )

                # Initialize Vertex AI
                vertexai.init(
                    project=self.project_id,
                    location=self.location,
                    credentials=self.credentials,
                )

                # Initialize Gemini Flash model
                self.model = GenerativeModel("gemini-1.5-flash")
                logger.info("Vertex AI and Gemini model initialized successfully")

            else:
                raise Exception("Service Account not found")

        except Exception as e:
            logger.error(f"Failed to initialize Vertex AI: {str(e)}")
            raise

    def generate_presentation_content(self, prompt: str, layout: List[str], content: List[Dict], filename: str, 
                                    include_citations: bool = True, citation_style: str = 'apa') -> Dict:
        """
        Single inference function to generate all slide content at once.
        
        Args:
            prompt: Main topic/prompt for the presentation
            layout: List of slide types ["title", "bullet", "two-column", "content-image"]
            content: List of content objects, empty {} for slides needing generation
            filename: Name of the presentation file
            
        Returns:
            Dict with structure:
            {
                "file_name": "presentation.pptx",
                "content": [
                    {"title_text": "Generated Title"},
                    {"heading_text": "...", "bullet_points": [...]},
                    {},  # User provided content remains empty
                    {"main_heading": "...", "sub_heading": "..."}
                ]
            }
        """
        
        # Generate cache key for this request
        cache_key_data = {
            'prompt': prompt,
            'layout': layout,
            'content': content,
            'include_citations': include_citations,
            'citation_style': citation_style
        }
        
        # Try to get from cache first
        cached_result = performance_cache.get('gemini_responses', cache_key_data)
        if cached_result is not None:
            logger.info("Using cached Gemini response")
            return cached_result
            
        start_time = time.time()
        
        try:
            # Create comprehensive prompt for Gemini
            system_prompt = self._create_system_prompt(include_citations, citation_style)
            user_prompt = self._create_user_prompt(prompt, layout, content, filename, include_citations, citation_style)
            
            # Generate content using Gemini
            response = self.model.generate_content([system_prompt, user_prompt])
            
            # Parse and validate response
            result = self._parse_gemini_response(response.text, layout, content)
            
            # Cache the successful result
            generation_time = time.time() - start_time
            logger.info(f"Gemini generation completed in {generation_time:.2f}s")
            performance_cache.set('gemini_responses', cache_key_data, result, ttl=3600)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in Gemini generation: {str(e)}")
            # Return original content array as fallback
            fallback_result = {"file_name": filename, "content": content}
            # Cache fallback for shorter time to avoid repeated failures
            performance_cache.set('gemini_responses', cache_key_data, fallback_result, ttl=300)
            return fallback_result
    
    def _create_system_prompt(self, include_citations: bool = True, citation_style: str = 'apa') -> str:
        """Create system prompt for Gemini"""
        
        citation_instructions = ""
        slide_schemas = {
            "title": '{"title_text": "string"}',
            "bullet": '{"heading_text": "string", "bullet_points": ["string1", "string2", ...]}',
            "two-column": '{"heading_text": "string", "left_content": ["string1", ...], "right_content": ["string1", ...]}',
            "content-image": '{"main_heading": "string", "sub_heading": "string"}'
        }
        
        if include_citations:
            citation_instructions = f"""
8. INCLUDE CITATIONS: For each slide with generated content, include a "citations" array with relevant, credible sources
9. CITATION STYLE: Use {citation_style.upper()} format for all citations
10. CITATION QUALITY: Include 2-4 high-quality, recent sources per slide (academic papers, reputable websites, books)
11. CITATION FORMAT: Each citation should be a complete, properly formatted reference

CITATION EXAMPLES ({citation_style.upper()} style):
- APA: "Smith, J. (2023). AI in Healthcare. Journal of Medical Technology, 15(3), 45-62."
- MLA: "Smith, John. 'AI in Healthcare.' Journal of Medical Technology, vol. 15, no. 3, 2023, pp. 45-62."
- Chicago: "Smith, John. 'AI in Healthcare.' Journal of Medical Technology 15, no. 3 (2023): 45-62."
- IEEE: "J. Smith, 'AI in Healthcare,' Journal of Medical Technology, vol. 15, no. 3, pp. 45-62, 2023."
"""
            # Update schemas to include citations
            slide_schemas = {
                "title": '{"title_text": "string", "citations": ["citation1", "citation2", ...]}',
                "bullet": '{"heading_text": "string", "bullet_points": ["string1", "string2", ...], "citations": ["citation1", ...]}',
                "two-column": '{"heading_text": "string", "left_content": ["string1", ...], "right_content": ["string1", ...], "citations": ["citation1", ...]}',
                "content-image": '{"main_heading": "string", "sub_heading": "string", "citations": ["citation1", ...]}'
            }
        
        return f"""You are an expert presentation content generator with expertise in academic research and citation. Your task is to generate high-quality, professional slide content with proper citations based on the user's requirements.

IMPORTANT RULES:
1. Generate content ONLY for slides with empty objects {{}} in the content array
2. Keep existing user-provided content unchanged (non-empty objects)
3. Return valid JSON matching the exact structure requested
4. Make content engaging, informative, and professional
5. Ensure bullet points are concise and impactful
6. Headings should be clear and descriptive
7. Don't format the content in any way, just return the content without bolding, italics, or any other formatting{citation_instructions}

SLIDE TYPES AND THEIR SCHEMAS:
- "title": {slide_schemas["title"]}
- "bullet": {slide_schemas["bullet"]}
- "two-column": {slide_schemas["two-column"]}
- "content-image": {slide_schemas["content-image"]}

RESPONSE FORMAT:
{{
  "file_name": "provided_filename.pptx",
  "content": [
    // Array matching input layout with generated content for empty objects only
  ]
}}"""

    def _create_user_prompt(self, prompt: str, layout: List[str], content: List[Dict], filename: str, 
                           include_citations: bool = True, citation_style: str = 'apa') -> str:
        """Create user prompt with specific requirements"""
        
        slides_needing_generation = []
        for i, slide_content in enumerate(content):
            if not slide_content:  # Empty object needs generation
                slides_needing_generation.append(f"Slide {i+1} ({layout[i]})")
        
        citation_requirements = ""
        if include_citations:
            citation_requirements = f"""
- Include {citation_style.upper()} style citations for all generated content
- Provide 2-4 credible, recent sources per slide
- Citations should be from academic papers, reputable websites, or authoritative books
- Format citations properly according to {citation_style.upper()} standards
"""

        user_prompt = f"""
PRESENTATION TOPIC: {prompt}

SLIDE LAYOUT: {layout}

CURRENT CONTENT ARRAY: {content}

FILENAME: {filename}

SLIDES NEEDING GENERATION: {', '.join(slides_needing_generation) if slides_needing_generation else 'None'}

CITATION REQUIREMENTS: {"Enabled" if include_citations else "Disabled"}
CITATION STYLE: {citation_style.upper() if include_citations else "N/A"}

TASK: Generate content for the empty objects {{}} in the content array. Keep all non-empty objects exactly as they are.

Generate professional, engaging content that flows logically through the presentation. Make sure:
- Title slides are compelling and clear
- Bullet points are concise (3-6 points, each 2-8 words)
- Two-column content is balanced and complementary
- Content-image slides have descriptive headings and informative sub-headings
- All content relates to the main topic: {prompt}{citation_requirements}

Return the complete content array with generated content filled in for empty objects only.
"""
        return user_prompt
    
    def _parse_gemini_response(self, response_text: str, layout: List[str], original_content: List[Dict]) -> Dict:
        """Parse and validate Gemini response"""
        try:
            import json
            import re
            
            # Extract JSON from response (handle markdown code blocks)
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try to find JSON without code blocks
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                else:
                    raise ValueError("No valid JSON found in response")
            
            # Parse JSON
            parsed_response = json.loads(json_str)
            
            # Validate structure
            if 'content' not in parsed_response:
                raise ValueError("Response missing 'content' field")
            
            generated_content = parsed_response['content']
            
            # Ensure we have the right number of slides
            if len(generated_content) != len(layout):
                raise ValueError(f"Generated content length ({len(generated_content)}) doesn't match layout length ({len(layout)})")
            
            # Validate each slide content matches expected schema
            validated_content = []
            for i, (slide_type, gen_content) in enumerate(zip(layout, generated_content)):
                # Always use generated content from Gemini response (it should only contain content for empty slides)
                if gen_content and isinstance(gen_content, dict):
                    validated_content.append(self._validate_slide_schema(slide_type, gen_content))
                else:
                    # If no generated content, keep original (this preserves user-provided content)
                    validated_content.append(original_content[i] if i < len(original_content) else {})
            
            return {
                "file_name": parsed_response.get("file_name", "presentation.pptx"),
                "content": validated_content
            }
            
        except Exception as e:
            logger.error(f"Error parsing Gemini response: {str(e)}")
            # Return original content as fallback
            return {"file_name": "presentation.pptx", "content": original_content}
    
    def _validate_slide_schema(self, slide_type: str, content: Dict) -> Dict:
        """Validate generated content matches slide schema"""
        try:
            if slide_type == "title":
                return {"title_text": str(content.get("title_text", "Untitled"))}
            
            elif slide_type == "bullet":
                return {
                    "heading_text": str(content.get("heading_text", "Heading")),
                    "bullet_points": content.get("bullet_points", ["Point 1", "Point 2", "Point 3"])
                }
            
            elif slide_type == "two-column":
                return {
                    "heading_text": str(content.get("heading_text", "Heading")),
                    "left_content": content.get("left_content", ["Left content"]),
                    "right_content": content.get("right_content", ["Right content"])
                }
            
            elif slide_type == "content-image":
                return {
                    "main_heading": str(content.get("main_heading", "Main Heading")),
                    "sub_heading": str(content.get("sub_heading", "Sub heading"))
                }
            
            else:
                return content
                
        except Exception as e:
            logger.error(f"Error validating slide schema for {slide_type}: {str(e)}")
            return content
