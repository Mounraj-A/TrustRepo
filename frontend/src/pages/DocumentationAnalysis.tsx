import { useAnalysisStore } from '@/store';
import EmptyState from '@/components/EmptyState';
import { BookOpen, FileText, Search } from 'lucide-react';
import EvidenceCard from './Documentation/EvidenceCard';
import EvidenceDrawer from './Documentation/EvidenceDrawer';
import { useState, useMemo } from 'react';
import { DocumentationClaim, FeatureFinding } from '@/types/api';

type FilterType = 'ALL' | 'VERIFIED' | 'MISSING_DOCUMENTATION' | 'CONTRADICTED';

export default function DocumentationAnalysis() {
  const { analysisResult, isAnalyzing } = useAnalysisStore();
  const [searchQuery, setSearchQuery] = useState('');
  const [activeFilter, setActiveFilter] = useState<FilterType>('ALL');
  
  const [drawerData, setDrawerData] = useState<{ data: DocumentationClaim | FeatureFinding; type: 'claim' | 'feature' } | null>(null);

  if (!analysisResult && !isAnalyzing) return <EmptyState />;
  if (isAnalyzing && !analysisResult) {
    return (
      <div className="p-6 flex flex-col items-center justify-center min-h-[500px]">
        <div className="w-10 h-10 border-4 border-primary border-t-transparent rounded-full animate-spin mb-4" />
        <p className="text-muted-foreground font-medium">Analyzing documentation...</p>
      </div>
    );
  }

  const report = analysisResult?.report;
  const summary = analysisResult?.verification_summary;

  if (!report || !summary) return <EmptyState />;

  const claims = report.documentation_claims || [];
  const features = report.feature_findings || [];

  // Merge the arrays into a unified list
  const mergedItems = useMemo(() => {
    const claimItems = claims.map(c => ({ data: c, type: 'claim' as const, status: c.verdict, text: c.claim_text }));
    const featureItems = features.map(f => ({ data: f, type: 'feature' as const, status: f.status, text: f.feature }));
    
    // Sort logic: Contradicted first, then Missing, then Verified, then others
    const sortOrder = { 'CONTRADICTED': 0, 'MISSING_DOCUMENTATION': 1, 'VERIFIED': 2 };
    
    return [...claimItems, ...featureItems].sort((a, b) => {
      const orderA = sortOrder[a.status as keyof typeof sortOrder] ?? 99;
      const orderB = sortOrder[b.status as keyof typeof sortOrder] ?? 99;
      return orderA - orderB;
    });
  }, [claims, features]);

  const filteredItems = useMemo(() => {
    return mergedItems.filter(item => {
      const matchesSearch = item.text.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesFilter = activeFilter === 'ALL' || item.status === activeFilter;
      return matchesSearch && matchesFilter;
    });
  }, [mergedItems, searchQuery, activeFilter]);

  const hasCoverage = report.summary && report.summary.coverage_percentage != null;
  const coveragePct = report.summary?.coverage_percentage || 0;

  return (
    <div className="p-6 space-y-8 animate-in max-w-6xl mx-auto">
      
      {/* HEADER */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-border pb-6">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2 text-foreground uppercase tracking-tight">
            <BookOpen size={24} className="text-primary" />
            Documentation Verification
          </h1>
          <p className="text-muted-foreground mt-1">Documentation ↔ Repository Evidence</p>
        </div>
        {report.metadata?.documentation_sources && report.metadata.documentation_sources.length > 0 && (
          <div className="text-sm font-medium text-foreground bg-muted/50 px-4 py-2 rounded-lg border border-border flex flex-col items-end">
            <span className="text-xs text-muted-foreground uppercase tracking-wider mb-0.5">Documentation Source</span>
            {report.metadata.documentation_sources.join(', ')}
          </div>
        )}
      </div>

      {/* VERIFICATION SUMMARY CARDS */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="glass rounded-xl p-5 border-l-4 border-l-primary/50">
          <div className="text-xs font-bold text-muted-foreground uppercase tracking-wider mb-1">Claims</div>
          <div className="text-3xl font-bold text-foreground">{report.summary?.total_claims || 0}</div>
        </div>
        <div className="glass rounded-xl p-5 border-l-4 border-l-emerald-500">
          <div className="text-xs font-bold text-emerald-600 uppercase tracking-wider mb-1">Verified</div>
          <div className="text-3xl font-bold text-emerald-600">{report.summary?.verified_claims || 0}</div>
        </div>
        <div className="glass rounded-xl p-5 border-l-4 border-l-amber-500">
          <div className="text-xs font-bold text-amber-600 uppercase tracking-wider mb-1">Missing Docs</div>
          <div className="text-3xl font-bold text-amber-600">{report.summary?.missing_documentation || 0}</div>
        </div>
        <div className="glass rounded-xl p-5 border-l-4 border-l-rose-500">
          <div className="text-xs font-bold text-rose-600 uppercase tracking-wider mb-1">Contradicted</div>
          <div className="text-3xl font-bold text-rose-600">{report.summary?.contradicted_claims || report.summary?.contradicted || 0}</div>
        </div>
      </div>

      {/* DOCUMENTATION COVERAGE */}
      {hasCoverage && (
        <div className="glass rounded-xl p-6">
          <div className="flex justify-between items-end mb-2">
            <h3 className="text-sm font-bold text-muted-foreground uppercase tracking-wider">Documentation Coverage</h3>
            <span className="text-2xl font-bold text-primary">{coveragePct}%</span>
          </div>
          <div className="w-full bg-muted rounded-full h-3 overflow-hidden border border-border">
            <div
              className="bg-primary h-full rounded-full transition-all duration-500"
              style={{ width: `${coveragePct}%` }}
            />
          </div>
        </div>
      )}

      {/* DOCUMENTATION ↔ CODE VERIFICATION LIST */}
      <div className="space-y-6 pt-4">
        <h2 className="text-xl font-bold text-foreground uppercase tracking-wider">Documentation ↔ Code Verification</h2>
        
        {/* Filters and Search */}
        <div className="flex flex-col md:flex-row gap-4 items-center justify-between">
          <div className="relative w-full md:w-96">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" size={18} />
            <input 
              type="text" 
              placeholder="Search claims and features..." 
              className="w-full pl-10 pr-4 py-2 bg-background border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
            />
          </div>
          
          <div className="flex flex-wrap gap-2 w-full md:w-auto">
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
              onClick={() => setActiveFilter('MISSING_DOCUMENTATION')}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors border ${activeFilter === 'MISSING_DOCUMENTATION' ? 'bg-amber-500 text-white border-amber-600' : 'bg-amber-500/5 text-amber-700 dark:text-amber-400 border-amber-500/20 hover:bg-amber-500/10'}`}
            >
              ⚠ Missing
            </button>
            <button 
              onClick={() => setActiveFilter('CONTRADICTED')}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors border ${activeFilter === 'CONTRADICTED' ? 'bg-rose-500 text-white border-rose-600' : 'bg-rose-500/5 text-rose-700 dark:text-rose-400 border-rose-500/20 hover:bg-rose-500/10'}`}
            >
              ✕ Contradicted
            </button>
          </div>
        </div>

        {/* List */}
        <div className="space-y-4">
          {filteredItems.length > 0 ? (
            filteredItems.map((item, idx) => (
              <EvidenceCard 
                key={idx} 
                type={item.type} 
                data={item.data} 
                onClick={() => setDrawerData({ data: item.data, type: item.type })}
              />
            ))
          ) : (
            <div className="text-sm text-muted-foreground p-12 text-center border border-dashed border-border rounded-xl glass">
              No verification results match your filters.
            </div>
          )}
        </div>
      </div>

      {/* GLOBAL RECOMMENDATIONS */}
      {report.recommendations && report.recommendations.length > 0 && (
        <div className="mt-12 pt-8 border-t border-border">
          <div className="glass rounded-xl p-6 border border-primary/20 bg-primary/5">
            <h3 className="font-semibold text-lg text-primary mb-4 flex items-center gap-2 uppercase tracking-wider">
              <FileText size={18} />
              Recommendations
            </h3>
            <ul className="list-decimal list-inside space-y-3 text-sm text-foreground">
              {report.recommendations.map((rec, idx) => {
                const text = typeof rec === 'string' ? rec : rec.message;
                return <li key={idx} className="leading-relaxed">{text}</li>;
              })}
            </ul>
          </div>
        </div>
      )}

      <EvidenceDrawer 
        isOpen={!!drawerData} 
        onClose={() => setDrawerData(null)} 
        data={drawerData?.data || null} 
        type={drawerData?.type || null}
      />

    </div>
  );
}
