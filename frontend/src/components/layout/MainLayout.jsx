// frontend/src/components/layout/MainLayout.jsx

import React from 'react';
import { Navbar, Footer } from '../common'; // Assuming Navbar and Footer are exported from common/index.js

const MainLayout = ({ children }) => {
  return (
    <div className="flex flex-col min-h-screen bg-gray-50">
      <Navbar />
      <main className="flex-grow container mx-auto px-4 py-8">
        {/* 'children' will be whatever page component is being rendered by the router */}
        {children}
      </main>
      <Footer />
    </div>
  );
};

export default MainLayout;