import React from 'react';
import { Image as ImageIcon, Film, Radio } from 'lucide-react';

export type Mode = 'image' | 'video' | 'live';

interface BottomNavBarProps {
  activeMode: Mode;
  setActiveMode: (mode: Mode) => void;
}

const BottomNavBar: React.FC<BottomNavBarProps> = ({ activeMode, setActiveMode }) => {
  return (
    <nav className="bottom-nav">
      <button 
        className={`nav-item ${activeMode === 'image' ? 'active' : ''}`}
        onClick={() => setActiveMode('image')}
      >
        <div className="nav-icon-container">
          <ImageIcon size={24} />
          <div className="nav-indicator"></div>
        </div>
        <span>Image</span>
      </button>
      
      <button 
        className={`nav-item ${activeMode === 'video' ? 'active' : ''}`}
        onClick={() => setActiveMode('video')}
      >
        <div className="nav-icon-container">
          <Film size={24} />
          <div className="nav-indicator"></div>
        </div>
        <span>Video</span>
      </button>

      <button 
        className={`nav-item ${activeMode === 'live' ? 'active' : ''}`}
        onClick={() => setActiveMode('live')}
      >
        <div className="nav-icon-container">
          <Radio size={24} />
          <div className="nav-indicator"></div>
        </div>
        <span>Live</span>
      </button>
    </nav>
  );
};

export default BottomNavBar;
