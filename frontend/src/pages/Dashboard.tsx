import { motion } from 'framer-motion';
import {
  FileCode2, GitGraph, Cpu, ShieldCheck, Clock, AlertTriangle,
  CheckCircle2, XCircle, HelpCircle, ArrowRight, Activity, Layers, Zap,
  BookOpen
} from 'lucide-react';
import { useAnalysisStore } from '@/store';
import MetricsCard from '@/components/MetricsCard';
import TrustScoreGauge from '@/components/TrustScoreGauge';
import PipelineTimeline from '@/components/PipelineTimeline';
import EmptyState from '@/components/EmptyState';
import { cn, formatDuration, formatNumber } from '@/lib/utils';

export default function Dashboard() {
  const { analysisResult, isAnalyzing } = useAnalysisStore();

  if (!analysisResult && !isAnalyzing) return <EmptyState />;

  const r = analysisResult;
  const code = r?.code_metrics;
  const graph = r?.graph_metrics;
  const report = r?.report;
  const trace = r?.execution_trace ?? [];
  const summary = report?.summary;

  return (
    <div className="p-6 space-y-8 animate-in">
      {/* ── 1. Repository Header ──────────────────────────────────────── */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">
            {report?.metadata?.repository_url?.split(/[\/\\]/).pop() ?? 'Repository Analysis'}
          </h1>
          <p className="text-muted-foreground text-sm mt-1">
            {report?.metadata?.analysis_date
              ? new Date(report.metadata.analysis_date).toLocaleString()
              : 'Analysis Complete'}
            {r?.processing_time_seconds && (
              <span className="ml-2">· {formatDuration(r.processing_time_seconds)}</span>
            )}
          </p>
        </div>
        {/* Analyze button is in global header */}
      </div>

      {/* ── 3. Repository Metrics ─────────────────────────────────────── */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <MetricsCard label="Source Files" value={code?.source_files} icon={FileCode2} color="primary" loading={isAnalyzing} />
        <MetricsCard label="AST Nodes" value={code?.ast_nodes} icon={GitGraph} color="violet" loading={isAnalyzing} />
        <MetricsCard label="Symbols" value={code?.symbols} icon={Layers} color="primary" loading={isAnalyzing} />
        <MetricsCard label="Technologies" value={graph?.technologies?.length} icon={Cpu} color="emerald" loading={isAnalyzing} />
        <MetricsCard label="Graph Nodes" value={graph?.nodes} icon={Activity} color="amber" loading={isAnalyzing} />
        <MetricsCard label="Capabilities" value={graph?.capabilities?.length} icon={Zap} color="violet" loading={isAnalyzing} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* ── 2. Trust Assessment ─────────────────────────────────────── */}
        <div className="glass rounded-2xl p-6 flex flex-col items-center gap-6 text-center">
          {report?.trust_assessment?.score !== undefined && (
            <TrustScoreGauge score={report.trust_assessment.score} size="lg" showLabel={false} />
          )}
          {report?.trust_assessment && (
            <div className="space-y-2">
              <h3 className="font-semibold text-lg">{report.trust_assessment.status}</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">
                {report.trust_assessment.details}
              </p>
            </div>
          )}
        </div>

        {/* ── 4, 5, 6. Tech, Architecture, Features ───────────────────── */}
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
              <h2 className="text-sm font-semibold">Semantic Features</h2>
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

        {/* ── 7. Pipeline Execution ───────────────────────────────────── */}
        <div className="glass rounded-2xl p-6">
          <h2 className="text-sm font-semibold mb-4 flex items-center gap-2">
            <Activity size={14} className="text-primary" />
            Pipeline Execution
          </h2>
          <PipelineTimeline traces={trace.slice(0, 7)} />
        </div>
      </div>

      {/* ── 8. Overall Assessment ─────────────────────────────────────── */}
      {summary && (
        <div className="glass rounded-2xl p-6">
          <h2 className="text-sm font-semibold mb-4">Overall Assessment</h2>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-100 flex flex-col items-center justify-center text-center">
              <BookOpen size={20} className="text-indigo-500 mb-2" />
              <span className="text-2xl font-bold text-slate-900">{Math.round(summary.coverage_percentage ?? 0)}%</span>
              <span className="text-xs text-muted-foreground mt-1">Documentation Coverage</span>
            </div>
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-100 flex flex-col items-center justify-center text-center">
              <CheckCircle2 size={20} className="text-emerald-500 mb-2" />
              <span className="text-2xl font-bold text-slate-900">{summary.verified_claims ?? 0}</span>
              <span className="text-xs text-muted-foreground mt-1">Verified Claims</span>
            </div>
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-100 flex flex-col items-center justify-center text-center">
              <AlertTriangle size={20} className="text-amber-500 mb-2" />
              <span className="text-2xl font-bold text-slate-900">{summary.missing_documentation ?? 0}</span>
              <span className="text-xs text-muted-foreground mt-1">Missing Documentation</span>
            </div>
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-100 flex flex-col items-center justify-center text-center">
              <XCircle size={20} className="text-red-500 mb-2" />
              <span className="text-2xl font-bold text-slate-900">{summary.contradicted ?? 0}</span>
              <span className="text-xs text-muted-foreground mt-1">Contradictions</span>
            </div>
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-100 flex flex-col items-center justify-center text-center">
              <HelpCircle size={20} className="text-slate-400 mb-2" />
              <span className="text-2xl font-bold text-slate-900">{summary.insufficient_evidence ?? 0}</span>
              <span className="text-xs text-muted-foreground mt-1">Insufficient Evidence</span>
            </div>
          </div>
        </div>
      )}

      {/* ── 9. Recommendations ────────────────────────────────────────── */}
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
