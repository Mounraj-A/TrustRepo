import { useState, useMemo } from 'react';
import { useAnalysisStore } from '@/store';
import EmptyState from '@/components/EmptyState';
import { Search, X, CheckCircle2, AlertTriangle, XCircle, HelpCircle, ArrowRight, Layers, FileCode2, ChevronDown } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { Link } from 'react-router-dom';

const STATUS_THEMES: Record<string, any> = {
  'VERIFIED': {
    color: '#10b981', // emerald-500
    bgClass: 'bg-emerald-50/60',
    borderClass: 'border-emerald-200',
    hoverBorderClass: 'hover:border-emerald-400',
    textClass: 'text-emerald-700',
    iconClass: 'text-emerald-600',
    iconBgClass: 'bg-emerald-100',
    activeFilterClass: 'bg-emerald-100 text-emerald-800 border-emerald-300',
    Icon: CheckCircle2,
    label: 'Verified'
  },
  'MISSING_DOCUMENTATION': {
    color: '#f59e0b', // amber-500
    bgClass: 'bg-amber-50/60',
    borderClass: 'border-amber-200',
    hoverBorderClass: 'hover:border-amber-400',
    textClass: 'text-amber-700',
    iconClass: 'text-amber-600',
    iconBgClass: 'bg-amber-100',
    activeFilterClass: 'bg-amber-100 text-amber-800 border-amber-300',
    Icon: AlertTriangle,
    label: 'Missing Documentation'
  },
  'CONTRADICTED': {
    color: '#f43f5e', // rose-500
    bgClass: 'bg-rose-50/60',
    borderClass: 'border-rose-200',
    hoverBorderClass: 'hover:border-rose-400',
    textClass: 'text-rose-700',
    iconClass: 'text-rose-600',
    iconBgClass: 'bg-rose-100',
    activeFilterClass: 'bg-rose-100 text-rose-800 border-rose-300',
    Icon: XCircle,
    label: 'Contradicted'
  },
  'INSUFFICIENT_EVIDENCE': {
    color: '#6366f1', // indigo-500
    bgClass: 'bg-indigo-50/60',
    borderClass: 'border-indigo-200',
    hoverBorderClass: 'hover:border-indigo-400',
    textClass: 'text-indigo-700',
    iconClass: 'text-indigo-600',
    iconBgClass: 'bg-indigo-100',
    activeFilterClass: 'bg-indigo-100 text-indigo-800 border-indigo-300',
    Icon: HelpCircle,
    label: 'Insufficient Evidence'
  },
  'UNSUPPORTED': {
    color: '#64748b',
    bgClass: 'bg-slate-50',
    borderClass: 'border-slate-200',
    hoverBorderClass: 'hover:border-slate-400',
    textClass: 'text-slate-700',
    iconClass: 'text-slate-600',
    iconBgClass: 'bg-slate-200',
    activeFilterClass: 'bg-slate-100 text-slate-800 border-slate-300',
    Icon: HelpCircle,
    label: 'Unsupported'
  }
};

const getStatusTheme = (status: string) => STATUS_THEMES[status] || STATUS_THEMES['UNSUPPORTED'];

// A very generic secondary color badge for the category if provided
const getCategoryBadgeStyle = (category: string) => {
  const cat = (category || '').toLowerCase();
  if (cat.includes('database') || cat.includes('data')) return 'bg-orange-50 text-orange-700 border-orange-200';
  if (cat.includes('api') || cat.includes('integration')) return 'bg-purple-50 text-purple-700 border-purple-200';
  if (cat.includes('ui') || cat.includes('front')) return 'bg-pink-50 text-pink-700 border-pink-200';
  if (cat.includes('arch')) return 'bg-amber-50 text-amber-700 border-amber-200';
  if (cat.includes('infra')) return 'bg-cyan-50 text-cyan-700 border-cyan-200';
  return 'bg-slate-50 text-slate-600 border-slate-200';
};

const ALL_STATUSES = ['VERIFIED', 'MISSING_DOCUMENTATION', 'CONTRADICTED', 'INSUFFICIENT_EVIDENCE'];

