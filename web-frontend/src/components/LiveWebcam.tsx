import React, { useEffect, useRef, useState } from 'react';
import { Camera, CameraOff, AlertCircle } from 'lucide-react';
import { type HistoryItem } from '../hooks/usePredictionHistory';
import HistoryList from './HistoryList';

interface Props {
  history: HistoryItem[];
  addPrediction: (
    pred: string,
    mode: 'image' | 'video' | 'live'
  ) => void;
  clearHistory: () => void;
}

const LiveWebcam: React.FC<Props> = ({
  history,
  addPrediction,
  clearHistory
}) => {

  const videoRef =
    useRef<HTMLVideoElement>(null);

  const canvasRef =
    useRef<HTMLCanvasElement>(null);

  const wsRef =
    useRef<WebSocket | null>(null);

  const streamRef =
    useRef<MediaStream | null>(null);

  const [isStreaming, setIsStreaming] =
    useState(false);

  const [prediction, setPrediction] =
    useState<string>('Waiting for stream...');

  const [error, setError] =
    useState<string | null>(null);

  // -------------------- Start Stream --------------------

  const startStream = async () => {

    try {

      setError(null);

      // Webcam Permission

      const stream =
        await navigator.mediaDevices.getUserMedia({
          video: {
            width: 640,
            height: 480,
            facingMode: 'user'
          }
        });

      streamRef.current = stream;

      if (videoRef.current) {

        videoRef.current.srcObject = stream;
      }

      // -------------------- WebSocket --------------------

      const ws = new WebSocket(
        'ws://127.0.0.1:8000/ws/live'
      );

      ws.onopen = () => {

        console.log('WebSocket Connected');

        setIsStreaming(true);

        setPrediction(
          'AI Model Connected...'
        );

        sendFramesLoop();
      };

      ws.onmessage = (event) => {

        try {

          const data = JSON.parse(event.data);

          const result =
            `${data.prediction}`;

          setPrediction(result);

          addPrediction(
            result,
            'live'
          );

        } catch (err) {

          console.error(err);
        }
      };

      ws.onerror = () => {

        setError(
          'WebSocket Error: Backend connection failed.'
        );

        stopStream();
      };

      ws.onclose = () => {

        console.log(
          'WebSocket Closed'
        );

        setIsStreaming(false);
      };

      wsRef.current = ws;

    } catch (err) {

      console.error(err);

      setError(
        'Could not access webcam.'
      );
    }
  };

  // -------------------- Stop Stream --------------------

  const stopStream = () => {

    setIsStreaming(false);

    // Close WebSocket

    if (wsRef.current) {

      wsRef.current.close();

      wsRef.current = null;
    }

    // Stop Webcam

    if (streamRef.current) {

      streamRef.current
        .getTracks()
        .forEach(track => track.stop());

      streamRef.current = null;
    }

    if (videoRef.current) {

      videoRef.current.srcObject = null;
    }

    setPrediction('Stream stopped.');
  };

  // -------------------- Send Frames --------------------

  const sendFramesLoop = () => {

    if (!wsRef.current) return;

    if (
      wsRef.current.readyState ===
      WebSocket.OPEN
    ) {

      if (
        videoRef.current &&
        canvasRef.current
      ) {

        const video = videoRef.current;

        const canvas = canvasRef.current;

        const ctx =
          canvas.getContext('2d');

        if (
          ctx &&
          video.videoWidth > 0 &&
          video.videoHeight > 0
        ) {

          canvas.width =
            video.videoWidth;

          canvas.height =
            video.videoHeight;

          ctx.drawImage(
            video,
            0,
            0,
            canvas.width,
            canvas.height
          );

          // -------------------- FIXED BASE64 --------------------

          const base64Data = canvas
            .toDataURL(
              'image/jpeg',
              0.7
            )
            .split(',')[1];

          wsRef.current.send(
            base64Data
          );
        }
      }
    }

    // Loop every 200ms

    if (
      isStreaming ||
      (
        wsRef.current &&
        (
          wsRef.current.readyState ===
          WebSocket.OPEN ||

          wsRef.current.readyState ===
          WebSocket.CONNECTING
        )
      )
    ) {

      setTimeout(
        sendFramesLoop,
        200
      );
    }
  };

  // -------------------- Cleanup --------------------

  useEffect(() => {

    return () => {

      stopStream();
    };

  }, []);

  // -------------------- UI --------------------

  return (

    <div className="two-column-layout">

      {/* Input Column */}

      <div className="input-column">

        <div className="glass-panel">

          <h2
            style={{
              marginBottom: '1.5rem',
              fontFamily:
                'Outfit, sans-serif'
            }}
          >
            Webcam Input
          </h2>

          <div className="webcam-container">

            {/* Live Badge */}

            {isStreaming && (

              <div className="live-indicator">

                <div className="live-dot" />

                LIVE

              </div>
            )}

            {/* Webcam */}

            <video
              ref={videoRef}
              className="webcam-video"
              autoPlay
              playsInline
              muted
              style={{
                display:
                  isStreaming
                    ? 'block'
                    : 'none'
              }}
            />

            {/* Hidden Canvas */}

            <canvas
              ref={canvasRef}
              style={{
                display: 'none'
              }}
            />

            {/* Prediction Overlay */}

            {isStreaming && (

              <div className="live-prediction-overlay">

                {prediction}

              </div>
            )}

            {/* Placeholder */}

            {!isStreaming && (

              <div
                style={{
                  height: '300px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent:
                    'center',
                  background:
                    'rgba(0,0,0,0.3)',
                  width: '100%'
                }}
              >

                <CameraOff
                  size={48}
                  color="var(--text-secondary)"
                />

              </div>
            )}
          </div>

          {/* Start / Stop Button */}

          <button
            className="btn-primary"
            style={{
              background: isStreaming
                ? 'rgba(239,68,68,0.1)'
                : undefined,

              border: isStreaming
                ? '1px solid var(--error)'
                : undefined,

              color: isStreaming
                ? 'var(--error)'
                : undefined,

              boxShadow: isStreaming
                ? 'none'
                : undefined,

              marginTop: 0
            }}
            onClick={
              isStreaming
                ? stopStream
                : startStream
            }
          >

            {isStreaming ? (
              <>
                <CameraOff size={20} />
                Stop Live Stream
              </>
            ) : (
              <>
                <Camera size={20} />
                Start Live Stream
              </>
            )}

          </button>

          {/* Error */}

          {error && (

            <div
              style={{
                color: 'var(--error)',
                marginTop: '1rem',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                justifyContent:
                  'center'
              }}
            >

              <AlertCircle size={20} />

              <p>{error}</p>

            </div>
          )}

        </div>
      </div>

      {/* Output Column */}

      <div className="output-column">

        <div
          className="glass-panel"
          style={{ padding: 0 }}
        >

          <HistoryList
            history={history}
            clearHistory={clearHistory}
          />

        </div>
      </div>

    </div>
  );
};

export default LiveWebcam;