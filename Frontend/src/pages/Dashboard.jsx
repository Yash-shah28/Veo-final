import SceneForm from '../scenes/SceneForm';
import SceneMemory from '../scenes/SceneMemory';
import CharacterForm from '../components/CharacterForm';

export default function Dashboard() {
  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <header className="mb-10">
        <h1 className="text-4xl font-extrabold bg-gradient-to-r from-purple-400 to-blue-500 bg-clip-text text-transparent">
          Project Dashboard
        </h1>
      </header>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="space-y-8">
          <CharacterForm />
          <SceneForm />
        </div>
        <div>
          <SceneMemory />
        </div>
      </div>
    </div>
  );
}
