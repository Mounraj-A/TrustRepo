import { useAnalysisStore } from '@/store';
import EmptyState from '@/components/EmptyState';
import { Search, BrainCircuit, CheckCircle2, AlertTriangle, XCircle, HelpCircle } from 'lucide-react';
import { useState, useMemo, useEffect } from 'react';
import { DocumentationClaim } from '@/types/api';
import ReasoningClaimCard from './Reasoning/ReasoningClaimCard';
import ReasoningTimeline from './Reasoning/ReasoningTimeline';
import { useLocation } from 'react-router-dom';

export default function ReasoningExplorer() {
  const { analysisResult, isAnalyzing } = useAnalysisStore();
  const [searchQuery, setSearchQuery] = useState('');
  const [activeFilter, setActiveFilter] = useState<string>('ALL');
  const [selectedClaimId, setSelectedClaimId] = useState<string | null>(null);

  // Parse claim query param for deep linking
  const location = useLocation();
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const claimParam = params.get('claim');
    if (claimParam) {
      setSelectedClaimId(claimParam);
    }
  }, [location.search]);

  if (!analysisResult && !isAnalyzing) return <EmptyState />;
  
  if (isAnalyzing && !analysisResult) {
    return (
      <div className="p-6 flex flex-col items-center justify-center min-h-[500px]">
        <div className="w-10 h-10 border-4 border-primary border-t-transparent rounded-full animate-spin mb-4" />
        <p className="text-muted-foreground font-medium">Loading reasoning traces...</p>
      </div>
    );
  }

  const claimsList: DocumentationClaim[] = analysisResult?.report?.documentation_claims || [];
  
  // Extract unique verdicts for the dynamic filters
  const uniqueVerdicts = useMemo(() => {
    const v = new Set<string>();
    claimsList.forEach((c: DocumentationClaim) => {
      if (c.verdict) v.add(c.verdict.toUpperCase());
    });
    return Array.from(v).sort();
  }, [claimsList]);

  // Filter claims based on search query and active filter
  const filteredClaims = useMemo(() => {
    return claimsList.filter((claim: DocumentationClaim) => {
      const v = claim.verdict?.toUpperCase() || '';
      const matchesFilter = activeFilter === 'ALL' || v === activeFilter;
      
      const q = searchQuery.toLowerCase();
      
      // Search text against actual backend reasoning trace fields
      const matchesSearch = 
        claim.claim_text.toLowerCase().includes(q) ||
        (claim.reasoning_trace?.explanation || '').toLowerCase().includes(q) ||
        (claim.reasoning_trace?.steps || []).some((step: any) => 
          step.title.toLowerCase().includes(q) || 
          (step.description || '').toLowerCase().includes(q) ||
          (step.source || '').toLowerCase().includes(q) ||
          (step.source_file || '').toLowerCase().includes(q)
        );
      
      return matchesFilter && matchesSearch;
    });
  }, [claimsList, searchQuery, activeFilter]);

  const selectedClaim = claimsList.find((c: DocumentationClaim) => c.claim_id === selectedClaimId) || null;

  return (
    <div className="p-6 space-y-8 animate-in max-w-7xl mx-auto h-full flex flex-col">
      
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 border-b border-border/50 pb-6 shrink-0">
        <div>
          <div className="inline-flex items-center justify-center p-2.5 bg-gradient-to-br from-primary/20 to-primary/5 text-primary rounded-xl mb-3 shadow-inner">
            <BrainCircuit size={24} />
          </div>
          <h1 className="text-3xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-foreground to-foreground/70 uppercase tracking-tight">
            Reasoning Explorer
          </h1>
          <p className="text-muted-foreground mt-1.5 font-medium">Auditable, step-by-step verification logic derived directly from the backend.</p>
        </div>
        
        <div className="relative w-full md:w-96 group">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-muted-foreground transition-colors group-focus-within:text-primary" size={18} />
          <input 
            type="text" 
            placeholder="Search claims and reasoning..." 
            className="w-full pl-11 pr-4 py-3 bg-background/50 border border-border rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 shadow-sm backdrop-blur-xl transition-all hover:bg-background"
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      {/* Main Two-Panel Layout */}
      <div className="flex flex-col lg:flex-row gap-6 flex-1 min-h-0">
        
        {/* Left Panel: Claim Inventory */}
        <div className="w-full lg:w-1/3 flex flex-col h-[calc(100vh-250px)]">
          <div className="mb-4 shrink-0 overflow-x-auto pb-2">
            <div className="flex gap-2">
              <button 
                onClick={() => setActiveFilter('ALL')}
                className={`px-3 py-1.5 rounded-lg text-xs font-bold tracking-wider uppercase whitespace-nowrap transition-all duration-300 border shadow-sm ${activeFilter === 'ALL' ? 'bg-primary text-primary-foreground border-primary shadow-primary/20 shadow-md scale-105' : 'bg-background hover:bg-muted text-muted-foreground border-border'}`}
              >
                All
              </button>
              {uniqueVerdicts.map(verdict => (
                <button 
                  key={verdict}
                  onClick={() => setActiveFilter(verdict)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-bold tracking-wider uppercase whitespace-nowrap transition-all duration-300 border shadow-sm ${activeFilter === verdict ? 'bg-primary text-primary-foreground border-primary shadow-primary/20 shadow-md scale-105' : 'bg-background hover:bg-muted text-muted-foreground border-border'}`}
                >
                  {verdict.replace('_', ' ')}
                </button>
              ))}
            </div>
          </div>

          <div className="flex-1 overflow-y-auto pr-2 space-y-3 custom-scrollbar">
            {filteredClaims.length === 0 ? (
              <div className="p-8 text-center border border-dashed border-border rounded-xl text-muted-foreground text-sm">
                No claims match your filters.
              </div>
            ) : (
              filteredClaims.map((claim: DocumentationClaim) => (
                <ReasoningClaimCard 
                  key={claim.claim_id} 
                  claim={claim} 
                  isSelected={selectedClaimId === claim.claim_id}
                  onClick={() => setSelectedClaimId(claim.claim_id)} 
                />
              ))
            )}
          </div>
        </div>

        {/* Right Panel: Reasoning Details */}
        <div className="w-full lg:w-2/3 flex flex-col h-[calc(100vh-250px)] glass rounded-2xl border border-border shadow-sm overflow-hidden">
          {selectedClaim ? (
            <div className="flex-1 overflow-y-auto p-6 lg:p-10 custom-scrollbar">
              
              <div className="mb-10 pb-6 border-b border-border/50">
                <div className="text-xs font-bold text-muted-foreground uppercase tracking-wider mb-3">Selected Claim</div>
                <h2 className="text-xl font-medium text-foreground leading-snug">"{selectedClaim.claim_text}"</h2>
                
                <div className="mt-4 flex items-center gap-4">
                  <div className="text-xs font-bold uppercase tracking-wider text-muted-foreground">Verdict:</div>
                  <div className={`px-3 py-1 rounded-md text-xs font-bold uppercase tracking-wider border ${getVerdictColorStyle(selectedClaim.verdict)}`}>
                    {selectedClaim.verdict.replace('_', ' ')}
                  </div>
                </div>
              </div>

              <ReasoningTimeline trace={selectedClaim.reasoning_trace || null} />

            </div>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center p-12 text-center text-muted-foreground">
              <BrainCircuit size={48} className="text-muted/30 mb-6" />
              <h3 className="text-lg font-medium text-foreground mb-2">Select a claim</h3>
              <p className="text-sm max-w-sm">Choose a documentation claim from the list to view its authoritative verification path.</p>
            </div>
          )}
        </div>

      </div>
    </div>
  );
}

// Helper for the verdict badge color in the header
function getVerdictColorStyle(v: string) {
  const verdict = v.toUpperCase();
  if (verdict === 'VERIFIED') return 'bg-emerald-50 text-emerald-600 border-emerald-200';
  if (verdict === 'PARTIALLY_VERIFIED' || verdict === 'UNSUPPORTED') return 'bg-amber-50 text-amber-600 border-amber-200';
  if (verdict === 'CONTRADICTED') return 'bg-rose-50 text-rose-600 border-rose-200';
  if (verdict === 'MISSING_DOCUMENTATION') return 'bg-orange-50 text-orange-600 border-orange-200';
  return 'bg-indigo-50 text-indigo-600 border-indigo-200';
}
