// frontend/src/components/layout/DashboardLayout.jsx

import React from 'react';
import { Navbar, Footer } from '../common';
import DashboardSidebar from '../dashboard/DashboardSidebar';

const DashboardLayout = ({ children }) => {
  return (
    <div className="flex flex-col min-h-screen bg-slate-50">
      <Navbar />
      <div className="flex flex-1 container mx-auto">
        <DashboardSidebar />
        <main className="flex-1 p-8">
          {/* Dashboard page content will be rendered here */}
          {children}
        </main>
      </div>
      <Footer />
    </div>
  );
};

export default DashboardLayout;