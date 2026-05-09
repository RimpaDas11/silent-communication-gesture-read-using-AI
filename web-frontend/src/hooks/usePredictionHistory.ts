import { useState, useEffect } from 'react';

export interface HistoryItem {
  id: string;
  timestamp: number;
  prediction: string;
  mode: 'image' | 'video' | 'live';
}

const STORAGE_KEY = 'gesture-history';

export function usePredictionHistory() {
  const [history, setHistory] = useState<HistoryItem[]>([]);

  // Load from localStorage on mount
  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        setHistory(JSON.parse(stored));
      }
    } catch (e) {
      console.error('Failed to parse history from localStorage', e);
    }
  }, []);

  // Save to localStorage whenever history changes
  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
  }, [history]);

  const addPrediction = (prediction: string, mode: 'image' | 'video' | 'live') => {
    if (!prediction || prediction.trim() === '' || prediction.includes('Waiting for stream')) return;
    
    // Ignore empty/invalid detections so they don't pollute the chat history
    if (prediction === 'No Detection' || prediction === 'Invalid ROI') return;
    
    setHistory(prev => {
      // Prevent duplicate consecutive entries (mostly for webcam mode)
      if (prev.length > 0 && prev[prev.length - 1].prediction === prediction) {
        return prev;
      }
      
      const newItem: HistoryItem = {
        id: crypto.randomUUID ? crypto.randomUUID() : Date.now().toString(),
        timestamp: Date.now(),
        prediction,
        mode
      };
      
      return [...prev, newItem];
    });
  };

  const clearHistory = () => {
    setHistory([]);
  };

  return { history, addPrediction, clearHistory };
}
