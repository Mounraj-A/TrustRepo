import { useAnalysisStore } from '@/store';
import EmptyState from '@/components/EmptyState';
import { FolderTree, File, GitBranch, Package } from 'lucide-react';
import MetricsCard from '@/components/MetricsCard';
import { extractRepoName } from '@/lib/utils';

export default function RepositoryExplorer() {
  const { analysisResult, isAnalyzing, repositoryUrl } = useAnalysisStore();
  if (!analysisResult && !isAnalyzing) return <EmptyState />;

  const code = analysisResult?.code_metrics;
  const graph = analysisResult?.graph_metrics;
  const report = analysisResult?.report;
  const intel = analysisResult?.code_intelligence;

  const repoName = report?.repository_name ?? extractRepoName(repositoryUrl);
  const isLocal = repositoryUrl?.startsWith('D:') || repositoryUrl?.startsWith('C:') || repositoryUrl?.startsWith('/');

  return (
    <div className="p-6 space-y-6 animate-in">
      <div className="flex items-center gap-3">
        <div className="p-2.5 bg-primary/10 rounded-xl">
          <FolderTree size={20} className="text-primary" />
        </div>
        <div>
          <h1 className="text-2xl font-bold">{repoName}</h1>
          <p className="text-xs text-muted-foreground font-mono">{repositoryUrl}</p>
        </div>
        <span className={`status-badge border ml-auto ${isLocal ? 'bg-violet-500/10 text-violet-400 border-violet-500/20' : 'bg-primary/10 text-primary border-primary/20'}`}>
          {isLocal ? 'Local Path' : 'GitHub'}
        </span>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricsCard label="Source Files"   value={code?.source_files}   icon={File}       loading={isAnalyzing} />
        <MetricsCard label="Parsed Files"   value={code?.parsed_files}   icon={File}       color="emerald" loading={isAnalyzing} />
        <MetricsCard label="Symbols"        value={code?.symbols}        icon={Package}    color="violet"  loading={isAnalyzing} />
        <MetricsCard label="Relationships"  value={code?.relationships}  icon={GitBranch}  color="amber"   loading={isAnalyzing} />
      </div>

      {/* Languages */}
      {graph?.technologies?.length ? (
        <div className="glass rounded-2xl p-6">
          <h2 className="text-sm font-semibold mb-3">Technology Stack</h2>
          <div className="flex flex-wrap gap-2">
            {graph.technologies.map((t) => (
              <span key={t} className="status-badge bg-muted text-foreground border border-border">{t}</span>
            ))}
          </div>
        </div>
      ) : null}

      {/* Components from code intelligence */}
      {intel?.detected_components?.length ? (
        <div className="glass rounded-2xl p-6">
          <h2 className="text-sm font-semibold mb-3">Detected Components ({intel.detected_components.length})</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2">
            {intel.detected_components.map((c) => (
              <div key={c} className="flex items-center gap-2 text-sm bg-muted/40 rounded-lg px-3 py-2">
                <File size={12} className="text-muted-foreground shrink-0" />
                <span className="font-mono text-xs truncate">{c}</span>
              </div>
            ))}
          </div>
        </div>
      ) : null}

      {/* Missing docs */}
      {intel?.missing_documentation?.length ? (
        <div className="glass rounded-2xl p-6 border border-amber-500/20">
          <h2 className="text-sm font-semibold text-amber-400 mb-3">Missing Documentation</h2>
          <ul className="space-y-2">
            {intel.missing_documentation.map((d, i) => (
              <li key={i} className="text-sm text-muted-foreground flex items-center gap-2">
                <span className="w-1.5 h-1.5 bg-amber-400 rounded-full shrink-0" />
                {d}
              </li>
            ))}
          </ul>
        </div>
      ) : null}
    </div>
  );
}
