import { useAnalysisStore } from '@/store';
import EmptyState from '@/components/EmptyState';
import MetricsCard from '@/components/MetricsCard';
import { FileCode2, GitMerge, Layers, Link2, Code2, GitGraph } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { motion } from 'framer-motion';
import { formatNumber } from '@/lib/utils';

export default function CodeIntelligence() {
  const { analysisResult, isAnalyzing } = useAnalysisStore();
  if (!analysisResult && !isAnalyzing) return <EmptyState />;

  const code = analysisResult?.code_metrics;
  const intel = analysisResult?.code_intelligence;

  const chartData = code ? [
    { name: 'Source Files', value: code.source_files },
    { name: 'Parsed Files', value: code.parsed_files },
    { name: 'AST Nodes',    value: code.ast_nodes },
    { name: 'Symbols',      value: code.symbols },
    { name: 'UIR Files',    value: code.uir_files },
    { name: 'Relationships',value: code.relationships },
  ] : [];

  return (
    <div className="p-6 space-y-6 animate-in">
      <h1 className="text-2xl font-bold">Code Intelligence</h1>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <MetricsCard label="Source Files"  value={code?.source_files}   icon={FileCode2}  loading={isAnalyzing} />
        <MetricsCard label="Parsed Files"  value={code?.parsed_files}   icon={GitMerge}   loading={isAnalyzing} />
        <MetricsCard label="AST Nodes"     value={code?.ast_nodes}      icon={GitGraph}   color="violet" loading={isAnalyzing} />
        <MetricsCard label="UIR Files"     value={code?.uir_files}      icon={Layers}     loading={isAnalyzing} />
        <MetricsCard label="Symbols"       value={code?.symbols}        icon={Code2}      color="emerald" loading={isAnalyzing} />
        <MetricsCard label="Relationships" value={code?.relationships}  icon={Link2}      color="amber" loading={isAnalyzing} />
      </div>

      {/* Chart */}
      <div className="glass rounded-2xl p-6">
        <h2 className="text-sm font-semibold mb-4">Code Pipeline Metrics</h2>
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={chartData} barSize={32}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
            <XAxis dataKey="name" tick={{ fontSize: 11, fill: 'hsl(var(--muted-foreground))' }} />
            <YAxis tick={{ fontSize: 11, fill: 'hsl(var(--muted-foreground))' }} />
            <Tooltip
              contentStyle={{ background: 'hsl(var(--card))', border: '1px solid hsl(var(--border))', borderRadius: 8 }}
              labelStyle={{ color: 'hsl(var(--foreground))', fontWeight: 600 }}
            />
            <Bar dataKey="value" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Code Intelligence Mode */}
      {intel?.mode === 'code_intelligence' && (
        <div className="glass rounded-2xl p-6 space-y-4">
          <div className="flex items-center gap-2">
            <Code2 size={16} className="text-primary" />
            <h2 className="text-sm font-semibold">Code Intelligence Mode</h2>
            <span className="status-badge bg-amber-500/10 text-amber-400 border border-amber-500/20">
              No Documentation
            </span>
          </div>

          {intel.detected_components?.length ? (
            <div>
              <p className="text-xs text-muted-foreground mb-2">Detected Components ({intel.detected_components.length})</p>
              <div className="flex flex-wrap gap-1.5">
                {intel.detected_components.map((c) => (
                  <span key={c} className="status-badge bg-primary/10 text-primary border border-primary/20 font-mono text-[11px]">
                    {c}
                  </span>
                ))}
              </div>
            </div>
          ) : null}

          {intel.missing_documentation?.length ? (
            <div>
              <p className="text-xs text-muted-foreground mb-2">Missing Documentation</p>
              <ul className="space-y-1">
                {intel.missing_documentation.map((d) => (
                  <li key={d} className="text-sm text-amber-400 flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-amber-400 shrink-0" />
                    {d}
                  </li>
                ))}
              </ul>
            </div>
          ) : null}

          {intel.recommendations?.length ? (
            <div>
              <p className="text-xs text-muted-foreground mb-2">Recommendations</p>
              <ul className="space-y-2">
                {intel.recommendations.map((rec, i) => (
                  <li key={i} className="text-sm text-muted-foreground leading-snug">{rec}</li>
                ))}
              </ul>
            </div>
          ) : null}
        </div>
      )}
    </div>
  );
}
