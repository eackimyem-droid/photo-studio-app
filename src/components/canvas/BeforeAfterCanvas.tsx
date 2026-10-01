import React, { useState, useRef, useCallback } from 'react';
import { Sliders, Sparkles } from 'lucide-react';

interface BeforeAfterCanvasProps {
  beforeImage: str; // Base64 ឬ Image URL នៃរូបដើម
  afterImage: str;  // Base64 ឬ Image URL នៃរូបភាពដែលបានកែ
  className?: str;
}

export const BeforeAfterCanvas: React.FC<BeforeAfterCanvasProps> = ({
  beforeImage,
  afterImage,
  className = '',
}) => {
  // ភាគរយទីតាំង Slider (0 ដល់ 100%)
  const [sliderPosition, setSliderPosition] = useState<number>(50);
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const containerRef = useRef<HTMLDivElement>(null);

  // គណនាទីតាំង Slider ពេលអ្នកប្រើប្រាស់ Drag ឬ Move Mouse/Touch
  const handleMove = useCallback(
    (clientX: number) => {
      if (!containerRef.current) return;
      const rect = containerRef.current.getBoundingClientRect();
      const x = clientX - rect.left;
      let percentage = (x / rect.width) * 100;

      // វ៉ាស់កម្រិតរវាង 0% ដល់ 100%
      if (percentage < 0) percentage = 0;
      if (percentage > 100) percentage = 100;

      setSliderPosition(percentage);
    },
    []
  );

  const handleMouseDown = () => setIsDragging(true);
  const handleMouseUp = () => setIsDragging(false);

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging) return;
    handleMove(e.clientX);
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    if (!isDragging) return;
    handleMove(e.touches[0].clientX);
  };

  return (
    <div
      ref={containerRef}
      className={`relative w-full h-[600px] overflow-hidden rounded-xl border border-slate-700 bg-slate-900 select-none cursor-ew-resize ${className}`}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
      onTouchMove={handleTouchMove}
      onTouchEnd={handleMouseUp}
    >
      {/* 1. រូបភាពបន្ទាប់បន្សំ (AFTER Image - Full Background Layer) */}
      <img
        src={afterImage}
        alt="After Processing"
        className="absolute inset-0 w-full h-full object-contain pointer-events-none"
      />

      {/* Label: AFTER */}
      <div className="absolute top-4 right-4 bg-emerald-500/80 backdrop-blur-md text-white text-xs font-bold px-3 py-1.5 rounded-full shadow-lg flex items-center gap-1.5 z-10">
        <Sparkles size={14} />
        <span>AFTER (កែរួច)</span>
      </div>

      {/* 2. រូបភាពដើម (BEFORE Image - Cropped Layer using Clip-Path) */}
      <div
        className="absolute inset-0 w-full h-full overflow-hidden pointer-events-none"
        style={{
          clipPath: `polygon(0 0, ${sliderPosition}% 0, ${sliderPosition}% 100%, 0 100%)`,
        }}
      >
        <img
          src={beforeImage}
          alt="Before Processing"
          className="absolute inset-0 w-full h-full object-contain"
        />

        {/* Label: BEFORE */}
        <div className="absolute top-4 left-4 bg-slate-800/80 backdrop-blur-md text-slate-200 text-xs font-bold px-3 py-1.5 rounded-full shadow-lg border border-slate-600 flex items-center gap-1.5 z-10">
          <Sliders size={14} />
          <span>BEFORE (រូបដើម)</span>
        </div>
      </div>

      {/* 3. ខ្សែបន្ទាត់ Dividers & Divider Handle Button */}
      <div
        className="absolute top-0 bottom-0 w-0.5 bg-white/80 shadow-[0_0_10px_rgba(0,0,0,0.5)] z-20"
        style={{ left: `${sliderPosition}%` }}
      >
        {/* ប៊ូតុងរំកិលចំពាក់កណ្តាល (Circular Handle Bar) */}
        <div
          onMouseDown={handleMouseDown}
          onTouchStart={handleMouseDown}
          className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 w-10 h-10 rounded-full bg-white text-slate-800 shadow-xl border-2 border-emerald-500 flex items-center justify-center cursor-ew-resize hover:scale-110 active:scale-95 transition-transform"
        >
          <svg
            className="w-5 h-5 text-slate-700"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2.5}
              d="M8 9l-3 3 3 3m8-6l3 3-3 3"
            />
          </svg>
        </div>
      </div>
    </div>
  );
};