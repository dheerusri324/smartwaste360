import React from 'react';
import { Link } from 'react-router-dom';
import { Camera, Map, TrendingUp, Package } from 'lucide-react';

const Home = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-16 text-center">
        <h1 className="text-5xl font-bold text-green-800 mb-6">
          Welcome to SmartWaste360
        </h1>
        <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
          Revolutionizing waste management through technology. Our platform helps communities 
          manage waste efficiently while promoting recycling and sustainability.
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <Camera className="h-12 w-12 text-green-600 mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">Waste Detection</h3>
            <p className="text-gray-600">Use AI to identify and classify waste materials</p>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-md">
            <Map className="h-12 w-12 text-green-600 mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">Collection Points</h3>
            <p className="text-gray-600">Find nearby waste collection centers</p>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-md">
            <TrendingUp className="h-12 w-12 text-green-600 mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">Leaderboard</h3>
            <p className="text-gray-600">Track your recycling progress and compete</p>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-md">
            <Package className="h-12 w-12 text-green-600 mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">Collector Portal</h3>
            <p className="text-gray-600">Manage waste collection schedules</p>
          </div>
        </div>
        
        <div className="space-x-4">
          <Link
            to="/login"
            className="bg-green-600 hover:bg-green-700 text-white px-8 py-3 rounded-lg text-lg font-semibold"
          >
            Get Started
          </Link>
          <Link
            to="/register"
            className="border border-green-600 text-green-600 hover:bg-green-50 px-8 py-3 rounded-lg text-lg font-semibold"
          >
            Create Account
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Home;