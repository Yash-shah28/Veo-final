import { useParams, useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import { useAuth } from "../auth/useAuth";
import api from "../api/client";
import Navbar from "../components/Navbar";

export default function CharacterPage() {
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
                subtitle="Talking Character Mode"
                showBackButton={true}
                backPath="/dashboard"
            />

            {/* Main Content */}
            <main className="max-w-7xl mx-auto px-6 py-8">
                <div className="bg-gradient-to-b from-slate-900/90 to-slate-950/90 backdrop-blur-xl border border-slate-800/50 rounded-2xl p-8">
                    <div className="text-center py-20">
                        <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-gradient-to-br from-purple-600 to-indigo-600 mb-6 shadow-lg shadow-purple-600/50">
                            <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                            </svg>
                        </div>

                        <h2 className="text-3xl font-bold mb-3">Talking Character Workspace</h2>
                        <p className="text-slate-400 mb-8 max-w-2xl mx-auto">
                            Create engaging videos with talking characters. Perfect for educational content,
                            health tips, and fun character-based videos.
                        </p>

                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
                            <div className="p-6 bg-slate-800/30 rounded-xl border border-slate-700/50">
                                <div className="w-12 h-12 rounded-full bg-purple-600/20 flex items-center justify-center mb-4 mx-auto">
                                    <span className="text-2xl">🥕</span>
                                </div>
                                <h3 className="font-semibold mb-2">Character Selection</h3>
                                <p className="text-sm text-slate-400">Choose from fruits, vegetables, and more</p>
                            </div>

                            <div className="p-6 bg-slate-800/30 rounded-xl border border-slate-700/50">
                                <div className="w-12 h-12 rounded-full bg-purple-600/20 flex items-center justify-center mb-4 mx-auto">
                                    <span className="text-2xl">💬</span>
                                </div>
                                <h3 className="font-semibold mb-2">Topic Selection</h3>
                                <p className="text-sm text-slate-400">Benefits or side effects mode</p>
                            </div>

                            <div className="p-6 bg-slate-800/30 rounded-xl border border-slate-700/50">
                                <div className="w-12 h-12 rounded-full bg-purple-600/20 flex items-center justify-center mb-4 mx-auto">
                                    <span className="text-2xl">🌍</span>
                                </div>
                                <h3 className="font-semibold mb-2">Language Support</h3>
                                <p className="text-sm text-slate-400">Generate in Hindi or English</p>
                            </div>
                        </div>

                        <div className="mt-8">
                            <p className="text-sm text-slate-500">Coming soon: Full talking character workspace</p>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
}
