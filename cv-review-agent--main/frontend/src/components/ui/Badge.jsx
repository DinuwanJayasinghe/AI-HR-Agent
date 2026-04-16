import React from 'react';

const Badge = ({
  children,
  variant = 'success',
  className = '',
  ...props
}) => {
  const variants = {
    success: 'badge-success',
    warning: 'badge-warning',
    error: 'badge-error',
    info: 'badge-info',
  };

  return (
    <span
      className={`badge ${variants[variant]} ${className}`}
      {...props}
    >
      {children}
    </span>
  );
};

export default Badge;
