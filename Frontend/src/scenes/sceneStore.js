import { create } from 'zustand';

export const useSceneStore = create((set) => ({
  scenes: [],
  addScene: (scene) => set((state) => ({ scenes: [...state.scenes, scene] })),
  removeScene: (id) => set((state) => ({ scenes: state.scenes.filter((s) => s.id !== id) })),
}));
