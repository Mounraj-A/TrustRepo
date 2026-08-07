import { useAnalysisStore } from '@/store';
import EmptyState from '@/components/EmptyState';
import MetricsCard from '@/components/MetricsCard';
import { Cpu, Package, TrendingUp, AlertTriangle } from 'lucide-react';
import { motion } from 'framer-motion';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts';

const TECH_COLORS = [
  '#6366f1', '#8b5cf6', '#ec4899', '#14b8a6', '#f59e0b',
  '#22c55e', '#3b82f6', '#ef4444', '#f97316', '#06b6d4',
];

export default function Technologies() {
  const { analysisResult, isAnalyzing } = useAnalysisStore();
  if (!analysisResult && !isAnalyzing) return <EmptyState />;

  const graph = analysisResult?.graph_metrics;
  const techs = graph?.technologies ?? [];
  const categories = graph?.technology_categories ?? {};
  const schema = graph?.schema_validation;

  const pieData = techs.map((t, i) => ({ name: t, value: 1, color: TECH_COLORS[i % TECH_COLORS.length] }));

  return (
    <div className="p-6 space-y-6 animate-in">
      <h1 className="text-2xl font-bold">Technologies</h1>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricsCard label="Technologies Detected" value={techs.length} icon={Cpu} color="primary" loading={isAnalyzing} />
        <MetricsCard label="Categories" value={Object.keys(categories).length} icon={Package} color="violet" loading={isAnalyzing} />
        <MetricsCard label="Graph Nodes" value={graph?.nodes} icon={TrendingUp} color="emerald" loading={isAnalyzing} />
        <MetricsCard label="Graph Integrity"
          value={schema?.integrity_score !== undefined ? `${Math.round(schema.integrity_score * 100)}%` : '—'}
          icon={AlertTriangle} color="amber" loading={isAnalyzing}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Technology badges */}
        <div className="glass rounded-2xl p-6">
          <h2 className="text-sm font-semibold mb-4">Detected Technologies ({techs.length})</h2>
          {techs.length ? (
            <div className="flex flex-wrap gap-2">
              {techs.map((tech, i) => (
                <motion.span
                  key={tech}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: i * 0.04 }}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium
                             border transition-all hover:scale-105"
                  style={{
                    borderColor: `${TECH_COLORS[i % TECH_COLORS.length]}40`,
                    background: `${TECH_COLORS[i % TECH_COLORS.length]}15`,
                    color: TECH_COLORS[i % TECH_COLORS.length],
                  }}
                >
                  <span className="w-2 h-2 rounded-full" style={{ background: TECH_COLORS[i % TECH_COLORS.length] }} />
                  {tech}
                </motion.span>
              ))}
            </div>
          ) : (
            <p className="text-muted-foreground text-sm">No technologies detected.</p>
          )}
        </div>

        {/* Pie chart */}
        {pieData.length > 0 && (
          <div className="glass rounded-2xl p-6">
            <h2 className="text-sm font-semibold mb-4">Technology Distribution</h2>
            <ResponsiveContainer width="100%" height={260}>
              <PieChart>
                <Pie data={pieData} cx="50%" cy="50%" innerRadius={60} outerRadius={100}
                  paddingAngle={3} dataKey="value">
                  {pieData.map((d, i) => (
                    <Cell key={d.name} fill={d.color} stroke="transparent" />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ background: 'hsl(var(--card))', border: '1px solid hsl(var(--border))', borderRadius: 8 }}
                />
                <Legend formatter={(v) => <span style={{ fontSize: 11 }}>{v}</span>} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {/* By category */}
      {Object.keys(categories).length > 0 && (
        <div className="glass rounded-2xl p-6">
          <h2 className="text-sm font-semibold mb-4">By Category</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
            {Object.entries(categories).map(([cat, items]) => (
              <div key={cat} className="bg-muted/40 rounded-xl p-4">
                <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">{cat}</p>
                <div className="flex flex-wrap gap-1.5">
                  {(items as string[]).map((t) => (
                    <span key={t} className="status-badge bg-background text-foreground border border-border text-[11px]">{t}</span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Schema validation warnings */}
      {schema?.warnings?.length ? (
        <div className="glass rounded-2xl p-6 border border-amber-500/20">
          <h2 className="text-sm font-semibold text-amber-400 mb-3 flex items-center gap-2">
            <AlertTriangle size={14} />
            Graph Schema Warnings
          </h2>
          <ul className="space-y-1.5">
            {schema.warnings.map((w, i) => (
              <li key={i} className="text-xs text-muted-foreground">{w}</li>
            ))}
          </ul>
        </div>
      ) : null}
    </div>
  );
}
