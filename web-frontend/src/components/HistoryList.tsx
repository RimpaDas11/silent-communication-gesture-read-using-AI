import React, { useEffect, useRef, useState } from 'react';
import { type HistoryItem } from '../hooks/usePredictionHistory';
import { Trash2, MessageSquare, Image as ImageIcon, Film, Radio, AlertTriangle } from 'lucide-react';

interface HistoryListProps {
  history: HistoryItem[];
  clearHistory: () => void;
}

const HistoryList: React.FC<HistoryListProps> = ({ history, clearHistory }) => {
  const listRef = useRef<HTMLDivElement>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Auto-scroll to bottom when new history is added
  useEffect(() => {
    if (listRef.current) {
      listRef.current.scrollTop = listRef.current.scrollHeight;
    }
  }, [history]);

  const getModeIcon = (mode: string) => {
    switch (mode) {
      case 'image': return <ImageIcon size={14} />;
      case 'video': return <Film size={14} />;
      case 'live': return <Radio size={14} />;
      default: return null;
    }
  };

  const formatTime = (ts: number) => {
    const date = new Date(ts);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  };

  const handleClearConfirm = () => {
    clearHistory();
    setIsModalOpen(false);
  };

  return (
    <div className="chat-container" style={{ position: 'relative' }}>
      <div className="chat-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-primary)', fontWeight: 600 }}>
          <MessageSquare size={18} />
          <span>Translation History</span>
        </div>
        {history.length > 0 && (
          <button className="clear-history-btn" onClick={() => setIsModalOpen(true)} title="Clear History">
            <Trash2 size={16} />
          </button>
        )}
      </div>

      <div className="chat-messages" ref={listRef}>
        {history.length === 0 ? (
          <div className="empty-chat">
            <MessageSquare size={48} style={{ opacity: 0.1, marginBottom: '1rem' }} />
            <p>No gestures translated yet.</p>
            <p style={{ fontSize: '0.8rem', marginTop: '0.5rem' }}>Upload media or start the webcam to begin.</p>
          </div>
        ) : (
          history.map((item) => (
            <div key={item.id} className="chat-bubble-wrapper">
              <div className={`chat-bubble mode-${item.mode}`}>
                <div className="chat-bubble-header">
                  <span className="chat-mode">{getModeIcon(item.mode)} {item.mode}</span>
                  <span className="chat-time">{formatTime(item.timestamp)}</span>
                </div>
                <div className="chat-text">
                  {item.prediction}
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Confirmation Modal Overlay */}
      {isModalOpen && (
        <div className="modal-overlay" onClick={() => setIsModalOpen(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <AlertTriangle size={48} color="var(--error)" style={{ margin: '0 auto 1rem auto' }} />
            <h3>Clear History?</h3>
            <p>Are you sure you want to delete all translation history? This action cannot be undone.</p>
            <div className="modal-actions">
              <button className="modal-btn cancel" onClick={() => setIsModalOpen(false)}>
                Cancel
              </button>
              <button className="modal-btn danger" onClick={handleClearConfirm}>
                Clear History
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default HistoryList;
