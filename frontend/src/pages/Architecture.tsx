import { useAnalysisStore } from '@/store';
import EmptyState from '@/components/EmptyState';
import { Building2, Layers, ArrowRight } from 'lucide-react';
import { motion } from 'framer-motion';

const ARCH_DESCRIPTIONS: Record<string, string> = {
  'REST API': 'Exposes HTTP endpoints following REST constraints. Supports CRUD operations over resources.',
  'Secured Application': 'Authentication & Authorization enforced. CORS, session, or JWT-based security detected.',
  'Layered MVC': 'Model-View-Controller pattern. Clear separation between data, logic, and presentation.',
  'Microservices': 'Distributed service architecture. Multiple independent deployable services.',
  'Monolith': 'Single deployable unit. All components tightly coupled in one codebase.',
};

export default function Architecture() {
  const { analysisResult, isAnalyzing } = useAnalysisStore();
  if (!analysisResult && !isAnalyzing) return <EmptyState />;

  const graph = analysisResult?.graph_metrics;
  const architectures = graph?.architectures ?? [];
  const features = graph?.features ?? [];
  const capabilities = graph?.capabilities ?? [];

  return (
    <div className="p-6 space-y-6 animate-in">
      <h1 className="text-2xl font-bold flex items-center gap-2">
        <Building2 size={20} className="text-primary" />
        Architecture
      </h1>

      {architectures.length > 0 ? (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {architectures.map((arch, idx) => (
              <motion.div
                key={arch}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.1 }}
                className="glass rounded-2xl p-6 border border-primary/20"
              >
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <p className="text-xs text-muted-foreground mb-1">Architecture Pattern</p>
                    <h2 className="text-xl font-bold gradient-text">{arch}</h2>
                  </div>
                  <div className="p-2.5 bg-primary/10 rounded-xl">
                    <Building2 size={18} className="text-primary" />
                  </div>
                </div>

                <p className="text-sm text-muted-foreground mb-4">
                  {ARCH_DESCRIPTIONS[arch] ?? 'Architecture pattern detected from code structure and semantic features.'}
                </p>

                <div className="space-y-3">
                  <div>
                    <p className="text-[10px] text-muted-foreground uppercase tracking-wide mb-1.5">Evidence (Features)</p>
                    <div className="flex flex-wrap gap-1">
                      {features.map((f) => (
                        <span key={f} className="status-badge bg-primary/10 text-primary border border-primary/20 text-[10px]">{f}</span>
                      ))}
                    </div>
                  </div>
                  <div>
                    <p className="text-[10px] text-muted-foreground uppercase tracking-wide mb-1.5">Capabilities Driving This</p>
                    <div className="flex flex-wrap gap-1">
                      {capabilities.map((c) => (
                        <span key={c} className="status-badge bg-violet-500/10 text-violet-400 border border-violet-500/20 text-[10px]">{c}</span>
                      ))}
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>

          {/* Pipeline flow */}
          <div className="glass rounded-2xl p-6">
            <h2 className="text-sm font-semibold mb-4">Architecture Detection Evidence Flow</h2>
            <div className="flex flex-wrap items-center gap-2 text-sm">
              {[
                'Code Parser', 'AST', 'UIR', 'Knowledge Graph',
                'Technology Detection', 'Feature Extraction', 'Semantic Registry',
                'Architecture Detection',
              ].map((step, i, arr) => (
                <span key={step} className="flex items-center gap-2">
                  <span className="status-badge bg-muted/60 text-foreground border border-border">{step}</span>
                  {i < arr.length - 1 && <ArrowRight size={12} className="text-muted-foreground shrink-0" />}
                </span>
              ))}
            </div>
          </div>
        </>
      ) : (
        <div className="glass rounded-2xl p-8 text-center text-muted-foreground">
          <Building2 size={32} className="mx-auto mb-3 opacity-30" />
          <p>No architecture patterns detected.</p>
          <p className="text-sm mt-1">Ensure the repository has sufficient code structure for analysis.</p>
        </div>
      )}
    </div>
  );
}
