import React, { useEffect, useRef, useState } from 'react';
import { Camera, CameraOff, AlertCircle } from 'lucide-react';
import { type HistoryItem } from '../hooks/usePredictionHistory';
import HistoryList from './HistoryList';

interface Props {
  history: HistoryItem[];
  addPrediction: (pred: string, mode: 'image' | 'video' | 'live') => void;
  clearHistory: () => void;
}

const LiveWebcam: React.FC<Props> = ({ history, addPrediction, clearHistory }) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  
  const [isStreaming, setIsStreaming] = useState(false);
  const [prediction, setPrediction] = useState<string>('Waiting for stream...');
  const [error, setError] = useState<string | null>(null);

  const startStream = async () => {
    try {
      setError(null);
      // Request webcam access
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { width: 640, height: 480, facingMode: 'user' } 
      });
      streamRef.current = stream;
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }

      // Connect WebSocket
      const ws = new WebSocket('ws://localhost:8000/ws/live');
      
      ws.onopen = () => {
        setIsStreaming(true);
        setPrediction('Connecting model...');
        console.log('WebSocket connected');
        // Start sending frames
        sendFramesLoop();
      };

      ws.onmessage = (event) => {
        const text = event.data;
        setPrediction(text);
        addPrediction(text, 'live');
      };

      ws.onerror = () => {
        setError('WebSocket error: Could not connect to backend.');
        stopStream();
      };

      ws.onclose = () => {
        setIsStreaming(false);
      };

      wsRef.current = ws;
      
    } catch (err) {
      console.error(err);
      setError('Could not access webcam. Please check permissions.');
    }
  };

  const stopStream = () => {
    setIsStreaming(false);
    
    // Close WebSocket
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    // Stop Webcam
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }

    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    
    setPrediction('Stream stopped.');
  };

  const sendFramesLoop = () => {
    if (!wsRef.current) return;
    
    // Only send frame if open
    if (wsRef.current.readyState === WebSocket.OPEN) {
      if (videoRef.current && canvasRef.current) {
        const video = videoRef.current;
        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');

        if (ctx && video.videoWidth > 0 && video.videoHeight > 0) {
          canvas.width = video.videoWidth;
          canvas.height = video.videoHeight;
          ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
          
          // Convert canvas to Base64 JPEG
          const base64Data = canvas.toDataURL('image/jpeg', 0.7);
          wsRef.current.send(base64Data);
        }
      }
    }

    // Recursively call every 200ms
    if (isStreaming || wsRef.current.readyState === WebSocket.OPEN || wsRef.current.readyState === WebSocket.CONNECTING) {
      setTimeout(sendFramesLoop, 200);
    }
  };



  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopStream();
    };
  }, []);

  return (
    <div className="two-column-layout">
      {/* Input Column */}
      <div className="input-column">
        <div className="glass-panel">
          <h2 style={{ marginBottom: '1.5rem', fontFamily: 'Outfit, sans-serif' }}>Webcam Input</h2>
          
          <div className="webcam-container">
            {/* Live Indicator */}
            {isStreaming && (
              <div className="live-indicator">
                <div className="live-dot" /> LIVE
              </div>
            )}
            
            {/* Video feed */}
            <video 
              ref={videoRef} 
              className="webcam-video" 
              autoPlay 
              playsInline 
              muted 
              style={{ display: isStreaming ? 'block' : 'none' }}
            />
            
            {/* Hidden canvas for capturing frames */}
            <canvas ref={canvasRef} style={{ display: 'none' }} />
            
            {/* Live Prediction Overlay */}
            {isStreaming && (
              <div className="live-prediction-overlay">
                {prediction}
              </div>
            )}
            
            {/* Placeholder when not streaming */}
            {!isStreaming && (
              <div style={{ height: '300px', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'rgba(0,0,0,0.3)', width: '100%' }}>
                <CameraOff size={48} color="var(--text-secondary)" />
              </div>
            )}
          </div>

          <button 
            className="btn-primary" 
            style={{ 
              background: isStreaming ? 'rgba(239, 68, 68, 0.1)' : undefined,
              border: isStreaming ? '1px solid var(--error)' : undefined,
              color: isStreaming ? 'var(--error)' : undefined,
              boxShadow: isStreaming ? 'none' : undefined,
              marginTop: 0
            }}
            onClick={isStreaming ? stopStream : startStream}
          >
            {isStreaming ? (
              <><CameraOff size={20} /> Stop Live Stream</>
            ) : (
              <><Camera size={20} /> Start Live Stream</>
            )}
          </button>

          {error && (
            <div style={{ color: 'var(--error)', marginTop: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem', justifyContent: 'center' }}>
              <AlertCircle size={20} />
              <p>{error}</p>
            </div>
          )}
        </div>
      </div>

      {/* Output Column */}
      <div className="output-column">
        <div className="glass-panel" style={{ padding: 0 }}>
          <HistoryList history={history} clearHistory={clearHistory} />
        </div>
      </div>
    </div>
  );
};

export default LiveWebcam;
