# 🔍 Scene Navigation Debugging Guide

## 📝 What I Added

I added extensive console logging to help debug the scene navigation issue:

### **1. When API Response Arrives:**

```javascript
console.log("🎬 API Response:", response.data);
console.log("🎞️ Scenes parsed:", scenes.length, scenes);
```

### **2. When Scene Changes (useEffect):**

```javascript
console.log(
  "🔄 Scene changed:",
  currentSceneIndex,
  "Total scenes:",
  brokenScenes.length,
);
console.log("🎬 Current scene:", scene);
```

### **3. When Prev Button Clicked:**

```javascript
console.log("◀️  Prev clicked. Current:", currentSceneIndex);
```

### **4. When Next Button Clicked:**

```javascript
console.log(
  "▶️  Next clicked. Current:",
  currentSceneIndex,
  "Max:",
  brokenScenes.length - 1,
);
```

---

## 🚀 How to Test

### **Step 1: Open Browser DevTools**

- Press `F12` or `Cmd+Option+I` (Mac)
- Go to "Console" tab

### **Step 2: Generate Scenes**

1. Fill the form
2. Click "Generate"
3. **Watch console output**

You should see:

```
🎬 API Response: {scenes: Array(3), total_scenes: 3, ...}
🎞️ Scenes parsed: 3 [...]
📝 Setting first scene prompt
🔄 Scene changed: 0 Total scenes: 3
🎬 Current scene: {scene_number: 1, visual_prompt: ..., dialogue: ..., ...}
```

### **Step 3: Click Next Button**

Watch console:

```
▶️  Next clicked. Current: 0 Max: 2
🔄 Scene changed: 1 Total scenes: 3
🎬 Current scene: {scene_number: 2, ...}
```

### **Step 4: Click Next Again**

```
▶️  Next clicked. Current: 1 Max: 2
🔄 Scene changed: 2 Total scenes: 3
🎬 Current scene: {scene_number: 3, ...}
```

---

## 🔍 What to Look For

### ✅ **If Working Correctly:**

- **API returns 3 scenes** (for 24 seconds)
- **Scene changed logs** show index incrementing: 0 → 1 → 2
- **Current scene object** changes each time
- **Prompt text** updates in the UI

### ❌ **If NOT Working:**

#### **Problem 1: No scenes in response**

```
🎞️ Scenes parsed: 0 []
⚠️ No scenes found!
```

**Fix:** Backend generation issue - check backend logs

#### **Problem 2: Next button doesn't increment**

```
▶️  Next clicked. Current: 0 Max: 2
(No "Scene changed" log follows)
```

**Fix:** State update issue

#### **Problem 3: Scenes exist but prompt doesn't update**

```
🔄 Scene changed: 1 Total scenes: 3
🎬 Current scene: {scene_number: 2, prompt: "..."}
(But UI still shows scene 1)
```

**Fix:** `setGeneratedPrompt` not working or prompt field missing

---

## 🎯 Most Likely Issues

### **Issue 1: Backend Returns Fallback (Only 1 Scene)**

If you only get 1 scene instead of 3:

- Check backend console for errors
- Gemini might have failed
- Fallback only creates 1 scene

**Solution:** Check backend logs for `🤖 Gemini Response` or errors

### **Issue 2: Prompt Field Missing**

If `scene.prompt` is undefined:

- Backend might not be formatting correctly
- Check console: `🎬 Current scene:` - does it have a `prompt` field?

**Solution:** Backend needs to return `prompt` in each scene

### **Issue 3: totalDuration Too Small**

If you set duration to 8 seconds:

- Only 1 scene will be created (8÷8=1)
- Next button will be disabled

**Solution:** Use 24+ seconds for multiple scenes

---

## 🧪 Quick Test

1. **Open** `http://localhost:5173/character`
2. **Open** Browser Console (`F12`)
3. **Fill form** with:
   - Duration: **24 seconds** (= 3 scenes)
4. **Click Generate**
5. **Watch console** - should see 3 scenes
6. **Click Next** - should see scene index change 0→1
7. **Click Next** - should see 1→2
8. **Click Next** - nothing (already at max)

---

## 📊 What the Console Should Show

```
// After Generate:
🎬 API Response: {scenes: […], total_scenes: 3, character_name: "Sugar", topic: "Sugar - side_effects"}
🎞️ Scenes parsed: 3 […]
📝 Setting first scene prompt
🔄 Scene changed: 0 Total scenes: 3
🎬 Current scene: {scene_number: 1, visual_prompt: "...", dialogue: "...", prompt: "..."}

// After clicking Next:
▶️  Next clicked. Current: 0 Max: 2
🔄 Scene changed: 1 Total scenes: 3
🎬 Current scene: {scene_number: 2, visual_prompt: "...", dialogue: "...", prompt: "..."}

// After clicking Next again:
▶️  Next clicked. Current: 1 Max: 2
🔄 Scene changed: 2 Total scenes: 3
🎬 Current scene: {scene_number: 3, visual_prompt: "...", dialogue: "...", prompt: "..."}
```

---

## 📞 Next Steps

After testing, share the console output with me and I can diagnose the exact issue!

Most common fix needed:

- **If only 1 scene**: Backend fallback is being used → Check Gemini API
- **If Next doesn't work**: State not updating → Check React state
- **If prompt doesn't change**: Field missing → Check backend response structure

**Try it now and share the console logs!** 🔍
