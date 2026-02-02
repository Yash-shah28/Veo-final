import { create } from "zustand";

export const useSceneStore = create((set) => ({
  scenes: [],
  currentIndex: 0,

  setScenes: (scenes) =>
    set({
      scenes,
      currentIndex: 0, // reset on new analysis
    }),
  nextScene: () =>
    set((state) => {
      const max = state.scenes.length - 1;
      return {
        currentIndex: Math.min(state.currentIndex + 1, max),
      };
    }),

  prevScene: () =>
    set((state) => ({
      currentIndex: Math.max(state.currentIndex - 1, 0),
    })),
  clear: () => set({ scenes: [], currentIndex: 0 }),
}));
