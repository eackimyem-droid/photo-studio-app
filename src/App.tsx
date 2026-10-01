import React, { useEffect } from 'react';
import { useImageProcessor } from './hooks/useImageProcessor';

export const App: React.FC = () => {
  const {
    isEngineReady,
    isProcessing,
    currentImage,
    error,
    initEngine,
    cropFace,
    applyRetouch,
    generateA4Grid,
    setCurrentImage
  } = useImageProcessor();

  // ១. ចាប់ផ្តើម Init Engine ពេល App ដើរដំបូង
  useEffect(() => {
    initEngine();
  }, [initEngine]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setCurrentImage(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleAutoCrop3x4 = async () => {
    if (!currentImage) return;
    try {
      await cropFace(currentImage, '3x4');
    } catch (err) {
      console.error('Crop Error:', err);
    }
  };

  return (
    <div className="p-6 bg-slate-950 min-h-screen text-white">
      <h1 className="text-xl font-bold mb-4">📸 Photo Studio Studio Dashboard</h1>

      {/* Engine Status Bar */}
      <div className="mb-4 flex items-center gap-3 text-sm">
        <span className={`w-3 h-3 rounded-full ${isEngineReady ? 'bg-emerald-500' : 'bg-rose-500'}`} />
        <span>Status: {isEngineReady ? 'Ready' : 'Initializing AI Engine...'}</span>
        {isProcessing && <span className="text-amber-400 font-semibold animate-pulse">⚙️ Processing Image...</span>}
      </div>

      {error && <div className="p-3 mb-4 bg-rose-900/50 border border-rose-500 text-rose-200 rounded-lg text-sm">{error}</div>}

      <div className="flex gap-4 mb-4">
        <input type="file" accept="image/*" onChange={handleFileChange} className="text-sm text-slate-300" />
        <button
          onClick={handleAutoCrop3x4}
          disabled={!currentImage || isProcessing}
          className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 rounded-lg disabled:opacity-50 font-medium text-sm"
        >
          Auto Crop 3x4
        </button>
      </div>

      {/* Canvas Preview */}
      {currentImage && (
        <div className="max-w-md border border-slate-800 rounded-xl overflow-hidden bg-slate-900 p-2">
          <img src={currentImage} alt="Preview" className="w-full h-auto rounded-lg object-contain" />
        </div>
      )}
    </div>
  );
};