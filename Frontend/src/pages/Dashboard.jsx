import { useState, useEffect } from "react";
import { useAuth } from "../auth/useAuth";
import { useNavigate } from "react-router-dom";
import api from "../api/client";
import Navbar from "../components/Navbar";

export default function Dashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [showNewProjectModal, setShowNewProjectModal] = useState(false);
  const [newProject, setNewProject] = useState({
    name: "",
    videoType: ""
  });
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [creating, setCreating] = useState(false);

  const videoTypes = [
    { value: "storytelling", label: "Story Telling" },
    { value: "character", label: "Talking Character" },
    { value: "ugc", label: "UGC/Advertisement (Coming Soon)", disabled: true }
  ];

  // Fetch projects on component mount
  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      setLoading(true);
      const response = await api.get("/projects");
      setProjects(response.data);
      setError("");
    } catch (err) {
      console.error("Failed to fetch projects:", err);
      setError("Failed to load projects. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProject = async () => {
    if (!newProject.name || !newProject.videoType) return;

    setCreating(true);
    try {
      const response = await api.post("/projects", {
        project_name: newProject.name,
        project_type: newProject.videoType
      });

      // Add new project to the list
      setProjects([response.data, ...projects]);
      setShowNewProjectModal(false);
      setNewProject({ name: "", videoType: "" });
      setError("");

      // Navigate to appropriate page based on project type
      const projectId = response.data._id;
      if (response.data.project_type === "storytelling") {
        navigate(`/project/${projectId}/storytelling`);
      } else if (response.data.project_type === "character") {
        navigate(`/project/${projectId}/character`);
      }
    } catch (err) {
      console.error("Failed to create project:", err);
      setError(err.response?.data?.detail || "Failed to create project. Please try again.");
    } finally {
      setCreating(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const handleOpenProject = (project) => {
    const projectId = project._id;
    if (project.project_type === "storytelling") {
      navigate(`/project/${projectId}/storytelling`);
    } else if (project.project_type === "character") {
      navigate(`/project/${projectId}/character`);
    }
  };

  // Format date
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
  };

  // Get display label for project type
  const getProjectTypeLabel = (type) => {
    const typeMap = {
      "storytelling": "Story Telling",
      "character": "Talking Character",
      "ugc": "UGC/Advertisement"
    };
    return typeMap[type] || type;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950 text-white">
      {/* Navbar */}
      <Navbar title="Veo Studio" subtitle="Video Creation Platform" />

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Page Header */}
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-bold mb-2">My Projects</h2>
            <p className="text-slate-400">Create and manage your video projects</p>
          </div>

          <button
            onClick={() => setShowNewProjectModal(true)}
            className="px-6 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 rounded-xl font-semibold transition-all duration-300 transform hover:scale-105 active:scale-95 shadow-lg shadow-purple-600/30 flex items-center space-x-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            <span>New Project</span>
          </button>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-500/10 border border-red-500/50 rounded-xl text-red-400 text-sm">
            {error}
          </div>
        )}

        {/* Loading State */}
        {loading ? (
          <div className="text-center py-20">
            <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-slate-800/50 mb-4">
              <svg className="animate-spin h-10 w-10 text-purple-500" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </div>
            <p className="text-slate-400">Loading projects...</p>
          </div>
        ) : projects.length === 0 ? (
          <div className="text-center py-20">
            <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-slate-800/50 mb-4">
              <svg className="w-10 h-10 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold mb-2 text-slate-300">No projects yet</h3>
            <p className="text-slate-500 mb-6">Get started by creating your first video project</p>
            <button
              onClick={() => setShowNewProjectModal(true)}
              className="px-6 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 rounded-xl font-semibold transition-all duration-300 transform hover:scale-105 active:scale-95 shadow-lg shadow-purple-600/30"
            >
              Create New Project
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {projects.map((project) => (
              <div
                key={project._id}
                className="group bg-gradient-to-b from-slate-900/90 to-slate-950/90 backdrop-blur-xl border border-slate-800/50 rounded-xl overflow-hidden hover:shadow-xl hover:shadow-purple-900/20 transition-all duration-300 cursor-pointer transform hover:scale-[1.02]"
              >
                <div className="aspect-video bg-gradient-to-br from-purple-600/20 to-indigo-600/20 flex items-center justify-center relative overflow-hidden">
                  <div className="absolute inset-0 bg-gradient-to-t from-slate-900 to-transparent opacity-60"></div>
                  <svg className="w-16 h-16 text-purple-300 relative z-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div className="p-5">
                  <h3 className="text-lg font-semibold mb-1 text-white truncate">{project.project_name}</h3>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-purple-400 font-medium">{getProjectTypeLabel(project.project_type)}</span>
                    <span className="text-slate-500">{formatDate(project.created_at)}</span>
                  </div>
                  <button
                    onClick={() => handleOpenProject(project)}
                    className="mt-4 w-full py-2 bg-slate-800/50 hover:bg-purple-600 rounded-lg transition-all duration-300 text-sm font-medium border border-slate-700/50 hover:border-purple-500"
                  >
                    Open Project
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      {/* New Project Modal */}
      {showNewProjectModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-fadeIn">
          <div className="bg-gradient-to-b from-slate-900 to-slate-950 border border-slate-800/50 rounded-2xl max-w-lg w-full p-8 shadow-2xl transform animate-scaleIn">
            {/* Modal Header */}
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-indigo-400 bg-clip-text text-transparent">
                  Create New Project
                </h3>
                <p className="text-slate-400 text-sm mt-1">Start your video creation journey</p>
              </div>
              <button
                onClick={() => setShowNewProjectModal(false)}
                className="text-slate-400 hover:text-white transition-colors duration-300"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Modal Body */}
            <div className="space-y-5">
              {/* Project Name */}
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Project Name
                </label>
                <input
                  type="text"
                  value={newProject.name}
                  onChange={(e) => setNewProject({ ...newProject, name: e.target.value })}
                  className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700/50 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-purple-600 focus:border-transparent transition-all duration-300"
                  placeholder="e.g., Summer Vacation Video"
                />
              </div>

              {/* Video Type */}
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Video Type
                </label>
                <select
                  value={newProject.videoType}
                  onChange={(e) => setNewProject({ ...newProject, videoType: e.target.value })}
                  className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700/50 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-purple-600 focus:border-transparent transition-all duration-300 cursor-pointer"
                >
                  <option value="" className="bg-slate-900">Select video type...</option>
                  {videoTypes.map((type) => (
                    <option
                      key={type.value}
                      value={type.value}
                      disabled={type.disabled}
                      className="bg-slate-900"
                    >
                      {type.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Modal Footer */}
            <div className="flex items-center space-x-3 mt-8">
              <button
                onClick={() => setShowNewProjectModal(false)}
                disabled={creating}
                className="flex-1 px-4 py-3 bg-slate-800/50 hover:bg-slate-700/50 rounded-xl font-semibold transition-all duration-300 border border-slate-700/50 disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                onClick={handleCreateProject}
                disabled={!newProject.name || !newProject.videoType || creating}
                className="flex-1 px-4 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 rounded-xl font-semibold transition-all duration-300 transform hover:scale-105 active:scale-95 shadow-lg shadow-purple-600/30 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
              >
                {creating ? (
                  <div className="flex items-center justify-center">
                    <svg className="animate-spin h-5 w-5 mr-2" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Creating...
                  </div>
                ) : (
                  "Create Project"
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Custom Animations */}
      <style>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
          }
          to {
            opacity: 1;
          }
        }

        @keyframes scaleIn {
          from {
            opacity: 0;
            transform: scale(0.95);
          }
          to {
            opacity: 1;
            transform: scale(1);
          }
        }

        .animate-fadeIn {
          animation: fadeIn 0.2s ease-out;
        }

        .animate-scaleIn {
          animation: scaleIn 0.3s ease-out;
        }
      `}</style>
    </div>
  );
}

