import { motion } from 'framer-motion';
import { CheckCircle2, XCircle, SkipForward, Clock, AlertCircle } from 'lucide-react';
import { cn, formatDuration, formatNumber, statusColor } from '@/lib/utils';
import type { LayerTrace } from '@/types/api';

interface PipelineTimelineProps {
  traces: LayerTrace[];
  className?: string;
}

const STATUS_ICON = {
  OK: CheckCircle2,
  FAILED: XCircle,
  SKIPPED: SkipForward,
  PENDING: Clock,
};

export default function PipelineTimeline({ traces, className }: PipelineTimelineProps) {
  if (!traces?.length) {
    return (
      <div className="text-center py-10 text-muted-foreground text-sm">
        No execution trace available. Run an analysis first.
      </div>
    );
  }

  const totalTime = traces.reduce((acc, t) => acc + t.time_s, 0);

  return (
    <div className={cn('space-y-1', className)}>
      {traces.map((trace, idx) => {
        const Icon = STATUS_ICON[trace.status] ?? AlertCircle;
        const widthPct = totalTime > 0 ? (trace.time_s / totalTime) * 100 : 0;

        return (
          <motion.div
            key={idx}
            initial={{ opacity: 0, x: -12 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3, delay: idx * 0.06 }}
            className="group glass rounded-xl p-4 hover:border-primary/30 transition-all"
          >
            <div className="flex items-start gap-3">
              {/* Icon */}
              <div className={cn('mt-0.5 p-1.5 rounded-lg shrink-0',
                trace.status === 'OK' ? 'bg-emerald-500/10' :
                  trace.status === 'FAILED' ? 'bg-red-500/10' :
                    trace.status === 'SKIPPED' ? 'bg-slate-500/10' :
                      'bg-amber-500/10'
              )}>
                <Icon size={13} className={statusColor(trace.status)} />
              </div>

              <div className="flex-1 min-w-0">
                {/* Layer name + status + time */}
                <div className="flex items-center justify-between gap-3 flex-wrap">
                  <p className="text-sm font-semibold">{trace.layer}</p>
                  <div className="flex items-center gap-3 text-xs text-muted-foreground">
                    <span className={cn('font-mono font-medium', statusColor(trace.status))}>
                      {trace.status}
                    </span>
                    <span className="font-mono">{formatDuration(trace.time_s)}</span>
                  </div>
                </div>

                {/* Progress bar */}
                {trace.status === 'OK' && (
                  <div className="mt-2 h-1 bg-border rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${widthPct}%` }}
                      transition={{ duration: 0.8, delay: idx * 0.06 + 0.2 }}
                      className="h-full rounded-full bg-primary/60"
                    />
                  </div>
                )}

                {/* Details grid */}
                <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted-foreground">
                  {trace.objects_created > 0 && (
                    <span>Objects: <span className="text-foreground font-medium">{formatNumber(trace.objects_created)}</span></span>
                  )}
                  {trace.evidence_count > 0 && (
                    <span>Evidence: <span className="text-foreground font-medium">{formatNumber(trace.evidence_count)}</span></span>
                  )}
                  {Object.entries(trace.details || {}).slice(0, 4).map(([k, v]) => (
                    v !== undefined && v !== null && (
                      <span key={k}>
                        {k.replace(/_/g, ' ')}:{' '}
                        <span className="text-foreground font-medium">
                          {typeof v === 'object' ? JSON.stringify(v).slice(0, 40) : String(v)}
                        </span>
                      </span>
                    )
                  ))}
                </div>

                {/* Warnings / Errors */}
                {trace.warnings?.length > 0 && (
                  <div className="mt-2 space-y-0.5">
                    {trace.warnings.map((w, i) => (
                      <p key={i} className="text-[11px] text-amber-400 flex items-start gap-1.5">
                        <AlertCircle size={10} className="mt-0.5 shrink-0" />
                        {w}
                      </p>
                    ))}
                  </div>
                )}
                {trace.errors?.length > 0 && (
                  <div className="mt-2 space-y-0.5">
                    {trace.errors.map((e, i) => (
                      <p key={i} className="text-[11px] text-red-400 flex items-start gap-1.5">
                        <XCircle size={10} className="mt-0.5 shrink-0" />
                        {e}
                      </p>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        );
      })}

      {/* Total */}
      <div className="flex justify-end pt-1 text-xs text-muted-foreground">
        Total: <span className="ml-1 font-mono font-medium text-foreground">{formatDuration(totalTime)}</span>
      </div>
    </div>
  );
}
