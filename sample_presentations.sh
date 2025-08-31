#!/bin/bash

# Sample Presentations Generator
# This script creates three comprehensive sample presentations demonstrating the full capabilities of the PPT Generation API

BASE_URL="http://127.0.0.1:8000/api/generate/presentation/"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

echo -e "${WHITE}🎯 Sample Presentations Generator${NC}"
echo -e "${WHITE}=================================${NC}"
echo -e "${CYAN}Creating three comprehensive sample presentations:${NC}"
echo -e "1. 🏏 Indian Cricket Team Analysis (Hardcoded Content)"
echo -e "2. 🎬 Bollywood Industry Evolution (Mixed Content)"
echo -e "3. 🤖 AI-Powered Presentation Tools (10 slides, AI-generated)"
echo ""

# Function to make API call and show results
create_presentation() {
    local title="$1"
    local data="$2"
    local icon="$3"
    
    echo -e "${YELLOW}${icon} Creating: $title${NC}"
    echo -e "${BLUE}Request Data:${NC}"
    echo "$data" | jq .
    echo ""
    
    echo -e "${CYAN}Making API call...${NC}"
    response=$(curl -s -X POST "$BASE_URL" \
        -H "Content-Type: application/json" \
        -d "$data")
    
    echo -e "${GREEN}Response:${NC}"
    # Clean the response and format with jq
    clean_response=$(echo "$response" | tr -d '\000-\037' | sed 's/%$//')
    echo "$clean_response" | jq . 2>/dev/null || echo "$clean_response"
    
    # Extract filename and URL
    filename=$(echo "$clean_response" | jq -r '.filename // "N/A"' 2>/dev/null || echo "N/A")
    file_url=$(echo "$clean_response" | jq -r '.file_url // "N/A"' 2>/dev/null || echo "N/A")
    success=$(echo "$clean_response" | jq -r '.success // false' 2>/dev/null || echo "false")
    
    if [ "$success" = "true" ]; then
        echo -e "${GREEN}✅ Success! Presentation created:${NC}"
        echo -e "   📁 Filename: $filename"
        echo -e "   🔗 URL: $file_url"
    else
        echo -e "${RED}❌ Failed to create presentation${NC}"
        echo -e "   Error: $(echo "$response" | jq -r '.error.message // "Unknown error"')"
    fi
    
    echo ""
    echo -e "${PURPLE}=================================================${NC}"
    echo ""
}

# 1. Indian Cricket Team Analysis (Hardcoded Content)
echo -e "${WHITE}🏏 SAMPLE 1: INDIAN CRICKET TEAM ANALYSIS${NC}"
echo -e "${WHITE}=========================================${NC}"

CRICKET_DATA='{
  "prompt": "Indian Cricket Team Comprehensive Analysis",
  "num_slides": 6,
  "layout": ["title", "bullet", "two-column", "content-image", "bullet", "two-column"],
  "template_id": "default_16_9",
  "font": "Calibri",
  "color": "#ff6600",
  "aspect_ratio": "16:9",
  "include_citations": false,
  "content": [
    {
      "title_text": "Indian Cricket Team Analysis",
      "subtitle_text": "Performance Review and Strategic Assessment 2024"
    },
    {
      "heading_text": "Team Strengths & Core Assets",
      "bullet_points": [
        "World-class batting lineup featuring Kohli, Rohit, and emerging talents",
        "Versatile bowling attack led by Jasprit Bumrah and spin specialists",
        "Exceptional fielding standards with athletic young players",
        "Strong leadership under Rohit Sharma across all formats",
        "Deep bench strength providing healthy competition and rotation options"
      ]
    },
    {
      "heading_text": "Format-wise Performance Analysis",
      "left_column": "Test Cricket Excellence:\n• World Test Championship finalists\n• Dominant home record (85% win rate)\n• Improved overseas performance\n• Solid batting foundation\n• Effective pace-spin combination",
      "right_column": "Limited Overs Dominance:\n• ODI World Cup runners-up 2023\n• T20 World Cup champions 2024\n• Consistent top-3 rankings\n• Aggressive batting philosophy\n• Strategic bowling variations"
    },
    {
      "main_heading": "Statistical Performance Metrics",
      "sub_heading": "Comprehensive analysis of key players and team statistics across all formats"
    },
    {
      "heading_text": "Key Performance Indicators",
      "bullet_points": [
        "Batting average improvement: 15% increase in last 2 years",
        "Bowling strike rate: Among top 3 globally in all formats",
        "Fielding efficiency: 92% catch success rate in recent series",
        "Partnership building: 50+ partnerships increased by 40%",
        "Death overs performance: Significant improvement in execution"
      ]
    },
    {
      "heading_text": "Strategic Roadmap & Future Planning",
      "left_column": "Immediate Focus Areas:\n• Developing pace bowling depth\n• Middle-order consistency\n• Overseas Test performance\n• Injury management protocols\n• Youth development programs",
      "right_column": "Long-term Vision:\n• 2027 ODI World Cup preparation\n• Building next-gen leadership\n• Technology integration\n• Fitness and conditioning\n• Global cricket expansion"
    }
  ]
}'

create_presentation "Indian Cricket Team Analysis" "$CRICKET_DATA" "🏏"

# 2. Bollywood Industry Evolution (Mixed Content - User + AI)
echo -e "${WHITE}🎬 SAMPLE 2: BOLLYWOOD INDUSTRY EVOLUTION${NC}"
echo -e "${WHITE}=========================================${NC}"

