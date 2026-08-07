import { useAnalysisStore } from '@/store';
import EmptyState from '@/components/EmptyState';
import { Search, Link2, FileText, GitGraph } from 'lucide-react';

export default function EvidenceExplorer() {
  const { analysisResult, isAnalyzing } = useAnalysisStore();
  if (!analysisResult && !isAnalyzing) return <EmptyState />;

  const graph = analysisResult?.graph_metrics;
  const trace = analysisResult?.execution_trace ?? [];
  const evidenceLayer = trace.find(t => t.layer.includes('Evidence'));

  const evidenceCount = graph?.evidence_chain_count ?? 0;
  const totalObjects = evidenceLayer?.objects_created ?? 0;

  return (
    <div className="p-6 space-y-6 animate-in">
      <h1 className="text-2xl font-bold flex items-center gap-2">
        <Search size={20} className="text-primary" />
        Evidence Explorer
      </h1>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="metric-card">
          <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Evidence Chains</p>
          <p className="text-3xl font-bold">{evidenceCount}</p>
        </div>
        <div className="metric-card">
          <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Claim Evidence Sets</p>
          <p className="text-3xl font-bold">{totalObjects}</p>
        </div>
        <div className="metric-card">
          <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Graph Nodes</p>
          <p className="text-3xl font-bold">{graph?.nodes ?? 0}</p>
        </div>
        <div className="metric-card">
          <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Graph Edges</p>
          <p className="text-3xl font-bold">{graph?.edges ?? 0}</p>
        </div>
      </div>

      {/* Evidence pipeline description */}
      <div className="glass rounded-2xl p-6">
        <h2 className="text-sm font-semibold mb-4">Evidence Pipeline Architecture</h2>
        <div className="space-y-3">
          {[
            { icon: FileText, step: '1. Document Parsing', desc: 'Claims extracted from README/documentation via section parsing and atomic statement normalization.' },
            { icon: GitGraph, step: '2. Code Evidence', desc: 'AST nodes (Annotations, Imports, Classes, Dependencies) matched to claim intents via the Semantic Registry.' },
            { icon: Search, step: '3. Evidence Retrieval', desc: 'Pre-collected evidence from the Knowledge Graph matched to each normalized claim.' },
            { icon: Link2, step: '4. Evidence Fusion', desc: 'Multi-stream evidence from Code Agent, Documentation Agent, and KG Agent fused and ranked by confidence.' },
          ].map(({ icon: Icon, step, desc }) => (
            <div key={step} className="flex items-start gap-4 p-4 bg-muted/30 rounded-xl">
              <div className="p-2 bg-primary/10 rounded-lg shrink-0">
                <Icon size={14} className="text-primary" />
              </div>
              <div>
                <p className="text-sm font-semibold">{step}</p>
                <p className="text-xs text-muted-foreground mt-1">{desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Layer trace */}
      {evidenceLayer && (
        <div className="glass rounded-2xl p-6">
          <h2 className="text-sm font-semibold mb-3">Layer 4: Evidence Retrieval — Runtime Trace</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            <div className="bg-muted/40 rounded-xl p-4">
              <p className="text-xs text-muted-foreground">Status</p>
              <p className={`text-lg font-bold mt-1 ${evidenceLayer.status === 'OK' ? 'text-emerald-400' : 'text-red-400'}`}>
                {evidenceLayer.status}
              </p>
            </div>
            <div className="bg-muted/40 rounded-xl p-4">
              <p className="text-xs text-muted-foreground">Objects Created</p>
              <p className="text-lg font-bold mt-1">{evidenceLayer.objects_created}</p>
            </div>
            <div className="bg-muted/40 rounded-xl p-4">
              <p className="text-xs text-muted-foreground">Execution Time</p>
              <p className="text-lg font-bold mt-1 font-mono">{(evidenceLayer.time_s * 1000).toFixed(1)}ms</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
