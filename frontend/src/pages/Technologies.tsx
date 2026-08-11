import { useState, useMemo } from 'react';
import { useAnalysisStore } from '@/store';
import EmptyState from '@/components/EmptyState';
import { Search, X, CheckCircle2, LayoutTemplate, Layers, Database, Server, Code2, FileJson, Network, Box, ChevronRight } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts';

const CATEGORY_THEMES: Record<string, any> = {
  'Backend Framework': {
    color: '#8b5cf6', // purple
    bgClass: 'bg-purple-50/50',
    borderClass: 'border-purple-200',
    hoverBorderClass: 'hover:border-purple-400',
    textClass: 'text-purple-700',
    iconClass: 'text-purple-600',
    iconBgClass: 'bg-purple-100',
    activeFilterClass: 'bg-purple-100 text-purple-800 border-purple-300'
  },
  'Frontend Framework': {
    color: '#10b981', // green
    bgClass: 'bg-emerald-50/50',
    borderClass: 'border-emerald-200',
    hoverBorderClass: 'hover:border-emerald-400',
    textClass: 'text-emerald-700',
    iconClass: 'text-emerald-600',
    iconBgClass: 'bg-emerald-100',
    activeFilterClass: 'bg-emerald-100 text-emerald-800 border-emerald-300'
  },
  'Database': {
    color: '#f97316', // orange
    bgClass: 'bg-orange-50/50',
    borderClass: 'border-orange-200',
    hoverBorderClass: 'hover:border-orange-400',
    textClass: 'text-orange-700',
    iconClass: 'text-orange-600',
    iconBgClass: 'bg-orange-100',
    activeFilterClass: 'bg-orange-100 text-orange-800 border-orange-300'
  },
  'API Documentation': {
    color: '#ec4899', // pink
    bgClass: 'bg-pink-50/50',
    borderClass: 'border-pink-200',
    hoverBorderClass: 'hover:border-pink-400',
    textClass: 'text-pink-700',
    iconClass: 'text-pink-600',
    iconBgClass: 'bg-pink-100',
    activeFilterClass: 'bg-pink-100 text-pink-800 border-pink-300'
  },
  'Serialization': {
    color: '#3b82f6', // blue
    bgClass: 'bg-blue-50/50',
    borderClass: 'border-blue-200',
    hoverBorderClass: 'hover:border-blue-400',
    textClass: 'text-blue-700',
    iconClass: 'text-blue-600',
    iconBgClass: 'bg-blue-100',
    activeFilterClass: 'bg-blue-100 text-blue-800 border-blue-300'
  },
  'Other': {
    color: '#64748b', // slate
    bgClass: 'bg-slate-50',
    borderClass: 'border-slate-200',
    hoverBorderClass: 'hover:border-slate-400',
    textClass: 'text-slate-700',
    iconClass: 'text-slate-600',
    iconBgClass: 'bg-slate-200',
    activeFilterClass: 'bg-slate-100 text-slate-800 border-slate-300'
  }
};

const getCategoryTheme = (category: string) => {
  const cat = (category || '').toLowerCase();
  if (cat.includes('backend')) return CATEGORY_THEMES['Backend Framework'];
  if (cat.includes('frontend')) return CATEGORY_THEMES['Frontend Framework'];
  if (cat.includes('database') || cat.includes('data')) return CATEGORY_THEMES['Database'];
  if (cat.includes('api')) return CATEGORY_THEMES['API Documentation'];
  if (cat.includes('serializ') || cat.includes('json')) return CATEGORY_THEMES['Serialization'];
  
  return CATEGORY_THEMES[category] || CATEGORY_THEMES['Other'];
};

const getCategoryIcon = (category: string) => {
  const cat = (category || '').toLowerCase();
  if (cat.includes('database')) return Database;
  if (cat.includes('backend')) return Server;
  if (cat.includes('frontend')) return Code2;
  if (cat.includes('serializ')) return FileJson;
  if (cat.includes('api')) return Network;
  return Box;
};

