import React from 'react';

/**
 * TATTVA Brand Emblem & Logo
 * Stylized geometric drafting compass / mine stope pyramid symbol with ore node at the apex
 * and horizontal datum baseline, matching MOIL ore intelligence identity.
 */
export default function TattvaLogo({ className = 'w-7 h-7', ...props }) {
  return (
    <svg
      viewBox="0 0 100 100"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={`inline-block select-none ${className}`}
      aria-label="TATTVA Ore Intelligence"
      role="img"
      {...props}
    >
      {/* Centerline vertical alignment ticks */}
      <rect x="48.8" y="8" width="2.4" height="4.5" fill="#B8A995" />
      <rect x="48.8" y="41" width="2.4" height="4.2" fill="#B8A995" />
      <rect x="48.8" y="84" width="2.4" height="4.5" fill="#B8A995" />

      {/* Inner Stope Triangle (Sandstone Linen Tan Fill) */}
      <polygon
        points="50,47 31,76 69,76"
        fill="#D9C8B2"
        stroke="#261D1C"
        strokeWidth="3.8"
        strokeLinejoin="miter"
      />

      {/* Outer Drafting Compass / Headframe Legs (Deep Espresso Burgundy) */}
      <line
        x1="50"
        y1="27"
        x2="17"
        y2="76"
        stroke="#3D1B1E"
        strokeWidth="5.2"
        strokeLinecap="round"
      />
      <line
        x1="50"
        y1="27"
        x2="83"
        y2="76"
        stroke="#3D1B1E"
        strokeWidth="5.2"
        strokeLinecap="round"
      />

      {/* Apex Pivot Ore Sphere */}
      <circle
        cx="50"
        cy="27"
        r="8"
        fill="#3D1B1E"
        stroke="#261D1C"
        strokeWidth="1.5"
      />
      <rect x="48.8" y="25.8" width="2.4" height="2.4" fill="#F7F4EF" />

      {/* Horizontal Datum Ground Baseline */}
      <rect
        x="5"
        y="74.5"
        width="90"
        height="3.8"
        rx="0.5"
        fill="#261D1C"
      />
    </svg>
  );
}
