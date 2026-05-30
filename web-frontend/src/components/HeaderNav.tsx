import React from 'react';
import { Sun, Moon, HandMetal } from 'lucide-react';

interface HeaderNavProps {
  theme: 'light' | 'dark';
  toggleTheme: () => void;
}

const HeaderNav: React.FC<HeaderNavProps> = ({ theme, toggleTheme }) => {
  return (
    <header className="header-nav">
      <div className="header-logo" style={{ alignItems: 'flex-start', gap: '0.75rem' }}>
        <HandMetal size={32} style={{ marginTop: '0.1rem' }} />
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.1rem' }}>
          <span>Silent Communication</span>
          <span style={{ fontSize: '0.85rem', fontWeight: 500, color: 'var(--text-secondary)', letterSpacing: '0.5px', fontFamily: 'Inter, sans-serif' }}>
            Connect Through Gesture ...
          </span>
        </div>
      </div>
      
      <button 
        className="theme-toggle" 
        onClick={toggleTheme}
        aria-label="Toggle Theme"
      >
        {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
      </button>
    </header>
  );
};

export default HeaderNav;
