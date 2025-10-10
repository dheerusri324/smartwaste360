// frontend/src/pages/Camera.jsx

import React, { useState } from 'react';
import CameraInterface from '../components/camera/CameraInterface';
import ImagePreview from '../components/camera/ImagePreview';
import ClassificationResult from '../components/camera/ClassificationResult';
import { classifyWasteImage } from '../services/waste';

const Camera = () => {
  const [capturedImage, setCapturedImage] = useState(null);
  const [classificationResult, setClassificationResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleCapture = (imageDataUrl) => {
    setCapturedImage(imageDataUrl);
  };

  const handleRetake = () => {
    setCapturedImage(null);
    setClassificationResult(null);
    setError(null);
  };

  // This function now accepts the weight from the ImagePreview component
  const handleUsePhoto = async (weight) => {
    if (!capturedImage) return;

    setIsLoading(true);
    setError(null);
    try {
      // Pass both the image and the weight to the API service
      const result = await classifyWasteImage(capturedImage, weight);
      setClassificationResult(result);
    } catch (err) {
      setError(err.error || 'Classification failed.');
    } finally {
      setIsLoading(false);
      setCapturedImage(null); // Hide the preview after submission
    }
  };

  const handleDone = () => {
    setClassificationResult(null);
    setError(null);
  };

  // This function determines which component to show based on the current state
  const renderContent = () => {
    if (isLoading) {
      return <div className="text-white text-xl font-semibold">Analyzing...</div>;
    }
    if (error) {
        return (
            <div className="text-center text-white p-4">
                <p className="text-red-400 mb-4 font-medium">{error}</p>
                <button onClick={handleDone} className="px-6 py-2 bg-emerald-600 text-white font-semibold rounded-lg hover:bg-emerald-700">
                    Try Again
                </button>
            </div>
        );
    }
    if (classificationResult) {
      return <ClassificationResult result={classificationResult} onDone={handleDone} />;
    }
    if (capturedImage) {
      return <ImagePreview imageDataUrl={capturedImage} onRetake={handleRetake} onUsePhoto={handleUsePhoto} />;
    }
    return <CameraInterface onCapture={handleCapture} />;
  };

  return (
    <div className="flex flex-col items-center justify-center bg-black min-h-screen w-full">
      {renderContent()}
    </div>
  );
};

export default Camera;