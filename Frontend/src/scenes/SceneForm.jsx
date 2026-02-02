import { useState } from "react";
import { useSceneStore } from "./sceneStore";
import api from "../api/client";
import CharacterForm from "../components/CharacterForm";

export default function SceneForm() {
  const [sceneDescription, setSceneDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const { scenes, setScenes } = useSceneStore();

  const analyzeScript = async () => {
    if (!sceneDescription.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const res = await api.post("/scenes/analyze", {
        text: sceneDescription,
      });

      setScenes(res.data.scenes || []);
    } catch (err) {
      setError("Failed to analyze script. Try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-zinc-900 p-6 rounded-lg shadow-lg border border-zinc-800">
      <h3 className="text-xl font-semibold mb-4 text-zinc-100">Script Analysis</h3>
      <textarea
        className="w-full p-3 bg-zinc-800 text-white rounded border border-zinc-700 focus:border-purple-500 min-h-[120px] mb-4"
        placeholder="Paste your script here to analyze scenes..."
        onChange={(e) => setSceneDescription(e.target.value)}
      />
      <button 
        disabled={loading}
        className="w-full bg-purple-600 hover:bg-purple-700 disabled:opacity-50 text-white font-medium p-2 rounded transition mb-6" 
        onClick={analyzeScript}
      >
        {loading ? "Analyzing..." : "Break into Scenes"}
      </button>

      {error && <p className="text-red-400 mt-2 mb-4">{error}</p>}

      <CharacterForm />
    </div>
  );
}
