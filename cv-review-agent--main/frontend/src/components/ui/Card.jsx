import React from 'react';

const Card = ({
  children,
  className = '',
  hover = false,
  glass = false,
  ...props
}) => {
  const baseStyles = 'card';
  const hoverStyles = hover ? 'card-hover cursor-pointer' : '';
  const glassStyles = glass ? 'glass glass-hover' : '';

  return (
    <div
      className={`${baseStyles} ${hoverStyles} ${glassStyles} ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};

export const CardHeader = ({ children, className = '' }) => (
  <div className={`mb-4 ${className}`}>{children}</div>
);

export const CardTitle = ({ children, className = '' }) => (
  <h3 className={`text-xl font-bold text-gray-100 ${className}`}>{children}</h3>
);

export const CardDescription = ({ children, className = '' }) => (
  <p className={`text-sm text-gray-400 mt-1 ${className}`}>{children}</p>
);

export const CardContent = ({ children, className = '' }) => (
  <div className={className}>{children}</div>
);

export const CardFooter = ({ children, className = '' }) => (
  <div className={`mt-6 pt-4 border-t border-dark-700 ${className}`}>{children}</div>
);

export default Card;
