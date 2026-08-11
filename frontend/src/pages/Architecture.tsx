import { useState, useMemo } from 'react';
import { useAnalysisStore } from '@/store';
import EmptyState from '@/components/EmptyState';
import { Search, Building2, X, ArrowRight, Layers, Link2, AlertTriangle, CheckCircle2, XCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const CATEGORY_THEMES: Record<string, any> = {
  'mvc': {
    bgClass: 'bg-purple-50/60',
    borderClass: 'border-purple-200',
    hoverBorderClass: 'hover:border-purple-400',
    textClass: 'text-purple-700',
    iconClass: 'text-purple-600',
    iconBgClass: 'bg-purple-100',
  },
  'api': {
    bgClass: 'bg-blue-50/60',
    borderClass: 'border-blue-200',
    hoverBorderClass: 'hover:border-blue-400',
    textClass: 'text-blue-700',
    iconClass: 'text-blue-600',
    iconBgClass: 'bg-blue-100',
  },
  'database': {
    bgClass: 'bg-emerald-50/60',
    borderClass: 'border-emerald-200',
    hoverBorderClass: 'hover:border-emerald-400',
    textClass: 'text-emerald-700',
    iconClass: 'text-emerald-600',
    iconBgClass: 'bg-emerald-100',
  },
  'event': {
    bgClass: 'bg-orange-50/60',
    borderClass: 'border-orange-200',
    hoverBorderClass: 'hover:border-orange-400',
    textClass: 'text-orange-700',
    iconClass: 'text-orange-600',
    iconBgClass: 'bg-orange-100',
  },
  'security': {
    bgClass: 'bg-pink-50/60',
    borderClass: 'border-pink-200',
    hoverBorderClass: 'hover:border-pink-400',
    textClass: 'text-pink-700',
    iconClass: 'text-pink-600',
    iconBgClass: 'bg-pink-100',
  },
  'default': {
    bgClass: 'bg-slate-50',
    borderClass: 'border-slate-200',
    hoverBorderClass: 'hover:border-slate-400',
    textClass: 'text-slate-700',
    iconClass: 'text-slate-600',
    iconBgClass: 'bg-slate-200',
  }
};

const getTheme = (name: string) => {
  const str = (name || '').toLowerCase();
  if (str.includes('mvc') || str.includes('layer')) return CATEGORY_THEMES.mvc;
  if (str.includes('api') || str.includes('service') || str.includes('microservice')) return CATEGORY_THEMES.api;
  if (str.includes('data') || str.includes('persist')) return CATEGORY_THEMES.database;
  if (str.includes('event') || str.includes('message')) return CATEGORY_THEMES.event;
  if (str.includes('security') || str.includes('secured')) return CATEGORY_THEMES.security;
  return CATEGORY_THEMES.default;
};

const getStatusBadge = (status: string) => {
  switch (status) {
    case 'DETECTED':
    case 'VERIFIED':
    case 'Detected':
      return (
        <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-100 text-emerald-800 text-xs font-bold uppercase tracking-wider border border-emerald-200 shadow-sm">
          <CheckCircle2 size={12} /> {status}
        </span>
      );
    case 'INSUFFICIENT_EVIDENCE':
    case 'Inferred':
      return (
        <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-amber-100 text-amber-800 text-xs font-bold uppercase tracking-wider border border-amber-200 shadow-sm">
          <AlertTriangle size={12} /> {status === 'Inferred' ? 'INFERRED' : 'INSUFFICIENT EVIDENCE'}
        </span>
      );
    case 'CONTRADICTED':
      return (
        <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-rose-100 text-rose-800 text-xs font-bold uppercase tracking-wider border border-rose-200 shadow-sm">
          <XCircle size={12} /> CONTRADICTED
        </span>
      );
    default:
      return (
        <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-100 text-slate-700 text-xs font-bold uppercase tracking-wider border border-slate-200 shadow-sm">
           {status}
        </span>
      );
  }
};

export default function Architecture() {
  const { analysisResult, isAnalyzing } = useAnalysisStore();
  
  const [search, setSearch] = useState('');
  const [selectedArchId, setSelectedArchId] = useState<string | null>(null);

  // 1. Process Real Backend Data directly from report.architecture_findings
  const architectures = useMemo(() => {
    // If we have architecture_findings, use them.
    if (analysisResult?.report?.architecture_findings && analysisResult.report.architecture_findings.length > 0) {
      return analysisResult.report.architecture_findings;
    }
    
    // Backward compatibility fallback to graph_metrics.architectures
    const baseArchs = analysisResult?.graph_metrics?.architectures || [];
    return baseArchs.map((name: string) => ({
      id: name,
      name: name,
      status: 'DETECTED', // Fallback status
      supporting_features: [],
      evidence: [],
      reasoning: 'Fallback string representation from legacy graph_metrics.architectures.'
    }));
  }, [analysisResult]);

  // 2. Filtering
  const filteredArchs = useMemo(() => {
    return architectures.filter(a => 
      a.name.toLowerCase().includes(search.toLowerCase())
    );
  }, [architectures, search]);

  const selectedArch = architectures.find(a => a.id === selectedArchId);

  if (!analysisResult && !isAnalyzing) return <EmptyState />;

  return (
    <div className="p-6 h-full flex flex-col animate-in">
      {/* ── 1. Header ─────────────────────────────────────────────── */}
      <div className="mb-8 shrink-0">
        <h1 className="text-3xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
          <Building2 size={28} className="text-slate-900" />
          Architecture
        </h1>
        <p className="text-slate-500 mt-2 mb-8">
          Architectural patterns derived from repository evidence.
        </p>

        {/* Search */}
        <div className="relative w-full md:w-80">
          <Search className="absolute left-3 top-2.5 text-slate-400" size={18} />
          <input 
            type="text" 
            placeholder="Search architecture patterns..." 
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-white border border-slate-200 rounded-xl pl-10 pr-4 py-2.5 text-sm focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 shadow-sm transition-all"
          />
        </div>
      </div>

      {/* ── 2. Main Content Area ────────────────────────────────────── */}
      <div className="flex-1 flex gap-8 min-h-0 relative">
        <div className="flex-1 flex flex-col min-w-0">
          
          <div className="flex-1 overflow-y-auto custom-scrollbar pr-2">
            <h2 className="text-xs font-bold text-slate-400 mb-5 uppercase tracking-widest">Architecture Patterns</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5 pb-6">
              {filteredArchs.length === 0 ? (
                <div className="col-span-full py-12 text-center bg-slate-50 rounded-3xl border border-dashed border-slate-200">
                   <Building2 size={32} className="mx-auto mb-4 text-slate-300" />
                   {search ? (
                     <p className="text-slate-500 font-medium">No architecture patterns match your search.</p>
                   ) : (
                     <p className="text-slate-500 font-medium">No architectural patterns were detected in this repository.</p>
                   )}
                </div>
              ) : (
                filteredArchs.map((arch, i) => {
                  const isSelected = selectedArchId === arch.id;
                  const theme = getTheme(arch.name);
                  
                  return (
                    <motion.div 
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: i * 0.03 }}
                      key={arch.id} 
                      onClick={() => setSelectedArchId(isSelected ? null : arch.id)}
                      className={`p-5 rounded-3xl border-2 transition-all cursor-pointer flex flex-col justify-between min-h-[180px] group
                        ${isSelected ? 'ring-4 ring-primary/20 scale-[1.02] z-10' : 'hover:-translate-y-1 hover:shadow-lg'}
                        ${theme.bgClass} ${theme.borderClass} ${theme.hoverBorderClass}
                      `}
                    >
                      <div>
                        <div className="flex items-center justify-between mb-4">
                          <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 shadow-sm border border-white/50 ${theme.iconBgClass}`}>
                            <Building2 className={theme.iconClass} size={20} />
                          </div>
                        </div>
                        <div>
                          <h3 className="font-bold text-slate-900 text-[16px] leading-tight mb-3">{arch.name}</h3>
                          <div className="mb-2">
                             {getStatusBadge(arch.status)}
                          </div>
                        </div>
                      </div>
                      
                      <div className="mt-4 pt-4 border-t border-black/5 flex flex-col gap-1.5">
                        <div className="flex justify-between items-center text-xs">
                          {arch.evidence && arch.evidence.length > 0 ? (
                            <span className="font-semibold text-slate-600 flex items-center gap-1.5">
                              <Link2 size={12} /> {arch.evidence.length} evidence sources
                            </span>
                          ) : (
                            <span /> // Do not render zero evidence or fake counts
                          )}
                        </div>
                        
                        <div className="flex justify-between items-center text-xs mt-2">
                           <span />
                           <span className={`${theme.textClass} font-semibold opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-1`}>
                             View Details <ArrowRight size={14} />
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

        {/* ── 3. Right Side Details Drawer ────────────────────────────── */}
        <AnimatePresence>
          {selectedArch && (
            <motion.div 
              initial={{ opacity: 0, x: 20, width: 0 }}
              animate={{ opacity: 1, x: 0, width: 420 }}
              exit={{ opacity: 0, x: 20, width: 0 }}
              className="shrink-0 h-full overflow-hidden hidden md:block"
            >
              <div className="w-[420px] h-full bg-white rounded-3xl border border-slate-100 shadow-2xl shadow-slate-200/50 flex flex-col overflow-hidden">
                
                {/* Dynamic Header */}
                {(() => {
                  const theme = getTheme(selectedArch.name);
                  return (
                    <div className={`p-6 border-b border-slate-100 ${theme.bgClass} flex justify-between items-start`}>
                      <div className="flex items-start gap-4">
                        <div className={`w-12 h-12 rounded-2xl flex items-center justify-center shrink-0 shadow-sm border border-white/50 ${theme.iconBgClass}`}>
                           <Building2 className={theme.iconClass} size={24} />
                        </div>
                        <div>
                          <p className="text-[10px] font-bold uppercase tracking-widest text-slate-500 mb-1">Architecture Pattern</p>
                          <h3 className="font-bold text-xl text-slate-900 leading-tight mb-2">{selectedArch.name}</h3>
                          {getStatusBadge(selectedArch.status)}
                        </div>
                      </div>
                      <button 
                        onClick={() => setSelectedArchId(null)} 
                        className="p-1.5 rounded-xl text-slate-400 hover:text-slate-700 hover:bg-white transition-colors shadow-sm"
                      >
                        <X size={18} />
                      </button>
                    </div>
                  );
                })()}
                
                <div className="flex-1 overflow-y-auto custom-scrollbar p-6 space-y-8">
                  
                  {/* REASONING */}
                  {selectedArch.reasoning && (
                    <div>
                      <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-3">
                        Reasoning
                      </h4>
                      <p className="text-sm text-slate-700 bg-slate-50 p-4 rounded-2xl border border-slate-100">
                        {selectedArch.reasoning}
                      </p>
                    </div>
                  )}

                  {/* SUPPORTING FEATURES (Evidence) */}
                  {selectedArch.supporting_features && selectedArch.supporting_features.length > 0 && (
                    <div>
                      <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-3 flex items-center gap-2">
                        <Layers size={14} /> Supporting Features
                      </h4>
                      <div className="bg-slate-50 border border-slate-100 rounded-2xl p-4 space-y-3">
                         {selectedArch.supporting_features.map((feat: any, idx: number) => (
                           <div key={idx} className="flex items-center gap-3">
                             <div className="w-1.5 h-1.5 rounded-full bg-slate-400" />
                             <span className="text-sm font-semibold text-slate-700">{feat.name || feat.id}</span>
                           </div>
                         ))}
                      </div>
                    </div>
                  )}

                  {/* SOURCE EVIDENCE (Files/Paths) */}
                  {selectedArch.evidence && selectedArch.evidence.length > 0 && (
                    <div>
                      <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-3 flex items-center gap-2">
                        <Link2 size={14} /> Source Evidence
                      </h4>
                      <div className="bg-slate-50 border border-slate-100 rounded-2xl p-4 space-y-4">
                         {selectedArch.evidence.map((chain: any, idx: number) => {
                           // Mapping EvidenceChain -> EvidenceItems
                           const sequence = chain.sequence || [];
                           return (
                             <div key={idx} className="space-y-2">
                               {sequence.map((ev: any, evIdx: number) => (
                                 <div key={evIdx} className="text-sm bg-white p-3 rounded-xl border border-slate-200">
                                   <div className="font-semibold text-slate-800 mb-1 flex items-center gap-2">
                                     <span className="text-xs text-slate-400 font-normal uppercase tracking-wider">{ev.context_type || 'Evidence'}</span>
                                   </div>
                                   {ev.source?.file_path && (
                                     <div className="text-xs font-mono text-slate-500 break-all mb-2">
                                       {ev.source.file_path}
                                       {ev.source.line_number ? ` : ${ev.source.line_number}` : ''}
                                     </div>
                                   )}
                                   {ev.code_snippet && (
                                      <pre className="text-[10px] bg-slate-50 p-2 rounded text-slate-600 overflow-x-auto">
                                        {ev.code_snippet}
                                      </pre>
                                   )}
                                 </div>
                               ))}
                             </div>
                           );
                         })}
                      </div>
                    </div>
                  )}
                  
                  {(!selectedArch.supporting_features?.length) && (!selectedArch.evidence?.length) && (
                    <div className="text-center py-8">
                       <p className="text-slate-500 text-sm">This architecture was detected, but supporting evidence is not currently exposed.</p>
                    </div>
                  )}

                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
