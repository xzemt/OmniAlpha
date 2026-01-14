import React from 'react';
import { Bell, Search, Languages } from 'lucide-react';
import { useTranslation } from '../../contexts/LanguageContext';

const Header: React.FC = () => {
  const { t, toggleLanguage, language } = useTranslation();

  return (
    <header className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-6">
      <div className="flex items-center w-96">
        <div className="relative w-full">
          <span className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Search className="h-4 w-4 text-gray-400" />
          </span>
          <input
            type="text"
            className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-gray-50 placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            placeholder={t('header.search')}
          />
        </div>
      </div>
      <div className="flex items-center space-x-4">
        <button 
          onClick={toggleLanguage}
          className="p-2 rounded-full hover:bg-gray-100 flex items-center text-gray-600 transition-colors"
          title="Switch Language"
        >
          <Languages className="w-5 h-5 mr-1" />
          <span className="text-sm font-medium">{language === 'en' ? 'EN' : '中文'}</span>
        </button>

        <button className="p-2 rounded-full hover:bg-gray-100 relative">
          <Bell className="w-5 h-5 text-gray-600" />
          <span className="absolute top-1 right-1 h-2 w-2 rounded-full bg-red-500"></span>
        </button>
      </div>
    </header>
  );
};

export default Header;
