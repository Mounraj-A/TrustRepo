import { useAnalysisStore } from '@/store';
import EmptyState from '@/components/EmptyState';
import PipelineTimeline from '@/components/PipelineTimeline';
import MetricsCard from '@/components/MetricsCard';
import { Activity, Clock, AlertTriangle, XCircle, Package, CheckCircle2 } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { cn, formatDuration, formatNumber, statusColor } from '@/lib/utils';
import { motion } from 'framer-motion';

export default function RuntimeDashboard() {
  const { analysisResult, isAnalyzing } = useAnalysisStore();
  if (!analysisResult && !isAnalyzing) return <EmptyState />;

  const trace = analysisResult?.execution_trace ?? [];

  const okCount = trace.filter(t => t.status === 'OK').length;
  const failedCount = trace.filter(t => t.status === 'FAILED').length;
  const skippedCount = trace.filter(t => t.status === 'SKIPPED').length;
  const totalTime = trace.reduce((a, t) => a + t.time_s, 0);
  const totalObjs = trace.reduce((a, t) => a + t.objects_created, 0);
  const allWarnings = trace.flatMap(t => t.warnings ?? []);
  const allErrors = trace.flatMap(t => t.errors ?? []);

  const chartData = trace.map(t => ({
    name: t.layer.replace(/^\d+[AB]?: /, ''),
    time_ms: parseFloat((t.time_s * 1000).toFixed(1)),
    objects: t.objects_created,
  }));

  return (
    <div className="p-6 space-y-6 animate-in">
      <h1 className="text-2xl font-bold flex items-center gap-2">
        <Activity size={20} className="text-primary" />
        Runtime Dashboard
      </h1>

      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        <MetricsCard label="Total Layers" value={trace.length} icon={Package} loading={isAnalyzing} />
        <MetricsCard label="Successful" value={okCount} icon={CheckCircle2} color="emerald" loading={isAnalyzing} />
        <MetricsCard label="Failed" value={failedCount} icon={XCircle} color="red" loading={isAnalyzing} />
        <MetricsCard label="Skipped" value={skippedCount} icon={Clock} loading={isAnalyzing} />
        <MetricsCard label="Total Time" value={formatDuration(totalTime)} icon={Clock} color="amber" loading={isAnalyzing} />
        <MetricsCard label="Objects" value={totalObjs} icon={Package} color="violet" loading={isAnalyzing} />
      </div>

      {/* Execution time chart */}
      <div className="glass rounded-2xl p-6">
        <h2 className="text-sm font-semibold mb-4">Execution Time per Layer (ms)</h2>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={chartData} barSize={28}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
            <XAxis dataKey="name" tick={{ fontSize: 10, fill: 'hsl(var(--muted-foreground))' }} />
            <YAxis tick={{ fontSize: 10, fill: 'hsl(var(--muted-foreground))' }} />
            <Tooltip
              contentStyle={{ background: 'hsl(var(--card))', border: '1px solid hsl(var(--border))', borderRadius: 8 }}
            />
            <Bar dataKey="time_ms" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} name="Time (ms)" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Full pipeline trace */}
      <div className="glass rounded-2xl p-6">
        <h2 className="text-sm font-semibold mb-4">Full Execution Trace</h2>
        <PipelineTimeline traces={trace} />
      </div>

      {/* Warnings */}
      {allWarnings.length > 0 && (
        <div className="glass rounded-2xl p-6 border border-amber-500/20">
          <h2 className="text-sm font-semibold text-amber-400 flex items-center gap-2 mb-3">
            <AlertTriangle size={14} />
            Pipeline Warnings ({allWarnings.length})
          </h2>
          <div className="space-y-1.5">
            {allWarnings.map((w, i) => (
              <p key={i} className="text-xs text-muted-foreground">{w}</p>
            ))}
          </div>
        </div>
      )}

      {/* Errors */}
      {allErrors.length > 0 && (
        <div className="glass rounded-2xl p-6 border border-red-500/20">
          <h2 className="text-sm font-semibold text-red-400 flex items-center gap-2 mb-3">
            <XCircle size={14} />
            Pipeline Errors ({allErrors.length})
          </h2>
          <div className="space-y-1.5">
            {allErrors.map((e, i) => (
              <p key={i} className="text-xs text-red-300/80">{e}</p>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
