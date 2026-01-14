import React from 'react';

const NotFound: React.FC = () => {
  return (
    <div className="flex flex-col items-center justify-center h-full text-gray-600">
      <h1 className="text-4xl font-bold mb-4">404</h1>
      <p>Page not found</p>
    </div>
  );
};

export default NotFound;
