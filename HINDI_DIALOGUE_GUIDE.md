# Hindi Dialogue Format (Devanagari + English Technical Terms)

## Overview
When users select **"Hindi"** language, the system generates dialogues in **Devanagari script** (proper Hindi) with **English technical terms** that don't have good Hindi equivalents.

## Format Rules

### ✅ Write in Devanagari Script
All Hindi words should be written in Devanagari (आज, मैं, आपको, बताऊँगा, कैसे, etc.)

### ✅ Keep Technical Terms in English
Technical, modern, and brand terms should stay in English (Latin script):
- **Technical**: AI, ML, API, Cloud, Server, Database, Algorithm, Code, Query
- **Modern**: Video, Audio, Digital, Online, App, Software, Hardware
- **Business**: Meeting, Presentation, Project, Schedule, Deadline, Team
- **Abstract**: Availability, Configuration, Settings, Features, Performance
- **Numbers**: 50%, 100MB, 5 minutes, 10 seconds
- **Brands**: Google, Python, JavaScript, MySQL, AWS, React

### ✅ Mix Both Scripts Naturally
Hindi (Devanagari) + English (Latin) in the same sentence

## Correct Examples

### Example 1: AI Video Generation
```
✅ "आज मैं आपको बताऊँगा कि AI वीडियो कैसे बनाए जाते हैं।"
```
**Breakdown:**
- Devanagari: आज, मैं, आपको, बताऊँगा, कि, कैसे, बनाए, जाते, हैं
- English: AI, वीडियो (Video)

### Example 2: Database Query
```
✅ "Database में data सेव करने के लिए query लिखनी पड़ती है।"
```
**Breakdown:**
- Devanagari: में, सेव करने के लिए, लिखनी पड़ती है
- English: Database, data, query

### Example 3: Server Availability
```
✅ "सबसे पहले server की availability चेक करनी चाहिए।"
```
**Breakdown:**
- Devanagari: सबसे पहले, की, चेक करनी चाहिए
- English: server, availability

### Example 4: Algorithm Performance
```
✅ "यह algorithm बहुत तेज़ है और अच्छा performance देता है।"
```
**Breakdown:**
- Devanagari: यह, बहुत तेज़ है, और, अच्छा, देता है
- English: algorithm, performance

### Example 5: Cloud Storage
```
✅ "Cloud storage में अपनी files सुरक्षित रख सकते हैं।"
```
**Breakdown:**
- Devanagari: में, अपनी, सुरक्षित, रख सकते हैं
- English: Cloud storage, files

### Example 6: Meeting Schedule
```
✅ "Meeting schedule करने से पहले सभी की availability देख लें।"
```
**Breakdown:**
- Devanagari: करने से पहले, सभी की, देख लें
- English: Meeting, schedule, availability

### Example 7: Python Programming
```
✅ "Python में coding करने के लिए variables डिफाइन करते हैं।"
```
**Breakdown:**
- Devanagari: में, करने के लिए, डिफाइन करते हैं
- English: Python, coding, variables

## Wrong Examples

### ❌ Example 1: Using Roman Script for Hindi
```
❌ "Aaj main aapko bataunga AI videos kaise banate hain"
```
**Problem:** Hindi words in Roman script (Aaj, main, aapko) - MUST use Devanagari

**Correct:**
```
✅ "आज मैं आपको बताऊँगा AI videos कैसे बनाते हैं"
```

### ❌ Example 2: Translating Technical Terms
```
❌ "आज मैं आपको बताऊँगा कि कृत्रिम बुद्धिमत्ता वीडियो कैसे बनाए जाते हैं।"
```
**Problem:** "कृत्रिम बुद्धिमत्ता" (Artificial Intelligence) - DON'T translate "AI"

**Correct:**
```
✅ "आज मैं आपको बताऊँगा कि AI वीडियो कैसे बनाए जाते हैं।"
```

### ❌ Example 3: Over-Translation
```
❌ "डेटाबेस में आंकड़े संग्रहण करने के लिए प्रश्न लिखना पड़ता है।"
```
**Problem:** Translating Database→डेटाबेस, data→आंकड़े, query→प्रश्न

**Correct:**
```
✅ "Database में data सेव करने के लिए query लिखनी पड़ती है।"
```

## Why This Approach?

### 1. **Natural Communication**
This is how Indians actually speak when discussing technology - proper Hindi with English tech terms mixed in.

### 2. **Clarity**
Technical terms in English are universally understood and avoid confusion from literal translations.

### 3. **Professional**
Matches real-world communication in Indian tech education and industry.

### 4. **Accessibility**
Students and professionals already know these terms in English from their education.

## Common Technical Terms to Keep in English

### Programming & Development
```
- Code, Coding, Programming, Developer
- Variable, Function, Class, Object
- Array, List, Dictionary, String
- Loop, Condition, If-Else, Switch
```

### Data & Storage
```
- Database, Query, Table, Row
- Data, Storage, Backup, Cache
- Index, Schema, Migration
```

### Web & Internet
```
- Website, App, Application, Interface
- API, Endpoint, Request, Response
- Frontend, Backend, Server, Client
- URL, Link, Domain, Hosting
```

### Cloud & Infrastructure
```
- Cloud, Server, Network, Protocol
- Availability, Uptime, Downtime
- Load Balancer, CDN, DNS
```

### Modern Technology
```
- AI, ML, Deep Learning, Neural Network
- Blockchain, Cryptocurrency, NFT
- IoT, AR, VR, Metaverse
```

## Implementation Example

### User Input:
- Topic: "Database management and queries"
- Language: "Hindi"

### Expected Output:
```
Scene 1:
"आज मैं आपको Database management के बारे में बताऊँगा।"

Scene 2:
"Database में data को efficiently store करने के लिए indexing का use करते हैं।"

Scene 3:
"Query optimize करने से performance बहुत improve होती है।"
```

## Summary

**Format: Devanagari (Hindi) + English (Technical Terms)**

✅ **Do:**
- Write Hindi words in Devanagari: आज, मैं, बताऊँगा, कैसे
- Keep technical terms in English: AI, Database, Server, Cloud
- Mix both naturally in sentences
- Sound like Indian teacher/professional speaking

❌ **Don't:**
- Use Roman script for Hindi words (aaj, main, kaise)
- Translate technical terms (AI → कृत्रिम बुद्धिमत्ता)
- Use pure English or pure Hindi/Sanskrit

**This creates authentic, professional educational content in proper Hindi! 🇮🇳**
