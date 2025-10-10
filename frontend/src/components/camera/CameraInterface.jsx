// frontend/src/components/camera/CameraInterface.jsx

import React, { useRef, useEffect, useState } from 'react';
import CaptureButton from './CaptureButton';
import { Upload, Camera } from 'lucide-react';
import PropTypes from 'prop-types';

const CameraInterface = ({ onCapture }) => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const fileInputRef = useRef(null);
  const [error, setError] = useState(null);
  const [mode, setMode] = useState('camera'); // 'camera' or 'upload'
  const [isDragOver, setIsDragOver] = useState(false);

  useEffect(() => {
    let stream = null;
    const startCamera = async () => {
      try {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
          throw new Error("Camera API not supported by this browser.");
        }
        stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: 'environment', width: 1280, height: 720 }
        });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      } catch (err) {
        setError(err.name === "NotAllowedError" ? "Camera permission denied." : "Could not access camera.");
      }
    };
    startCamera();
    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  const handleCaptureClick = () => {
    if (videoRef.current && canvasRef.current) {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const context = canvas.getContext('2d');
      context.drawImage(video, 0, 0, video.videoWidth, video.videoHeight);
      const imageDataUrl = canvas.toDataURL('image/jpeg');
      onCapture(imageDataUrl);
    }
  };

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file && file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = (e) => {
        onCapture(e.target.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    const files = e.dataTransfer.files;
    if (files.length > 0 && files[0].type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = (e) => {
        onCapture(e.target.result);
      };
      reader.readAsDataURL(files[0]);
    }
  };

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-white p-4 space-y-6">
        <div className="text-red-400 text-center">
          <Camera className="mx-auto mb-2" size={48} />
          <p>{error}</p>
        </div>
        <div className="text-center">
          <p className="mb-4">You can still upload an image from your device:</p>
          <button
            onClick={handleUploadClick}
            className="flex items-center gap-2 px-6 py-3 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors"
          >
            <Upload size={20} />
            Upload Image
          </button>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleFileUpload}
            className="hidden"
          />
        </div>
      </div>
    );
  }

  return (
    <div className="relative w-full max-w-4xl h-full flex flex-col items-center justify-center">
      {/* Mode Toggle */}
      <div className="absolute top-4 left-4 z-10">
        <div className="flex bg-black bg-opacity-50 rounded-lg p-1">
          <button
            onClick={() => setMode('camera')}
            className={`flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
              mode === 'camera' 
                ? 'bg-emerald-600 text-white' 
                : 'text-gray-300 hover:text-white'
            }`}
          >
            <Camera size={16} />
            Camera
          </button>
          <button
            onClick={() => setMode('upload')}
            className={`flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
              mode === 'upload' 
                ? 'bg-emerald-600 text-white' 
                : 'text-gray-300 hover:text-white'
            }`}
          >
            <Upload size={16} />
            Upload
          </button>
        </div>
      </div>

      {mode === 'camera' ? (
        <>
          <video ref={videoRef} autoPlay playsInline muted className="w-full h-auto rounded-lg" />
          <canvas ref={canvasRef} style={{ display: 'none' }} />
          <div className="absolute bottom-6">
            <CaptureButton onClick={handleCaptureClick} />
          </div>
        </>
      ) : (
        <div className="flex flex-col items-center justify-center h-full text-white space-y-6">
          <div 
            className={`text-center p-8 border-2 border-dashed rounded-lg transition-colors ${
              isDragOver 
                ? 'border-emerald-400 bg-emerald-900 bg-opacity-20' 
                : 'border-gray-400 hover:border-emerald-400'
            }`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <Upload className="mx-auto mb-4" size={64} />
            <h3 className="text-xl font-semibold mb-2">Upload Waste Image</h3>
            <p className="text-gray-300 mb-6">
              {isDragOver 
                ? 'Drop your image here!' 
                : 'Drag & drop an image here, or click to select'
              }
            </p>
            <button
              onClick={handleUploadClick}
              className="flex items-center gap-2 px-8 py-4 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors text-lg font-medium"
            >
              <Upload size={24} />
              Select Image
            </button>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleFileUpload}
              className="hidden"
            />
          </div>
        </div>
      )}
    </div>
  );
};

CameraInterface.propTypes = {
  onCapture: PropTypes.func.isRequired,
};

export default CameraInterface;