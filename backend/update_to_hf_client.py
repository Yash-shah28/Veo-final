#!/usr/bin/env python3
"""
Update service.py to use huggingface_hub InferenceClient
"""

import re

SERVICE_FILE = "/Users/priyanshimodi/Documents/projects/TSC/Veo react/Veo-final/backend/app/character/service.py"

with open(SERVICE_FILE, 'r') as f:
    content = f.read()

# 1. Update imports
content = content.replace(
    'from openai import AsyncOpenAI',
    'from huggingface_hub import InferenceClient'
)

# 2. Update __init__ method
old_init = '''    def __init__(self):
        # Initialize Hugging Face client (FREE inference API)
        self.api_key = HUGGINGFACE_CONFIG["api_key"]
        self.base_url = HUGGINGFACE_CONFIG["base_url"]
        self.model = HUGGINGFACE_CONFIG["model"]
        self.api_url = f"{self.base_url}/{self.model}"
        
        if not self.api_key:
            raise ValueError("HUGGINGFACE_API_KEY not configured. Get one from https://huggingface.co/settings/tokens")'''

new_init = '''    def __init__(self):
        # Initialize Hugging Face InferenceClient
        self.api_key = HUGGINGFACE_CONFIG["api_key"]
        self.model = HUGGINGFACE_CONFIG["model"]
        
        if not self.api_key:
            raise ValueError("HUGGINGFACE_API_KEY not configured. Get one from https://huggingface.co/settings/tokens")
        
        self.client = InferenceClient(api_key=self.api_key)'''

content = content.replace(old_init, new_init)

# 3. Remove the old _call_huggingface_api method (we don't need it)
# Find and remove the method
pattern = r'    async def _call_huggingface_api\(.*?\n(?:.*?\n)*?        return str\(result\)\n'
content = re.sub(pattern, '', content, flags=re.DOTALL)

# 4. Update detection API call
old_detection = '''                result = await self._call_huggingface_api(detection_prompt, max_tokens=10, temperature=0.1)
                result = result.strip().upper()'''

new_detection = '''                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": detection_prompt}],
                    temperature=0.1,
                    max_tokens=10
                )
                result = response.choices[0].message.content.strip().upper()'''

content = content.replace(old_detection, new_detection)

# 5. Update main API call
old_main = '''            # Combine prompts for Hugging Face
            full_prompt = f"{system_prompt}\\n\\n{user_prompt}"
            
            raw_output = await self._call_huggingface_api(full_prompt, max_tokens=8192, temperature=0.8)
            
            print(f"✅ Hugging Face responded: {len(raw_output)} chars")'''

new_main = '''            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.8,
                max_tokens=8192
            )
            
            raw_output = response.choices[0].message.content
            
            print(f"✅ Hugging Face responded: {len(raw_output)} chars")'''

content = content.replace(old_main, new_main)

# Write back
with open(SERVICE_FILE, 'w') as f:
    f.write(content)

print("✅ Successfully updated to use huggingface_hub InferenceClient!")
print("\n📝 Next step:")
print("pip3 install huggingface_hub")
