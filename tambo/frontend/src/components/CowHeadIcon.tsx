interface CowHeadIconProps {
  size?: number;
  className?: string;
}

export function CowHeadIcon({ size = 32, className }: CowHeadIconProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 64 64"
      className={className}
      role="img"
      aria-label="Logo vaca"
    >
      <ellipse cx="16" cy="22" rx="7" ry="9" fill="#f4ede1" stroke="#3b2a1a" strokeWidth="2" />
      <ellipse cx="48" cy="22" rx="7" ry="9" fill="#f4ede1" stroke="#3b2a1a" strokeWidth="2" />
      <ellipse cx="16" cy="22" rx="3.2" ry="4.4" fill="#e8a2b0" />
      <ellipse cx="48" cy="22" rx="3.2" ry="4.4" fill="#e8a2b0" />
      <path
        d="M13 12c1-4 4-6 6-6M51 12c-1-4-4-6-6-6"
        stroke="#3b2a1a"
        strokeWidth="2"
        strokeLinecap="round"
        fill="none"
      />
      <ellipse cx="32" cy="34" rx="24" ry="21" fill="#fffdf9" stroke="#3b2a1a" strokeWidth="2.5" />
      <path
        d="M14 24c3-2 8-1 9 3-3 2-8 1-9-3zM50 24c-3-2-8-1-9 3 3 2 8 1 9-3z"
        fill="#3b2a1a"
      />
      <path d="M40 40c4 3 5 8 2 11-4-1-8-4-8-9 2-2 4-2 6-2z" fill="#3b2a1a" opacity="0.85" />
      <ellipse cx="32" cy="44" rx="12" ry="9" fill="#f6c9d4" stroke="#3b2a1a" strokeWidth="2" />
      <circle cx="27" cy="45" r="1.6" fill="#3b2a1a" />
      <circle cx="37" cy="45" r="1.6" fill="#3b2a1a" />
      <circle cx="24" cy="30" r="2.6" fill="#3b2a1a" />
      <circle cx="41" cy="28" r="3.4" fill="#3b2a1a" />
    </svg>
  );
}
