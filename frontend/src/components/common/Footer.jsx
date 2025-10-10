// src/components/common/Footer.jsx

import React from 'react';
import { FaGithub, FaTwitter, FaLinkedin } from 'react-icons/fa';

const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-gray-800 text-white">
      <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <div className="flex justify-center space-x-6">
          <a href="#" className="text-gray-400 hover:text-white"><span className="sr-only">GitHub</span><FaGithub className="h-6 w-6" /></a>
          <a href="#" className="text-gray-400 hover:text-white"><span className="sr-only">Twitter</span><FaTwitter className="h-6 w-6" /></a>
          <a href="#" className="text-gray-400 hover:text-white"><span className="sr-only">LinkedIn</span><FaLinkedin className="h-6 w-6" /></a>
        </div>
        <p className="mt-8 text-center text-base text-gray-400">
          &copy; {currentYear} SmartWaste360. All rights reserved.
        </p>
      </div>
    </footer>
  );
};

export default Footer;