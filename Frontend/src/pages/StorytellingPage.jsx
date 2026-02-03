import { useParams, useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import { useAuth } from "../auth/useAuth";
import api from "../api/client";
import Navbar from "../components/Navbar";

export default function StorytellingPage() {
    const { projectId } = useParams();
    const navigate = useNavigate();
    const { logout } = useAuth();
    const [project, setProject] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    // Script and Scenes state
    const [script, setScript] = useState("");
    const [scenes, setScenes] = useState([]);
    const [breakingScript, setBreakingScript] = useState(false);
    const [scriptError, setScriptError] = useState("");

    // Character state
    const [showCharacterModal, setShowCharacterModal] = useState(false);
    const [characters, setCharacters] = useState([]);
    const [newCharacter, setNewCharacter] = useState({
        role: "",
        name: "",
        description: "",
        voiceType: "",
        voiceTone: "",
        image: null
    });

    const characterRoles = ["protagonist", "antagonist", "supporting1", "supporting2", "narrator"];
    const voiceTypes = ["deep_male", "light_male", "deep_female", "light_female", "child", "elderly"];
    const voiceTones = ["authoritative", "friendly", "mysterious", "cheerful", "serious", "calm"];

    useEffect(() => {
        fetchProject();
    }, [projectId]);

    const fetchProject = async () => {
        try {
            setLoading(true);
            const response = await api.get(`/projects/${projectId}`);
            setProject(response.data);

            // Load existing characters if any
            if (response.data.characters) {
                const charArray = Object.entries(response.data.characters).map(([role, data]) => ({
                    role,
                    ...data
                }));
                setCharacters(charArray);
            }

            setError("");
        } catch (err) {
            console.error("Failed to fetch project:", err);
            setError("Failed to load project");
        } finally {
            setLoading(false);
        }
    };

    const handleBreakScript = async () => {
        if (!script.trim()) {
            setScriptError("Please enter a script to break into scenes");
            return;
        }

        setBreakingScript(true);
        setScriptError("");

        try {
            // Call backend API to break script with AI (LangChain + Gemini)
            const response = await api.post(`/projects/${projectId}/break-script`, {
                script: script
            });

            // Set scenes from AI response
            setScenes(response.data.scenes);
            setScriptError("");

            // Optional: Show success message
            console.log("Script broken successfully:", response.data.message);
        } catch (err) {
            console.error("Failed to break script:", err);
            setScriptError(
                err.response?.data?.detail ||
                "Failed to break script. Please try again."
            );
        } finally {
            setBreakingScript(false);
        }
    };

    const handleAddCharacter = () => {
        if (!newCharacter.role || !newCharacter.name) {
            alert("Please fill in role and name");
            return;
        }

        setCharacters([...characters, { ...newCharacter }]);
        setNewCharacter({
            role: "",
            name: "",
            description: "",
            voiceType: "",
            voiceTone: "",
            image: null
        });
        setShowCharacterModal(false);
    };

    const handleImageUpload = (e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onloadend = () => {
                setNewCharacter({ ...newCharacter, image: reader.result });
            };
            reader.readAsDataURL(file);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950 text-white flex items-center justify-center">
                <div className="text-center">
                    <svg className="animate-spin h-12 w-12 text-purple-500 mx-auto mb-4" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <p className="text-slate-400">Loading project...</p>
                </div>
            </div>
        );
    }

    if (error || !project) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950 text-white flex items-center justify-center">
                <div className="text-center">
                    <p className="text-red-400 mb-4">{error || "Project not found"}</p>
                    <button
                        onClick={() => navigate("/dashboard")}
                        className="px-6 py-3 bg-purple-600 hover:bg-purple-700 rounded-xl transition-all"
                    >
                        Back to Dashboard
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950 text-white">
            <Navbar
                title={project.project_name}
                subtitle="Story Telling Mode"
                showBackButton={true}
                backPath="/dashboard"
            />

            <main className="max-w-7xl mx-auto px-6 py-8">
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Left Column - Script & Characters */}
                    <div className="lg:col-span-2 space-y-6">
                        {/* Script Input Section */}
                        <div className="bg-gradient-to-b from-slate-900/90 to-slate-950/90 backdrop-blur-xl border border-slate-800/50 rounded-2xl p-6">
                            <div className="flex items-center justify-between mb-4">
                                <div className="flex items-center space-x-3">
                                    <div className="w-10 h-10 rounded-full bg-purple-600/20 flex items-center justify-center">
                                        <span className="text-xl">📝</span>
                                    </div>
                                    <div>
                                        <h2 className="text-xl font-bold">Script Input</h2>
                                        <p className="text-sm text-slate-400">Enter your story to break into scenes</p>
                                    </div>
                                </div>
                            </div>

                            <textarea
                                value={script}
                                onChange={(e) => setScript(e.target.value)}
                                placeholder="Paste your script here... AI will break it into optimal 8-second scenes for video generation."
                                className="w-full h-64 px-4 py-3 bg-slate-900/50 border border-slate-700/50 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-purple-600 focus:border-transparent resize-none"
                            />

                            {scriptError && (
                                <p className="text-red-400 text-sm mt-2">{scriptError}</p>
                            )}

                            <button
                                onClick={handleBreakScript}
                                disabled={breakingScript || !script.trim()}
                                className="mt-4 w-full px-6 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 rounded-xl font-semibold transition-all duration-300 transform hover:scale-105 active:scale-95 shadow-lg shadow-purple-600/30 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
                            >
                                {breakingScript ? (
                                    <div className="flex items-center justify-center">
                                        <svg className="animate-spin h-5 w-5 mr-2" viewBox="0 0 24 24">
                                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle>
                                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                        </svg>
                                        Breaking Script...
                                    </div>
                                ) : (
                                    <>🤖 Break Into Scenes with AI</>
                                )}
                            </button>
                        </div>

                        {/* Scenes Display */}
                        {scenes.length > 0 && (
                            <div className="bg-gradient-to-b from-slate-900/90 to-slate-950/90 backdrop-blur-xl border border-slate-800/50 rounded-2xl p-6">
                                <div className="flex items-center justify-between mb-4">
                                    <div className="flex items-center space-x-3">
                                        <div className="w-10 h-10 rounded-full bg-indigo-600/20 flex items-center justify-center">
                                            <span className="text-xl">🎬</span>
                                        </div>
                                        <div>
                                            <h2 className="text-xl font-bold">Generated Scenes</h2>
                                            <p className="text-sm text-slate-400">{scenes.length} scenes created</p>
                                        </div>
                                    </div>
                                </div>

                                <div className="space-y-3">
                                    {scenes.map((scene) => (
                                        <div
                                            key={scene.scene_number}
                                            className="p-4 bg-slate-800/30 rounded-lg border border-slate-700/50 hover:border-purple-500/50 transition-all"
                                        >
                                            <div className="flex items-start justify-between">
                                                <div className="flex-1">
                                                    <div className="flex items-center space-x-2 mb-2">
                                                        <span className="px-2 py-1 bg-purple-600/20 text-purple-300 text-xs font-semibold rounded">
                                                            Scene {scene.scene_number}
                                                        </span>
                                                        <span className="text-xs text-slate-500">{scene.duration}s</span>
                                                    </div>
                                                    <p className="text-sm text-slate-300">{scene.description}</p>
                                                    <div className="flex items-center space-x-2 mt-2">
                                                        {scene.characters.map((char, idx) => (
                                                            <span key={idx} className="text-xs px-2 py-1 bg-slate-700/50 rounded text-slate-400">
                                                                {char}
                                                            </span>
                                                        ))}
                                                    </div>
                                                </div>
                                                <button className="ml-4 p-2 hover:bg-slate-700/50 rounded transition-colors">
                                                    <svg className="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                                                    </svg>
                                                </button>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Right Column - Characters */}
                    <div className="space-y-6">
                        <div className="bg-gradient-to-b from-slate-900/90 to-slate-950/90 backdrop-blur-xl border border-slate-800/50 rounded-2xl p-6">
                            <div className="flex items-center justify-between mb-4">
                                <div className="flex items-center space-x-3">
                                    <div className="w-10 h-10 rounded-full bg-indigo-600/20 flex items-center justify-center">
                                        <span className="text-xl">👥</span>
                                    </div>
                                    <div>
                                        <h2 className="text-xl font-bold">Characters</h2>
                                        <p className="text-sm text-slate-400">{characters.length} added</p>
                                    </div>
                                </div>
                                <button
                                    onClick={() => setShowCharacterModal(true)}
                                    className="p-2 bg-purple-600 hover:bg-purple-700 rounded-lg transition-colors"
                                >
                                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                                    </svg>
                                </button>
                            </div>

                            {/* Characters List */}
                            <div className="space-y-3">
                                {characters.length === 0 ? (
                                    <div className="text-center py-8">
                                        <p className="text-slate-500 text-sm">No characters yet</p>
                                        <button
                                            onClick={() => setShowCharacterModal(true)}
                                            className="mt-3 text-purple-400 hover:text-purple-300 text-sm font-medium"
                                        >
                                            + Add Character
                                        </button>
                                    </div>
                                ) : (
                                    characters.map((char, idx) => (
                                        <div
                                            key={idx}
                                            className="p-4 bg-slate-800/30 rounded-lg border border-slate-700/50"
                                        >
                                            <div className="flex items-start space-x-3">
                                                {char.image ? (
                                                    <img src={char.image} alt={char.name} className="w-12 h-12 rounded-full object-cover" />
                                                ) : (
                                                    <div className="w-12 h-12 rounded-full bg-gradient-to-br from-purple-600 to-indigo-600 flex items-center justify-center">
                                                        <span className="text-lg font-bold">{char.name.charAt(0)}</span>
                                                    </div>
                                                )}
                                                <div className="flex-1">
                                                    <h3 className="font-semibold text-sm">{char.name}</h3>
                                                    <p className="text-xs text-purple-400 capitalize">{char.role}</p>
                                                    {char.description && (
                                                        <p className="text-xs text-slate-400 mt-1 line-clamp-2">{char.description}</p>
                                                    )}
                                                </div>
                                            </div>
                                        </div>
                                    ))
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            </main>

            {/* Add Character Modal */}
            {showCharacterModal && (
                <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                    <div className="bg-gradient-to-b from-slate-900 to-slate-950 border border-slate-800/50 rounded-2xl max-w-2xl w-full p-8 shadow-2xl max-h-[90vh] overflow-y-auto">
                        <div className="flex items-center justify-between mb-6">
                            <div>
                                <h3 className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-indigo-400 bg-clip-text text-transparent">
                                    Add Character
                                </h3>
                                <p className="text-slate-400 text-sm mt-1">Define character details for consistency</p>
                            </div>
                            <button
                                onClick={() => setShowCharacterModal(false)}
                                className="text-slate-400 hover:text-white transition-colors"
                            >
                                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                </svg>
                            </button>
                        </div>

                        <div className="space-y-5">
                            {/* Character Role */}
                            <div>
                                <label className="block text-sm font-medium text-slate-300 mb-2">Character Role</label>
                                <select
                                    value={newCharacter.role}
                                    onChange={(e) => setNewCharacter({ ...newCharacter, role: e.target.value })}
                                    className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700/50 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-purple-600 cursor-pointer"
                                >
                                    <option value="">Select role...</option>
                                    {characterRoles.map((role) => (
                                        <option key={role} value={role} className="bg-slate-900 capitalize">
                                            {role.replace(/\d/g, ' $&').trim()}
                                        </option>
                                    ))}
                                </select>
                            </div>

                            {/* Character Name */}
                            <div>
                                <label className="block text-sm font-medium text-slate-300 mb-2">Character Name</label>
                                <input
                                    type="text"
                                    value={newCharacter.name}
                                    onChange={(e) => setNewCharacter({ ...newCharacter, name: e.target.value })}
                                    className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700/50 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-purple-600"
                                    placeholder="e.g., Emperor Ashoka"
                                />
                            </div>

                            {/* Character Description */}
                            <div>
                                <label className="block text-sm font-medium text-slate-300 mb-2">
                                    Physical Description
                                    <span className="text-slate-500 text-xs ml-2">(For AI consistency)</span>
                                </label>
                                <textarea
                                    value={newCharacter.description}
                                    onChange={(e) => setNewCharacter({ ...newCharacter, description: e.target.value })}
                                    className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700/50 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-purple-600 resize-none"
                                    rows="3"
                                    placeholder="e.g., Medium skin tone, sharp jawline, deep-set brown eyes, strong nose, medium build"
                                />
                            </div>

                            {/* Voice Type & Tone */}
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-slate-300 mb-2">Voice Type</label>
                                    <select
                                        value={newCharacter.voiceType}
                                        onChange={(e) => setNewCharacter({ ...newCharacter, voiceType: e.target.value })}
                                        className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700/50 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-purple-600 cursor-pointer"
                                    >
                                        <option value="">Select...</option>
                                        {voiceTypes.map((type) => (
                                            <option key={type} value={type} className="bg-slate-900 capitalize">
                                                {type.replace(/_/g, ' ')}
                                            </option>
                                        ))}
                                    </select>
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-slate-300 mb-2">Voice Tone</label>
                                    <select
                                        value={newCharacter.voiceTone}
                                        onChange={(e) => setNewCharacter({ ...newCharacter, voiceTone: e.target.value })}
                                        className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700/50 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-purple-600 cursor-pointer"
                                    >
                                        <option value="">Select...</option>
                                        {voiceTones.map((tone) => (
                                            <option key={tone} value={tone} className="bg-slate-900 capitalize">
                                                {tone}
                                            </option>
                                        ))}
                                    </select>
                                </div>
                            </div>

                            {/* Character Image Upload */}
                            <div>
                                <label className="block text-sm font-medium text-slate-300 mb-2">
                                    Character Reference Image
                                    <span className="text-slate-500 text-xs ml-2">(Optional)</span>
                                </label>
                                <div className="flex items-center space-x-4">
                                    {newCharacter.image && (
                                        <img src={newCharacter.image} alt="Preview" className="w-20 h-20 rounded-lg object-cover" />
                                    )}
                                    <label className="flex-1 px-4 py-3 bg-slate-900/50 border border-slate-700/50 rounded-xl text-white hover:bg-slate-800/50 cursor-pointer transition-colors flex items-center justify-center">
                                        <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                        </svg>
                                        <span className="text-sm">Upload Image</span>
                                        <input
                                            type="file"
                                            accept="image/*"
                                            onChange={handleImageUpload}
                                            className="hidden"
                                        />
                                    </label>
                                </div>
                            </div>
                        </div>

                        {/* Modal Footer */}
                        <div className="flex items-center space-x-3 mt-8">
                            <button
                                onClick={() => setShowCharacterModal(false)}
                                className="flex-1 px-4 py-3 bg-slate-800/50 hover:bg-slate-700/50 rounded-xl font-semibold transition-all duration-300 border border-slate-700/50"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={handleAddCharacter}
                                disabled={!newCharacter.role || !newCharacter.name}
                                className="flex-1 px-4 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 rounded-xl font-semibold transition-all duration-300 transform hover:scale-105 active:scale-95 shadow-lg shadow-purple-600/30 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
                            >
                                Add Character
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