export default function Technologies() {
  const { analysisResult, isAnalyzing } = useAnalysisStore();
  
  const [search, setSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [selectedTechId, setSelectedTechId] = useState<string | null>(null);

  const graph = analysisResult?.graph_metrics;
  const categoriesMap = graph?.technology_categories || {};

  // 1. Extract unified Technology Dataset
  const techDataset = useMemo(() => {
    const techNames = graph?.technologies || [];
    
    return techNames.map(name => {
      // Determine category from the categories map provided by backend
      let category = 'Other';
      const foundEntry = Object.entries(categoriesMap).find(([_, items]) => (items as string[]).includes(name));
      if (foundEntry) {
        category = foundEntry[0];
      }

      return {
        id: name,
        name,
        category,
        confidence: undefined, // Explicitly undefined as per backend structure
        evidenceBacked: false,
        evidenceList: [],
        relatedFeatures: [],
        relatedArchitecture: []
      };
    }).sort((a, b) => a.name.localeCompare(b.name));
  }, [graph?.technologies, categoriesMap]);

  // 2. Filter available categories from the actual dataset
  const availableCategories = useMemo(() => {
    const set = new Set<string>();
    techDataset.forEach(t => { if (t.category) set.add(t.category); });
    return ['All', ...Array.from(set).sort()];
  }, [techDataset]);

  // 3. Filter technologies based on search & category selection
  const filteredTechs = useMemo(() => {
    return techDataset.filter(t => {
      const matchesSearch = t.name.toLowerCase().includes(search.toLowerCase()) || 
                            t.category.toLowerCase().includes(search.toLowerCase());
      const matchesCategory = selectedCategory === 'All' || t.category === selectedCategory;
      return matchesSearch && matchesCategory;
    });
  }, [techDataset, search, selectedCategory]);

  // 4. Calculate Distribution Chart Data
  const chartData = useMemo(() => {
    const counts: Record<string, number> = {};
    filteredTechs.forEach(t => {
      counts[t.category] = (counts[t.category] || 0) + 1;
    });
    return Object.entries(counts)
      .map(([name, value]) => {
        const theme = getCategoryTheme(name);
        return { name, value, color: theme.color };
      })
      .sort((a, b) => b.value - a.value);
  }, [filteredTechs]);

  const selectedTech = techDataset.find(t => t.id === selectedTechId);

  if (!analysisResult && !isAnalyzing) return <EmptyState />;

  return (
    <div className="p-6 h-full flex flex-col animate-in">
      {/* ── 1. Header & Filters ─────────────────────────────────────── */}
      <div className="mb-8 shrink-0">
        <h1 className="text-3xl font-bold text-slate-900 tracking-tight">Technologies</h1>
        <p className="text-slate-500 mt-2 mb-8">
          Technology stack detected from repository evidence.
        </p>
        
        <div className="flex flex-col md:flex-row gap-4 items-start md:items-center">
          <div className="relative w-full md:w-80">
            <Search className="absolute left-3 top-2.5 text-slate-400" size={18} />
            <input 
              type="text" 
              placeholder="Search technologies..." 
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-white border border-slate-200 rounded-xl pl-10 pr-4 py-2.5 text-sm focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 shadow-sm transition-all"
            />
          </div>
          
          <div className="flex flex-wrap gap-2">
            {availableCategories.map(cat => {
              const theme = cat !== 'All' ? getCategoryTheme(cat) : CATEGORY_THEMES['Other'];
              const isActive = selectedCategory === cat;
              
              return (
                <button
                  key={cat}
                  onClick={() => setSelectedCategory(cat)}
                  className={`px-4 py-2 rounded-xl text-sm font-semibold transition-all border ${
                    isActive 
                      ? cat === 'All' ? 'bg-slate-800 text-white border-slate-800 shadow-md' : theme.activeFilterClass + ' shadow-sm'
                      : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50'
                  }`}
                >
                  {cat}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* ── 2. Main Content Area ────────────────────────────────────── */}
      <div className="flex-1 flex gap-8 min-h-0 relative">
        <div className="flex-1 flex flex-col min-w-0">
          
          <div className="flex flex-col lg:flex-row gap-8 h-full min-h-0">
            {/* Inventory Grid */}
            <div className="flex-1 overflow-y-auto custom-scrollbar pr-4">
              <h2 className="text-xs font-bold text-slate-400 mb-5 uppercase tracking-widest">Technology Inventory</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 pb-6">
                {filteredTechs.length === 0 ? (
                  <p className="text-sm text-slate-500 col-span-full py-8 text-center bg-slate-50 rounded-2xl border border-dashed border-slate-200">
                    No technologies match your filters.
                  </p>
                ) : (
                  filteredTechs.map((tech, i) => {
                    const isSelected = selectedTechId === tech.id;
                    const theme = getCategoryTheme(tech.category);
                    const Icon = getCategoryIcon(tech.category);
                    
                    return (
                      <motion.div 
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: i * 0.03 }}
                        key={tech.id} 
                        onClick={() => setSelectedTechId(isSelected ? null : tech.id)}
                        className={`p-5 rounded-2xl border-2 transition-all cursor-pointer flex flex-col justify-between min-h-[140px] group
                          ${isSelected ? 'ring-4 ring-primary/20 scale-[1.02] z-10' : 'hover:-translate-y-1 hover:shadow-lg'}
                          ${theme.bgClass} ${theme.borderClass} ${theme.hoverBorderClass}
                        `}
                      >
                        <div className="flex justify-between items-start gap-4">
                          <div className="flex items-start gap-3">
                            <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 shadow-sm border border-white/50 ${theme.iconBgClass}`}>
                              <Icon className={theme.iconClass} size={20} />
                            </div>
                            <div className="min-w-0">
                              <h3 className="font-bold text-slate-900 text-[15px] truncate" title={tech.name}>{tech.name}</h3>
                              <span className={`inline-block px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider mt-1 border bg-white/50 ${theme.textClass} ${theme.borderClass}`}>
                                {tech.category}
                              </span>
                            </div>
                          </div>
                        </div>
                        
                        <div className="mt-5 pt-4 border-t border-black/5 flex items-center justify-between text-xs">
                          <span className="flex items-center gap-1.5 text-slate-600 font-medium">
                            <span className="w-1.5 h-1.5 rounded-full" style={{backgroundColor: theme.color}} /> Detected
                          </span>
                          
                          <span className={`${theme.textClass} font-semibold opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-1`}>
                            Details <ChevronRight size={14} />
                          </span>
                        </div>
                      </motion.div>
                    );
                  })
                )}
              </div>
            </div>

            {/* Distribution Chart */}
            <div className="w-full lg:w-80 shrink-0">
              <div className="bg-white rounded-3xl p-6 border border-slate-100 shadow-xl shadow-slate-200/40 sticky top-0">
                <h2 className="text-xs font-bold text-slate-400 mb-6 uppercase tracking-widest text-center">Distribution</h2>
                
                {chartData.length > 0 ? (
                  <div className="h-64 relative">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie 
                          data={chartData} 
                          cx="50%" 
                          cy="50%" 
                          innerRadius={65} 
                          outerRadius={95}
                          paddingAngle={4} 
                          dataKey="value"
                          stroke="none"
                        >
                          {chartData.map((d) => (
                            <Cell key={d.name} fill={d.color} />
                          ))}
                        </Pie>
                        <Tooltip
                          contentStyle={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 12, fontSize: 13, fontWeight: 600, boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                          itemStyle={{ color: '#0f172a' }}
                        />
                      </PieChart>
                    </ResponsiveContainer>
                    
                    {/* Donut Center */}
                    <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                      <span className="text-3xl font-black text-slate-800">{filteredTechs.length}</span>
                      <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Technologies</span>
                    </div>
                  </div>
                ) : (
                  <div className="h-64 flex items-center justify-center text-sm text-slate-400">No data available</div>
                )}
                
                <div className="mt-8 space-y-3">
                  {chartData.map(d => (
                    <div key={d.name} className="flex justify-between items-center text-sm">
                      <div className="flex items-center gap-3">
                        <span className="w-3 h-3 rounded-full shadow-sm" style={{ backgroundColor: d.color }} />
                        <span className="text-slate-600 font-medium">{d.name}</span>
                      </div>
                      <span className="font-bold text-slate-900 bg-slate-50 px-2.5 py-0.5 rounded-lg border border-slate-100">{d.value}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* ── 3. Right Side Detail Drawer ───────────────────────────── */}
        <AnimatePresence>
          {selectedTech && (
            <motion.div 
              initial={{ opacity: 0, x: 20, width: 0 }}
              animate={{ opacity: 1, x: 0, width: 360 }}
              exit={{ opacity: 0, x: 20, width: 0 }}
              className="shrink-0 h-full overflow-hidden"
            >
              <div className="w-[360px] h-full bg-white rounded-3xl border border-slate-100 shadow-xl shadow-slate-200/40 flex flex-col overflow-hidden">
                
                {/* Dynamic Header */}
                <div className={`p-6 border-b border-slate-100 ${getCategoryTheme(selectedTech.category).bgClass} flex justify-between items-start`}>
                  <div className="flex items-start gap-4">
                    <div className={`w-12 h-12 rounded-2xl flex items-center justify-center shrink-0 shadow-sm bg-white`}>
                       {(() => {
                         const Icon = getCategoryIcon(selectedTech.category);
                         const theme = getCategoryTheme(selectedTech.category);
                         return <Icon className={theme.iconClass} size={24} />;
                       })()}
                    </div>
                    <div>
                      <h3 className="font-bold text-xl text-slate-900">{selectedTech.name}</h3>
                      <span className={`inline-block mt-2 px-2.5 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-white ${getCategoryTheme(selectedTech.category).textClass}`}>
                        {selectedTech.category}
                      </span>
                    </div>
                  </div>
                  <button 
                    onClick={() => setSelectedTechId(null)} 
                    className="p-1.5 rounded-xl text-slate-400 hover:text-slate-700 hover:bg-white transition-colors shadow-sm"
                  >
                    <X size={18} />
                  </button>
                </div>
                
                <div className="flex-1 overflow-y-auto custom-scrollbar p-6 space-y-8">
                  
                  {/* Detection */}
                  <div>
                    <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-3">Detection</h4>
                    <div className="flex justify-between items-center bg-slate-50 border border-slate-100 rounded-xl p-4">
                      <span className="flex items-center gap-2 text-sm font-semibold text-slate-700">
                        <CheckCircle2 size={18} className={getCategoryTheme(selectedTech.category).textClass} />
                        Detected
                      </span>
                    </div>
                  </div>

                  {/* Dynamic sections only rendered if data exists (per strict rule) */}
                  {selectedTech.confidence !== undefined && (
                     <div>
                       <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-3">Confidence</h4>
                       <div className="bg-slate-50 border border-slate-100 rounded-xl p-4">
                         <div className="flex justify-between items-baseline mb-2">
                            <span className="font-bold text-slate-800 text-lg">{Math.round(selectedTech.confidence * 100)}%</span>
                         </div>
                         <div className="w-full bg-slate-200 rounded-full h-2">
                            <div className="h-2 rounded-full" style={{ width: `${selectedTech.confidence * 100}%`, backgroundColor: getCategoryTheme(selectedTech.category).color }} />
                         </div>
                       </div>
                     </div>
                  )}

                  {selectedTech.evidenceList && selectedTech.evidenceList.length > 0 && (
                    <div>
                      <div className="flex justify-between items-baseline mb-3">
                        <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Evidence Sources</h4>
                        <span className="text-xs font-semibold text-slate-500 bg-slate-100 px-2 py-0.5 rounded-full">
                          {selectedTech.evidenceList.length} sources
                        </span>
                      </div>
                      <div className="bg-slate-50 border border-slate-100 rounded-xl p-1.5">
                        {selectedTech.evidenceList.map((ev, i) => (
                          <div key={i} className="px-3 py-2 text-xs font-mono text-slate-600 border-b border-slate-100 last:border-0 truncate" title={ev}>
                            {ev}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {selectedTech.relatedFeatures && selectedTech.relatedFeatures.length > 0 && (
                    <div>
                      <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-3 flex items-center gap-1.5">
                        <LayoutTemplate size={14} /> Related Features
                      </h4>
                      <div className="flex flex-wrap gap-2">
                        {selectedTech.relatedFeatures.map((feat, i) => (
                          <span key={i} className="text-xs font-medium bg-slate-50 text-slate-700 border border-slate-200 px-3 py-1.5 rounded-lg shadow-sm">
                            {feat}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {selectedTech.relatedArchitecture && selectedTech.relatedArchitecture.length > 0 && (
                    <div>
                      <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-3 flex items-center gap-1.5">
                        <Layers size={14} /> Related Architecture
                      </h4>
                      <div className="flex flex-wrap gap-2">
                        {selectedTech.relatedArchitecture.map((arch, i) => (
                          <span key={i} className="text-xs font-medium bg-slate-50 text-slate-700 border border-slate-200 px-3 py-1.5 rounded-lg shadow-sm">
                            {arch}
                          </span>
                        ))}
                      </div>
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
