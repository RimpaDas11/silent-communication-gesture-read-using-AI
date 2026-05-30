import React, { useState, useEffect } from 'react';
import ImageUpload from './components/ImageUpload';
import VideoUpload from './components/VideoUpload';
import LiveWebcam from './components/LiveWebcam';
import HeaderNav from './components/HeaderNav';
import BottomNavBar, { type Mode } from './components/BottomNavBar';
import { usePredictionHistory } from './hooks/usePredictionHistory';

function App() {
  const [activeMode, setActiveMode] = useState<Mode>('image');
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');
  const { history, addPrediction, clearHistory } = usePredictionHistory();

  // Load theme from localStorage on mount
  useEffect(() => {
    const savedTheme = localStorage.getItem('app-theme');
    if (savedTheme === 'light' || savedTheme === 'dark') {
      setTheme(savedTheme);
    }
  }, []);

  // Update data-theme on body/document when theme changes
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('app-theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'dark' ? 'light' : 'dark');
  };

  return (
    <>
      <HeaderNav theme={theme} toggleTheme={toggleTheme} />

      <main className="app-container">
        {/* Animated transition wrapper could go here if desired */}
        <div style={{ maxWidth: '1000px', margin: '0 auto', width: '100%', height: '100%', display: 'flex', flexDirection: 'column', minHeight: 0 }}>
          {activeMode === 'image' && <ImageUpload history={history} addPrediction={addPrediction} clearHistory={clearHistory} />}
          {activeMode === 'video' && <VideoUpload history={history} addPrediction={addPrediction} clearHistory={clearHistory} />}
          {activeMode === 'live' && <LiveWebcam history={history} addPrediction={addPrediction} clearHistory={clearHistory} />}
        </div>
      </main>

      <BottomNavBar activeMode={activeMode} setActiveMode={setActiveMode} />
    </>
  );
}

export default App;
