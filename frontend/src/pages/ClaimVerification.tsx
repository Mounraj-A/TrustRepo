import { useAnalysisStore } from '@/store';
import EmptyState from '@/components/EmptyState';
import { ClipboardCheck, Search } from 'lucide-react';
import ClaimCard from './ClaimVerification/ClaimCard';
import ClaimEvidenceDrawer from './ClaimVerification/ClaimEvidenceDrawer';
import { useState, useMemo } from 'react';
import { DocumentationClaim } from '@/types/api';

type FilterType = 'ALL' | 'VERIFIED' | 'PARTIAL' | 'REFUTED' | 'INSUFFICIENT';

export default function ClaimVerification() {
  const { analysisResult, isAnalyzing } = useAnalysisStore();
  const [searchQuery, setSearchQuery] = useState('');
  const [activeFilter, setActiveFilter] = useState<FilterType>('ALL');
  
  const [selectedClaim, setSelectedClaim] = useState<DocumentationClaim | null>(null);

  if (!analysisResult && !isAnalyzing) return <EmptyState />;
  if (isAnalyzing && !analysisResult) {
    return (
      <div className="p-6 flex flex-col items-center justify-center min-h-[500px]">
        <div className="w-10 h-10 border-4 border-primary border-t-transparent rounded-full animate-spin mb-4" />
        <p className="text-muted-foreground font-medium">Analyzing claims...</p>
      </div>
    );
  }

  const verify = analysisResult?.verification_summary;
  const claims = analysisResult?.report?.documentation_claims ?? [];

  const filteredClaims = useMemo(() => {
    return claims.filter(claim => {
      const matchesSearch = claim.claim_text?.toLowerCase().includes(searchQuery.toLowerCase());
      
      let matchesFilter = true;
      if (activeFilter === 'VERIFIED') matchesFilter = claim.verdict === 'VERIFIED';
      else if (activeFilter === 'PARTIAL') matchesFilter = claim.verdict === 'UNSUPPORTED'; // As mapped in ClaimCard
      else if (activeFilter === 'REFUTED') matchesFilter = claim.verdict === 'CONTRADICTED';
      else if (activeFilter === 'INSUFFICIENT') matchesFilter = claim.verdict === 'INSUFFICIENT_EVIDENCE';
      
      return matchesSearch && matchesFilter;
    });
  }, [claims, searchQuery, activeFilter]);

  return (
    <div className="p-6 space-y-8 animate-in max-w-6xl mx-auto">
      
      {/* HEADER */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 border-b border-border pb-6">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2 text-foreground uppercase tracking-tight">
            <ClipboardCheck size={24} className="text-primary" />
            Claim Verification
          </h1>
          <p className="text-muted-foreground mt-1">Verify what the documentation says against the repository.</p>
        </div>
        
        <div className="relative w-full md:w-80">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" size={18} />
          <input 
            type="text" 
            placeholder="Search claims..." 
            className="w-full pl-10 pr-4 py-2 bg-background border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      {/* VERIFICATION SUMMARY CARDS */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="glass rounded-xl p-5 border-l-4 border-l-emerald-500">
          <div className="text-xs font-bold text-emerald-600 uppercase tracking-wider mb-1">✓ Verified</div>
          <div className="text-3xl font-bold text-emerald-600">{verify?.verified || 0}</div>
        </div>
        <div className="glass rounded-xl p-5 border-l-4 border-l-amber-500">
          <div className="text-xs font-bold text-amber-600 uppercase tracking-wider mb-1">◐ Partial</div>
          <div className="text-3xl font-bold text-amber-600">{verify?.partially_verified || 0}</div>
        </div>
        <div className="glass rounded-xl p-5 border-l-4 border-l-rose-500">
          <div className="text-xs font-bold text-rose-600 uppercase tracking-wider mb-1">✕ Refuted</div>
          <div className="text-3xl font-bold text-rose-600">{verify?.refuted || 0}</div>
        </div>
        <div className="glass rounded-xl p-5 border-l-4 border-l-indigo-500">
          <div className="text-xs font-bold text-indigo-600 uppercase tracking-wider mb-1">? Insufficient</div>
          <div className="text-3xl font-bold text-indigo-600">{verify?.insufficient || 0}</div>
        </div>
      </div>

      {/* CLAIM INVENTORY LIST */}
      <div className="space-y-6 pt-4">
        <h2 className="text-xl font-bold text-foreground uppercase tracking-wider">Claim Inventory</h2>
        
        {/* Filters */}
        <div className="flex flex-wrap gap-2 w-full">
          <button 
            onClick={() => setActiveFilter('ALL')}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors border ${activeFilter === 'ALL' ? 'bg-primary text-primary-foreground border-primary' : 'bg-muted/30 text-foreground border-border hover:bg-muted'}`}
          >
            All
          </button>
          <button 
            onClick={() => setActiveFilter('VERIFIED')}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors border ${activeFilter === 'VERIFIED' ? 'bg-emerald-500 text-white border-emerald-600' : 'bg-emerald-500/5 text-emerald-700 dark:text-emerald-400 border-emerald-500/20 hover:bg-emerald-500/10'}`}
          >
            ✓ Verified
          </button>
          <button 
            onClick={() => setActiveFilter('PARTIAL')}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors border ${activeFilter === 'PARTIAL' ? 'bg-amber-500 text-white border-amber-600' : 'bg-amber-500/5 text-amber-700 dark:text-amber-400 border-amber-500/20 hover:bg-amber-500/10'}`}
          >
            ◐ Partial
          </button>
          <button 
            onClick={() => setActiveFilter('REFUTED')}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors border ${activeFilter === 'REFUTED' ? 'bg-rose-500 text-white border-rose-600' : 'bg-rose-500/5 text-rose-700 dark:text-rose-400 border-rose-500/20 hover:bg-rose-500/10'}`}
          >
            ✕ Refuted
          </button>
          <button 
            onClick={() => setActiveFilter('INSUFFICIENT')}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors border ${activeFilter === 'INSUFFICIENT' ? 'bg-indigo-500 text-white border-indigo-600' : 'bg-indigo-500/5 text-indigo-700 dark:text-indigo-400 border-indigo-500/20 hover:bg-indigo-500/10'}`}
          >
            ? Insufficient
          </button>
        </div>

        {/* List */}
        <div className="space-y-4">
          {filteredClaims.length > 0 ? (
            filteredClaims.map((claim) => (
              <ClaimCard 
                key={claim.claim_id} 
                claim={claim} 
                onClick={() => setSelectedClaim(claim)}
              />
            ))
          ) : (
            <div className="text-sm text-muted-foreground p-12 text-center border border-dashed border-border rounded-xl glass">
              No verification results match your filters.
            </div>
          )}
        </div>
      </div>

      <ClaimEvidenceDrawer 
        isOpen={!!selectedClaim} 
        onClose={() => setSelectedClaim(null)} 
        claim={selectedClaim} 
      />

    </div>
  );
}
