// frontend/src/components/dashboard/QuickActions.jsx

import React from 'react';
import { Link } from 'react-router-dom';
import { Camera, Map, BarChart2 } from 'lucide-react';

const ActionCard = ({ to, icon, title, description }) => (
    <Link to={to} className="block p-6 bg-white rounded-lg shadow-md hover:shadow-lg hover:scale-105 transition-transform duration-200">
        <div className="flex items-center">
            <div className="p-3 bg-emerald-100 text-emerald-600 rounded-full mr-4">
                {icon}
            </div>
            <div>
                <h4 className="font-bold text-lg text-gray-800">{title}</h4>
                <p className="text-sm text-gray-500">{description}</p>
            </div>
        </div>
    </Link>
);

const QuickActions = () => {
    return (
        <div className="space-y-6">
            <h3 className="text-xl font-bold text-gray-800">Quick Actions</h3>
            <ActionCard
                to="/camera"
                icon={<Camera />}
                title="Scan New Waste"
                description="Classify an item and earn points."
            />
            <ActionCard
                to="/maps"
                icon={<Map />}
                title="View Map"
                description="Find collection points near you."
            />
            <ActionCard
                to="/leaderboard"
                icon={<BarChart2 />}
                title="Leaderboard"
                description="Check your colony's ranking."
            />
        </div>
    );
};

export default QuickActions;