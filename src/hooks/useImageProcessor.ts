import { useState, useEffect, useCallback, useRef } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { listen, UnlistenFn } from '@tauri-apps/api/event';

// 1. Types & Interfaces definitions
export interface ProcessResponsePayload {
  status: 'success' | 'error';
  data?: any;
  error?: string;
  details?: string;
}

export interface UseImageProcessorReturn {
  isEngineReady: boolean;
  isProcessing: boolean;
  currentImage: string | null;
  error: string | null;
  initEngine: () => Promise<void>;
  cropFace: (imageBase64: string, preset: string) => Promise<string>;
  applyRetouch: (imageBase64: string, smoothness: number, brightness: number) => Promise<string>;
  generateA4Grid: (imageBase64: string, sizeType: string, cropMarks?: boolean) => Promise<string>;
  setCurrentImage: (image: string | null) => void;
}

export const useImageProcessor = (): UseImageProcessorReturn => {
  const [isEngineReady, setIsEngineReady] = useState<boolean>(false);
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [currentImage, setCurrentImage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // រក្សាទុក Pending Promise Resolve/Reject References
  const pendingResolver = useRef<{
    resolve: (data: any) => void;
    reject: (reason: any) => void;
  } | null>(null);

  // 2. Setup Event Listeners ពី Tauri Rust (python-response & python-error)
  useEffect(() => {
    let unlistenResponse: UnlistenFn | null = null;
    let unlistenError: UnlistenFn | null = null;

    const setupListeners = async () => {
      // Listen stdout responses ពី Python Engine
      unlistenResponse = await listen<string>('python-response', (event) => {
        setIsProcessing(false);
        try {
          const res: ProcessResponsePayload = JSON.parse(event.payload);

          if (res.status === 'success') {
            if (pendingResolver.current) {
              pendingResolver.current.resolve(res.data);
              pendingResolver.current = null;
            }
          } else {
            const errMsg = res.error || 'មានបញ្ហាក្នុងការប្រមែប្រមូលរូបភាព';
            setError(errMsg);
            if (pendingResolver.current) {
              pendingResolver.current.reject(new Error(errMsg));
              pendingResolver.current = null;
            }
          }
        } catch (err) {
          console.error('Failed to parse Python response JSON:', err);
          setError('Invalid JSON response format from Python engine.');
          if (pendingResolver.current) {
            pendingResolver.current.reject(err);
            pendingResolver.current = null;
          }
        }
      });

      // Listen stderr logs ពី Python Engine
      unlistenError = await listen<string>('python-error', (event) => {
        console.error('[Python Sidecar Stderr]:', event.payload);
      });
    };

    setupListeners();

    // Cleanup Listeners ពេល Component Unmount
    return () => {
      if (unlistenResponse) unlistenResponse();
      if (unlistenError) unlistenError();
    };
  }, []);

  // 3. Command: ចាប់ផ្តើម Spawn Python Sidecar Engine
  const initEngine = useCallback(async () => {
    try {
      setError(null);
      await invoke('init_python_sidecar');
      setIsEngineReady(true);
      console.log('✅ Python Engine initialized successfully.');
    } catch (err: any) {
      console.error('Failed to init Python sidecar:', err);
      setError(`Failed to start AI Engine: ${err}`);
      setIsEngineReady(false);
    }
  }, []);

  // 4. Helper Function សម្រាប់ផ្ញើ Command ទៅ Python
  const sendCommand = useCallback((command: string, payload: any): Promise<any> => {
    return new Promise(async (resolve, reject) => {
      setError(null);
      setIsProcessing(true);

      // រក្សាទុក Promise Resolver សម្រាប់បំពេញនៅពេល Event python-response ត្រឡប់មកវិញ
      pendingResolver.current = { resolve, reject };

      try {
        await invoke('send_to_python', { command, payload });
      } catch (err) {
        setIsProcessing(false);
        pendingResolver.current = null;
        setError(`Failed to send IPC request: ${err}`);
        reject(err);
      }
    });
  }, []);

  // 5. Business Operations
  const cropFace = useCallback(
    async (imageBase64: string, preset: string = '3x4'): Promise<string> => {
      const data = await sendCommand('CROP_FACE', { image: imageBase64, preset });
      if (data && data.image) {
        setCurrentImage(data.image);
        return data.image;
      }
      throw new Error('No image data returned from crop command.');
    },
    [sendCommand]
  );

  const applyRetouch = useCallback(
    async (
      imageBase64: string,
      smoothness: number = 0.35,
      brightness: number = 0.1
    ): Promise<string> => {
      const data = await sendCommand('RETOUCH', {
        image: imageBase64,
        smoothness,
        brightness,
      });
      if (data && data.image) {
        setCurrentImage(data.image);
        return data.image;
      }
      throw new Error('No image data returned from retouch command.');
    },
    [sendCommand]
  );

  const generateA4Grid = useCallback(
    async (
      imageBase64: string,
      sizeType: string = '3x4',
      cropMarks: boolean = true
    ): Promise<string> => {
      const data = await sendCommand('GENERATE_A4', {
        image: imageBase64,
        size_type: sizeType,
        crop_marks: cropMarks,
      });
      if (data && data.image) {
        return data.image;
      }
      throw new Error('No image data returned from A4 grid generator.');
    },
    [sendCommand]
  );

  return {
    isEngineReady,
    isProcessing,
    currentImage,
    error,
    initEngine,
    cropFace,
    applyRetouch,
    generateA4Grid,
    setCurrentImage,
  };
};