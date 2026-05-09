import React, { useState, useRef } from 'react';
import { Upload, Image as ImageIcon, X, Loader2, AlertCircle } from 'lucide-react';
import { uploadImage } from '../api/axios';
import { type HistoryItem } from '../hooks/usePredictionHistory';
import HistoryList from './HistoryList';

interface Props {
  history: HistoryItem[];
  addPrediction: (pred: string, mode: 'image' | 'video' | 'live') => void;
  clearHistory: () => void;
}

const ImageUpload: React.FC<Props> = ({ history, addPrediction, clearHistory }) => {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [prediction, setPrediction] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      setFile(selectedFile);
      setPreview(URL.createObjectURL(selectedFile));
      setPrediction(null);
      setError(null);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const selectedFile = e.dataTransfer.files[0];
      if (selectedFile.type.startsWith('image/')) {
        setFile(selectedFile);
        setPreview(URL.createObjectURL(selectedFile));
        setPrediction(null);
        setError(null);
      } else {
        setError('Please drop an image file.');
      }
    }
  };

  const handleSubmit = async () => {
    if (!file) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const result = await uploadImage(file);
      setPrediction(result.prediction);
      addPrediction(result.prediction, 'image');
    } catch (err) {
      console.error(err);
      setError('Failed to analyze image. Please ensure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  const clearSelection = () => {
    setFile(null);
    setPreview(null);
    setPrediction(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="two-column-layout">
      {/* Input Column */}
      <div className="input-column">
        <div className="glass-panel">
          <h2 style={{ marginBottom: '1.5rem', fontFamily: 'Outfit, sans-serif' }}>Image Input</h2>
          {!preview ? (
            <div 
              className="upload-area"
              onDragOver={(e) => e.preventDefault()}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
            >
              <input 
                type="file" 
                ref={fileInputRef} 
                style={{ display: 'none' }} 
                accept="image/*"
                onChange={handleFileChange}
              />
              <ImageIcon size={48} className="upload-icon" />
              <h3 style={{ fontSize: '1.5rem', marginBottom: '0.5rem', fontWeight: 600 }}>Upload an Image</h3>
              <p style={{ color: 'var(--text-secondary)' }}>Drag and drop or click to browse</p>
            </div>
          ) : (
            <div className="preview-container">
              <button className="remove-btn" onClick={clearSelection}>
                <X size={20} />
              </button>
              <img src={preview} alt="Preview" className="preview-media" />
            </div>
          )}

          {file && (
            <button 
              className="btn-primary" 
              onClick={handleSubmit} 
              disabled={loading}
            >
              {loading ? (
                <><Loader2 className="loader-spinner" /> Analyzing Image...</>
              ) : (
                <><Upload /> Analyze Gesture</>
              )}
            </button>
          )}

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

export default ImageUpload;
