import { AuthProvider } from './auth/useAuth';
import Dashboard from './pages/Dashboard';

function App() {
  return (
    <AuthProvider>
      <Dashboard />
    </AuthProvider>
  );
}

export default App;
