export function CowHero({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 320 320" className={className} role="img" aria-label="Ilustración de una vaca en el campo">
      <defs>
        <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#dff2e1" />
          <stop offset="100%" stopColor="#f4ede1" />
        </linearGradient>
      </defs>

      <rect x="0" y="0" width="320" height="320" rx="24" fill="url(#sky)" />
      <circle cx="256" cy="64" r="30" fill="#ffd873" opacity="0.9" />
      <path d="M0 240c60-24 100-24 160-6s120 18 160-6v92H0z" fill="#4f8a55" />
      <path d="M0 258c50-16 110-14 160 2s110 14 160-4v64H0z" fill="#3f7548" />

      <ellipse cx="160" cy="205" rx="78" ry="46" fill="#fffdf9" stroke="#3b2a1a" strokeWidth="3" />
      <path
        d="M96 178c14-10 34-10 40 8-12 10-34 8-40-8zM224 178c-14-10-34-10-40 8 12 10 34 8 40-8z"
        fill="#3b2a1a"
      />
      <path d="M200 190c16 8 20 26 10 38-14-2-26-14-26-30 6-6 10-8 16-8z" fill="#3b2a1a" opacity="0.85" />

      <rect x="120" y="240" width="16" height="34" rx="6" fill="#fffdf9" stroke="#3b2a1a" strokeWidth="3" />
      <rect x="184" y="240" width="16" height="34" rx="6" fill="#fffdf9" stroke="#3b2a1a" strokeWidth="3" />
      <rect x="120" y="240" width="16" height="12" rx="4" fill="#3b2a1a" />
      <rect x="184" y="240" width="16" height="12" rx="4" fill="#3b2a1a" />

      <ellipse cx="110" cy="150" rx="30" ry="34" fill="#fffdf9" stroke="#3b2a1a" strokeWidth="3" />
      <ellipse cx="88" cy="132" rx="9" ry="12" fill="#f4ede1" stroke="#3b2a1a" strokeWidth="2.5" />
      <ellipse cx="118" cy="122" rx="9" ry="12" fill="#f4ede1" stroke="#3b2a1a" strokeWidth="2.5" />
      <ellipse cx="88" cy="132" rx="4" ry="5.5" fill="#e8a2b0" />
      <ellipse cx="118" cy="122" rx="4" ry="5.5" fill="#e8a2b0" />
      <path
        d="M82 118c1.5-6 6-9 9-9M124 108c-1.5-6-6-9-9-9"
        stroke="#3b2a1a"
        strokeWidth="2.5"
        strokeLinecap="round"
        fill="none"
      />
      <circle cx="98" cy="148" r="3" fill="#3b2a1a" />
      <circle cx="120" cy="146" r="3" fill="#3b2a1a" />
      <ellipse cx="106" cy="164" rx="15" ry="11" fill="#f6c9d4" stroke="#3b2a1a" strokeWidth="2.5" />
      <circle cx="101" cy="165" r="2" fill="#3b2a1a" />
      <circle cx="112" cy="165" r="2" fill="#3b2a1a" />

      <ellipse cx="60" cy="290" rx="14" ry="6" fill="#3f7548" opacity="0.5" />
      <ellipse cx="250" cy="296" rx="20" ry="7" fill="#3f7548" opacity="0.5" />
    </svg>
  );
}
