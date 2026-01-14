import React from 'react';
import { Home, TrendingUp, BarChart2, Cpu, Settings } from 'lucide-react';
import { clsx } from 'clsx';
import { Link, useLocation } from 'react-router-dom';

interface SidebarProps {
  className?: string;
}

const Sidebar: React.FC<SidebarProps> = ({ className }) => {
  const location = useLocation();

  const navItems = [
    { name: 'Home', path: '/', icon: Home },
    { name: 'Technical Selection', path: '/technical', icon: TrendingUp },
    { name: 'Alpha Selection', path: '/alpha', icon: BarChart2 },
    { name: 'AI Selection', path: '/ai', icon: Cpu },
    { name: 'Settings', path: '/settings', icon: Settings },
  ];

  return (
    <div className={clsx('w-64 bg-gray-900 text-white flex flex-col', className)}>
      <div className="h-16 flex items-center px-6 border-b border-gray-800">
        <span className="text-xl font-bold bg-gradient-to-r from-blue-400 to-teal-400 bg-clip-text text-transparent">
          OmniAlpha
        </span>
      </div>
      <nav className="flex-1 py-4">
        <ul>
          {navItems.map((item) => {
            const isActive = location.pathname === item.path || (item.path !== '/' && location.pathname.startsWith(item.path));
            return (
              <li key={item.name}>
                <Link
                  to={item.path}
                  className={clsx(
                    'flex items-center px-6 py-3 hover:bg-gray-800 transition-colors',
                    isActive ? 'bg-gray-800 border-r-4 border-blue-500' : 'border-r-4 border-transparent'
                  )}
                >
                  <item.icon className="w-5 h-5 mr-3" />
                  <span>{item.name}</span>
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>
      <div className="p-4 border-t border-gray-800">
        <div className="flex items-center">
          <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center font-bold">
            U
          </div>
          <div className="ml-3">
            <p className="text-sm font-medium">User</p>
            <p className="text-xs text-gray-400">Admin</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
