import React from 'react';

export default function BrandLogo({ size = 28, className = '' }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 64 64"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      style={{ display: 'inline-block', verticalAlign: 'middle', flexShrink: 0 }}
      aria-label="GenericMeds AI Logo"
    >
      <defs>
        <linearGradient id="gmBrandGrad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#cf4d20" />
          <stop offset="100%" stopColor="#a33610" />
        </linearGradient>
        <linearGradient id="gmPillGrad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#ffffff" />
          <stop offset="100%" stopColor="#fff3ec" />
        </linearGradient>
      </defs>

      {/* Terracotta Brand Squircle Container */}
      <rect width="64" height="64" rx="16" fill="url(#gmBrandGrad)" />

      {/* Modern Medical Cross + Angled Capsule */}
      <g transform="translate(32, 32) rotate(-45) translate(-32, -32)">
        {/* Top Half of Capsule */}
        <path
          d="M23 20C23 15.0294 27.0294 11 32 11C36.9706 11 41 15.0294 41 20V31H23V20Z"
          fill="url(#gmPillGrad)"
        />
        {/* Bottom Half of Capsule */}
        <path
          d="M23 33H41V44C41 48.9706 36.9706 53 32 53C27.0294 53 23 48.9706 23 44V33Z"
          fill="#fceee6"
        />
        {/* Crisp Central Dividing Band */}
        <line x1="23" y1="32" x2="41" y2="32" stroke="#b84218" strokeWidth="2.5" />

        {/* Medical Cross Symbol on Top Half */}
        <rect x="29.5" y="18" width="5" height="9" rx="1.5" fill="#b84218" />
        <rect x="27.5" y="20" width="9" height="5" rx="1.5" fill="#b84218" />
      </g>
    </svg>
  );
}
