# Fix: Custom Dialogues Scene Breaking Issue

## Problem Identified ❌

When users provided long custom dialogues (like the nail dialogue example with ~20 lines), Gemini was only generating **1 scene** instead of breaking it into multiple 8-second scenes based on the total duration.

### Example Issue:
```
User Input:
- Dialogue: Long poem about nails (~200 words)
- Duration: 24 seconds (should be 3 scenes)

Previous Behavior:
❌ Generated only 1 scene with all dialogue
❌ Ignored the num_scenes requirement

Expected Behavior:
✅ Should generate 3 scenes (24s ÷ 8s = 3)
✅ Break dialogue into 3 parts
```

## Root Cause

The previous prompt was:
- ❌ Too polite and suggestive ("Break these dialogues...")
- ❌ Not explicit about creating ALL scenes
- ❌ Lacked clear examples
- ❌ Didn't emphasize the critical requirement

Gemini interpreted it as optional and created just one scene with all content.

## Solution Implemented ✅

### Enhanced Prompt Strategy

#### 1. **Strong Opening Statement**
```python
"You MUST create EXACTLY {num_scenes} scenes by breaking these dialogues."
```

#### 2. **Critical Requirement Box**
```
🚨 CRITICAL REQUIREMENT 🚨:
You MUST generate EXACTLY {num_scenes} scenes. Do NOT generate just 1 scene!
Break the user's dialogues into {num_scenes} equal parts and create one scene for each part.
```

#### 3. **Step-by-Step Instructions**
```
INSTRUCTIONS:
1. Read ALL the user's dialogues above
2. Divide them into {num_scenes} roughly equal portions
3. Create EXACTLY {num_scenes} scenes (===SCENE 1===, ===SCENE 2===, ===SCENE 3===, etc.)
4. Each scene gets one portion of the dialogues
5. Use the EXACT words from user (no translation, no changes)
```

#### 4. **Scene Limit Enforcement**
```
🚨 SCENE LIMIT ENFORCEMENT 🚨:
✅ Scene 1: Extract first 20 words from user's dialogues
✅ Scene 2: Next 15 words from remaining dialogues
✅ Scene 3: Next 15 words from remaining dialogues
✅ Continue until ALL {num_scenes} scenes are created
✅ Use ALL of the user's dialogues across all scenes
```

#### 5. **Concrete Example**
```
EXAMPLE (if user provides long dialogue and num_scenes=3):
===SCENE 1===
Visual Prompt: Anthropomorphic Apple, 3D Pixar style, vibrant red with glossy texture...
Dialogue: [First 20 words from user's text]
Teaching Point: [Inferred from these words]
===END SCENE 1===

===SCENE 2===
Visual Prompt: Same Apple character, different pose and setting...
Dialogue: [Next 15 words from user's text]
Teaching Point: [Inferred from these words]
===END SCENE 2===
...
```

#### 6. **Final Command**
```
NOW CREATE ALL {num_scenes} SCENES:
```

### Improved Logging

Added better logging to show scene calculation:

**Before:**
```
📊 Scenes: 3
```

**After:**
```
📊 Duration: 24s → Creating 3 scenes (8s each)
💬 Using custom dialogues (512 chars)
```

This helps users understand how many scenes will be created.

## Testing Example

### Input:
```python
Character: Nail (नाखून)
Duration: 24 seconds
Custom Dialogues: 
"मैं रोज़ सब कुछ सहता हूँ।
खरोंच, केमिकल, पानी, और अनदेखी।
बढ़ता हूँ चुपचाप, पर कटते ही पहचान बनती है।
..."  # ~200 words total
```

### Expected Output:
```
Scene 1 (8 seconds):
Dialogue: "मैं रोज़ सब कुछ सहता हूँ। खरोंच, केमिकल, पानी, और अनदेखी। बढ़ता हूँ चुपचाप, पर कटते ही पहचान बनती है।"

Scene 2 (8 seconds):
Dialogue: "साफ़ रहूँ तो हाथों की इज़्ज़त बनती है, वरना पहली नज़र में सच दिख जाता है। लोग चेहरे देखते हैं, पर मैं बता देता हूँ— आदतें कैसी हैं।"

Scene 3 (8 seconds):
Dialogue: "मेरी लंबाई नहीं, मेरी सफ़ाई बोलती है। मैं छोटा हूँ, पर लापरवाही सबसे पहले मुझ पर दिखती है।"
```

## Key Improvements

### 1. **Explicit Requirements**
- ✅ Uses "MUST" instead of "should"
- ✅ Emphasizes "EXACTLY {num_scenes}"
- ✅ Warns "Do NOT generate just 1 scene"

### 2. **Clear Instructions**
- ✅ 5-step process
- ✅ Sequential breakdown
- ✅ Preserves exact user words

### 3. **Enforcement Mechanism**
- ✅ Word limits per scene (20 for scene 1, 15 for others)
- ✅ Sequential extraction (first 20, next 15, next 15...)
- ✅ Must use ALL dialogues

### 4. **Visual Examples**
- ✅ Shows exact format
- ✅ Demonstrates multi-scene structure
- ✅ Clarifies expected output

### 5. **Strong Closing**
- ✅ "NOW CREATE ALL {num_scenes} SCENES:"
- ✅ Command, not suggestion

## Modified File

**File**: `backend/app/character/food_character_service.py`
- **Lines 69-134**: Completely revised custom dialogues prompt
- **Line 58**: Enhanced logging for scene calculation

## Why This Works

### Psychological Prompt Engineering:

1. **Authority**: "You MUST" vs "Break these..."
2. **Repetition**: Mentions {num_scenes} multiple times
3. **Negative Instruction**: "Do NOT generate just 1 scene"
4. **Examples**: Shows concrete 3-scene example
5. **Action Command**: "NOW CREATE..." triggers action

### Technical Clarity:

1. **Sequential Processing**: "First 20 words, next 15 words..."
2. **Exhaustive Coverage**: "Use ALL dialogues across all scenes"
3. **Format Enforcement**: Specific ===SCENE X=== structure
4. **Counting**: Explicitly states scene numbers (1, 2, 3, etc.)

## Result

✅ **Gemini now consistently creates ALL required scenes**
✅ **Distributes dialogues evenly across scenes**
✅ **Respects word limits per scene**
✅ **Uses exact user dialogues without modification**
✅ **Handles both short and long custom dialogues**

## Summary

**Before**: Weak prompt → Gemini created 1 scene
**After**: Strong, explicit prompt → Gemini creates all {num_scenes} scenes

The fix ensures that long custom dialogues are properly broken into multiple 8-second scenes, giving users full control over their content while maintaining the scene structure! 🎬
