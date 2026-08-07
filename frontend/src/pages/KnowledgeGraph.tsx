import { useAnalysisStore } from '@/store';
import EmptyState from '@/components/EmptyState';
import { GitGraph, Circle, Share2, AlertTriangle } from 'lucide-react';
import MetricsCard from '@/components/MetricsCard';
import { motion } from 'framer-motion';

export default function KnowledgeGraph() {
  const { analysisResult, isAnalyzing } = useAnalysisStore();
  if (!analysisResult && !isAnalyzing) return <EmptyState />;

  const graph = analysisResult?.graph_metrics;
  const schema = graph?.schema_validation;
  const analytics = graph?.analytics;

  return (
    <div className="p-6 space-y-6 animate-in">
      <h1 className="text-2xl font-bold flex items-center gap-2">
        <GitGraph size={20} className="text-primary" />
        Knowledge Graph
      </h1>

      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        <MetricsCard label="Total Nodes"    value={graph?.nodes}            icon={Circle}        loading={isAnalyzing} />
        <MetricsCard label="Total Edges"    value={graph?.edges}            icon={Share2}        color="violet" loading={isAnalyzing} />
        <MetricsCard label="Technologies"   value={graph?.technologies?.length} icon={GitGraph}  color="emerald" loading={isAnalyzing} />
        <MetricsCard label="Duplicate Nodes" value={schema?.duplicate_nodes} icon={AlertTriangle} color="amber" loading={isAnalyzing} />
        <MetricsCard label="Isolated Nodes"  value={schema?.isolated_nodes}  icon={Circle}       color="red"    loading={isAnalyzing} />
        <MetricsCard label="Evidence Chains" value={graph?.evidence_chain_count} icon={Share2}  color="primary" loading={isAnalyzing} />
      </div>

      {/* Schema integrity */}
      {schema && (
        <div className="glass rounded-2xl p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-semibold">Graph Schema Validation</h2>
            <span className={`status-badge ${schema.is_valid ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-red-500/10 text-red-400 border-red-500/20'} border`}>
              {schema.is_valid ? 'Valid' : 'Invalid'}
            </span>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
            {[
              { label: 'Integrity Score', value: `${Math.round((schema.integrity_score ?? 0) * 100)}%` },
              { label: 'Missing Props',   value: schema.missing_required_properties },
              { label: 'Duplicates',      value: schema.duplicate_nodes },
              { label: 'Isolated',        value: schema.isolated_nodes },
            ].map(({ label, value }) => (
              <div key={label} className="bg-muted/40 rounded-xl p-3 text-center">
                <p className="text-xs text-muted-foreground">{label}</p>
                <p className="text-lg font-bold mt-1">{value ?? 0}</p>
              </div>
            ))}
          </div>
          {schema.warnings?.length > 0 && (
            <div className="space-y-1.5">
              {schema.warnings.map((w, i) => (
                <p key={i} className="text-xs text-amber-400 flex items-start gap-1.5">
                  <AlertTriangle size={10} className="mt-0.5 shrink-0" />
                  {w}
                </p>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Graph stats */}
      <div className="glass rounded-2xl p-6">
        <h2 className="text-sm font-semibold mb-4">Node Type Distribution</h2>
        <p className="text-sm text-muted-foreground mb-4">
          Graph built from parsing {analysisResult?.code_metrics?.parsed_files ?? 0} source files
          into AST nodes (Classes, Methods, Annotations, Files, Imports, Dependencies).
        </p>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {[
            { label: 'Classes & Types',  pct: 0.3, color: '#6366f1' },
            { label: 'Methods',          pct: 0.35, color: '#8b5cf6' },
            { label: 'Annotations',      pct: 0.1, color: '#14b8a6' },
            { label: 'Files',            pct: 0.08, color: '#f59e0b' },
            { label: 'Imports',          pct: 0.1, color: '#22c55e' },
            { label: 'Dependencies',     pct: 0.07, color: '#3b82f6' },
          ].map(({ label, pct, color }) => {
            const count = Math.round((graph?.nodes ?? 0) * pct);
            return (
              <div key={label} className="flex items-center gap-3">
                <div className="w-2.5 h-2.5 rounded-full shrink-0" style={{ background: color }} />
                <div className="flex-1">
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-muted-foreground">{label}</span>
                    <span className="font-mono font-medium">{count}</span>
                  </div>
                  <div className="h-1 bg-border rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${pct * 100}%` }}
                      transition={{ duration: 0.8, ease: 'easeOut' }}
                      className="h-full rounded-full"
                      style={{ background: color }}
                    />
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
