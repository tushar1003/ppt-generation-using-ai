#!/bin/bash

# Generate Content API Test Script
# This script tests all endpoints in the generate_content app
# Make sure the Django server is running on http://127.0.0.1:8000

BASE_URL="http://127.0.0.1:8000/api/generate"
echo "🧪 Generate Content API Test Suite"
echo "=================================="
echo "Base URL: $BASE_URL"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print test results
print_test_result() {
    local test_name="$1"
    local status_code="$2"
    local expected_code="$3"
    
    if [ "$status_code" -eq "$expected_code" ]; then
        echo -e "${GREEN}✅ PASS${NC} - $test_name (Status: $status_code)"
    else
        echo -e "${RED}❌ FAIL${NC} - $test_name (Expected: $expected_code, Got: $status_code)"
    fi
}

# Function to make API call and return status code
api_call() {
    local method="$1"
    local endpoint="$2"
    local data="$3"
    local headers="$4"
    
    if [ -n "$data" ]; then
        curl -s -o /dev/null -w "%{http_code}" -X "$method" "$BASE_URL$endpoint" \
             -H "Content-Type: application/json" $headers -d "$data"
    else
        curl -s -o /dev/null -w "%{http_code}" -X "$method" "$BASE_URL$endpoint" $headers
    fi
}

# Function to make API call and show response
api_call_with_response() {
    local method="$1"
    local endpoint="$2"
    local data="$3"
    local headers="$4"
    
    echo -e "${BLUE}Request:${NC} $method $BASE_URL$endpoint"
    if [ -n "$data" ]; then
        echo -e "${BLUE}Data:${NC} $data"
        curl -s -X "$method" "$BASE_URL$endpoint" \
             -H "Content-Type: application/json" $headers -d "$data" | jq . 2>/dev/null || echo "Response received (not JSON)"
    else
        curl -s -X "$method" "$BASE_URL$endpoint" $headers | jq . 2>/dev/null || echo "Response received (not JSON)"
    fi
    echo ""
}

echo "🔍 1. SYSTEM HEALTH CHECKS"
echo "========================="

# Test 1: Health Check
echo -e "${YELLOW}Test 1: Health Check${NC}"
api_call_with_response "GET" "/health/"
status=$(api_call "GET" "/health/")
print_test_result "Health Check" "$status" "200"
echo ""

# Test 2: Performance Stats
echo -e "${YELLOW}Test 2: Performance Statistics${NC}"
api_call_with_response "GET" "/performance/"
status=$(api_call "GET" "/performance/")
print_test_result "Performance Stats" "$status" "200"
echo ""

echo "🎨 2. TEMPLATE MANAGEMENT"
echo "========================"

# Test 3: Available Templates
echo -e "${YELLOW}Test 3: Get Available Templates${NC}"
api_call_with_response "GET" "/templates/"
status=$(api_call "GET" "/templates/")
print_test_result "Available Templates" "$status" "200"
echo ""

# Test 4: Templates by Category
echo -e "${YELLOW}Test 4: Templates by Category (business)${NC}"
api_call_with_response "GET" "/templates/category/business/"
status=$(api_call "GET" "/templates/category/business/")
print_test_result "Templates by Category" "$status" "200"
echo ""

# Test 5: Templates by Aspect Ratio
echo -e "${YELLOW}Test 5: Templates by Aspect Ratio (16:9)${NC}"
api_call_with_response "GET" "/templates/aspect-ratio/16:9/"
status=$(api_call "GET" "/templates/aspect-ratio/16:9/")
print_test_result "Templates by Aspect Ratio" "$status" "200"
echo ""

# Test 6: Template Details
echo -e "${YELLOW}Test 6: Template Details (default_16_9)${NC}"
api_call_with_response "GET" "/templates/default_16_9/"
status=$(api_call "GET" "/templates/default_16_9/")
print_test_result "Template Details - Default" "$status" "200"
echo ""

# Test 6a: Frost Template Details
echo -e "${YELLOW}Test 6a: Template Details (frost_16_9)${NC}"
api_call_with_response "GET" "/templates/frost_16_9/"
status=$(api_call "GET" "/templates/frost_16_9/")
print_test_result "Template Details - Frost" "$status" "200"
echo ""

# Test 6b: Galaxy Template Details
echo -e "${YELLOW}Test 6b: Template Details (galaxy_16_9)${NC}"
api_call_with_response "GET" "/templates/galaxy_16_9/"
status=$(api_call "GET" "/templates/galaxy_16_9/")
print_test_result "Template Details - Galaxy" "$status" "200"
echo ""

