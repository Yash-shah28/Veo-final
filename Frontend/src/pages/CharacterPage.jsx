import { useParams, useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import { useAuth } from "../auth/useAuth";
import api from "../api/client";
import Navbar from "../components/Navbar";

// 🎤 SIMPLE VOICE OPTIONS
const VOICE_TONES = [
    { value: "child_happy", label: "👶 Child - Happy & Playful" },
    { value: "child_excited", label: "🧒 Child - Excited & Energetic" },
    { value: "male_friendly", label: "👨 Male - Friendly" },
    { value: "male_strong", label: "💪 Male - Strong & Confident" },
    { value: "female_friendly", label: "👩 Female - Friendly" },
    { value: "female_soft", label: "🌸 Female - Soft & Gentle" },
    { value: "cheerful", label: "😊 Cheerful & Upbeat" },
    { value: "calm", label: "😌 Calm & Soothing" },
    { value: "wise", label: "🧙 Wise Teacher" },
    { value: "cartoon", label: "🎭 Cartoon Character" },
    { value: "superhero", label: "🦸 Superhero" },
    { value: "narrator", label: "📻 Narrator" }
];

const VISUAL_STYLES = [
    "3D Animation (Pixar/Disney) - Best",
    "Cinematic Photorealism",
    "Cartoon Style",
    "Anime Style"
];

const DURATION_OPTIONS = [8, 16, 24, 32, 40, 48, 56];

export default function CharacterPage() {
    const navigate = useNavigate();
    const { logout } = useAuth();
    
    // Removed project state - not needed
    const [loading, setLoading] = useState(false);

    // Current scene state
    const [currentSceneIndex, setCurrentSceneIndex] = useState(0);
    const [brokenScenes, setBrokenScenes] = useState([]);

    // Form state
    const [characterName, setCharacterName] = useState("");
    const [voiceTone, setVoiceTone] = useState("child_happy");
    const [topicMode, setTopicMode] = useState("benefits");
    const [scenario, setScenario] = useState("");
    const [visualStyle, setVisualStyle] = useState("3D Animation (Pixar/Disney) - Best");
    const [language, setLanguage] = useState("hindi");
    const [totalDuration, setTotalDuration] = useState(8);

    // Generation state
    const [generating, setGenerating] = useState(false);
    const [generatedPrompt, setGeneratedPrompt] = useState("");
    const [generationError, setGenerationError] = useState("");

    useEffect(() => {
        if (brokenScenes.length > 0 && currentSceneIndex < brokenScenes.length) {
            const scene = brokenScenes[currentSceneIndex];
            setGeneratedPrompt(scene.prompt || "");
        }
    }, [currentSceneIndex, brokenScenes]);

    const handleGeneratePrompt = async () => {
        try {
            setGenerating(true);
            setGenerationError("");

            const response = await api.post(`/gemini/generate-character-dialogue`, {
                character_name: characterName,
                voice_tone: voiceTone,
                topic_mode: topicMode,
                scenario: scenario,
                visual_style: visualStyle,
                language: language,
                total_duration: totalDuration
            });

            const scenes = response.data.scenes || [];
            setBrokenScenes(scenes);
            setCurrentSceneIndex(0);
            
            if (scenes.length > 0) {
                setGeneratedPrompt(scenes[0].prompt || response.data.prompt || "");
            }
        } catch (err) {
            console.error("Failed to generate prompt:", err);
            setGenerationError(err.response?.data?.detail || "Failed to generate prompt. Please try again.");
        } finally {
            setGenerating(false);
        }
    };

    const handlePrevScene = () => {
        if (currentSceneIndex > 0) {
            setCurrentSceneIndex(currentSceneIndex - 1);
        }
    };

    const handleNextScene = () => {
        if (currentSceneIndex < brokenScenes.length - 1) {
            setCurrentSceneIndex(currentSceneIndex + 1);
        }
    };

    const handleCopyPrompt = () => {
        navigator.clipboard.writeText(generatedPrompt);
        alert("Prompt copied to clipboard!");
    };

    const handleDownloadPrompt = () => {
        const blob = new Blob([generatedPrompt], { type: "text/plain" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `${characterName}_scene_${currentSceneIndex + 1}.txt`;
        a.click();
        URL.revokeObjectURL(url);
    };

    const handleOpenVeo = () => {
        window.open("https://veo.google", "_blank");
    };

    const totalScenes = brokenScenes.length;
    const currentScene = totalScenes > 0 ? currentSceneIndex + 1 : 0;

    if (loading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950 text-white flex items-center justify-center">
                <div className="text-center">
                    <svg className="animate-spin h-12 w-12 text-purple-500 mx-auto mb-4" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <p className="text-slate-400">Loading...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950 text-white">
            <Navbar
                title="Talking Character Mode"
                subtitle="Create educational character dialogues"
                showBackButton={true}
                backPath="/dashboard"
            />

            <main className="max-w-7xl mx-auto px-6 py-8">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    {/* Left Panel: Configuration */}
                    <div className="bg-gradient-to-b from-slate-900/90 to-slate-950/90 backdrop-blur-xl border border-slate-800/50 rounded-2xl p-8">
                        <div className="flex items-center gap-3 mb-6">
                            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-purple-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-purple-600/50">
                                <span className="text-2xl">🗣️</span>
                            </div>
                            <div>
                                <h2 className="text-2xl font-bold">Talking Character</h2>
                                {totalScenes > 0 && (
                                    <p className="text-sm text-slate-400">Scene {currentScene} of {totalScenes}</p>
                                )}
                            </div>
                        </div>

                        <div className="space-y-6">
                            {/* Character Name */}
                            <div>
                                <label className="block text-sm font-medium text-slate-300 mb-2">
                                    Character Name / Type
                                </label>
                                <input
                                    type="text"
                                    value={characterName}
                                    onChange={(e) => setCharacterName(e.target.value)}
                                    placeholder="e.g. Apple, Carrot, Protein Bar"
                                    className="w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all"
                                />
                            </div>

                            {/* Voice Tone */}
                            <div>
                                <label className="block text-sm font-medium text-slate-300 mb-2">
                                    🎤 Voice Tone
                                </label>
                                <select
                                    value={voiceTone}
                                    onChange={(e) => setVoiceTone(e.target.value)}
                                    className="w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all"
                                >
                                    {VOICE_TONES.map((voice) => (
                                        <option key={voice.value} value={voice.value}>
                                            {voice.label}
                                        </option>
                                    ))}
                                </select>
                            </div>

                            {/* Topic Mode */}
                            <div>
                                <label className="block text-sm font-medium text-slate-300 mb-2">
                                    Talking Topic
                                </label>
                                <select
                                    value={topicMode}
                                    onChange={(e) => setTopicMode(e.target.value)}
                                    className="w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all"
                                >
                                    <option value="benefits">💚 Health Benefits (Why to eat me)</option>
                                    <option value="side_effects">⚠️ Side Effects</option>
                                </select>
                            </div>

                            {/* Scenario */}
                            <div>
                                <label className="block text-sm font-medium text-slate-300 mb-2">
                                    Scenario (What is happening?)
                                </label>
                                <textarea
                                    value={scenario}
                                    onChange={(e) => setScenario(e.target.value)}
                                    placeholder="e.g. He just found out he is going into a salad"
                                    className="w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all min-h-[100px] resize-y"
                                />
                            </div>

                            {/* Visual Style */}
                            <div>
                                <label className="block text-sm font-medium text-slate-300 mb-2">
                                    Visual Style
                                </label>
                                <select
                                    value={visualStyle}
                                    onChange={(e) => setVisualStyle(e.target.value)}
                                    className="w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all"
                                >
                                    {VISUAL_STYLES.map((style) => (
                                        <option key={style} value={style}>
                                            {style}
                                        </option>
                                    ))}
                                </select>
                            </div>

                            {/* Language */}
                            <div>
                                <label className="block text-sm font-medium text-slate-300 mb-2">
                                    Dialogue Language
                                </label>
                                <select
                                    value={language}
                                    onChange={(e) => setLanguage(e.target.value)}
                                    className="w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all"
                                >
                                    <option value="hindi">🇮🇳 Hindi (Default)</option>
                                    <option value="english">🇬🇧 English</option>
                                </select>
                            </div>

                            {/* Total Video Duration */}
                            <div>
                                <label className="block text-sm font-medium text-slate-300 mb-2">
                                    Total Video Duration
                                </label>
                                <select
                                    value={totalDuration}
                                    onChange={(e) => setTotalDuration(Number(e.target.value))}
                                    className="w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all"
                                >
                                    {DURATION_OPTIONS.map((duration) => (
                                        <option key={duration} value={duration}>
                                            {duration} Seconds
                                        </option>
                                    ))}
                                </select>
                                <p className="text-xs text-slate-500 mt-1">
                                    AI will break your story into 8-second scenes
                                </p>
                            </div>

                            {/* Generate Button */}
                            <button
                                onClick={handleGeneratePrompt}
                                disabled={generating || !characterName.trim()}
                                className="w-full px-6 py-4 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 rounded-xl font-semibold text-lg shadow-lg shadow-purple-600/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                            >
                                {generating ? (
                                    <>
                                        <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle>
                                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                        </svg>
                                        Generating...
                                    </>
                                ) : (
                                    <>🥕 Generate Dialogue & Break into Scenes</>
                                )}
                            </button>

                            {generationError && (
                                <div className="p-4 bg-red-500/10 border border-red-500/50 rounded-xl">
                                    <p className="text-red-400 text-sm">{generationError}</p>
                                </div>
                            )}

                            {/* Scene Navigation */}
                            {totalScenes > 0 && (
                                <div className="p-4 bg-green-500/10 border border-green-500/50 rounded-xl">
                                    <div className="flex items-center justify-between">
                                        <button
                                            onClick={handlePrevScene}
                                            disabled={currentSceneIndex === 0}
                                            className="px-4 py-2 bg-slate-800/50 hover:bg-slate-800 border border-slate-700 rounded-lg transition-all disabled:opacity-30 disabled:cursor-not-allowed"
                                        >
                                            ◀ Prev
                                        </button>
                                        <span className="text-green-400 font-bold">
                                            Scene {currentScene} of {totalScenes}
                                        </span>
                                        <button
                                            onClick={handleNextScene}
                                            disabled={currentSceneIndex === totalScenes - 1}
                                            className="px-4 py-2 bg-slate-800/50 hover:bg-slate-800 border border-slate-700 rounded-lg transition-all disabled:opacity-30 disabled:cursor-not-allowed"
                                        >
                                            Next ▶
                                        </button>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Right Panel: Output */}
                    <div className="bg-gradient-to-b from-slate-900/90 to-slate-950/90 backdrop-blur-xl border border-slate-800/50 rounded-2xl p-8">
                        <div className="flex items-center gap-3 mb-6">
                            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-green-600 to-emerald-600 flex items-center justify-center shadow-lg shadow-green-600/50">
                                <span className="text-2xl">📝</span>
                            </div>
                            <div>
                                <h2 className="text-2xl font-bold">Generated Prompt</h2>
                                <p className="text-sm text-slate-400">Veo-ready video prompt</p>
                            </div>
                        </div>

                        {generatedPrompt ? (
                            <div className="space-y-4">
                                <div className="p-6 bg-slate-800/30 border border-slate-700/50 rounded-xl min-h-[300px] max-h-[500px] overflow-y-auto">
                                    <p className="text-slate-200 whitespace-pre-wrap leading-relaxed">
                                        {generatedPrompt}
                                    </p>
                                </div>

                                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                                    <button
                                        onClick={handleCopyPrompt}
                                        className="px-4 py-3 bg-slate-800/50 hover:bg-slate-800 border border-slate-700 rounded-xl transition-all flex items-center justify-center gap-2"
                                    >
                                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                                        </svg>
                                        Copy
                                    </button>
                                    <button
                                        onClick={handleDownloadPrompt}
                                        className="px-4 py-3 bg-slate-800/50 hover:bg-slate-800 border border-slate-700 rounded-xl transition-all flex items-center justify-center gap-2"
                                    >
                                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                                        </svg>
                                        Download
                                    </button>
                                    <button
                                        onClick={handleOpenVeo}
                                        className="px-4 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 rounded-xl transition-all flex items-center justify-center gap-2 shadow-lg shadow-purple-600/30"
                                    >
                                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                                        </svg>
                                        Open Veo
                                    </button>
                                </div>
                            </div>
                        ) : (
                            <div className="flex flex-col items-center justify-center py-20 text-center">
                                <div className="w-20 h-20 rounded-full bg-slate-800/30 flex items-center justify-center mb-4">
                                    <span className="text-4xl">💬</span>
                                </div>
                                <h3 className="text-xl font-semibold text-slate-300 mb-2">
                                    Ready to Generate
                                </h3>
                                <p className="text-slate-400 max-w-md">
                                    Fill in the character details and click generate. AI will create your dialogue and break it into 8-second scenes automatically.
                                </p>
                            </div>
                        )}
                    </div>
                </div>
            </main>
        </div>
    );
}
