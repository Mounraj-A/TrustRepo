import { useState, useMemo } from 'react';
import { useAnalysisStore } from '@/store';
import EmptyState from '@/components/EmptyState';
import { Search, Zap, X, ArrowRight, Layers, Box, Link2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const CATEGORY_THEMES: Record<string, any> = {
  'api': {
    bgClass: 'bg-purple-50/60',
    borderClass: 'border-purple-200',
    hoverBorderClass: 'hover:border-purple-400',
    textClass: 'text-purple-700',
    iconClass: 'text-purple-600',
    iconBgClass: 'bg-purple-100',
    activeFilterClass: 'bg-purple-100 text-purple-800 border-purple-300'
  },
  'database': {
    bgClass: 'bg-emerald-50/60',
    borderClass: 'border-emerald-200',
    hoverBorderClass: 'hover:border-emerald-400',
    textClass: 'text-emerald-700',
    iconClass: 'text-emerald-600',
    iconBgClass: 'bg-emerald-100',
    activeFilterClass: 'bg-emerald-100 text-emerald-800 border-emerald-300'
  },
  'frontend': {
    bgClass: 'bg-blue-50/60',
    borderClass: 'border-blue-200',
    hoverBorderClass: 'hover:border-blue-400',
    textClass: 'text-blue-700',
    iconClass: 'text-blue-600',
    iconBgClass: 'bg-blue-100',
    activeFilterClass: 'bg-blue-100 text-blue-800 border-blue-300'
  },
  'architecture': {
    bgClass: 'bg-orange-50/60',
    borderClass: 'border-orange-200',
    hoverBorderClass: 'hover:border-orange-400',
    textClass: 'text-orange-700',
    iconClass: 'text-orange-600',
    iconBgClass: 'bg-orange-100',
    activeFilterClass: 'bg-orange-100 text-orange-800 border-orange-300'
  },
  'security': {
    bgClass: 'bg-amber-50/60',
    borderClass: 'border-amber-200',
    hoverBorderClass: 'hover:border-amber-400',
    textClass: 'text-amber-700',
    iconClass: 'text-amber-600',
    iconBgClass: 'bg-amber-100',
    activeFilterClass: 'bg-amber-100 text-amber-800 border-amber-300'
  },
  'default': {
    bgClass: 'bg-slate-50',
    borderClass: 'border-slate-200',
    hoverBorderClass: 'hover:border-slate-400',
    textClass: 'text-slate-700',
    iconClass: 'text-slate-600',
    iconBgClass: 'bg-slate-200',
    activeFilterClass: 'bg-slate-100 text-slate-800 border-slate-300'
  }
};

const getTheme = (nameOrCategory: string) => {
  const str = (nameOrCategory || '').toLowerCase();
  if (str.includes('api') || str.includes('integration')) return CATEGORY_THEMES.api;
  if (str.includes('data') || str.includes('storage')) return CATEGORY_THEMES.database;
  if (str.includes('front') || str.includes('ui')) return CATEGORY_THEMES.frontend;
  if (str.includes('arch')) return CATEGORY_THEMES.architecture;
  if (str.includes('auth') || str.includes('secur')) return CATEGORY_THEMES.security;
  return CATEGORY_THEMES.default;
};

export default function Capabilities() {
  const { analysisResult, isAnalyzing } = useAnalysisStore();
  
  const [search, setSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [selectedCapId, setSelectedCapId] = useState<string | null>(null);

  // 1. Process Real Backend Data using graph.capabilities as authoritative base
  const capabilities = useMemo(() => {
    // Base capability strings provided by backend
    const baseCaps = analysisResult?.graph_metrics?.capabilities || [];
    
    // Optional graph data for enrichment
    const rawNodes = analysisResult?.graph_metrics?.raw_nodes || [];
    const rawEdges = analysisResult?.graph_metrics?.raw_edges || [];
    const nodeMap = new Map(rawNodes.map(n => [n.id, n]));
    
    // Find all potential capability nodes
    const capNodes = rawNodes.filter(n => 
      n.type?.toLowerCase() === 'capability' || 
      n.labels?.some((l: string) => l.toLowerCase() === 'capability')
    );
    
    return baseCaps.map(capName => {
      // Find matching node for enrichment
      const capNode = capNodes.find(n => n.name === capName || n.id === capName);
      
      const features: any[] = [];
      const technologies: any[] = [];
      const evidenceNodes: any[] = [];
      
      // If a graph node exists, traverse edges to find real relationships
      if (capNode) {
        const relatedEdges = rawEdges.filter(e => e.source === capNode.id || e.target === capNode.id);
        
        relatedEdges.forEach(edge => {
          const otherId = edge.source === capNode.id ? edge.target : edge.source;
          const otherNode = nodeMap.get(otherId);
          if (!otherNode) return;
          
          const type = (otherNode.type || otherNode.labels?.[0] || '').toLowerCase();
          
          if (type === 'feature' || type === 'semanticfeature' || type === 'claim') {
            features.push(otherNode);
          } else if (type === 'technology') {
            technologies.push(otherNode);
          } else if (type === 'evidence' || type === 'file' || type === 'code' || type === 'document') {
            evidenceNodes.push(otherNode);
          }
        });
      }
      
      return {
        id: capNode?.id || capName,
        name: capName,
        category: capNode?.category || capNode?.properties?.category || null,
        properties: capNode?.properties || {},
        features,
        technologies,
        evidence: evidenceNodes
      };
    }).sort((a, b) => a.name.localeCompare(b.name));
  }, [analysisResult]);

  // 2. Only show Category filters if backend explicitly provided categories
  const availableCategories = useMemo(() => {
    const set = new Set<string>();
    capabilities.forEach(c => {
      if (c.category) set.add(c.category);
    });
    return set.size > 0 ? ['All', ...Array.from(set).sort()] : [];
  }, [capabilities]);

  // 3. Filtering
  const filteredCaps = useMemo(() => {
    return capabilities.filter(c => {
      const matchesSearch = c.name.toLowerCase().includes(search.toLowerCase());
      const matchesCategory = selectedCategory === 'All' || c.category === selectedCategory;
      return matchesSearch && matchesCategory;
    });
  }, [capabilities, search, selectedCategory]);

  const selectedCap = capabilities.find(c => c.id === selectedCapId);

  if (!analysisResult && !isAnalyzing) return <EmptyState />;

  return (
    <div className="p-6 h-full flex flex-col animate-in">
      {/* ── 1. Header ─────────────────────────────────────────────── */}
      <div className="mb-8 shrink-0">
        <h1 className="text-3xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
          <Zap size={28} className="text-slate-900" />
          Capabilities
        </h1>
        <p className="text-slate-500 mt-2 mb-8">
          System capabilities strictly derived from repository graph evidence and composition.
        </p>

        {/* Search & Dynamic Filters */}
        <div className="flex flex-col md:flex-row gap-4 items-start md:items-center">
          <div className="relative w-full md:w-80">
            <Search className="absolute left-3 top-2.5 text-slate-400" size={18} />
            <input 
              type="text" 
              placeholder="Search capabilities..." 
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-white border border-slate-200 rounded-xl pl-10 pr-4 py-2.5 text-sm focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 shadow-sm transition-all"
            />
          </div>
          
          {availableCategories.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {availableCategories.map(cat => {
                const theme = cat !== 'All' ? getTheme(cat) : null;
                const isActive = selectedCategory === cat;
                
                return (
                  <button
                    key={cat}
                    onClick={() => setSelectedCategory(cat)}
                    className={`px-4 py-2 rounded-xl text-sm font-semibold transition-all border ${
                      isActive 
                        ? cat === 'All' ? 'bg-slate-800 text-white border-slate-800 shadow-md' : (theme?.activeFilterClass + ' shadow-sm')
                        : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50'
                    }`}
                  >
                    {cat}
                  </button>
                );
              })}
            </div>
          )}
        </div>
      </div>

      {/* ── 2. Main Content Area ────────────────────────────────────── */}
      <div className="flex-1 flex gap-8 min-h-0 relative">
        <div className="flex-1 flex flex-col min-w-0">
          
          <div className="flex-1 overflow-y-auto custom-scrollbar pr-2">
            <h2 className="text-xs font-bold text-slate-400 mb-5 uppercase tracking-widest">Capability Inventory</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 pb-6">
              {filteredCaps.length === 0 ? (
                <div className="col-span-full py-12 text-center bg-slate-50 rounded-3xl border border-dashed border-slate-200">
                   <Zap size={32} className="mx-auto mb-4 text-slate-300" />
                   <p className="text-slate-500 font-medium">No capabilities match your search.</p>
                </div>
              ) : (
                filteredCaps.map((cap, i) => {
                  const isSelected = selectedCapId === cap.id;
                  const theme = getTheme(cap.category || cap.name);
                  
                  return (
                    <motion.div 
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: i * 0.03 }}
                      key={cap.id} 
                      onClick={() => setSelectedCapId(isSelected ? null : cap.id)}
                      className={`p-5 rounded-3xl border-2 transition-all cursor-pointer flex flex-col justify-between min-h-[160px] group
                        ${isSelected ? 'ring-4 ring-primary/20 scale-[1.02] z-10' : 'hover:-translate-y-1 hover:shadow-lg'}
                        ${theme.bgClass} ${theme.borderClass} ${theme.hoverBorderClass}
                      `}
                    >
                      <div>
                        <div className="flex items-center gap-3 mb-4">
                          <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 shadow-sm border border-white/50 ${theme.iconBgClass}`}>
                            <Zap className={theme.iconClass} size={20} />
                          </div>
                          <div>
                            <h3 className="font-bold text-slate-900 text-[16px] leading-tight mb-1">{cap.name}</h3>
                          </div>
                        </div>

                        {/* Rendering Supporting Features dynamically if they exist */}
                        {cap.features && cap.features.length > 0 && (
                           <div className="space-y-1 mb-4">
                             {cap.features.slice(0, 3).map((feat, idx) => (
                                <div key={idx} className="flex items-start gap-2 text-sm text-slate-700 font-medium">
                                  <Layers size={14} className={`shrink-0 mt-0.5 ${theme.iconClass}`} />
                                  <span className="truncate">{feat.name || feat.id}</span>
                                </div>
                             ))}
                             {cap.features.length > 3 && (
                                <div className="text-xs text-slate-500 font-semibold pl-6">
                                  + {cap.features.length - 3} more
                                </div>
                             )}
                           </div>
                        )}
                      </div>
                      
                      <div className="mt-4 pt-4 border-t border-black/5 flex flex-col gap-1.5">
                        <div className="flex justify-between items-center text-xs">
                          {cap.features && cap.features.length > 0 ? (
                            <span className="font-semibold text-slate-600 flex items-center gap-1.5">
                              <Layers size={12} /> {cap.features.length} supporting features
                            </span>
                          ) : cap.evidence && cap.evidence.length > 0 ? (
                            <span className="font-semibold text-slate-600 flex items-center gap-1.5">
                              <Link2 size={12} /> {cap.evidence.length} evidence sources
                            </span>
                          ) : <span />}
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
          {selectedCap && (
            <motion.div 
              initial={{ opacity: 0, x: 20, width: 0 }}
              animate={{ opacity: 1, x: 0, width: 420 }}
              exit={{ opacity: 0, x: 20, width: 0 }}
              className="shrink-0 h-full overflow-hidden hidden md:block"
            >
              <div className="w-[420px] h-full bg-white rounded-3xl border border-slate-100 shadow-2xl shadow-slate-200/50 flex flex-col overflow-hidden">
                
                {/* Dynamic Header */}
                {(() => {
                  const theme = getTheme(selectedCap.category || selectedCap.name);
                  return (
                    <div className={`p-6 border-b border-slate-100 ${theme.bgClass} flex justify-between items-start`}>
                      <div className="flex items-start gap-4">
                        <div className={`w-12 h-12 rounded-2xl flex items-center justify-center shrink-0 shadow-sm border border-white/50 ${theme.iconBgClass}`}>
                           <Zap className={theme.iconClass} size={24} />
                        </div>
                        <div>
                          <h3 className="font-bold text-xl text-slate-900 leading-tight mb-1">{selectedCap.name}</h3>
                          {selectedCap.category && (
                            <span className={`inline-block mt-1 px-2.5 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-white border ${theme.textClass} ${theme.borderClass}`}>
                              {selectedCap.category}
                            </span>
                          )}
                        </div>
                      </div>
                      <button 
                        onClick={() => setSelectedCapId(null)} 
                        className="p-1.5 rounded-xl text-slate-400 hover:text-slate-700 hover:bg-white transition-colors shadow-sm"
                      >
                        <X size={18} />
                      </button>
                    </div>
                  );
                })()}
                
                <div className="flex-1 overflow-y-auto custom-scrollbar p-6 space-y-8">
                  
                  {/* SUPPORTING FEATURES */}
                  {selectedCap.features && selectedCap.features.length > 0 && (
                    <div>
                      <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-3 flex items-center gap-2">
                        <Layers size={14} /> Supporting Features
                      </h4>
                      <div className="bg-slate-50 border border-slate-100 rounded-2xl p-4 space-y-3">
                         {selectedCap.features.map((feat, idx) => (
                           <div key={idx} className="flex items-center gap-3">
                             <div className="w-1.5 h-1.5 rounded-full bg-slate-400" />
                             <span className="text-sm font-semibold text-slate-700">{feat.name || feat.id}</span>
                           </div>
                         ))}
                      </div>
                    </div>
                  )}

                  {/* RELATED TECHNOLOGIES */}
                  {selectedCap.technologies && selectedCap.technologies.length > 0 && (
                    <div>
                      <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-3 flex items-center gap-2">
                        <Box size={14} /> Related Technologies
                      </h4>
                      <div className="flex flex-wrap gap-2">
                         {selectedCap.technologies.map((tech, idx) => (
                           <span key={idx} className="px-3 py-1.5 rounded-xl bg-slate-50 border border-slate-200 text-xs font-semibold text-slate-700 shadow-sm">
                             {tech.name || tech.id}
                           </span>
                         ))}
                      </div>
                    </div>
                  )}

                  {/* EVIDENCE */}
                  {selectedCap.evidence && selectedCap.evidence.length > 0 && (
                    <div>
                      <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-3 flex items-center gap-2">
                        <Link2 size={14} /> Backend Evidence Links
                      </h4>
                      <div className="bg-slate-50 border border-slate-100 rounded-2xl p-4 space-y-3">
                         {selectedCap.evidence.map((ev, idx) => (
                           <div key={idx} className="text-sm">
                             <div className="font-semibold text-slate-800 mb-1">{ev.name || ev.id}</div>
                             {ev.properties?.file_path && (
                               <div className="text-xs font-mono text-slate-500 break-all">
                                 {ev.properties.file_path}
                                 {ev.properties.line_number ? ` : ${ev.properties.line_number}` : ''}
                               </div>
                             )}
                           </div>
                         ))}
                      </div>
                    </div>
                  )}
                  
                  {(!selectedCap.features?.length) && (!selectedCap.technologies?.length) && (!selectedCap.evidence?.length) && (
                    <div className="text-center py-8">
                       <p className="text-slate-500 text-sm">No supporting relationships exposed.</p>
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
