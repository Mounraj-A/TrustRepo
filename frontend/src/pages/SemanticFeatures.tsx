import { useAnalysisStore } from '@/store';
import EmptyState from '@/components/EmptyState';
import { Layers, CheckCircle2, Link2, Database } from 'lucide-react';
import { motion } from 'framer-motion';

export default function SemanticFeatures() {
  const { analysisResult, isAnalyzing } = useAnalysisStore();
  if (!analysisResult && !isAnalyzing) return <EmptyState />;

  const graph = analysisResult?.graph_metrics;
  const features = graph?.features ?? [];
  const capabilities = graph?.capabilities ?? [];

  const featureCapMap: Record<string, string[]> = {};
  features.forEach((f) => {
    featureCapMap[f] = capabilities.filter((cap) =>
      cap.toLowerCase().includes(f.toLowerCase().split(' ')[0])
    );
  });

  return (
    <div className="p-6 space-y-6 animate-in">
      <h1 className="text-2xl font-bold flex items-center gap-2">
        <Layers size={20} className="text-primary" />
        Semantic Features
      </h1>

      <div className="grid grid-cols-2 gap-4">
        <div className="metric-card">
          <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Features Extracted</p>
          <p className="text-3xl font-bold">{features.length}</p>
        </div>
        <div className="metric-card">
          <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Evidence Chains</p>
          <p className="text-3xl font-bold">{graph?.evidence_chain_count ?? 0}</p>
        </div>
      </div>

      {features.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {features.map((feat, idx) => (
            <motion.div
              key={feat}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.08 }}
              className="glass rounded-xl p-5 hover:border-primary/30 transition-all"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="p-2 bg-primary/10 rounded-lg">
                  <Layers size={14} className="text-primary" />
                </div>
                <span className="status-badge bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  Detected
                </span>
              </div>
              <h3 className="font-semibold text-sm mb-2">{feat}</h3>

              <div className="flex items-center gap-1 text-xs text-muted-foreground">
                <CheckCircle2 size={10} className="text-emerald-400" />
                <span>Evidence-backed detection</span>
              </div>

              {featureCapMap[feat]?.length > 0 && (
                <div className="mt-3 pt-3 border-t border-border">
                  <p className="text-[10px] text-muted-foreground mb-1.5 uppercase tracking-wide">Capabilities</p>
                  <div className="flex flex-wrap gap-1">
                    {featureCapMap[feat].map((cap) => (
                      <span key={cap} className="status-badge bg-violet-500/10 text-violet-400 border border-violet-500/20 text-[10px]">
                        {cap}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </motion.div>
          ))}
        </div>
      ) : (
        <div className="glass rounded-2xl p-8 text-center text-muted-foreground">
          <Layers size={32} className="mx-auto mb-3 opacity-30" />
          <p>No semantic features detected.</p>
          <p className="text-sm mt-1">Ensure the repository has parseable source code.</p>
        </div>
      )}
    </div>
  );
}
