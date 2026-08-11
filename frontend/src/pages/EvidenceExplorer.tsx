import { useAnalysisStore } from '@/store';
import EmptyState from '@/components/EmptyState';
import { Search } from 'lucide-react';
import { useState, useMemo } from 'react';
import { UnifiedEvidenceItem } from '@/types/api';
import EvidenceInventoryCard from './EvidenceExplorer/EvidenceInventoryCard';
import EvidenceDetailsDrawer from './EvidenceExplorer/EvidenceDetailsDrawer';

export default function EvidenceExplorer() {
  const { analysisResult, isAnalyzing } = useAnalysisStore();
  const [searchQuery, setSearchQuery] = useState('');
  const [activeFilter, setActiveFilter] = useState<string>('ALL');
  const [selectedEvidence, setSelectedEvidence] = useState<UnifiedEvidenceItem | null>(null);

  if (!analysisResult && !isAnalyzing) return <EmptyState />;
  
  if (isAnalyzing && !analysisResult) {
    return (
      <div className="p-6 flex flex-col items-center justify-center min-h-[500px]">
        <div className="w-10 h-10 border-4 border-primary border-t-transparent rounded-full animate-spin mb-4" />
        <p className="text-muted-foreground font-medium">Loading evidence...</p>
      </div>
    );
  }

  const evidenceList = analysisResult?.report?.unified_evidence || [];
  const summary = analysisResult?.report?.evidence_summary;

  // Extract unique evidence types from the backend payload for the filters
  const uniqueTypes = useMemo(() => {
    const types = new Set<string>();
    evidenceList.forEach(e => {
      if (e.evidence_type) types.add(e.evidence_type.toUpperCase());
    });
    return Array.from(types).sort();
  }, [evidenceList]);

  // Filter evidence based on search query and active filter
  const filteredEvidence = useMemo(() => {
    return evidenceList.filter(evidence => {
      const type = evidence.evidence_type?.toUpperCase() || '';
      const matchesFilter = activeFilter === 'ALL' || type === activeFilter;
      
      const q = searchQuery.toLowerCase();
      const matchesSearch = 
        evidence.source_file?.toLowerCase().includes(q) ||
        evidence.snippet?.toLowerCase().includes(q) ||
        evidence.linked_claim?.claim_text.toLowerCase().includes(q) ||
        type.toLowerCase().includes(q);
      
      return matchesFilter && matchesSearch;
    });
  }, [evidenceList, searchQuery, activeFilter]);

  return (
    <div className="p-6 space-y-8 animate-in max-w-6xl mx-auto">
      
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 border-b border-border/50 pb-6">
        <div>
          <div className="inline-flex items-center justify-center p-2.5 bg-gradient-to-br from-primary/20 to-primary/5 text-primary rounded-xl mb-3 shadow-inner">
            <Search size={24} />
          </div>
          <h1 className="text-3xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-foreground to-foreground/70 uppercase tracking-tight">
            Evidence Explorer
          </h1>
          <p className="text-muted-foreground mt-1.5 font-medium">Repository evidence collected and linked to documentation claims.</p>
        </div>
        
        <div className="relative w-full md:w-96 group">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-muted-foreground transition-colors group-focus-within:text-primary" size={18} />
          <input 
            type="text" 
            placeholder="Search evidence, files, claims..." 
            className="w-full pl-11 pr-4 py-3 bg-background/50 border border-border rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 shadow-sm backdrop-blur-xl transition-all hover:bg-background"
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      {/* Backend-driven Summary Counters */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-5">
        <div className="glass rounded-2xl p-6 bg-gradient-to-br from-indigo-500/10 via-purple-500/5 to-transparent border-l-4 border-l-indigo-500 relative overflow-hidden group hover:shadow-lg transition-all hover:-translate-y-0.5">
          <div className="absolute -right-6 -top-6 w-24 h-24 bg-indigo-500/10 rounded-full blur-2xl group-hover:bg-indigo-500/20 transition-all"></div>
          <div className="text-xs font-extrabold text-indigo-600 dark:text-indigo-400 uppercase tracking-wider mb-2 relative z-10">Total Evidence</div>
          <div className="text-4xl font-black text-foreground relative z-10">{summary?.total_evidence || 0}</div>
        </div>
        <div className="glass rounded-2xl p-6 bg-gradient-to-br from-emerald-500/10 via-teal-500/5 to-transparent border-l-4 border-l-emerald-500 relative overflow-hidden group hover:shadow-lg transition-all hover:-translate-y-0.5">
          <div className="absolute -right-6 -top-6 w-24 h-24 bg-emerald-500/10 rounded-full blur-2xl group-hover:bg-emerald-500/20 transition-all"></div>
          <div className="text-xs font-extrabold text-emerald-600 dark:text-emerald-400 uppercase tracking-wider mb-2 relative z-10">Linked Claims</div>
          <div className="text-4xl font-black text-foreground relative z-10">{summary?.linked_claims || 0}</div>
        </div>
        <div className="glass rounded-2xl p-6 bg-gradient-to-br from-blue-500/10 via-cyan-500/5 to-transparent border-l-4 border-l-blue-500 relative overflow-hidden group hover:shadow-lg transition-all hover:-translate-y-0.5">
          <div className="absolute -right-6 -top-6 w-24 h-24 bg-blue-500/10 rounded-full blur-2xl group-hover:bg-blue-500/20 transition-all"></div>
          <div className="text-xs font-extrabold text-blue-600 dark:text-blue-400 uppercase tracking-wider mb-2 relative z-10">Source Files</div>
          <div className="text-4xl font-black text-foreground relative z-10">{summary?.source_files || 0}</div>
        </div>
      </div>

      {/* Inventory Section */}
      <div className="space-y-6 pt-4">
        
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <h2 className="text-xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-foreground to-foreground/60 uppercase tracking-widest">Evidence Inventory</h2>
          
          {/* Dynamic Filters */}
          <div className="flex flex-wrap gap-2">
            <button 
              onClick={() => setActiveFilter('ALL')}
              className={`px-4 py-2 rounded-xl text-xs font-bold tracking-wider uppercase transition-all duration-300 border shadow-sm ${activeFilter === 'ALL' ? 'bg-primary text-primary-foreground border-primary shadow-primary/20 shadow-lg scale-105' : 'bg-background hover:bg-muted text-muted-foreground border-border'}`}
            >
              All
            </button>
            {uniqueTypes.map(type => (
              <button 
                key={type}
                onClick={() => setActiveFilter(type)}
                className={`px-4 py-2 rounded-xl text-xs font-bold tracking-wider uppercase transition-all duration-300 border shadow-sm ${activeFilter === type ? 'bg-primary text-primary-foreground border-primary shadow-primary/20 shadow-lg scale-105' : 'bg-background hover:bg-muted text-muted-foreground border-border'}`}
              >
                {type}
              </button>
            ))}
          </div>
        </div>

        {/* Evidence List */}
        {evidenceList.length === 0 ? (
          <div className="text-sm text-muted-foreground p-12 text-center border border-dashed border-border rounded-xl glass">
            <p className="text-base font-medium mb-1">No evidence found</p>
            The backend did not return evidence for the current repository.
          </div>
        ) : filteredEvidence.length === 0 ? (
          <div className="text-sm text-muted-foreground p-12 text-center border border-dashed border-border rounded-xl glass">
            No evidence matches your search filters.
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {filteredEvidence.map(evidence => (
              <EvidenceInventoryCard 
                key={evidence.evidence_id} 
                evidence={evidence} 
                onClick={() => setSelectedEvidence(evidence)}
              />
            ))}
          </div>
        )}
      </div>

      <EvidenceDetailsDrawer 
        isOpen={!!selectedEvidence} 
        onClose={() => setSelectedEvidence(null)} 
        evidence={selectedEvidence} 
      />

    </div>
  );
}
