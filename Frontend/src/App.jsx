import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./auth/useAuth";
import Login from "./auth/Login";
import Register from "./auth/Register";
import Dashboard from "./pages/Dashboard";
import StorytellingPage from "./pages/StorytellingPage";
import CharacterPage from "./pages/CharacterPage";
import EducationalCharacterPage from "./pages/EducationalCharacterPage";


function ProtectedRoute({ children }) {
  const { user } = useAuth();
  return user ? children : <Navigate to="/login" replace />;
}

function PublicRoute({ children }) {
  const { user } = useAuth();
  return !user ? children : <Navigate to="/dashboard" replace />;
}

function AppContent() {
  return (
    <Routes>
      {/* Public routes */}
      <Route
        path="/login"
        element={
          <PublicRoute>
            <Login />
          </PublicRoute>
        }
      />
      <Route
        path="/register"
        element={
          <PublicRoute>
            <Register />
          </PublicRoute>
        }
      />

      {/* Protected routes */}
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      />

      {/* Project routes */}
      <Route
        path="/project/:projectId/storytelling"
        element={
          <ProtectedRoute>
            <StorytellingPage />
          </ProtectedRoute>
        }
      />
      
      {/* Character routes */}
      <Route
        path="/character/food"
        element={
          <ProtectedRoute>
            <CharacterPage />
          </ProtectedRoute>
        }
      />
      
      <Route
        path="/character/educational"
        element={
          <ProtectedRoute>
            <EducationalCharacterPage />
          </ProtectedRoute>
        }
      />
      
      {/* Legacy character route - redirect to food */}
      <Route
        path="/character"
        element={<Navigate to="/character/food" replace />}
      />

      {/* Default redirect */}
      <Route path="/" element={<Navigate to="/login" replace />} />
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </BrowserRouter>
  );
}

