import { cn, formatNumber } from '@/lib/utils';
import { LucideIcon } from 'lucide-react';
import { motion } from 'framer-motion';

interface MetricsCardProps {
  label: string;
  value: string | number | undefined;
  subValue?: string;
  icon: LucideIcon;
  trend?: 'up' | 'down' | 'neutral';
  color?: 'primary' | 'emerald' | 'amber' | 'red' | 'violet';
  className?: string;
  loading?: boolean;
}

const colorMap = {
  primary: 'text-primary bg-primary/10',
  emerald: 'text-emerald-400 bg-emerald-500/10',
  amber:   'text-amber-400  bg-amber-500/10',
  red:     'text-red-400    bg-red-500/10',
  violet:  'text-violet-400 bg-violet-500/10',
};

export default function MetricsCard({
  label, value, subValue, icon: Icon, color = 'primary', className, loading,
}: MetricsCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={cn('metric-card', className)}
    >
      {loading ? (
        <div className="space-y-3">
          <div className="h-4 rounded shimmer" />
          <div className="h-7 w-2/3 rounded shimmer" />
          <div className="h-3 w-1/2 rounded shimmer" />
        </div>
      ) : (
        <>
          <div className="flex items-start justify-between mb-3">
            <p className="text-xs text-muted-foreground font-medium uppercase tracking-wider">{label}</p>
            <div className={cn('p-2 rounded-lg', colorMap[color])}>
              <Icon size={14} />
            </div>
          </div>
          <p className="text-2xl font-bold tracking-tight">
            {typeof value === 'number' ? formatNumber(value) : (value ?? '—')}
          </p>
          {subValue && (
            <p className="text-xs text-muted-foreground mt-1">{subValue}</p>
          )}
        </>
      )}
    </motion.div>
  );
}
