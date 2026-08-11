import { useState, useMemo } from 'react';
import { useAnalysisStore } from '@/store';
import EmptyState from '@/components/EmptyState';
import MetricsCard from '@/components/MetricsCard';
import {
  FileCode2, GitMerge, Layers, Link2, Code2, GitGraph,
  Search, ArrowRight, Package, GitBranch, TerminalSquare, AlertCircle
} from 'lucide-react';
import { formatNumber } from '@/lib/utils';

export default function CodeIntelligence() {
  const { analysisResult, isAnalyzing } = useAnalysisStore();
  const [activeTab, setActiveTab] = useState<'symbols' | 'relationships'>('symbols');
  const [search, setSearch] = useState('');
  const [selectedSymbolId, setSelectedSymbolId] = useState<string | null>(null);

  if (!analysisResult && !isAnalyzing) return <EmptyState />;

  const code = analysisResult?.code_metrics;
  const graph = analysisResult?.graph_metrics;

  // Derive symbols
  const rawNodes = graph?.raw_nodes || [];
  const rawEdges = graph?.raw_edges || [];

  const symbols = useMemo(() => {
    // Only nodes that look like code symbols (Class, Method, Function, Interface, Variable, etc.)
    return rawNodes.filter(n => {
      const t = n.type.toLowerCase();
      return ['class', 'method', 'function', 'interface', 'variable', 'enum', 'struct', 'property'].includes(t) || t === 'symbol';
    });
  }, [rawNodes]);

  const filteredSymbols = useMemo(() => {
    if (!search) return symbols;
    const q = search.toLowerCase();
    return symbols.filter(s =>
      (s.name || '').toLowerCase().includes(q) ||
      (s.type || '').toLowerCase().includes(q) ||
      (s.file_path || '').toLowerCase().includes(q)
    );
  }, [symbols, search]);

  const selectedSymbol = useMemo(() => {
    return symbols.find(s => s.id === selectedSymbolId) || null;
  }, [symbols, selectedSymbolId]);

  const symbolEdges = useMemo(() => {
    if (!selectedSymbol) return { inbound: [], outbound: [] };
    return {
      inbound: rawEdges.filter(e => e.target === selectedSymbol.id),
      outbound: rawEdges.filter(e => e.source === selectedSymbol.id)
    };
  }, [selectedSymbol, rawEdges]);

  // Derive relationships summary
  const edgeSummary = useMemo(() => {
    const summary: Record<string, number> = {};
    for (const e of rawEdges) {
      summary[e.type] = (summary[e.type] || 0) + 1;
    }
    return Object.entries(summary).sort((a, b) => b[1] - a[1]);
  }, [rawEdges]);

  return (
    <div className="p-6 space-y-6 animate-in max-w-[1400px] mx-auto">

      {/* ── 1. Top Header & Metrics ───────────────────────────────────── */}
      <div className="space-y-6">
        <h1 className="text-2xl font-bold">Code Intelligence</h1>

        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          <MetricsCard label="Source Files" value={code?.source_files} icon={FileCode2} color="primary" loading={isAnalyzing} />
          <MetricsCard label="Parsed Files" value={code?.parsed_files} icon={GitMerge} color="emerald" loading={isAnalyzing} />
          <MetricsCard label="AST Nodes" value={code?.ast_nodes} icon={GitGraph} color="violet" loading={isAnalyzing} />
          <MetricsCard label="UIR Nodes" value={code?.uir_files} icon={Layers} color="amber" loading={isAnalyzing} />
          <MetricsCard label="Symbols" value={code?.symbols} icon={Code2} color="primary" loading={isAnalyzing} />
          <MetricsCard label="Relationships" value={code?.relationships} icon={Link2} color="red" loading={isAnalyzing} />
        </div>

        {/* ── 2. Code Analysis Pipeline ───────────────────────────────── */}
        <div className="glass rounded-2xl p-6">
          <h2 className="text-sm font-semibold mb-6 flex items-center gap-2">
            <TerminalSquare size={16} className="text-primary" />
            Code Analysis Pipeline
          </h2>
          <div className="flex flex-col md:flex-row items-center justify-between gap-4 md:gap-2">
            <PipelineStage name="Source Files" value={code?.source_files} icon={FileCode2} color="text-primary" bg="bg-primary/10" border="border-primary/20" />
            <ArrowRight className="text-slate-300 hidden md:block" />
            <PipelineStage name="Parser" value={code?.parsed_files} icon={GitMerge} color="text-emerald-500" bg="bg-emerald-500/10" border="border-emerald-500/20" />
            <ArrowRight className="text-slate-300 hidden md:block" />
            <PipelineStage name="AST" value={code?.ast_nodes} icon={GitGraph} color="text-violet-500" bg="bg-violet-500/10" border="border-violet-500/20" />
            <ArrowRight className="text-slate-300 hidden md:block" />
            <PipelineStage name="Canonical UIR" value={code?.uir_files} icon={Layers} color="text-amber-500" bg="bg-amber-500/10" border="border-amber-500/20" />
            <ArrowRight className="text-slate-300 hidden md:block" />
            <PipelineStage name="Semantic Symbols" value={code?.symbols} icon={Code2} color="text-indigo-500" bg="bg-indigo-500/10" border="border-indigo-500/20" />
            <ArrowRight className="text-slate-300 hidden md:block" />
            <PipelineStage name="Relationships" value={code?.relationships} icon={Link2} color="text-rose-500" bg="bg-rose-500/10" border="border-rose-500/20" />
          </div>
        </div>

        {/* Tabs */}
        <div className="flex items-center gap-6 border-b border-border">
          <button
            className={`pb-3 text-sm font-medium transition-colors border-b-2 ${activeTab === 'symbols' ? 'border-primary text-foreground' : 'border-transparent text-muted-foreground hover:text-foreground'}`}
            onClick={() => setActiveTab('symbols')}
          >
            Symbols
          </button>
          <button
            className={`pb-3 text-sm font-medium transition-colors border-b-2 ${activeTab === 'relationships' ? 'border-primary text-foreground' : 'border-transparent text-muted-foreground hover:text-foreground'}`}
            onClick={() => setActiveTab('relationships')}
          >
            Relationships
          </button>
        </div>
      </div>

      {/* ── 3. Tab Content ────────────────────────────────────────────── */}
      <div className="min-h-[600px] h-[600px]">
        {activeTab === 'symbols' && (
          <div className="h-full flex gap-6">
            {/* Symbol Explorer List */}
            <div className={`glass rounded-2xl flex flex-col h-full overflow-hidden transition-all duration-300 ${selectedSymbol ? 'w-2/3' : 'w-full'}`}>
              <div className="p-4 border-b border-border bg-slate-50/50 flex items-center justify-between shrink-0">
                <h3 className="font-semibold text-sm">Symbol Explorer</h3>
                <div className="relative w-64">
                  <Search className="absolute left-2.5 top-2 text-slate-400" size={14} />
                  <input
                    type="text"
                    placeholder="Search symbols..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    className="w-full bg-white border border-slate-200 rounded-lg pl-8 pr-3 py-1.5 text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/20 transition-all"
                  />
                </div>
              </div>
              <div className="flex-1 overflow-y-auto custom-scrollbar bg-white">
                <table className="w-full text-left text-sm whitespace-nowrap">
                  <thead className="bg-slate-50 sticky top-0 z-10 shadow-sm shadow-slate-100">
                    <tr>
                      <th className="px-6 py-3 font-semibold text-slate-600">Symbol</th>
                      <th className="px-6 py-3 font-semibold text-slate-600">Type</th>
                      <th className="px-6 py-3 font-semibold text-slate-600 w-full">File</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {filteredSymbols.map(sym => (
                      <tr
                        key={sym.id}
                        onClick={() => setSelectedSymbolId(sym.id)}
                        className={`cursor-pointer transition-colors ${selectedSymbolId === sym.id ? 'bg-indigo-50/50 hover:bg-indigo-50' : 'hover:bg-slate-50/80'}`}
                      >
                        <td className="px-6 py-3">
                          <span className="font-semibold text-slate-800">{sym.name || sym.id.split('.').pop()}</span>
                        </td>
                        <td className="px-6 py-3">
                          <span className="status-badge bg-slate-100 text-slate-600 border border-slate-200">
                            {sym.type}
                          </span>
                        </td>
                        <td className="px-6 py-3 font-mono text-xs text-muted-foreground truncate max-w-xs">
                          {sym.file_path || sym.location || '-'}
                        </td>
                      </tr>
                    ))}
                    {filteredSymbols.length === 0 && (
                      <tr>
                        <td colSpan={3} className="px-6 py-12 text-center text-muted-foreground">
                          No symbols match your search.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Symbol Details Panel */}
            {selectedSymbol && (
              <div className="w-1/3 glass rounded-2xl flex flex-col h-full overflow-hidden animate-in slide-in-from-right-4">
                <div className="p-5 border-b border-border bg-slate-50/50 shrink-0 flex justify-between items-start">
                  <div>
                    <h3 className="text-lg font-bold text-slate-800 break-all leading-tight">
                      {selectedSymbol.name || selectedSymbol.id.split('.').pop()}
                    </h3>
                    <div className="mt-2 flex gap-2">
                      <span className="status-badge bg-primary/10 text-primary border border-primary/20">{selectedSymbol.type}</span>
                      {selectedSymbol.language && (
                        <span className="status-badge bg-slate-100 text-slate-600 border border-slate-200">{selectedSymbol.language}</span>
                      )}
                    </div>
                  </div>
                  <button onClick={() => setSelectedSymbolId(null)} className="text-slate-400 hover:text-slate-600 p-1">
                    ✕
                  </button>
                </div>

                <div className="flex-1 overflow-y-auto custom-scrollbar p-5 space-y-6 bg-white">
                  <div>
                    <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Qualified Name</p>
                    <p className="font-mono text-sm text-slate-700 break-all p-3 bg-slate-50 rounded-lg border border-slate-100">
                      {selectedSymbol.id}
                    </p>
                  </div>

                  {selectedSymbol.file_path && (
                    <div>
                      <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">File Location</p>
                      <p className="font-mono text-sm text-slate-700 break-all p-3 bg-slate-50 rounded-lg border border-slate-100">
                        {selectedSymbol.file_path}
                      </p>
                    </div>
                  )}

                  <hr className="border-slate-100" />

                  <div>
                    <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">Relationships ({symbolEdges.outbound.length + symbolEdges.inbound.length})</p>
                    {symbolEdges.outbound.length > 0 && (
                      <div className="mb-4">
                        <p className="text-xs text-slate-400 mb-2 font-medium">Outbound</p>
                        <ul className="space-y-2">
                          {symbolEdges.outbound.map((e, i) => (
                            <li key={i} className="text-sm flex flex-col gap-1 p-2 bg-slate-50/50 rounded-md border border-slate-100">
                              <span className="text-[10px] font-bold text-slate-500 tracking-wider uppercase">{e.type} ➔</span>
                              <span className="font-mono text-xs text-slate-700 truncate" title={e.target}>{e.target.split('.').pop()}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {symbolEdges.inbound.length > 0 && (
                      <div>
                        <p className="text-xs text-slate-400 mb-2 font-medium">Inbound</p>
                        <ul className="space-y-2">
                          {symbolEdges.inbound.map((e, i) => (
                            <li key={i} className="text-sm flex flex-col gap-1 p-2 bg-slate-50/50 rounded-md border border-slate-100">
                              <span className="text-[10px] font-bold text-slate-500 tracking-wider uppercase">➔ {e.type}</span>
                              <span className="font-mono text-xs text-slate-700 truncate" title={e.source}>{e.source.split('.').pop()}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {symbolEdges.outbound.length === 0 && symbolEdges.inbound.length === 0 && (
                      <p className="text-sm text-muted-foreground italic">No relationships mapped.</p>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'relationships' && (
          <div className="glass rounded-2xl h-full flex flex-col overflow-hidden">
            <div className="p-5 border-b border-border bg-slate-50/50 shrink-0">
              <h3 className="font-semibold text-sm">Relationship Explorer</h3>
              <p className="text-xs text-muted-foreground mt-1">Found {formatNumber(rawEdges.length)} relationships across {edgeSummary.length} types</p>
            </div>
            <div className="flex-1 overflow-y-auto p-6 bg-white custom-scrollbar">
              {edgeSummary.length > 0 ? (
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                  {edgeSummary.map(([type, count]) => (
                    <div key={type} className="p-4 rounded-xl border border-slate-200 bg-slate-50 flex items-center justify-between hover:border-primary/30 transition-colors">
                      <span className="font-bold text-sm text-slate-700 tracking-wider uppercase">{type}</span>
                      <span className="px-2.5 py-1 rounded-full bg-white border border-slate-200 text-xs font-semibold text-slate-600 shadow-sm">
                        {formatNumber(count)}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="h-full flex flex-col items-center justify-center text-slate-400">
                  <GitBranch size={48} className="text-slate-200 mb-4" />
                  <p>No architectural relationships extracted.</p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function PipelineStage({ name, value, icon: Icon, color, bg, border }: any) {
  return (
    <div className={`flex flex-col items-center justify-center w-32 h-28 rounded-xl border ${border} ${bg} text-center p-3 relative`}>
      <Icon size={20} className={`${color} mb-2`} />
      <span className="text-xs font-medium text-slate-600 leading-tight">{name}</span>
      <span className={`text-lg font-bold mt-1 ${color}`}>{value !== undefined ? formatNumber(value) : '-'}</span>
    </div>
  );
}
