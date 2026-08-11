import { useState, useMemo } from 'react';
import { useAnalysisStore } from '@/store';
import EmptyState from '@/components/EmptyState';
import {
  FolderTree, File, GitBranch, Package, ChevronRight, ChevronDown,
  Search, Code2, LayoutTemplate, Layers, Link as LinkIcon
} from 'lucide-react';
import MetricsCard from '@/components/MetricsCard';
import { extractRepoName, formatDuration } from '@/lib/utils';
import type { FileTreeNode } from '@/types/api';

// --- FileTree Component ---
function FileTreeItem({
  node,
  level = 0,
  onSelect,
  selectedPath
}: {
  node: FileTreeNode;
  level?: number;
  onSelect: (n: FileTreeNode) => void;
  selectedPath?: string;
}) {
  const [isOpen, setIsOpen] = useState(false);
  const isDir = node.type === 'directory';
  const isSelected = selectedPath === node.path;

  const toggle = () => {
    if (isDir) setIsOpen(!isOpen);
    else onSelect(node);
  };

  return (
    <div className="w-full">
      <div
        className={`flex items-center gap-1.5 py-1 px-2 rounded-md cursor-pointer text-sm
          ${isSelected ? 'bg-primary/10 text-primary font-medium' : 'hover:bg-slate-50 text-slate-700'}
        `}
        style={{ paddingLeft: `${level * 12 + 8}px` }}
        onClick={toggle}
      >
        {isDir ? (
          isOpen ? <ChevronDown size={14} className="text-slate-400 shrink-0" /> : <ChevronRight size={14} className="text-slate-400 shrink-0" />
        ) : (
          <span className="w-[14px] shrink-0" /> // Spacer for alignment
        )}

        {isDir ? (
          <span className="text-amber-500 shrink-0">📁</span>
        ) : (
          <span className="text-slate-400 shrink-0">📄</span>
        )}

        <span className="truncate">{node.name}</span>
      </div>

      {isDir && isOpen && node.children && (
        <div className="flex flex-col w-full">
          {node.children.map((child, i) => (
            <FileTreeItem
              key={`${child.path || child.name}-${i}`}
              node={child}
              level={level + 1}
              onSelect={onSelect}
              selectedPath={selectedPath}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export default function RepositoryExplorer() {
  const { analysisResult, isAnalyzing, repositoryUrl } = useAnalysisStore();
  const [search, setSearch] = useState('');
  const [selectedFile, setSelectedFile] = useState<FileTreeNode | null>(null);

  if (!analysisResult && !isAnalyzing) return <EmptyState />;

  const code = analysisResult?.code_metrics;
  const graph = analysisResult?.graph_metrics;
  const report = analysisResult?.report;
  const fileTree = analysisResult?.file_tree ?? [];
  const meta = report?.metadata;

  const repoName = meta?.repository_url?.split(/[\/\\]/).pop() ?? extractRepoName(repositoryUrl);
  const duration = analysisResult?.processing_time_seconds
    ? formatDuration(analysisResult.processing_time_seconds)
    : '';

  // Filter file tree based on search (simplified flat match for now)
  const filteredTree = useMemo(() => {
    if (!search.trim()) return fileTree;
    const q = search.toLowerCase();

    // Recursive filter function
    const filterNode = (node: FileTreeNode): FileTreeNode | null => {
      if (node.type === 'file') {
        return node.name.toLowerCase().includes(q) ? node : null;
      }
      if (node.children) {
        const filteredChildren = node.children.map(filterNode).filter(Boolean) as FileTreeNode[];
        if (filteredChildren.length > 0 || node.name.toLowerCase().includes(q)) {
          return { ...node, children: filteredChildren };
        }
      }
      return null;
    };

    return fileTree.map(filterNode).filter(Boolean) as FileTreeNode[];
  }, [fileTree, search]);

  // Derive some symbols and relationships for the selected file if possible
  const fileSymbols = useMemo(() => {
    if (!selectedFile || !selectedFile.path || !graph?.raw_nodes) return [];
    // Just a heuristic: nodes whose file_path contains the selected file path
    // or namespace matches
    return graph.raw_nodes.filter(n =>
      n.file_path === selectedFile.path ||
      (n.location && typeof n.location === 'string' && n.location.includes(selectedFile.path))
    ).slice(0, 20); // Cap at 20 for display
  }, [selectedFile, graph?.raw_nodes]);

  const fileEdges = useMemo(() => {
    if (!fileSymbols.length || !graph?.raw_edges) return [];
    const symbolIds = new Set(fileSymbols.map(s => s.id));
    return graph.raw_edges.filter(e => symbolIds.has(e.source) || symbolIds.has(e.target)).slice(0, 20);
  }, [fileSymbols, graph?.raw_edges]);

  return (
    <div className="p-6 space-y-8 animate-in">
      {/* ── 1. Repository Header ──────────────────────────────────────── */}
      <div className="glass rounded-2xl p-6 flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <FolderTree className="text-primary" />
            {repoName}
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            {meta?.repository_url || repositoryUrl}
          </p>
          <div className="flex items-center gap-4 mt-4 text-sm text-slate-600">
            {meta?.languages?.[0] && <span><span className="font-semibold">{meta.languages[0]}</span></span>}
            {meta?.languages && meta.languages.length > 1 && <span>· {meta.languages.length} languages</span>}
            <span>· {code?.source_files ?? 0} files</span>
            {duration && <span>· analyzed {duration}</span>}
          </div>
        </div>
        <div className="flex gap-2">
          <a
            href={meta?.repository_url || repositoryUrl}
            target="_blank"
            rel="noreferrer"
            className="btn btn-outline text-sm py-1.5 px-3"
          >
            Open Source ↗
          </a>
        </div>
      </div>

      {/* ── 2. Statistics ─────────────────────────────────────────────── */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricsCard label="Source Files" value={code?.source_files} icon={File} color="primary" loading={isAnalyzing} />
        <MetricsCard label="Parsed Files" value={code?.parsed_files} icon={File} color="emerald" loading={isAnalyzing} />
        <MetricsCard label="Symbols" value={code?.symbols} icon={Package} color="violet" loading={isAnalyzing} />
        <MetricsCard label="Relationships" value={code?.relationships} icon={GitBranch} color="amber" loading={isAnalyzing} />
      </div>

      {/* ── 3. File Tree & Details ────────────────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* Left Pane: File Tree */}
        <div className="lg:col-span-1 glass rounded-2xl flex flex-col h-[600px] overflow-hidden">
          <div className="p-4 border-b border-border bg-slate-50/50">
            <h2 className="font-semibold text-sm mb-3">Repository Structure</h2>
            <div className="relative">
              <Search className="absolute left-2.5 top-2 text-slate-400" size={14} />
              <input
                type="text"
                placeholder="Search files, folders..."
                className="w-full bg-white border border-slate-200 rounded-lg pl-8 pr-3 py-1.5 text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/20 transition-all"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
          </div>
          <div className="flex-1 overflow-y-auto p-2 custom-scrollbar">
            {filteredTree.length > 0 ? (
              filteredTree.map((node, i) => (
                <FileTreeItem
                  key={`${node.path || node.name}-${i}`}
                  node={node}
                  onSelect={setSelectedFile}
                  selectedPath={selectedFile?.path}
                />
              ))
            ) : (
              <div className="p-4 text-sm text-center text-muted-foreground">
                No files found.
              </div>
            )}
          </div>
        </div>

        {/* Right Pane: File Details */}
        <div className="lg:col-span-2 glass rounded-2xl h-[600px] flex flex-col overflow-hidden">
          {selectedFile ? (
            <div className="flex-1 overflow-y-auto custom-scrollbar">
              <div className="p-6 border-b border-border bg-slate-50/50">
                <div className="flex items-center gap-3 mb-2">
                  <File className="text-primary" size={24} />
                  <h2 className="text-lg font-bold">{selectedFile.name}</h2>
                </div>
                <p className="text-sm font-mono text-muted-foreground">{selectedFile.path}</p>
                <div className="flex items-center gap-4 mt-4">
                  {selectedFile.language && (
                    <span className="status-badge bg-primary/10 text-primary border-primary/20">
                      {selectedFile.language}
                    </span>
                  )}
                  {selectedFile.size !== undefined && (
                    <span className="text-xs text-muted-foreground">
                      {(selectedFile.size / 1024).toFixed(1)} KB
                    </span>
                  )}
                </div>
              </div>

              <div className="p-6 space-y-6">
                <div>
                  <h3 className="text-sm font-semibold flex items-center gap-2 mb-3">
                    <Package size={16} className="text-violet-500" />
                    Symbols ({fileSymbols.length}{fileSymbols.length === 20 ? '+' : ''})
                  </h3>
                  {fileSymbols.length > 0 ? (
                    <div className="bg-slate-50 border border-slate-100 rounded-xl overflow-hidden">
                      {fileSymbols.map((sym, i) => (
                        <div key={i} className="flex flex-col px-4 py-2 text-sm border-b border-slate-100 last:border-0">
                          <span className="font-semibold text-slate-800">{sym.name || sym.id}</span>
                          <span className="text-xs text-muted-foreground font-mono truncate">{sym.type}</span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-sm text-muted-foreground">No symbols detected or mapped for this file.</p>
                  )}
                </div>

                <div>
                  <h3 className="text-sm font-semibold flex items-center gap-2 mb-3">
                    <GitBranch size={16} className="text-amber-500" />
                    Relationships ({fileEdges.length}{fileEdges.length === 20 ? '+' : ''})
                  </h3>
                  {fileEdges.length > 0 ? (
                    <div className="bg-slate-50 border border-slate-100 rounded-xl overflow-hidden">
                      {fileEdges.map((edge, i) => {
                        return (
                          <div key={i} className="flex items-center gap-2 px-4 py-2 text-sm border-b border-slate-100 last:border-0">
                            <span className="font-mono text-xs truncate max-w-[150px] text-slate-600" title={edge.source}>
                              {edge.source.split('.').pop()}
                            </span>
                            <span className="px-2 py-0.5 rounded text-[10px] font-bold tracking-wider bg-slate-200 text-slate-600">
                              {edge.type}
                            </span>
                            <span className="font-mono text-xs truncate max-w-[150px] text-slate-600" title={edge.target}>
                              {edge.target.split('.').pop()}
                            </span>
                          </div>
                        );
                      })}
                    </div>
                  ) : (
                    <p className="text-sm text-muted-foreground">No relationships mapped for this file.</p>
                  )}
                </div>
              </div>
            </div>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-slate-400 p-8 text-center bg-slate-50/30">
              <FolderTree size={48} className="text-slate-200 mb-4" />
              <p className="font-medium text-slate-600">Select a file to inspect</p>
              <p className="text-sm mt-2 max-w-sm">
                Explore its metadata, extracted symbols, and architectural relationships.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* ── 4. Repository Metadata ────────────────────────────────────── */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Languages Summary */}
        <div className="glass rounded-2xl p-5">
          <h3 className="text-sm font-semibold flex items-center gap-2 mb-3">
            <Code2 size={16} className="text-primary" /> Languages
          </h3>
          <div className="flex flex-wrap gap-1.5">
            {meta?.languages?.length ? (
              meta.languages.map(l => (
                <span key={l} className="px-2 py-1 bg-slate-100 text-slate-700 rounded-md text-xs font-medium">
                  {l}
                </span>
              ))
            ) : <span className="text-xs text-muted-foreground">None detected</span>}
          </div>
        </div>

        {/* Tech Summary */}
        <div className="glass rounded-2xl p-5">
          <h3 className="text-sm font-semibold flex items-center gap-2 mb-3">
            <Layers size={16} className="text-emerald-500" /> Technologies
          </h3>
          <div className="flex items-center justify-between">
            <span className="text-2xl font-bold">{graph?.technologies?.length || 0}</span>
            <span className="text-xs text-muted-foreground">detected</span>
          </div>
        </div>

        {/* Config Summary */}
        <div className="glass rounded-2xl p-5">
          <h3 className="text-sm font-semibold flex items-center gap-2 mb-3">
            <LayoutTemplate size={16} className="text-violet-500" /> Configuration
          </h3>
          <div className="flex flex-col gap-1 text-sm text-slate-600">
            <span className="truncate text-xs">Build & Config mapped</span>
          </div>
        </div>

        {/* Docs Summary */}
        <div className="glass rounded-2xl p-5">
          <h3 className="text-sm font-semibold flex items-center gap-2 mb-3">
            <LinkIcon size={16} className="text-amber-500" /> Documentation
          </h3>
          <div className="flex flex-col gap-1">
            {meta?.documentation_sources?.slice(0, 3).map((d, i) => (
              <span key={i} className="text-xs text-slate-600 font-mono truncate">{d.split(/[\/\\]/).pop()}</span>
            ))}
            {(!meta?.documentation_sources || meta.documentation_sources.length === 0) && (
              <span className="text-xs text-muted-foreground">No docs found</span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
