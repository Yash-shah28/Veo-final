import { AuthProvider, useAuth } from "./auth/useAuth";
import Login from "./auth/Login";
import Dashboard from "./pages/Dashboard";

function AppContent() {
  const { user } = useAuth();
  return user ? <Dashboard /> : <Login />;
}

export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}