echo "🎯 3. PRESENTATION GENERATION"
echo "============================="

# Test 7: Simple Presentation with User Content
echo -e "${YELLOW}Test 7: Simple Presentation (User Content)${NC}"
user_content_data='{
    "prompt": "API Testing Guide",
    "num_slides": 2,
    "layout": ["title", "bullet"],
    "font": "Arial",
    "color": "#1f4e79",
    "content": [
        {
            "title_text": "API Testing Guide"
        },
        {
            "heading_text": "Testing Steps",
            "bullet_points": [
                "Health check endpoints",
                "Template management",
                "Presentation generation",
                "Error handling"
            ]
        }
    ]
}'

api_call_with_response "POST" "/presentation/" "$user_content_data"
status=$(api_call "POST" "/presentation/" "$user_content_data")
print_test_result "Simple Presentation Generation" "$status" "201"
echo ""

# Test 8: Mixed Content Presentation
echo -e "${YELLOW}Test 8: Mixed Content Presentation (User + AI)${NC}"
mixed_content_data='{
    "prompt": "Data Science Workshop",
    "num_slides": 3,
    "layout": ["title", "bullet", "two-column"],
    "font": "Calibri",
    "color": "#2e7d32",
    "content": [
        {
            "title_text": "Data Science Workshop"
        },
        {},
        {
            "heading_text": "Tools & Technologies",
            "left_content": ["Python", "Pandas", "NumPy"],
            "right_content": ["Jupyter", "Matplotlib", "Scikit-learn"]
        }
    ]
}'

api_call_with_response "POST" "/presentation/" "$mixed_content_data"
status=$(api_call "POST" "/presentation/" "$mixed_content_data")
print_test_result "Mixed Content Presentation" "$status" "201"
echo ""

# Test 9: AI-Only Content Presentation
echo -e "${YELLOW}Test 9: AI-Generated Content Presentation${NC}"
ai_content_data='{
    "prompt": "Machine Learning Basics",
    "num_slides": 2,
    "layout": ["title", "bullet"],
    "content": [{}, {}]
}'

api_call_with_response "POST" "/presentation/" "$ai_content_data"
status=$(api_call "POST" "/presentation/" "$ai_content_data")
print_test_result "AI-Generated Presentation" "$status" "201"
echo ""

echo "🚫 4. ERROR HANDLING TESTS"
echo "=========================="

# Test 10: Validation Error - Invalid Input
echo -e "${YELLOW}Test 10: Validation Error (Invalid Input)${NC}"
invalid_data='{
    "prompt": "",
    "num_slides": 25,
    "layout": ["invalid_type"],
    "color": "invalid_color"
}'

api_call_with_response "POST" "/presentation/" "$invalid_data"
status=$(api_call "POST" "/presentation/" "$invalid_data")
print_test_result "Validation Error" "$status" "400"
echo ""

# Test 11: Template Not Found
echo -e "${YELLOW}Test 11: Template Not Found${NC}"
api_call_with_response "GET" "/templates/nonexistent_template/"
status=$(api_call "GET" "/templates/nonexistent_template/")
print_test_result "Template Not Found" "$status" "404"
echo ""

# Test 12: Invalid Category
echo -e "${YELLOW}Test 12: Invalid Template Category${NC}"
api_call_with_response "GET" "/templates/category/invalid_category/"
status=$(api_call "GET" "/templates/category/invalid_category/")
print_test_result "Invalid Category" "$status" "200"  # Returns empty list
echo ""

echo "⚡ 5. RATE LIMITING TESTS"
echo "========================"

echo -e "${YELLOW}Test 13: Rate Limiting (3 requests per minute)${NC}"
echo "Making 5 rapid requests to test rate limiting..."

for i in {1..5}; do
    echo "Request $i:"
    rate_test_data="{\"prompt\": \"Rate Test $i\", \"num_slides\": 1, \"layout\": [\"title\"], \"content\": [{\"title_text\": \"Test $i\"}]}"
    
    response=$(curl -s -X POST "$BASE_URL/presentation/" \
        -H "Content-Type: application/json" \
        -d "$rate_test_data")
    
    if echo "$response" | grep -q '"success":true'; then
        echo -e "${GREEN}✅ SUCCESS${NC} - Request processed"
    elif echo "$response" | grep -q "403\|429"; then
        echo -e "${RED}🚫 RATE LIMITED${NC} - Request blocked"
    else
        echo -e "${YELLOW}❓ OTHER${NC} - $(echo "$response" | head -c 50)..."
    fi
    
    sleep 1
done
echo ""

echo "🧹 6. CACHE MANAGEMENT TESTS"
echo "============================"

