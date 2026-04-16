import React from 'react';
import { Menu, Bell, Settings, User } from 'lucide-react';

const Header = ({ onMenuClick, title = 'Dashboard' }) => {
  return (
    <header className="h-20 bg-dark-800 border-b border-dark-700 flex items-center justify-between px-6 sticky top-0 z-30">
      {/* Left section */}
      <div className="flex items-center gap-4">
        <button
          onClick={onMenuClick}
          className="lg:hidden p-2 rounded-lg hover:bg-dark-700 transition-colors text-gray-400 hover:text-gray-200"
        >
          <Menu className="w-6 h-6" />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-gray-100">{title}</h1>
          <p className="text-sm text-gray-500">Welcome to HR Agent Dashboard</p>
        </div>
      </div>

      {/* Right section */}
      <div className="flex items-center gap-3">
        {/* Notifications */}
        <button className="relative p-2 rounded-lg hover:bg-dark-700 transition-colors text-gray-400 hover:text-gray-200">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1 right-1 w-2 h-2 bg-primary-500 rounded-full"></span>
        </button>

        {/* Settings */}
        <button className="p-2 rounded-lg hover:bg-dark-700 transition-colors text-gray-400 hover:text-gray-200">
          <Settings className="w-5 h-5" />
        </button>

        {/* Profile */}
        <button className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-dark-700 transition-colors">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary-600 to-primary-700 flex items-center justify-center">
            <User className="w-4 h-4 text-white" />
          </div>
          <div className="text-left hidden sm:block">
            <p className="text-sm font-semibold text-gray-200">HR Manager</p>
            <p className="text-xs text-gray-500">hr.agent@company.com</p>
          </div>
        </button>
      </div>
    </header>
  );
};

export default Header;
