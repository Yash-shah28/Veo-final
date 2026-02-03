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

    useEffect(() => {
        fetchProject();
    }, [projectId]);

    const fetchProject = async () => {
        try {
            setLoading(true);
            const response = await api.get(`/projects/${projectId}`);
            setProject(response.data);
            setError("");
        } catch (err) {
            console.error("Failed to fetch project:", err);
            setError("Failed to load project");
        } finally {
            setLoading(false);
        }
    };

    const handleBackToDashboard = () => {
        navigate("/dashboard");
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
                        onClick={handleBackToDashboard}
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
            {/* Navbar */}
            <Navbar
                title={project.project_name}
                subtitle="Story Telling Mode"
                showBackButton={true}
                backPath="/dashboard"
            />

            {/* Main Content */}
            <main className="max-w-7xl mx-auto px-6 py-8">
                <div className="bg-gradient-to-b from-slate-900/90 to-slate-950/90 backdrop-blur-xl border border-slate-800/50 rounded-2xl p-8">
                    <div className="text-center py-20">
                        <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-gradient-to-br from-purple-600 to-indigo-600 mb-6 shadow-lg shadow-purple-600/50">
                            <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                            </svg>
                        </div>

                        <h2 className="text-3xl font-bold mb-3">Story Telling Workspace</h2>
                        <p className="text-slate-400 mb-8 max-w-2xl mx-auto">
                            This is where you'll create multi-scene narratives with character consistency.
                            Features like script breaking, character management, and scene creation will be available here.
                        </p>

                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
                            <div className="p-6 bg-slate-800/30 rounded-xl border border-slate-700/50">
                                <div className="w-12 h-12 rounded-full bg-purple-600/20 flex items-center justify-center mb-4 mx-auto">
                                    <span className="text-2xl">📝</span>
                                </div>
                                <h3 className="font-semibold mb-2">Script Breaking</h3>
                                <p className="text-sm text-slate-400">Break your story into optimal 8-second scenes</p>
                            </div>

                            <div className="p-6 bg-slate-800/30 rounded-xl border border-slate-700/50">
                                <div className="w-12 h-12 rounded-full bg-purple-600/20 flex items-center justify-center mb-4 mx-auto">
                                    <span className="text-2xl">👥</span>
                                </div>
                                <h3 className="font-semibold mb-2">Character Manager</h3>
                                <p className="text-sm text-slate-400">Add and manage characters with consistency</p>
                            </div>

                            <div className="p-6 bg-slate-800/30 rounded-xl border border-slate-700/50">
                                <div className="w-12 h-12 rounded-full bg-purple-600/20 flex items-center justify-center mb-4 mx-auto">
                                    <span className="text-2xl">🎬</span>
                                </div>
                                <h3 className="font-semibold mb-2">Scene Creation</h3>
                                <p className="text-sm text-slate-400">Generate prompts for each scene</p>
                            </div>
                        </div>

                        <div className="mt-8">
                            <p className="text-sm text-slate-500">Coming soon: Full storytelling workspace</p>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
}