# Note: These tests require authentication, so they might fail
echo -e "${YELLOW}Test 14: Cache Cleanup (No Auth Required)${NC}"
api_call_with_response "POST" "/cache/cleanup/"
status=$(api_call "POST" "/cache/cleanup/")
print_test_result "Cache Cleanup" "$status" "200"
echo ""

echo "📊 7. COMPREHENSIVE FEATURE TEST"
echo "================================"

# Test 15: Frost Template Presentation
echo -e "${YELLOW}Test 15: Frost Template Presentation (Academic)${NC}"
frost_template_data='{
    "prompt": "Academic Research Methods",
    "num_slides": 2,
    "layout": ["title", "bullet"],
    "template_id": "frost_16_9",
    "font": "Calibri",
    "color": "#2c3e50",
    "content": [
        {
            "title_text": "Academic Research Methods"
        },
        {
            "heading_text": "Research Methodology",
            "bullet_points": [
                "Literature Review",
                "Data Collection",
                "Statistical Analysis",
                "Results Interpretation"
            ]
        }
    ]
}'

api_call_with_response "POST" "/presentation/" "$frost_template_data"
status=$(api_call "POST" "/presentation/" "$frost_template_data")
print_test_result "Frost Template Presentation" "$status" "201"
echo ""

# Test 16: Galaxy Template Presentation
echo -e "${YELLOW}Test 16: Galaxy Template Presentation (Creative)${NC}"
galaxy_template_data='{
    "prompt": "Creative Design Workshop",
    "num_slides": 2,
    "layout": ["title", "two-column"],
    "template_id": "galaxy_16_9",
    "font": "Arial",
    "color": "#8e44ad",
    "content": [
        {
            "title_text": "Creative Design Workshop"
        },
        {
            "heading_text": "Design Principles",
            "left_content": [
                "Color Theory",
                "Typography",
                "Layout Balance"
            ],
            "right_content": [
                "User Experience",
                "Visual Hierarchy",
                "Brand Consistency"
            ]
        }
    ]
}'

api_call_with_response "POST" "/presentation/" "$galaxy_template_data"
status=$(api_call "POST" "/presentation/" "$galaxy_template_data")
print_test_result "Galaxy Template Presentation" "$status" "201"
echo ""

# Test 17: Full Feature Presentation
echo -e "${YELLOW}Test 17: Full Feature Presentation${NC}"
full_feature_data='{
    "prompt": "Complete API Documentation",
    "num_slides": 4,
    "layout": ["title", "bullet", "two-column", "content-image"],
    "font": "Calibri",
    "color": "#1f4e79",
    "template_id": "default_16_9",
    "aspect_ratio": "16:9",
    "include_citations": true,
    "content": [
        {
            "title_text": "Complete API Documentation"
        },
        {
            "heading_text": "API Features",
            "bullet_points": [
                "RESTful endpoints",
                "Rate limiting protection",
                "Multi-level caching",
                "Comprehensive error handling",
                "Template management"
            ]
        },
        {
            "heading_text": "Technical Implementation",
            "left_content": [
                "Django REST Framework",
                "JWT Authentication",
                "Custom Exception Handling",
                "Input Validation"
            ],
            "right_content": [
                "Gemini AI Integration",
                "Performance Caching",
                "Template System",
                "Concurrent Processing"
            ]
        },
        {
            "heading_text": "System Architecture",
            "sub_heading": "Modular design with separation of concerns"
        }
    ]
}'

api_call_with_response "POST" "/presentation/" "$full_feature_data"
status=$(api_call "POST" "/presentation/" "$full_feature_data")
print_test_result "Full Feature Presentation" "$status" "201"
echo ""

echo "📋 TEST SUMMARY"
echo "==============="
echo "All 17+ tests completed! Check the results above."
echo ""
echo "🎨 New Templates Tested:"
echo "- ✅ Frost Template (Academic) - frost_16_9"
echo "- ✅ Galaxy Template (Creative) - galaxy_16_9"
echo "- ✅ Default Template (Business) - default_16_9"
echo ""
echo "🔧 Troubleshooting:"
echo "- If health check fails: Make sure Django server is running"
echo "- If rate limiting doesn't work: Check django-ratelimit configuration"
echo "- If AI generation fails: Check Gemini service configuration"
echo "- If template tests fail: Ensure templates are properly loaded"
echo ""
echo "📖 For detailed API documentation, see:"
echo "- generate_content_api.md (API reference)"
echo "- generate_content_code.md (Technical implementation)"
echo ""
echo "✨ Happy testing!"
