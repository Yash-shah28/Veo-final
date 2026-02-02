import { useSceneStore } from "./sceneStore";

export default function SceneMemory() {
  const { scenes, currentIndex, nextScene, prevScene } = useSceneStore();

  if (!scenes.length) return null;

  return (
    <div className="mt-6 p-4 bg-zinc-800 rounded border border-zinc-700 text-sm text-gray-300">
      <h3 className="text-lg font-semibold text-white mb-2">
        Scene {currentIndex + 1} of {scenes.length}
      </h3>

      <p className="text-zinc-400 mb-4">
        {scenes[currentIndex]?.description || "No description available"}
      </p>

      <div className="flex justify-between">
        <button
          onClick={prevScene}
          className="px-3 py-1 bg-zinc-700 rounded disabled:opacity-40 hover:bg-zinc-600 transition"
          disabled={currentIndex === 0}
        >
          ◀ Prev
        </button>

        <button
          onClick={nextScene}
          className="px-3 py-1 bg-zinc-700 rounded disabled:opacity-40 hover:bg-zinc-600 transition"
          disabled={currentIndex === scenes.length - 1}
        >
          Next ▶
        </button>
      </div>
    </div>
  );
}