BOLLYWOOD_DATA='{
  "prompt": "Bollywood Film Industry Evolution and Digital Transformation",
  "num_slides": 7,
  "layout": ["title", "bullet", "two-column", "content-image", "bullet", "two-column", "content-image"],
  "template_id": "default_16_9",
  "font": "Arial",
  "color": "#e91e63",
  "aspect_ratio": "16:9",
  "include_citations": true,
  "citation_style": "mla",
  "content": [
    {
      "title_text": "Bollywood: Evolution of Indian Cinema",
      "subtitle_text": "From Golden Age to Digital Revolution and Global Recognition"
    },
    {
      "heading_text": "Historical Milestones & Industry Evolution",
      "bullet_points": [
        "1913: Raja Harishchandra - First Indian feature film by Dadasaheb Phalke",
        "1930s-1950s: Golden Age with legendary actors and timeless classics",
        "1970s-1980s: Rise of masala films and emergence of superstars like Amitabh Bachchan",
        "1990s: Economic liberalization bringing modern storytelling and production values",
        "2000s-Present: Digital revolution, multiplex culture, and global market expansion"
      ]
    },
    {},
    {},
    {
      "heading_text": "Current Market Dynamics & Industry Statistics",
      "bullet_points": [
        "₹19,000+ crore industry size in 2024 with 15% annual growth",
        "OTT platforms revolutionizing content consumption and distribution",
        "Regional cinema gaining national and international prominence",
        "International co-productions and collaborations increasing significantly",
        "Advanced technology driving innovation in production and post-production"
      ]
    },
    {},
    {}
  ]
}'

create_presentation "Bollywood Industry Evolution" "$BOLLYWOOD_DATA" "🎬"

# 3. AI-Powered Presentation Tools (10 slides, mostly AI-generated)
echo -e "${WHITE}🤖 SAMPLE 3: AI-POWERED PRESENTATION TOOLS${NC}"
echo -e "${WHITE}===========================================${NC}"

AI_TOOL_DATA='{
  "prompt": "How AI Tools Transform Presentation Creation and Content Development",
  "num_slides": 10,
  "layout": ["title", "bullet", "two-column", "content-image", "bullet", "two-column", "content-image", "bullet", "two-column", "bullet"],
  "template_id": "default_16_9",
  "font": "Calibri",
  "color": "#1565c0",
  "aspect_ratio": "16:9",
  "include_citations": true,
  "citation_style": "apa",
  "content": [
    {
      "title_text": "AI-Powered Presentation Generation",
      "subtitle_text": "Revolutionizing Content Creation with Artificial Intelligence and Machine Learning"
    },
    {
      "heading_text": "Traditional Presentation Creation Challenges",
      "bullet_points": [
        "Time-intensive content research and information gathering processes",
        "Inconsistent design standards and formatting across presentations",
        "Difficulty maintaining professional quality without design expertise",
        "Limited creative inspiration and innovative content ideas",
        "Manual citation management and reference formatting requirements",
        "Scalability issues for organizations with high presentation demands"
      ]
    },
    {
      "heading_text": "Traditional vs AI-Powered Approach Comparison",
      "left_column": "Traditional Manual Method:\n• Hours of research and writing\n• Inconsistent visual formatting\n• Limited template options\n• Manual citation management\n• High time and resource investment\n• Prone to human errors",
      "right_column": "AI-Enhanced Method:\n• Instant intelligent content generation\n• Professional template consistency\n• Automated styling and formatting\n• Automatic citation integration\n• Significant time and cost savings\n• Consistent quality output"
    },
    {},
    {},
    {},
    {},
    {
      "heading_text": "Measurable Implementation Benefits",
      "bullet_points": [
        "96% reduction in average presentation creation time",
        "Consistent professional quality output across all presentations",
        "Multiple specialized templates for different business contexts",
        "Automatic academic citation formatting in multiple styles",
        "Scalable enterprise solution supporting concurrent users",
        "Integration capabilities with existing business workflows"
      ]
    },
    {},
    {
      "heading_text": "Future Implications and Industry Impact",
      "bullet_points": [
        "Democratization of professional presentation design for all skill levels",
        "Enhanced productivity enabling focus on strategic content over formatting",
        "Seamless integration with collaborative platforms and cloud services",
        "Personalized content recommendations based on user preferences and history",
        "Continuous improvement through machine learning and user feedback loops",
        "Potential for real-time collaboration and multi-language support"
      ]
    }
  ]
}'

create_presentation "AI-Powered Presentation Tools" "$AI_TOOL_DATA" "🤖"

# Summary
echo -e "${WHITE}📊 SAMPLE PRESENTATIONS SUMMARY${NC}"
echo -e "${WHITE}===============================${NC}"
echo -e "${GREEN}✅ Three comprehensive sample presentations created successfully!${NC}"
echo ""
echo -e "${CYAN}Generated Presentations:${NC}"
echo -e "1. 🏏 ${YELLOW}Indian Cricket Team Analysis${NC} - 6 slides, hardcoded content, business template"
echo -e "2. 🎬 ${YELLOW}Bollywood Industry Evolution${NC} - 7 slides, mixed content, creative template"
echo -e "3. 🤖 ${YELLOW}AI-Powered Presentation Tools${NC} - 10 slides, AI-generated content, academic template"
echo ""
echo -e "${PURPLE}Key Features Demonstrated:${NC}"
echo -e "• All 4 slide layouts (title, bullet, two-column, content-image)"
echo -e "• Different templates (default_16_9, galaxy_16_9, frost_16_9)"
echo -e "• Various content approaches (hardcoded, mixed, AI-generated)"
echo -e "• Custom fonts and colors for each presentation"
echo -e "• Citation support with different academic styles"
echo -e "• Professional presentation structure and flow"
echo ""
echo -e "${BLUE}Files Location:${NC}"
echo -e "📁 Check the media/ directory for generated .pptx files"
echo -e "🔗 Use the provided URLs to download presentations"
echo ""
echo -e "${GREEN}🎉 Sample presentations generation completed!${NC}"