export default function SemanticFeatures() {
  const { analysisResult, isAnalyzing } = useAnalysisStore();
  
  const [search, setSearch] = useState('');
  const [selectedStatus, setSelectedStatus] = useState<string>('All');
  const [selectedFeatureName, setSelectedFeatureName] = useState<string | null>(null);

  const findings = analysisResult?.report?.feature_findings || [];

  // Calculate Verification Summary exactly from the findings array
  const verificationCounts = useMemo(() => {
    const counts: Record<string, number> = {
      'VERIFIED': 0,
      'MISSING_DOCUMENTATION': 0,
      'CONTRADICTED': 0,
      'INSUFFICIENT_EVIDENCE': 0
    };
    findings.forEach(f => {
      if (f.status && counts[f.status] !== undefined) {
        counts[f.status]++;
      }
    });
    return counts;
  }, [findings]);

  // Filter features
  const filteredFindings = useMemo(() => {
    return findings.filter(f => {
      const matchesSearch = 
        (f.feature || '').toLowerCase().includes(search.toLowerCase()) || 
        (f.reasoning || '').toLowerCase().includes(search.toLowerCase());
      const matchesStatus = selectedStatus === 'All' || f.status === selectedStatus;
      return matchesSearch && matchesStatus;
    });
  }, [findings, search, selectedStatus]);

  const selectedFeature = findings.find(f => f.feature === selectedFeatureName);

  if (!analysisResult && !isAnalyzing) return <EmptyState />;

  return (
    <div className="p-6 h-full flex flex-col animate-in">
      {/* ── 1. Header ─────────────────────────────────────────────── */}
      <div className="mb-8 shrink-0">
        <h1 className="text-3xl font-bold text-slate-900 tracking-tight">Semantic Features</h1>
        <p className="text-slate-500 mt-2 mb-8">
          Features detected from repository evidence.
        </p>
        
        {/* Verification Summary Header */}
        <div className="flex flex-wrap gap-4 mb-8 p-4 bg-white rounded-2xl border border-slate-100 shadow-sm">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-widest w-full mb-1">Verification Summary</div>
          {ALL_STATUSES.map(status => {
            const theme = getStatusTheme(status);
            const count = verificationCounts[status];
            return (
              <div key={status} className={`flex items-center gap-3 px-4 py-2 rounded-xl border ${theme.bgClass} ${theme.borderClass}`}>
                <theme.Icon className={theme.iconClass} size={18} />
                <span className={`font-semibold ${theme.textClass}`}>{theme.label}</span>
                <span className={`font-black text-lg ${theme.textClass} ml-2`}>{count}</span>
              </div>
            );
          })}
        </div>

        {/* Search & Filters */}
        <div className="flex flex-col md:flex-row gap-4 items-start md:items-center">
          <div className="relative w-full md:w-80">
            <Search className="absolute left-3 top-2.5 text-slate-400" size={18} />
            <input 
              type="text" 
              placeholder="Search features..." 
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-white border border-slate-200 rounded-xl pl-10 pr-4 py-2.5 text-sm focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 shadow-sm transition-all"
            />
          </div>
          
          <div className="flex flex-wrap gap-2">
            {['All', ...ALL_STATUSES].map(status => {
              const theme = status !== 'All' ? getStatusTheme(status) : null;
              const isActive = selectedStatus === status;
              
              return (
                <button
                  key={status}
                  onClick={() => setSelectedStatus(status)}
                  className={`px-4 py-2 rounded-xl text-sm font-semibold transition-all border ${
                    isActive 
                      ? status === 'All' ? 'bg-slate-800 text-white border-slate-800 shadow-md' : (theme?.activeFilterClass + ' shadow-sm')
                      : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50'
                  }`}
                >
                  {theme ? theme.label : 'All'}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* ── 2. Main Content Area ────────────────────────────────────── */}
      <div className="flex-1 flex gap-8 min-h-0 relative">
        <div className="flex-1 flex flex-col min-w-0">
          
          <div className="flex-1 overflow-y-auto custom-scrollbar pr-2">
            <h2 className="text-xs font-bold text-slate-400 mb-5 uppercase tracking-widest">Feature Inventory</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5 pb-6">
              {filteredFindings.length === 0 ? (
                <div className="col-span-full py-12 text-center bg-slate-50 rounded-3xl border border-dashed border-slate-200">
                   <Layers size={32} className="mx-auto mb-4 text-slate-300" />
                   <p className="text-slate-500 font-medium">No semantic features match your search.</p>
                </div>
              ) : (
                filteredFindings.map((feat, i) => {
                  const isSelected = selectedFeatureName === feat.feature;
                  const theme = getStatusTheme(feat.status);
                  
                  return (
                    <motion.div 
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: i * 0.03 }}
                      key={feat.feature} 
                      onClick={() => setSelectedFeatureName(isSelected ? null : feat.feature)}
                      className={`p-5 rounded-3xl border-2 transition-all cursor-pointer flex flex-col justify-between min-h-[160px] group
                        ${isSelected ? 'ring-4 ring-primary/20 scale-[1.02] z-10' : 'hover:-translate-y-1 hover:shadow-lg'}
                        ${theme.bgClass} ${theme.borderClass} ${theme.hoverBorderClass}
                      `}
                    >
                      <div>
                        <div className="flex justify-between items-start gap-2 mb-3">
                          <div className={`w-8 h-8 rounded-xl flex items-center justify-center shrink-0 shadow-sm border border-white/50 ${theme.iconBgClass}`}>
                            <theme.Icon className={theme.iconClass} size={16} />
                          </div>
                          
                          {/* Optional Category Badge */}
                          {feat.category && (
                             <span className={`px-2 py-0.5 rounded-lg text-[9px] font-bold uppercase tracking-wider border ${getCategoryBadgeStyle(feat.category)} truncate max-w-[100px]`}>
                               {feat.category}
                             </span>
                          )}
                        </div>
                        
                        <h3 className="font-bold text-slate-900 text-[15px] leading-tight mb-2">{feat.feature}</h3>
                        <span className={`inline-block font-semibold text-[11px] uppercase tracking-wider ${theme.textClass}`}>
                          {theme.label}
                        </span>
                      </div>
                      
                      <div className="mt-4 pt-3 border-t border-black/5 flex flex-col gap-1.5">
                        <div className="flex justify-between items-center text-xs">
                          {feat.confidence !== undefined && feat.confidence !== null ? (
                             <span className="font-mono font-bold text-slate-700">{Math.round(feat.confidence * 100)}% <span className="text-slate-400 font-normal font-sans">Confidence</span></span>
                          ) : <span />}
                          
                          {feat.evidence_count !== undefined && feat.evidence_count > 0 && (
                            <span className="font-medium text-slate-500">{feat.evidence_count} sources</span>
                          )}
                        </div>
                        
                        <div className="flex justify-between items-center text-xs mt-2">
                           <span />
                           <span className={`${theme.textClass} font-semibold opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-1`}>
                             View Evidence <ArrowRight size={14} />
                           </span>
                        </div>
                      </div>
                    </motion.div>
                  );
                })
              )}
            </div>
          </div>
        </div>

        {/* ── 3. Right Side Feature Details Drawer ───────────────────── */}
        <AnimatePresence>
          {selectedFeature && (
            <motion.div 
              initial={{ opacity: 0, x: 20, width: 0 }}
              animate={{ opacity: 1, x: 0, width: 420 }}
              exit={{ opacity: 0, x: 20, width: 0 }}
              className="shrink-0 h-full overflow-hidden hidden md:block"
            >
              <div className="w-[420px] h-full bg-white rounded-3xl border border-slate-100 shadow-2xl shadow-slate-200/50 flex flex-col overflow-hidden">
                
                {/* Dynamic Header */}
                {(() => {
                  const theme = getStatusTheme(selectedFeature.status);
                  return (
                    <div className={`p-6 border-b border-slate-100 ${theme.bgClass} flex justify-between items-start`}>
                      <div className="flex items-start gap-4">
                        <div className={`w-12 h-12 rounded-2xl flex items-center justify-center shrink-0 shadow-sm border border-white/50 ${theme.iconBgClass}`}>
                           <theme.Icon className={theme.iconClass} size={24} />
                        </div>
                        <div>
                          <h3 className="font-bold text-xl text-slate-900 leading-tight mb-1">{selectedFeature.feature}</h3>
                          <span className={`inline-block px-2.5 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-white border ${theme.textClass} ${theme.borderClass}`}>
                            {theme.label}
                          </span>
                        </div>
                      </div>
                      <button 
                        onClick={() => setSelectedFeatureName(null)} 
                        className="p-1.5 rounded-xl text-slate-400 hover:text-slate-700 hover:bg-white transition-colors shadow-sm"
                      >
                        <X size={18} />
                      </button>
                    </div>
                  );
                })()}
                
                <div className="flex-1 overflow-y-auto custom-scrollbar p-6 space-y-8">
                  
                  {/* Evidence Assessment */}
                  {(selectedFeature.confidence !== null || selectedFeature.evidence_quality !== undefined || selectedFeature.evidence_diversity !== undefined) && (
                    <div>
                      <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-3">Evidence Assessment</h4>
                      <div className="bg-slate-50 border border-slate-100 rounded-2xl p-5 space-y-4">
                         
                         {selectedFeature.confidence !== null && selectedFeature.confidence !== undefined && (
                           <div>
                             <div className="flex justify-between items-baseline mb-2">
                                <span className="text-sm font-semibold text-slate-600">Confidence</span>
                                <span className="font-bold text-slate-900 text-lg">{Math.round(selectedFeature.confidence * 100)}%</span>
                             </div>
                             <div className="w-full bg-slate-200 rounded-full h-2">
                                <div className="h-2 rounded-full" style={{ width: `${selectedFeature.confidence * 100}%`, backgroundColor: getStatusTheme(selectedFeature.status).color }} />
                             </div>
                           </div>
                         )}
                         
                         <div className="grid grid-cols-2 gap-4 pt-2">
                            {selectedFeature.evidence_quality !== undefined && (
                               <div>
                                 <p className="text-[10px] uppercase font-bold text-slate-400 mb-1">Evidence Quality</p>
                                 <p className="font-mono font-medium text-slate-700">{selectedFeature.evidence_quality}</p>
                               </div>
                            )}
                            {selectedFeature.evidence_diversity !== undefined && (
                               <div>
                                 <p className="text-[10px] uppercase font-bold text-slate-400 mb-1">Evidence Diversity</p>
                                 <p className="font-mono font-medium text-slate-700">{selectedFeature.evidence_diversity}</p>
                               </div>
                            )}
                            {selectedFeature.evidence_count !== undefined && (
                               <div className="col-span-2 pt-2 border-t border-slate-200">
                                 <p className="text-[10px] uppercase font-bold text-slate-400 mb-1">Evidence Sources</p>
                                 <p className="font-medium text-slate-700">{selectedFeature.evidence_count}</p>
                               </div>
                            )}
                         </div>
                      </div>
                    </div>
                  )}

                  {/* Reasoning */}
                  {selectedFeature.reasoning && (
                    <div>
                      <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-3">Reasoning</h4>
                      <div className="bg-white border border-slate-100 shadow-sm rounded-2xl p-5 text-sm text-slate-700 leading-relaxed">
                        {selectedFeature.reasoning}
                      </div>
                    </div>
                  )}

                  {/* Evidence Chain Visualization */}
                  {selectedFeature.provenance_chain?.sequence && selectedFeature.provenance_chain.sequence.length > 0 && (
                    <div>
                      <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-3">Evidence Chain</h4>
                      <div className="bg-slate-50 border border-slate-100 rounded-2xl p-5">
                        <div className="space-y-0">
                          {selectedFeature.provenance_chain.sequence.map((item, index) => {
                            const isLast = index === selectedFeature.provenance_chain!.sequence.length - 1;
                            return (
                              <div key={item.id || index} className="relative flex gap-4">
                                {/* Timeline line */}
                                {!isLast && (
                                  <div className="absolute top-8 left-[11px] bottom-[-8px] w-px bg-slate-200" />
                                )}
                                
                                <div className="mt-1.5 shrink-0 z-10">
                                  <div className="w-6 h-6 rounded-full bg-white border-2 border-slate-300 flex items-center justify-center">
                                    <ChevronDown size={12} className="text-slate-400" />
                                  </div>
                                </div>
                                
                                <div className="pb-6 pt-1 w-full min-w-0">
                                  <div className="flex items-center gap-2 mb-1">
                                    <span className="text-[10px] font-bold uppercase tracking-widest text-slate-500">
                                      {item.evidence_type || item.node_type || 'Evidence'}
                                    </span>
                                  </div>
                                  
                                  <div className="bg-white border border-slate-200 rounded-xl p-3 shadow-sm">
                                    {item.symbol && <div className="font-semibold text-sm text-slate-800 mb-1">{item.symbol}</div>}
                                    
                                    {item.source?.file_path && (
                                      <div className="flex items-start gap-1.5 text-xs text-slate-500 font-mono mt-1">
                                        <FileCode2 size={12} className="shrink-0 mt-0.5" />
                                        <span className="truncate" title={item.source.file_path}>
                                          {item.source.file_path}
                                          {item.source.line_number ? ` : ${item.source.line_number}` : ''}
                                        </span>
                                      </div>
                                    )}
                                    
                                    {item.code_snippet && (
                                      <div className="mt-2 bg-slate-900 text-slate-50 p-2 rounded-lg text-[10px] font-mono overflow-x-auto whitespace-pre">
                                        {item.code_snippet}
                                      </div>
                                    )}
                                  </div>
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    </div>
                  )}

                  {/* View in Evidence Explorer Link */}
                  <div className="pt-4 border-t border-slate-100 flex justify-end">
                    <Link 
                      to="/dashboard/evidence" 
                      className="inline-flex items-center gap-2 px-4 py-2 bg-slate-900 text-white rounded-xl text-sm font-semibold hover:bg-slate-800 transition-colors shadow-md"
                    >
                      View in Evidence Explorer <ArrowRight size={16} />
                    </Link>
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
