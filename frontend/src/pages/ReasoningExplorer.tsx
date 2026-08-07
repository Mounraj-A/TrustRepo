import { useAnalysisStore } from '@/store';
import EmptyState from '@/components/EmptyState';
import { Brain, FileText, CheckCircle2, AlertTriangle, ArrowRight, XCircle, Search } from 'lucide-react';
import { useState } from 'react';

export default function ReasoningExplorer() {
  const { analysisResult, isAnalyzing } = useAnalysisStore();
  const [selectedClaimId, setSelectedClaimId] = useState<string | null>(null);

  if (!analysisResult && !isAnalyzing) return <EmptyState />;

  const claims = analysisResult?.report?.claim_reports || [];
  
  const selectedClaim = claims.find(c => c.claim_id === selectedClaimId);

  return (
    <div className="p-6 h-[calc(100vh-80px)] animate-in flex flex-col">
      <h1 className="text-2xl font-bold flex items-center gap-2 mb-6 shrink-0">
        <Brain size={20} className="text-primary" />
        Reasoning Explorer
      </h1>

      <div className="flex gap-6 h-full min-h-0">
        {/* Left pane: Claims list */}
        <div className="w-1/3 flex flex-col gap-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" size={16} />
            <input 
              type="text" 
              placeholder="Search claims..." 
              className="w-full bg-muted/30 border border-border rounded-lg pl-9 pr-4 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-primary"
            />
          </div>
          
          <div className="flex-1 overflow-y-auto pr-2 space-y-3 custom-scrollbar">
            {claims.map((claim) => (
              <div 
                key={claim.claim_id}
                onClick={() => setSelectedClaimId(claim.claim_id)}
                className={`glass p-4 rounded-xl cursor-pointer transition-all hover:bg-muted/20 border ${
                  selectedClaimId === claim.claim_id ? 'border-primary/50 bg-primary/5 shadow-[0_0_15px_rgba(59,130,246,0.1)]' : 'border-transparent'
                }`}
              >
                <div className="flex items-start justify-between mb-2">
                  <span className={`text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full ${
                    claim.verdict === 'VERIFIED' ? 'bg-emerald-500/10 text-emerald-400' :
                    claim.verdict === 'CONTRADICTION' ? 'bg-red-500/10 text-red-400' :
                    'bg-amber-500/10 text-amber-400'
                  }`}>
                    {claim.verdict.replace('_', ' ')}
                  </span>
                  <span className="text-xs font-mono text-muted-foreground">{Math.round(claim.trust_score)}% Trust</span>
                </div>
                <p className="text-sm line-clamp-3 text-foreground/90">{claim.claim_text}</p>
              </div>
            ))}
            {claims.length === 0 && !isAnalyzing && (
              <div className="text-center text-sm text-muted-foreground mt-10">No claims extracted.</div>
            )}
          </div>
        </div>

        {/* Right pane: Reasoning Trace */}
        <div className="w-2/3 glass rounded-2xl overflow-hidden flex flex-col border border-border/50">
          {selectedClaim ? (
            <div className="flex-1 overflow-y-auto p-6 space-y-8 custom-scrollbar">
              
              {/* Header */}
              <div>
                <h2 className="text-lg font-semibold mb-2 flex items-center gap-2">
                  <FileText size={16} className="text-primary" /> 
                  Claim Context
                </h2>
                <div className="bg-muted/20 border border-border/50 rounded-xl p-4 text-sm leading-relaxed">
                  {selectedClaim.claim_text}
                </div>
              </div>

              {/* Expected vs Observed */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <h3 className="text-sm font-semibold text-muted-foreground">Expected Features (Doc)</h3>
                  <div className="flex flex-wrap gap-2">
                    {selectedClaim.expected_features.length > 0 ? selectedClaim.expected_features.map(f => (
                      <span key={f} className="text-xs bg-muted/40 px-2 py-1 rounded-md border border-border/50">{f}</span>
                    )) : <span className="text-xs text-muted-foreground">None</span>}
                  </div>
                </div>
                <div className="space-y-2">
                  <h3 className="text-sm font-semibold text-muted-foreground">Observed Features (Code)</h3>
                  <div className="flex flex-wrap gap-2">
                    {selectedClaim.observed_features.length > 0 ? selectedClaim.observed_features.map(f => (
                      <span key={f} className="text-xs bg-emerald-500/10 text-emerald-400 px-2 py-1 rounded-md border border-emerald-500/20">{f}</span>
                    )) : <span className="text-xs text-muted-foreground">None</span>}
                  </div>
                </div>
              </div>

              {/* Metrics */}
              <div>
                <h3 className="text-sm font-semibold mb-3 flex items-center gap-2">
                  <Brain size={16} className="text-primary" /> Verification Metrics
                </h3>
                <div className="grid grid-cols-4 gap-3">
                  <div className="bg-muted/20 rounded-lg p-3 text-center border border-border/30">
                    <p className="text-xs text-muted-foreground">Evidence Count</p>
                    <p className="font-mono text-lg mt-1">{selectedClaim.evidence_count}</p>
                  </div>
                  <div className="bg-muted/20 rounded-lg p-3 text-center border border-border/30">
                    <p className="text-xs text-muted-foreground">Quality</p>
                    <p className="font-mono text-lg mt-1">{(selectedClaim.evidence_quality * 100).toFixed(0)}%</p>
                  </div>
                  <div className="bg-muted/20 rounded-lg p-3 text-center border border-border/30">
                    <p className="text-xs text-muted-foreground">Connectivity</p>
                    <p className="font-mono text-lg mt-1">{(selectedClaim.graph_connectivity * 100).toFixed(0)}%</p>
                  </div>
                  <div className="bg-muted/20 rounded-lg p-3 text-center border border-border/30">
                    <p className="text-xs text-muted-foreground">Agreement</p>
                    <p className="font-mono text-lg mt-1">{(selectedClaim.evidence_agreement * 100).toFixed(0)}%</p>
                  </div>
                </div>
              </div>

              {/* Conflict List */}
              {selectedClaim.contradicted_features.length > 0 && (
                <div>
                  <h3 className="text-sm font-semibold text-red-400 mb-3 flex items-center gap-2">
                    <XCircle size={16} /> Contradictions Detected
                  </h3>
                  <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4 space-y-2">
                    {selectedClaim.contradicted_features.map((c, i) => (
                      <p key={i} className="text-sm text-red-200 flex items-center gap-2">
                        <ArrowRight size={12} className="shrink-0" /> {c}
                      </p>
                    ))}
                  </div>
                </div>
              )}

              {/* Reasoning Trace (Timeline) */}
              <div>
                <h3 className="text-sm font-semibold mb-4 flex items-center gap-2">
                  <GitGraph size={16} className="text-primary" /> Reasoning Trace
                </h3>
                <div className="relative pl-4 space-y-4 before:content-[''] before:absolute before:left-1 before:top-2 before:bottom-2 before:w-[2px] before:bg-border">
                  {selectedClaim.reasoning_trace?.length > 0 ? selectedClaim.reasoning_trace.map((step, index) => (
                    <div key={index} className="relative">
                      <div className="absolute -left-[21px] top-1.5 w-2.5 h-2.5 rounded-full bg-primary ring-4 ring-background" />
                      <p className="text-sm text-foreground/80 leading-relaxed bg-muted/10 p-3 rounded-lg border border-border/50">{step}</p>
                    </div>
                  )) : (
                    <p className="text-sm text-muted-foreground">No reasoning trace available.</p>
                  )}
                </div>
              </div>

              {/* Explanation (LLM Output) */}
              {selectedClaim.explanation && (
                <div className="mt-8 border-t border-border/50 pt-6">
                  <h3 className="text-sm font-semibold mb-3">Synthesized Explanation</h3>
                  <p className="text-sm leading-relaxed text-muted-foreground bg-primary/5 p-4 rounded-xl border border-primary/20 italic">
                    "{selectedClaim.explanation}"
                  </p>
                </div>
              )}

            </div>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-muted-foreground">
              <Brain size={48} className="mb-4 opacity-20" />
              <p>Select a claim to view its evidence and reasoning timeline.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
