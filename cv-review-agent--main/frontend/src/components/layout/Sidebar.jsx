import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  FileCheck,
  Download,
  MessageSquare,
  Sparkles,
} from 'lucide-react';

const Sidebar = ({ isOpen, onClose }) => {
  const location = useLocation();

  const navItems = [
    {
      name: 'AI Assistant',
      path: '/',
      icon: MessageSquare,
    },
    {
      name: 'Dashboard',
      path: '/dashboard',
      icon: LayoutDashboard,
    },
    {
      name: 'CV Review',
      path: '/cv-review',
      icon: FileCheck,
    },
    {
      name: 'Download CVs',
      path: '/download',
      icon: Download,
    },
  ];

  const isActive = (path) => {
    return location.pathname === path;
  };

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-dark-900/80 backdrop-blur-sm lg:hidden z-40"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`
          fixed top-0 left-0 h-screen w-64 bg-dark-800 border-r border-dark-700
          transform transition-transform duration-300 ease-in-out z-50
          lg:translate-x-0 ${isOpen ? 'translate-x-0' : '-translate-x-full'}
        `}
      >
        {/* Logo */}
        <div className="h-20 flex items-center px-6 border-b border-dark-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-primary-600 to-primary-700 flex items-center justify-center">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold gradient-text">HR Agent</h1>
              <p className="text-xs text-gray-500">CV Automation</p>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="p-4 space-y-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = isActive(item.path);

            return (
              <Link
                key={item.path}
                to={item.path}
                onClick={onClose}
                className={`
                  flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200
                  ${
                    active
                      ? 'bg-gradient-to-r from-primary-600 to-primary-700 text-white shadow-lg shadow-primary-900/50'
                      : 'text-gray-400 hover:text-gray-200 hover:bg-dark-700'
                  }
                `}
              >
                <Icon className="w-5 h-5" />
                <span className="font-medium">{item.name}</span>
              </Link>
            );
          })}
        </nav>

        {/* Bottom info */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-dark-700">
          <div className="glass p-4 rounded-lg">
            <p className="text-xs text-gray-400 mb-1">Powered by</p>
            <div className="flex items-center gap-2">
              <span className="text-sm font-semibold gradient-text">OpenAI GPT-4</span>
              <span className="text-gray-600">+</span>
              <span className="text-sm font-semibold gradient-text">Google Gemini</span>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;
