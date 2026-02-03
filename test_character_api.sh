#!/bin/bash

# Test the Talking Character API endpoint
# Make sure backend is running on localhost:8000

echo "🧪 Testing Talking Character Backend API"
echo "=========================================="
echo ""

# First, let's test without auth to see if endpoint exists
echo "📍 Testing endpoint availability..."
curl -X POST http://localhost:8000/gemini/generate-character-dialogue \
  -H "Content-Type: application/json" \
  -d '{
    "character_name": "Apple",
    "voice_tone": "child_happy",
    "topic_mode": "benefits",
    "scenario": "Teaching kids about healthy eating",
    "visual_style": "3D Animation (Pixar/Disney) - Best",
    "language": "english",
    "total_duration": 16
  }' \
  -w "\n\nHTTP Status: %{http_code}\n" \
  2>/dev/null

echo ""
echo "=========================================="
echo "✅ Test completed!"
echo ""
echo "Expected responses:"
echo "  - 401: Authentication required (endpoint exists)"
echo "  - 200: Success (if you added Authorization header)"
echo "  - 500: Server error (check logs)"
echo "  - 404: Route not found (check router setup)"
