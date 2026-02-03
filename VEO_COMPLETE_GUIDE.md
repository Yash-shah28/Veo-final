# VEO Video Prompt Generator - Complete Implementation Guide

## Everything You Need to Know - All Doubts Covered

---

## 📌 Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture & Technology Stack](#architecture--technology-stack)
3. [Database Schema Explained](#database-schema-explained)
4. [Feature-by-Feature Implementation](#feature-by-feature-implementation)
5. [Common Doubts & Solutions](#common-doubts--solutions)
6. [API Endpoints Reference](#api-endpoints-reference)
7. [Development Workflow](#development-workflow)
8. [Testing Strategy](#testing-strategy)

---

## 🎯 Project Overview

### What is VEO?

VEO is a full-stack AI-powered application that helps users create professional video prompts for Google's Veo AI video generation platform. It supports three modes:

- **Story Telling**: Multi-scene narratives with character consistency
- **Talking Character**: Single character dialogue scenes
- **UGC/Advertisement**: Product showcase videos (Coming Soon)

### Current Status

✅ **Working**: Basic HTML/Flask prototype with all AI features  
🚧 **Building**: Full React + FastAPI app with authentication and user management

---

## 🏗️ Architecture & Technology Stack

### Frontend Stack

```
React 18
├── Vite (Build tool)
├── React Router DOM (Navigation)
├── Axios (API calls)
├── Context API (State management)
└── CSS Modules (Styling)
```

### Backend Stack

```
FastAPI (Python)
├── Motor (Async MongoDB driver)
├── PyJWT (Authentication)
├── Bcrypt (Password hashing)
├── Python-multipart (File uploads)
└── Google Gemini API (AI operations)
```

### Database

```
MongoDB (NoSQL)
├── Users Collection
├── Projects Collection
└── Scenes Collection
```

### AI Services

- **Google Gemini 2.5 Flash** (ONLY AI provider)
  - Character image analysis
  - Script breaking into scenes
  - Prompt generation
- ❌ **Removed**: Hugging Face (Llama, Qwen)

---

## 📊 Database Schema Explained

### 1. Users Collection

```javascript
{
  "_id": ObjectId("507f1f77bcf86cd799439011"),
  "email": "user@example.com",
  "password_hash": "$2b$12$abc123...",  // Bcrypt hashed
  "name": "John Doe",
  "created_at": ISODate("2024-01-15T10:30:00Z"),
  "api_keys": {
    "gemini": "AIza_encrypted_key"  // Encrypted Gemini API key
  }
}
```

**Purpose**: Store user credentials and API keys  
**Security**: Passwords hashed with bcrypt, API keys encrypted

---

### 2. Projects Collection

```javascript
{
  "_id": ObjectId("507f1f77bcf86cd799439012"),
  "user_id": ObjectId("507f1f77bcf86cd799439011"),  // Links to Users
  "project_name": "My Epic Story",
  "project_type": "storytelling",  // "storytelling" | "character"
  "created_at": ISODate("2024-01-15T11:00:00Z"),
  "last_updated": ISODate("2024-01-15T14:30:00Z"),

  // GLOBAL PROJECT CHARACTERS (Available to ALL scenes)
  "characters": {
    "protagonist": {
      "name": "Emperor Ashoka",

      // UNCHANGEABLE TRAITS (Stored once, used in all scenes)
      "base_description": "Medium skin tone, sharp jawline, deep-set brown eyes, strong nose, medium build",
      "voice_type": "deep_male",
      "voice_tone": "authoritative",

      // CHANGEABLE DEFAULTS (Can override per scene)
      "default_costume": "royal robes",
      "default_emotion": "neutral",

      // METADATA
      "added_in_scene": 1,
      "image_base64": "data:image/jpeg;base64,/9j/4AAQ..."
    },
    "antagonist": {
      "name": "General Vikram",
      "base_description": "...",
      "added_in_scene": 5  // Added later in Scene 5
    }
  },

  // PROJECT SETTINGS
  "settings": {
    "visual_style": "Cinematic Photorealism",
    "default_duration": 8
  },

  // SCRIPT BREAKING DATA (if used)
  "raw_script": "Full story text pasted by user...",
  "script_broken": true,
  "total_scenes": 7
}
```

**Key Points**:

- ✅ Characters stored at **PROJECT level**, not scene level
- ✅ Users can add characters at any time (Scene 1, 5, 10, etc.)
- ✅ Once added, characters available to all scenes

---

### 3. Scenes Collection

**IMPORTANT**: Each scene is a **SEPARATE DOCUMENT**

```javascript
// SCENE 1 (Separate document)
{
  "_id": ObjectId("507f1f77bcf86cd799439013"),
  "project_id": ObjectId("507f1f77bcf86cd799439012"),  // Links to Projects
  "user_id": ObjectId("507f1f77bcf86cd799439011"),     // Links to Users
  "scene_number": 1,

  // SCENE DATA
  "description": "Ashoka reflects on the Kalinga war aftermath",
  "duration": 8,
  "scene_type": "dialogue",  // "dialogue" | "scene_change" | "action"

  // CHARACTER OVERRIDES (Per-scene customization)
  "characters_in_scene": {
    "protagonist": {
      "emotion": "frustrated",      // OVERRIDE for this scene
      "costume": "battle armor",     // OVERRIDE for this scene
      "dialogue": "Why did we wage this war?",
      "action": "pacing back and forth"
    }
  },

  // GENERATED OUTPUT
  "generated_prompt": "8-second cinematic video in photorealistic style: Emperor Ashoka, medium skin tone, sharp jawline...",
  "generated_at": ISODate("2024-01-15T11:15:00Z"),

  // STORY CONTEXT (Summary of previous scenes)
  "story_context": "",  // Empty for Scene 1

  // METADATA
  "created_at": ISODate("2024-01-15T11:15:00Z"),
  "updated_at": ISODate("2024-01-15T11:15:00Z")
}

// SCENE 2 (Another separate document)
{
  "_id": ObjectId("507f1f77bcf86cd799439014"),
  "project_id": ObjectId("507f1f77bcf86cd799439012"),  // SAME project
  "user_id": ObjectId("507f1f77bcf86cd799439011"),     // SAME user
  "scene_number": 2,

  "description": "Ashoka visits the battlefield",
  "characters_in_scene": {
    "protagonist": {
      "emotion": "remorseful",       // DIFFERENT emotion
      "costume": "simple white robes", // DIFFERENT costume
      "dialogue": "What have I done?"
    }
  },

  "generated_prompt": "8-second cinematic video: Emperor Ashoka (same face as Scene 1) now wearing white robes...",
  "story_context": "Scene 1: Ashoka reflected on the war in his throne room, frustrated by the outcome."
}
```

**How to fetch all scenes for a project**:

```python
# Backend query
scenes = db.scenes.find(
    {"project_id": ObjectId(project_id)}
).sort("scene_number", 1)  # Sort by scene number
```

---

## 🔍 Common Doubts & Solutions

### ❓ Doubt 1: Can users add new characters in the middle of scenes?

**Answer: YES ✅**

**Scenario**:

1. User creates Scene 1 → Adds "Ashoka" character
2. User creates Scenes 2, 3, 4 → Uses "Ashoka"
3. User creates Scene 5 → Wants to add "General Vikram"

**What happens**:

```javascript
// Step 1: Scene 1 created, Ashoka added to project.characters
{
  "project_id": "123",
  "characters": {
    "protagonist": { "name": "Ashoka", "added_in_scene": 1 }
  }
}

// Step 2: Scene 5 created, General Vikram added
{
  "project_id": "123",
  "characters": {
    "protagonist": { "name": "Ashoka", "added_in_scene": 1 },
    "antagonist": { "name": "General Vikram", "added_in_scene": 5 }  // NEW
  }
}
```

**Result**:

- ✅ General Vikram available in Scene 5, 6, 7... onwards
- ✅ Can also use in Scene 1-4 if user edits them later
- ✅ Characters stored in `project.characters`, not individual scenes

---

### ❓ Doubt 2: How do multiple scenes work? Is each scene a separate document?

**Answer: YES ✅ - Each scene is a SEPARATE document**

**Example**:

```javascript
// MongoDB Scenes Collection
[
  { _id: "001", project_id: "123", scene_number: 1, description: "..." },
  { _id: "002", project_id: "123", scene_number: 2, description: "..." },
  { _id: "003", project_id: "123", scene_number: 3, description: "..." },
];
```

**Frontend API call**:

```javascript
// Fetch all scenes for a project
const response = await axios.get(`/api/projects/123/scenes`);
// Returns: [scene1, scene2, scene3, ...]
```

**Backend endpoint**:

```python
@app.get("/api/projects/{project_id}/scenes")
async def get_project_scenes(project_id: str):
    scenes = await db.scenes.find(
        {"project_id": ObjectId(project_id)}
    ).sort("scene_number", 1).to_list(100)

    return scenes
```

---

### ❓ Doubt 3: How to maintain character consistency but allow costumes/emotions to change?

**Answer: Two-level system ✅**

#### Level 1: Project-Level (NEVER CHANGES)

```javascript
{
  "characters": {
    "protagonist": {
      // CONSTANT TRAITS
      "base_description": "Medium skin tone, sharp jawline, brown eyes, medium build",
      "voice_type": "deep_male",
      "voice_tone": "authoritative"
    }
  }
}
```

#### Level 2: Scene-Level (CAN CHANGE)

```javascript
{
  "scene_number": 1,
  "characters_in_scene": {
    "protagonist": {
      "emotion": "frustrated",     // Scene 1: Frustrated
      "costume": "battle armor",   // Scene 1: Battle armor
      "dialogue": "Why this war?"
    }
  }
}

// Scene 2 - Different emotion/costume
{
  "scene_number": 2,
  "characters_in_scene": {
    "protagonist": {
      "emotion": "remorseful",           // Scene 2: Remorseful
      "costume": "simple white robes",   // Scene 2: White robes
      "dialogue": "I regret my actions"
    }
  }
}
```

#### Gemini Prompt Generation

```python
def generate_scene_prompt(project, scene):
    character_base = project["characters"]["protagonist"]
    scene_override = scene["characters_in_scene"]["protagonist"]

    prompt = f"""
Generate an 8-second Veo video prompt:

CHARACTER (MAINTAIN EXACT APPEARANCE):
- Face: {character_base["base_description"]}
- Voice: {character_base["voice_type"]}, {character_base["voice_tone"]}

SCENE-SPECIFIC CHANGES:
- Emotion: {scene_override["emotion"]}
- Costume: {scene_override["costume"]}
- Dialogue: {scene_override["dialogue"]}

IMPORTANT: Keep face, body, and voice EXACTLY the same. Only change emotion and costume.
"""

    return gemini_api.generate(prompt)
```

**What NEVER changes**: Face, skin tone, body build, voice type  
**What CAN change**: Emotion, costume, hairstyle, accessories

---

### ❓ Doubt 4: What's the difference between the working prototype and target app?

**Working Prototype (index.html + app.py)**:

- ✅ All AI features working
- ✅ Three modes functional
- ✅ Character consistency
- ❌ No authentication
- ❌ No user-specific projects
- ❌ Single-user only

**Target App (React + FastAPI)**:

- ✅ All AI features (same as prototype)
- ✅ User authentication (JWT)
- ✅ Multi-user support
- ✅ User-specific projects
- ✅ Project history
- ✅ Saved API keys per user
- ✅ Better UI/UX

---

### ❓ Doubt 5: Why Gemini only? Why remove Hugging Face?

**Reasons**:

1. **Simplicity**: One API key instead of two
2. **Cost**: Gemini Free tier = 1500 requests/day
3. **Quality**: Gemini 2.5 Flash performs well
4. **Consistency**: Same model for all tasks

**Before (Complex)**:

```
User needs:
1. Gemini key (character analysis)
2. Hugging Face token (prompt generation)
```

**After (Simple)**:

```
User needs:
1. Gemini key only ✅
```

**All tasks use Gemini**:

- Image analysis → Gemini 2.5 Flash
- Script breaking → Gemini 2.5 Flash
- Prompt generation → Gemini 2.5 Flash

---

### ❓ Doubt 6: How does scene breaking work?

**User Flow**:

```
1. User pastes full story/script
   ↓
2. Clicks "Break into Scenes"
   ↓
3. Backend sends to Gemini with prompt:
   "Break this story into 8-second scenes"
   ↓
4. Gemini returns JSON:
   {
     "scenes": [
       {"scene_number": 1, "description": "...", "dialogue": "..."},
       {"scene_number": 2, "description": "...", "dialogue": "..."}
     ]
   }
   ↓
5. Frontend displays: [◀ Prev] Scene 1 of 7 [Next ▶]
   ↓
6. Auto-fills scene form with data
   ↓
7. User edits if needed → Generates prompt
```

**Backend Implementation**:

```python
@app.post("/api/gemini/break-script")
async def break_script(script: str):
    prompt = f"""
Break this story into optimal 8-second video scenes.

STORY:
{script}

REQUIREMENTS:
1. Each scene = 8 seconds
2. Identify characters in each scene
3. Extract dialogue if present
4. Describe action/emotion
5. Maintain narrative flow

OUTPUT FORMAT (JSON):
{{
  "total_scenes": 5,
  "scenes": [
    {{
      "scene_number": 1,
      "description": "...",
      "characters": ["Ashoka"],
      "dialogue": "...",
      "emotion": "frustrated",
      "scene_type": "dialogue"
    }}
  ]
}}

Only return valid JSON, no markdown.
"""

    response = await gemini_api.generate_content(prompt)
    return json.loads(response.text)
```

---

### ❓ Doubt 7: How does Talking Character mode work without image upload?

**Old Design (Removed)**:

- User uploads vegetable image
- Gemini analyzes image

**New Design (Simplified)**:

- User selects from dropdown: Apple, Carrot, Broccoli, etc.
- No image upload needed
- Gemini generates based on character type

**UI**:

```
CHARACTER TYPE: [Apple ▼]

TALKING TOPIC:
○ Health Benefits (Why to eat me)
● Side Effects (Why NOT to eat me)

LANGUAGE: [Hindi ▼]

DURATION: [8 seconds ▼]
```

**Backend Logic**:

```python
@app.post("/api/gemini/generate-character-dialogue")
async def generate_character_dialogue(
    character_type: str,  # "apple"
    topic_mode: str,      # "benefits" or "side_effects"
    language: str         # "hindi" or "english"
):
    if topic_mode == "benefits":
        topic = f"Health benefits of eating {character_type}"
    else:
        topic = f"Potential side effects or when NOT to eat {character_type}"

    prompt = f"""
Generate an 8-second Veo video prompt for a talking {character_type}.

CHARACTER: Cute 3D animated {character_type} with expressive face
TOPIC: {topic}
LANGUAGE: {language}

Make it educational but fun, with 1-2 key points.
"""

    return await gemini_api.generate(prompt)
```

---

### ❓ Doubt 8: What's the story context memory?

**Purpose**: Help AI maintain continuity across scenes

**How it works**:

```javascript
// Scene 1
{
  "scene_number": 1,
  "description": "Ashoka in throne room",
  "story_context": ""  // Empty for first scene
}

// Scene 2
{
  "scene_number": 2,
  "description": "Ashoka visits battlefield",
  "story_context": "Scene 1: Ashoka reflected on the war in his throne room, feeling frustrated."
}

// Scene 3
{
  "scene_number": 3,
  "description": "Ashoka meets monks",
  "story_context": "Scene 1: Throne room reflection. Scene 2: Battlefield visit, saw destruction."
}
```

**Backend Summarization**:

```python
async def build_story_context(project_id: str, current_scene_number: int):
    previous_scenes = await db.scenes.find({
        "project_id": ObjectId(project_id),
        "scene_number": {"$lt": current_scene_number}
    }).sort("scene_number", 1).to_list(10)

    context = ""
    for scene in previous_scenes:
        context += f"Scene {scene['scene_number']}: {scene['description']}. "

    return context
```

**Usage in Prompt Generation**:

```python
prompt = f"""
STORY SO FAR:
{story_context}

CURRENT SCENE:
{current_scene_description}

Generate a prompt that maintains continuity with previous scenes.
"""
```

---

## 🔌 API Endpoints Reference

### Authentication

```
POST   /api/auth/signup
Body: { email, password, name }
Response: { user_id, token }

POST   /api/auth/login
Body: { email, password }
Response: { user_id, token, name }

GET    /api/auth/me
Headers: { Authorization: "Bearer <token>" }
Response: { user_id, email, name, api_keys }
```

### Projects

```
GET    /api/projects
Headers: { Authorization: "Bearer <token>" }
Response: [{ project_id, project_name, project_type, created_at, total_scenes }]

POST   /api/projects
Body: { project_name, project_type }
Response: { project_id, project_name, project_type }

GET    /api/projects/:id
Response: { project details, characters, settings }

PUT    /api/projects/:id
Body: { project_name, settings, characters }

DELETE /api/projects/:id
```

### Scenes

```
GET    /api/projects/:id/scenes
Response: [{ scene_id, scene_number, description, generated_prompt }]

POST   /api/projects/:id/scenes
Body: { scene_number, description, characters_in_scene, duration }
Response: { scene_id }

GET    /api/projects/:id/scenes/:scene_id
Response: { scene details }

PUT    /api/projects/:id/scenes/:scene_id
Body: { description, characters_in_scene }

DELETE /api/projects/:id/scenes/:scene_id
```

### Gemini AI

```
POST   /api/gemini/analyze-character
Body: { image_base64 }
Response: { base_description, visual_style }

POST   /api/gemini/break-script
Body: { script }
Response: { total_scenes, scenes: [...] }

POST   /api/gemini/generate-prompt
Body: { project_id, scene_number, project_type }
Response: { generated_prompt }
```

---

## 🚀 Development Workflow

### Setup (Day 1)

**Frontend**:

```bash
cd frontend
npm create vite@latest . -- --template react
npm install axios react-router-dom
npm run dev
```

**Backend**:

```bash
cd backend
pip install fastapi motor pyjwt bcrypt python-multipart uvicorn
uvicorn app.main:app --reload
```

**MongoDB**:

```bash
# Local MongoDB
docker run -d -p 27017:27017 --name mongo mongo:latest

# Or MongoDB Atlas (cloud)
# Copy connection string to .env
```

### Environment Variables

**Backend `.env`**:

```env
MONGODB_URI=mongodb://localhost:27017/veo_db
JWT_SECRET=your_secret_key_change_this
JWT_ALGORITHM=HS256
JWT_EXPIRATION=86400
```

**Frontend `.env`**:

```env
VITE_API_URL=http://localhost:8000/api
```

---

## 📅 10-Day Sprint Implementation Order

### Day 1-2: Foundation

- [ ] Backend: FastAPI project structure
- [ ] Backend: MongoDB connection
- [ ] Backend: User model + JWT auth
- [ ] Frontend: Vite + React setup
- [ ] Frontend: Login/Signup pages
- [ ] Frontend: AuthContext

### Day 3-4: Projects

- [ ] Backend: Projects CRUD endpoints
- [ ] Backend: Projects model
- [ ] Frontend: Dashboard page
- [ ] Frontend: Project creation modal
- [ ] Frontend: Project cards

### Day 5-6: Story Mode - Scene Breaking

- [ ] Backend: Gemini integration
- [ ] Backend: POST /gemini/break-script
- [ ] Frontend: ScriptBreaker component
- [ ] Frontend: Scene navigation (Prev/Next)
- [ ] Frontend: Auto-fill scene form

### Day 7: Story Mode - Characters & Prompts

- [ ] Backend: Character image analysis
- [ ] Backend: Scene prompt generation
- [ ] Backend: Scenes CRUD endpoints
- [ ] Frontend: CharacterForm
- [ ] Frontend: SceneForm
- [ ] Frontend: PromptOutput

### Day 8: Talking Character Mode

- [ ] Backend: Character dialogue endpoint
- [ ] Frontend: Character type dropdown
- [ ] Frontend: Topic selector (Benefits/Side Effects)
- [ ] Frontend: Language selector

### Day 9: Polish & Testing

- [ ] Loading states
- [ ] Error handling
- [ ] Responsive design
- [ ] UGC button (disabled + "Coming Soon")
- [ ] End-to-end testing

### Day 10: Deployment

- [ ] MongoDB Atlas setup
- [ ] Backend deployment (Render/Railway)
- [ ] Frontend deployment (Vercel/Netlify)
- [ ] Environment variables setup
- [ ] Production testing

---

## 🧪 Testing Strategy

### Unit Tests

```python
# Backend: test_auth.py
def test_signup():
    response = client.post("/api/auth/signup", json={
        "email": "test@example.com",
        "password": "password123",
        "name": "Test User"
    })
    assert response.status_code == 201
    assert "token" in response.json()

# Backend: test_projects.py
def test_create_project():
    response = client.post("/api/projects",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "project_name": "Test Project",
            "project_type": "storytelling"
        }
    )
    assert response.status_code == 201
```

### Integration Tests

```python
def test_full_story_flow():
    # 1. Create user
    # 2. Create project
    # 3. Add character
    # 4. Create scene
    # 5. Generate prompt
    # 6. Verify character consistency
```

### Frontend Tests

```javascript
// useAuth.test.js
test("login sets user and token", async () => {
  const { result } = renderHook(() => useAuth());

  await act(async () => {
    await result.current.login("test@example.com", "password");
  });

  expect(result.current.user).toBeDefined();
  expect(result.current.token).toBeDefined();
});
```

---

## 🔐 Security Best Practices

1. **Passwords**: Always hash with bcrypt (cost factor 12)
2. **API Keys**: Encrypt before storing in database
3. **JWT**: Set reasonable expiration (24 hours)
4. **CORS**: Whitelist frontend domain only
5. **Input Validation**: Validate all user inputs
6. **Rate Limiting**: Limit API calls per user

---

## 📝 Sample Gemini Prompts

### Character Analysis

```
Analyze this character image with these 12 parameters:
1. Skin tone (exact shade)
2. Eyes (color, shape, expression)
3. Eyebrows (thickness, arch)
4. Nose (shape, size)
5. Mouth (shape, lips)
6. Facial hair (if any)
7. Face shape (oval, square, etc.)
8. Hair (color, style, length)
9. Clothing (style, colors)
10. Jewelry/accessories
11. Distinguishing marks (scars, tattoos, tilak, bindi)
12. Body build (slim, muscular, average)

Also detect the visual style: Photorealism, 3D Animation, Anime, Cartoon, etc.

Provide a comprehensive description suitable for video generation.
```

### Script Breaking

```
Break this story into optimal 8-second video scenes.

STORY:
[User's full script]

REQUIREMENTS:
1. Each scene must be exactly 8 seconds
2. Identify all characters in each scene
3. Extract dialogue if present
4. Describe the main action/emotion
5. Maintain narrative continuity
6. Label scene type: dialogue, action, scene_change

OUTPUT FORMAT (JSON only, no markdown):
{
  "total_scenes": 5,
  "scenes": [
    {
      "scene_number": 1,
      "duration": 8,
      "description": "Brief scene description",
      "characters": ["Character1", "Character2"],
      "dialogue": "Exact dialogue if present",
      "emotion": "primary emotion",
      "scene_type": "dialogue"
    }
  ]
}
```

### Prompt Generation

```
Generate an 8-second Veo video prompt.

CHARACTER (MAINTAIN EXACT APPEARANCE):
- Name: Emperor Ashoka
- Base: Medium skin tone, sharp jawline, deep-set brown eyes, strong nose, medium build
- Voice: Deep male, authoritative tone

SCENE-SPECIFIC:
- Emotion: Frustrated
- Costume: Battle armor
- Dialogue: "Why did we fight this war?"
- Action: Pacing back and forth in throne room

STORY CONTEXT:
[Previous scenes summary]

VISUAL STYLE: Cinematic Photorealism
DURATION: 8 seconds

Generate a complete Veo-ready prompt that maintains character appearance exactly while showing the specified emotion and costume.
```

---

## ❗ Critical Implementation Notes

### Character Consistency Algorithm

```python
def ensure_character_consistency(base_description, scene_overrides):
    """
    Combine unchangeable base traits with scene-specific changes
    """
    return {
        "face": base_description["face"],      # NEVER CHANGE
        "body": base_description["body"],      # NEVER CHANGE
        "voice": base_description["voice"],    # NEVER CHANGE
        "emotion": scene_overrides["emotion"], # CAN CHANGE
        "costume": scene_overrides["costume"]  # CAN CHANGE
    }
```

### Scene Navigation Logic

```javascript
// Frontend state management
const [scenes, setScenes] = useState([]);
const [currentSceneIndex, setCurrentSceneIndex] = useState(0);

const nextScene = () => {
  if (currentSceneIndex < scenes.length - 1) {
    setCurrentSceneIndex(currentSceneIndex + 1);
  }
};

const prevScene = () => {
  if (currentSceneIndex > 0) {
    setCurrentSceneIndex(currentSceneIndex - 1);
  }
};

const currentScene = scenes[currentSceneIndex];
```

### Error Handling Pattern

```python
@app.post("/api/gemini/generate-prompt")
async def generate_prompt(request: PromptRequest):
    try:
        # Validate input
        if not request.scene_description:
            raise HTTPException(400, "Scene description required")

        # Call Gemini
        result = await gemini_service.generate(request)

        return {"prompt": result}

    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        logger.error(f"Prompt generation failed: {e}")
        raise HTTPException(500, "AI service error")
```

---

## 🎓 Key Takeaways

1. **Characters at Project Level**: Store once, use everywhere
2. **Scenes as Separate Documents**: Easy to query, update, delete
3. **Two-Level Consistency**: Base traits (constant) + Scene overrides (variable)
4. **Gemini Only**: Simplify user experience with one API key
5. **Scene Breaking**: AI-powered script analysis saves time
6. **Story Context**: Maintain narrative continuity across scenes

---

## 🚦 Ready to Start?

Follow this checklist:

- [ ] Read this entire document
- [ ] Understand database schema
- [ ] Review API endpoints
- [ ] Set up development environment
- [ ] Follow 10-day sprint plan
- [ ] Test each feature as you build
- [ ] Deploy and celebrate! 🎉

---

**Last Updated**: 2024-01-15  
**Version**: 1.0  
**Questions?** Review the "Common Doubts & Solutions" section above.
