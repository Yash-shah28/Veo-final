import { useSceneStore } from './sceneStore';

export default function SceneMemory() {
  const scenes = useSceneStore((state) => state.scenes);

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold text-white mb-4">Scene Memory</h2>
      {scenes.length === 0 ? (
        <p className="text-gray-400">No scenes created yet.</p>
      ) : (
        scenes.map((scene) => (
          <div key={scene.id} className="p-4 bg-gray-800 rounded border-l-4 border-purple-500">
            <p className="text-gray-300">{scene.description}</p>
          </div>
        ))
      )}
    </div>
  );
}
