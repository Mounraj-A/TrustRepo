import { motion } from 'framer-motion';
import {
  FileCode2, GitGraph, Cpu, ShieldCheck, Clock, AlertTriangle,
  CheckCircle2, XCircle, HelpCircle, ArrowRight, Activity, Layers, Zap
} from 'lucide-react';
import { useAnalysisStore } from '@/store';
import MetricsCard from '@/components/MetricsCard';
import TrustScoreGauge from '@/components/TrustScoreGauge';
import PipelineTimeline from '@/components/PipelineTimeline';
import EmptyState from '@/components/EmptyState';
import { cn, formatDuration, formatNumber } from '@/lib/utils';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

export default function Dashboard() {
  const { analysisResult, isAnalyzing } = useAnalysisStore();

  if (!analysisResult && !isAnalyzing) return <EmptyState />;

  const r = analysisResult;
  const code = r?.code_metrics;
  const graph = r?.graph_metrics;
  const verify = r?.verification_summary;
  const report = r?.report;
  const trace = r?.execution_trace ?? [];

  const verificationData = verify ? [
    { name: 'Verified', value: verify.verified, color: '#10b981' },
    { name: 'Partial', value: verify.partially_verified, color: '#f59e0b' },
    { name: 'Refuted', value: verify.refuted, color: '#ef4444' },
    { name: 'Insufficient', value: verify.insufficient, color: '#64748b' },
  ].filter(d => d.value > 0) : [];

  return (
    <div className="p-6 space-y-8 animate-in">
      {/* ── Header ─────────────────────────────────────────────── */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">
            {report?.repository_name ?? 'Repository Analysis'}
          </h1>
          <p className="text-muted-foreground text-sm mt-1">
            {report?.analysis_timestamp
              ? new Date(report.analysis_timestamp).toLocaleString()
              : 'Analysis Complete'}
            {r?.processing_time_seconds && (
              <span className="ml-2">· {formatDuration(r.processing_time_seconds)}</span>
            )}
          </p>
        </div>
        {report?.trust_score !== undefined && (
          <TrustScoreGauge score={report.trust_score} size="sm" showLabel={false} />
        )}
      </div>

      {/* ── Key Metrics ─────────────────────────────────────────── */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <MetricsCard label="Source Files" value={code?.source_files} icon={FileCode2} color="primary" loading={isAnalyzing} />
        <MetricsCard label="AST Nodes" value={code?.ast_nodes} icon={GitGraph} color="violet" loading={isAnalyzing} />
        <MetricsCard label="Symbols" value={code?.symbols} icon={Layers} color="primary" loading={isAnalyzing} />
        <MetricsCard label="Technologies" value={graph?.technologies?.length} icon={Cpu} color="emerald" loading={isAnalyzing} />
        <MetricsCard label="Graph Nodes" value={graph?.nodes} icon={Activity} color="amber" loading={isAnalyzing} />
        <MetricsCard label="Capabilities" value={graph?.capabilities?.length} icon={Zap} color="violet" loading={isAnalyzing} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* ── Trust Score + Verification ──────────────────────── */}
        <div className="glass rounded-2xl p-6 flex flex-col items-center gap-6">
          {report?.trust_score !== undefined && (
            <TrustScoreGauge score={report.trust_score} size="lg" />
          )}

          {/* Verification breakdown */}
          {verify && verify.total_claims > 0 && (
            <div className="w-full space-y-2">
              <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                Claim Verification ({verify.total_claims} claims)
              </p>
              {[
                { label: 'Verified', count: verify.verified, color: 'bg-emerald-500', Icon: CheckCircle2 },
                { label: 'Partial', count: verify.partially_verified, color: 'bg-amber-500', Icon: AlertTriangle },
                { label: 'Refuted', count: verify.refuted, color: 'bg-red-500', Icon: XCircle },
                { label: 'Insufficient', count: verify.insufficient, color: 'bg-slate-500', Icon: HelpCircle },
              ].map(({ label, count, color, Icon }) => count > 0 && (
                <div key={label} className="flex items-center gap-2 text-sm">
                  <Icon size={12} className={cn(
                    label === 'Verified' ? 'text-emerald-400' :
                      label === 'Partial' ? 'text-amber-400' :
                        label === 'Refuted' ? 'text-red-400' : 'text-slate-400'
                  )} />
                  <span className="text-muted-foreground flex-1">{label}</span>
                  <span className="font-mono font-semibold">{count}</span>
                  <div className="w-16 h-1.5 bg-border rounded-full overflow-hidden">
                    <div
                      className={cn('h-full rounded-full', color)}
                      style={{ width: `${(count / verify.total_claims) * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* ── Technologies + Architecture ─────────────────────── */}
        <div className="glass rounded-2xl p-6 space-y-4">
          <h2 className="text-sm font-semibold">Technology Stack</h2>
          {graph?.technologies?.length ? (
            <div className="flex flex-wrap gap-1.5">
              {graph.technologies.map((tech) => (
                <span key={tech} className="status-badge bg-primary/10 text-primary border border-primary/20">
                  {tech}
                </span>
              ))}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">No technologies detected</p>
          )}

          {graph?.architectures?.length ? (
            <>
              <hr className="border-border" />
              <h2 className="text-sm font-semibold">Architecture</h2>
              <div className="flex flex-wrap gap-1.5">
                {graph.architectures.map((a) => (
                  <span key={a} className="status-badge bg-violet-500/10 text-violet-400 border border-violet-500/20">
                    {a}
                  </span>
                ))}
              </div>
            </>
          ) : null}

          {graph?.features?.length ? (
            <>
              <hr className="border-border" />
              <h2 className="text-sm font-semibold">Features</h2>
              <div className="flex flex-wrap gap-1.5">
                {graph.features.map((f) => (
                  <span key={f} className="status-badge bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                    {f}
                  </span>
                ))}
              </div>
            </>
          ) : null}
        </div>

        {/* ── Pipeline Summary ────────────────────────────────── */}
        <div className="glass rounded-2xl p-6">
          <h2 className="text-sm font-semibold mb-4 flex items-center gap-2">
            <Activity size={14} className="text-primary" />
            Pipeline Execution
          </h2>
          <PipelineTimeline traces={trace.slice(0, 7)} />
        </div>
      </div>

      {/* ── Assessment ──────────────────────────────────────────── */}
      {report?.overall_assessment && (
        <div className="glass rounded-2xl p-6">
          <h2 className="text-sm font-semibold mb-3">Overall Assessment</h2>
          <p className="text-sm text-muted-foreground leading-relaxed">{report.overall_assessment}</p>
        </div>
      )}

      {/* ── Recommendations ─────────────────────────────────────── */}
      {report?.recommendations?.length ? (
        <div className="glass rounded-2xl p-6">
          <h2 className="text-sm font-semibold mb-3">Recommendations</h2>
          <ul className="space-y-2">
            {report.recommendations.map((rec, i) => {
              const text = typeof rec === 'string' ? rec : ((rec as any).message || JSON.stringify(rec));
              return (
                <li key={i} className="flex items-start gap-2 text-sm text-muted-foreground">
                  <ArrowRight size={12} className="mt-1 text-primary shrink-0" />
                  <span>{String(text)}</span>
                </li>
              );
            })}
          </ul>
        </div>
      ) : null}
    </div>
  );
}
