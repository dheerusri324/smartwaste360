// frontend/src/hooks/useCamera.js

import { useState, useEffect, useRef } from 'react';

/**
 * Manages the device's camera stream.
 * @param {boolean} startStream - Whether to immediately start the camera stream on mount.
 * @returns {{videoRef: React.RefObject<HTMLVideoElement>, stream: MediaStream|null, error: string|null, start: function, stop: function}}
 */
export const useCamera = (startStream = true) => {
  const videoRef = useRef(null);
  const [stream, setStream] = useState(null);
  const [error, setError] = useState(null);

  const start = async () => {
    setError(null);
    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error("Camera API not supported by this browser.");
      }
      const streamData = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment', width: 1280, height: 720 }
      });
      setStream(streamData);
      if (videoRef.current) {
        videoRef.current.srcObject = streamData;
      }
    } catch (err) {
      setError(err.name === "NotAllowedError" ? "Camera permission denied." : "Could not access camera.");
    }
  };

  const stop = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
    }
  };

  useEffect(() => {
    if (startStream) {
      start();
    }
    // Cleanup function: this will be called when the component unmounts
    return () => {
      stop();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [startStream]);

  return { videoRef, stream, error, start, stop };
};