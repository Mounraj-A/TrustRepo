import { cn, scoreColor, scoreGradient } from '@/lib/utils';
import { motion } from 'framer-motion';
import { ShieldCheck } from 'lucide-react';

interface TrustScoreGaugeProps {
  score: number;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
  className?: string;
}

const SIZES = {
  sm: { outer: 96, stroke: 8, fontSize: 'text-xl', icon: 14 },
  md: { outer: 140, stroke: 10, fontSize: 'text-3xl', icon: 18 },
  lg: { outer: 200, stroke: 14, fontSize: 'text-5xl', icon: 24 },
};

export default function TrustScoreGauge({
  score, size = 'md', showLabel = true, className,
}: TrustScoreGaugeProps) {
  const { outer, stroke, fontSize, icon } = SIZES[size];
  const radius = (outer - stroke) / 2;
  const circumference = 2 * Math.PI * radius;
  const pct = Math.min(Math.max(score, 0), 1);
  const offset = circumference * (1 - pct);
  const displayScore = Math.round(pct * 100);

  const gradientId = `trust-gradient-${size}`;

  return (
    <div className={cn('flex flex-col items-center gap-3', className)}>
      <div className="relative trust-ring" style={{ width: outer, height: outer }}>
        <svg width={outer} height={outer} viewBox={`0 0 ${outer} ${outer}`} className="rotate-[-90deg]">
          <defs>
            <linearGradient id={gradientId} x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor={pct >= 0.8 ? '#10b981' : pct >= 0.6 ? '#f59e0b' : '#ef4444'} />
              <stop offset="100%" stopColor={pct >= 0.8 ? '#34d399' : pct >= 0.6 ? '#fcd34d' : '#f87171'} />
            </linearGradient>
          </defs>
          {/* Track */}
          <circle
            cx={outer / 2} cy={outer / 2} r={radius}
            fill="none"
            stroke="hsl(var(--border))"
            strokeWidth={stroke}
          />
          {/* Value arc */}
          <motion.circle
            cx={outer / 2} cy={outer / 2} r={radius}
            fill="none"
            stroke={`url(#${gradientId})`}
            strokeWidth={stroke}
            strokeLinecap="round"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: offset }}
            transition={{ duration: 1.2, ease: 'easeOut' }}
          />
        </svg>

        {/* Center value */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <ShieldCheck size={icon} className={scoreColor(pct)} />
          <motion.span
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
            className={cn('font-extrabold tabular-nums', fontSize, scoreColor(pct))}
          >
            {displayScore}
          </motion.span>
          {showLabel && size !== 'sm' && (
            <span className="text-[10px] text-muted-foreground">/ 100</span>
          )}
        </div>
      </div>

      {showLabel && (
        <div className="text-center">
          <p className={cn('font-semibold', scoreColor(pct))}>
            {displayScore >= 80 ? 'Highly Trustworthy'
              : displayScore >= 60 ? 'Moderately Trustworthy'
                : displayScore >= 40 ? 'Low Trust'
                  : 'Untrusted'}
          </p>
          <p className="text-xs text-muted-foreground">Repository Trust Score</p>
        </div>
      )}
    </div>
  );
}
