import { useNavigate } from "react-router-dom";
import { useAuth } from "../auth/useAuth";

export default function Navbar({ title, subtitle, showBackButton = false, backPath = "/dashboard" }) {
    const navigate = useNavigate();
    const { user, logout } = useAuth();

    const handleLogout = () => {
        logout();
        navigate("/login");
    };

    const handleBack = () => {
        navigate(backPath);
    };

    return (
        <header className="bg-slate-900/50 backdrop-blur-xl border-b border-slate-800/50 sticky top-0 z-40">
            <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
                <div className="flex items-center space-x-3">
                    {showBackButton && (
                        <button
                            onClick={handleBack}
                            className="p-2 hover:bg-slate-800/50 rounded-lg transition-colors"
                            aria-label="Go back"
                        >
                            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                            </svg>
                        </button>
                    )}

                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-purple-600/50">
                        <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                        </svg>
                    </div>

                    <div>
                        <h1 className="text-xl font-bold bg-gradient-to-r from-purple-400 to-indigo-400 bg-clip-text text-transparent">
                            {title || "Veo Studio"}
                        </h1>
                        {subtitle && (
                            <p className="text-xs text-slate-400">{subtitle}</p>
                        )}
                    </div>
                </div>

                <div className="flex items-center space-x-4">
                    <div className="text-right hidden md:block">
                        <p className="text-sm font-medium text-slate-200">{user?.name || "User"}</p>
                        <p className="text-xs text-slate-400">{user?.email}</p>
                    </div>
                    <button
                        onClick={handleLogout}
                        className="px-4 py-2 bg-slate-800/50 hover:bg-slate-700/50 rounded-lg transition-colors duration-300 text-sm font-medium border border-slate-700/50"
                    >
                        Logout
                    </button>
                </div>
            </div>
        </header>
    );
}
