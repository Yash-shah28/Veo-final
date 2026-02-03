#!/bin/bash

echo "🧪 Testing Talking Character API (without auth)"
echo "================================================"
echo ""

# Test with a simple request
echo "📍 Sending request..."
response=$(curl -s -X POST http://localhost:8000/gemini/generate-character-dialogue \
  -H "Content-Type: application/json" \
  -d '{
    "character_name": "Apple",
    "voice_tone": "child_happy",
    "topic_mode": "benefits",
    "scenario": "Teaching kids about healthy eating",
    "visual_style": "3D Animation (Pixar/Disney) - Best",
    "language": "english",
    "total_duration": 8
  }')

echo "Response:"
echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
echo ""
echo "================================================"
echo ""

# Check if we got the expected 401 (needs auth)
if echo "$response" | grep -q "Not authenticated"; then
    echo "✅ Endpoint exists and requires authentication (expected)"
    echo "   Next step: Login to get a JWT token and test with auth"
elif echo "$response" | grep -q "scenes"; then
    echo "✅ SUCCESS! The API is working!"
elif echo "$response" | grep -q "error\|detail"; then
    echo "⚠️  Got an error response (check above)"
else
    echo "❓ Unexpected response (check above)"
fi
