import { create } from 'zustand';

interface StudioState {
  smoothness: number;
  brightness: number;
  sharpness: number;
  eyeEnhance: number;
  isProcessing: boolean;
  setSmoothness: (val: number) => void;
  setBrightness: (val: number) => void;
  setSharpness: (val: number) => void;
  setEyeEnhance: (val: number) => void;
  triggerAutoFix: () => void;
  resetToDefault: () => void;
}

export const useStudioStore = create<StudioState>((set) => ({
  smoothness: 0.35,
  brightness: 0.1,
  sharpness: 0.15,
  eyeEnhance: 0.2,
  isProcessing: false,
  setSmoothness: (smoothness) => set({ smoothness }),
  setBrightness: (brightness) => set({ brightness }),
  setSharpness: (sharpness) => set({ sharpness }),
  setEyeEnhance: (eyeEnhance) => set({ eyeEnhance }),
  triggerAutoFix: () => {
    set({
      smoothness: 0.5,
      brightness: 0.15,
      sharpness: 0.2,
      eyeEnhance: 0.3,
    });
  },
  resetToDefault: () => {
    set({
      smoothness: 0.0,
      brightness: 0.0,
      sharpness: 0.0,
      eyeEnhance: 0.0,
    });
  },
}));