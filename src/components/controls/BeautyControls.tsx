import React from 'react';
import { Sparkles, Sun, Smile, Eye, Zap, RotateCcw } from 'lucide-react';
import { useStudioStore } from '../../store/useStudioStore';

export const BeautyControls: React.FC = () => {
  const { 
    smoothness, 
    brightness, 
    sharpness, 
    eyeEnhance, 
    isProcessing,
    setSmoothness, 
    setBrightness, 
    setSharpness, 
    setEyeEnhance,
    triggerAutoFix,
    resetToDefault
  } = useStudioStore();

  return (
    <div className="w-80 bg-slate-900 border-l border-slate-800 p-5 flex flex-col justify-between h-full text-slate-200">
      <div className="space-y-6">
        {/* Header & Main Auto Fix Button */}
        <div>
          <h2 className="text-lg font-bold text-white mb-1 flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-amber-400" />
            <span>Beauty Retouch</span>
          </h2>
          <p className="text-xs text-slate-400 mb-4">កែសម្រួលផ្ទៃមុខ និងពន្លឺដោយស្វ័យប្រវត្តិ</p>
          
          <button
            onClick={triggerAutoFix}
            disabled={isProcessing}
            className="w-full py-3 px-4 bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-white font-bold rounded-xl shadow-lg shadow-emerald-950/50 flex items-center justify-center gap-2 transition-all active:scale-95 disabled:opacity-50"
          >
            <Zap className="w-5 h-5 text-amber-300 fill-amber-300" />
            <span>{isProcessing ? 'Processing...' : '✨ AUTO FIX'}</span>
          </button>
        </div>

        <hr className="border-slate-800" />

        {/* Sliders Group */}
        <div className="space-y-5">
          {/* 1. Skin Smoothness Slider */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs font-semibold">
              <span className="flex items-center gap-1.5 text-slate-300">
                <Smile className="w-4 h-4 text-emerald-400" />
                <span>រលោងស្បែក (Skin Smoothness)</span>
              </span>
              <span className="text-emerald-400">{Math.round(smoothness * 100)}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={smoothness}
              onChange={(e) => setSmoothness(parseFloat(e.target.value))}
              className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-emerald-500"
            />
          </div>

          {/* 2. Face Lighting / Brightness */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs font-semibold">
              <span className="flex items-center gap-1.5 text-slate-300">
                <Sun className="w-4 h-4 text-amber-400" />
                <span>ពន្លឺផ្ទៃមុខ (Face Light)</span>
              </span>
              <span className="text-amber-400">{Math.round(brightness * 100)}%</span>
            </div>
            <input
              type="range"
              min="-0.5"
              max="0.5"
              step="0.05"
              value={brightness}
              onChange={(e) => setBrightness(parseFloat(e.target.value))}
              className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-amber-500"
            />
          </div>

          {/* 3. Eye Enhancement */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs font-semibold">
              <span className="flex items-center gap-1.5 text-slate-300">
                <Eye className="w-4 h-4 text-cyan-400" />
                <span>បង្កើនពន្លឺភ្នែក (Eye Enhance)</span>
              </span>
              <span className="text-cyan-400">{Math.round(eyeEnhance * 100)}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={eyeEnhance}
              onChange={(e) => setEyeEnhance(parseFloat(e.target.value))}
              className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-500"
            />
          </div>
        </div>
      </div>

      {/* Footer Actions */}
      <div className="pt-4 border-t border-slate-800">
        <button
          onClick={resetToDefault}
          className="w-full py-2 px-3 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium rounded-lg flex items-center justify-center gap-2 transition-colors"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          <span>Reset Default Settings</span>
        </button>
      </div>
    </div>
  );
};