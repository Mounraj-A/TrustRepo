import { useAnalysisStore } from '@/store';
import EmptyState from '@/components/EmptyState';
import { Zap, ArrowRight } from 'lucide-react';
import { motion } from 'framer-motion';

const CAP_COLORS: Record<string, { bg: string; text: string; border: string }> = {
  'API Infrastructure':      { bg: 'bg-blue-500/10',   text: 'text-blue-400',   border: 'border-blue-500/20' },
  'Authentication & Security':{ bg: 'bg-amber-500/10', text: 'text-amber-400',  border: 'border-amber-500/20' },
  'Database Management':     { bg: 'bg-emerald-500/10', text: 'text-emerald-400', border: 'border-emerald-500/20' },
  'Frontend / UI':           { bg: 'bg-violet-500/10', text: 'text-violet-400', border: 'border-violet-500/20' },
  'Caching':                 { bg: 'bg-cyan-500/10',   text: 'text-cyan-400',   border: 'border-cyan-500/20' },
};

const DEFAULT_STYLE = { bg: 'bg-primary/10', text: 'text-primary', border: 'border-primary/20' };

export default function Capabilities() {
  const { analysisResult, isAnalyzing } = useAnalysisStore();
  if (!analysisResult && !isAnalyzing) return <EmptyState />;

  const graph = analysisResult?.graph_metrics;
  const capabilities = graph?.capabilities ?? [];
  const features = graph?.features ?? [];
  const technologies = graph?.technologies ?? [];

  return (
    <div className="p-6 space-y-6 animate-in">
      <h1 className="text-2xl font-bold flex items-center gap-2">
        <Zap size={20} className="text-primary" />
        Capabilities
      </h1>

      {capabilities.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
          {capabilities.map((cap, idx) => {
            const style = CAP_COLORS[cap] ?? DEFAULT_STYLE;
            const supportingFeatures = features.filter((f) =>
              cap.toLowerCase().includes(f.toLowerCase().split(' ')[0]) ||
              f.toLowerCase().includes(cap.toLowerCase().split(' ')[0])
            );
            const supportingTechs = technologies.slice(0, 3);

            return (
              <motion.div
                key={cap}
                initial={{ opacity: 0, scale: 0.97 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: idx * 0.08, type: 'spring', stiffness: 200, damping: 20 }}
                className={`glass rounded-2xl p-6 border ${style.border}`}
              >
                <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-lg ${style.bg} mb-4`}>
                  <Zap size={13} className={style.text} />
                  <span className={`text-xs font-bold ${style.text}`}>{cap}</span>
                </div>

                <p className="text-xs text-muted-foreground mb-4">
                  System capability derived from graph evidence and feature detection.
                </p>

                {supportingFeatures.length > 0 && (
                  <div className="mb-3">
                    <p className="text-[10px] text-muted-foreground uppercase tracking-wide mb-1.5">
                      Supporting Features
                    </p>
                    <div className="flex flex-wrap gap-1">
                      {supportingFeatures.map((f) => (
                        <span key={f} className="status-badge bg-muted/60 text-foreground border border-border text-[10px]">{f}</span>
                      ))}
                    </div>
                  </div>
                )}

                <div className="flex items-center gap-1 text-xs text-muted-foreground">
                  <ArrowRight size={10} className={style.text} />
                  <span>{supportingTechs.slice(0, 2).join(', ')}{supportingTechs.length > 2 ? ` +${supportingTechs.length - 2}` : ''}</span>
                </div>
              </motion.div>
            );
          })}
        </div>
      ) : (
        <div className="glass rounded-2xl p-8 text-center text-muted-foreground">
          <Zap size={32} className="mx-auto mb-3 opacity-30" />
          <p>No capabilities detected.</p>
        </div>
      )}
    </div>
  );
}
