import { useState } from 'react';
import { useSceneStore } from './sceneStore';

export default function SceneForm() {
  const addScene = useSceneStore((state) => state.addScene);
  const [description, setDescription] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!description.trim()) return;
    
    addScene({ id: Date.now(), description });
    setDescription('');
  };

  return (
    <form onSubmit={handleSubmit} className="p-4 bg-gray-800 rounded-lg">
      <h3 className="text-xl font-semibold mb-4 text-white">New Scene</h3>
      <textarea
        className="w-full p-3 rounded bg-gray-700 text-white border border-gray-600 focus:border-purple-500 mb-4"
        placeholder="Describe the scene..."
        value={description}
        onChange={(e) => setDescription(e.target.value)}
      />
      <button type="submit" className="px-4 py-2 bg-purple-600 hover:bg-purple-500 rounded text-white font-medium transition">
        Add Scene
      </button>
    </form>
  );
}
