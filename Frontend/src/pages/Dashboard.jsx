import SceneForm from "../scenes/SceneForm";
import SceneMemory from "../scenes/SceneMemory";

export default function Dashboard() {
  return (
    <div className="min-h-screen bg-black text-white p-8">
      <div className="max-w-4xl mx-auto space-y-8">
        <header className="mb-10 text-center">
            <h1 className="text-4xl font-extrabold bg-gradient-to-r from-purple-400 to-blue-500 bg-clip-text text-transparent">
            Project Dashboard
            </h1>
        </header>
        <SceneForm />
        <SceneMemory />
      </div>
    </div>
  );
}
