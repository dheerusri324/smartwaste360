// frontend/src/components/dashboard/DashboardSidebar.jsx
import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, BarChart3, History, Settings } from 'lucide-react';

const DashboardSidebar = () => {
  const navLinkClass = ({ isActive }) =>
    `flex items-center px-4 py-3 text-gray-700 rounded-lg transition-colors duration-200 ${
      isActive ? 'bg-emerald-100 text-emerald-700 font-semibold' : 'hover:bg-gray-100'
    }`;

  return (
    <aside className="w-64 p-4 bg-white border-r border-gray-200">
      <nav className="space-y-2">
        <NavLink to="/dashboard" className={navLinkClass} end>
          <LayoutDashboard className="w-5 h-5 mr-3" />
          Overview
        </NavLink>
        <NavLink to="/dashboard/stats" className={navLinkClass}>
          <BarChart3 className="w-5 h-5 mr-3" />
          Statistics
        </NavLink>
        <NavLink to="/dashboard/history" className={navLinkClass}>
          <History className="w-5 h-5 mr-3" />
          Waste History
        </NavLink>
        <NavLink to="/dashboard/settings" className={navLinkClass}>
          <Settings className="w-5 h-5 mr-3" />
          Settings
        </NavLink>
      </nav>
    </aside>
  );
};

export default DashboardSidebar;