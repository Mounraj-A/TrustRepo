import { useAnalysisStore } from '@/store';
import EmptyState from '@/components/EmptyState';
import TrustScoreGauge from '@/components/TrustScoreGauge';
import MetricsCard from '@/components/MetricsCard';
import { ShieldCheck, BookOpen, Cpu, Layers, Zap, Building2, Link2, BarChart3 } from 'lucide-react';
import { RadarChart, Radar, PolarGrid, PolarAngleAxis, ResponsiveContainer, Tooltip } from 'recharts';

export default function TrustScore() {
  const { analysisResult, isAnalyzing } = useAnalysisStore();
  if (!analysisResult && !isAnalyzing) return <EmptyState />;

  const report = analysisResult?.report;
  const graph = analysisResult?.graph_metrics;
  const verify = analysisResult?.verification_summary;

  const docScore    = report?.documentation_coverage ?? 0;
  const techCount   = graph?.technologies?.length ?? 0;
  const featCount   = graph?.features?.length ?? 0;
  const capCount    = graph?.capabilities?.length ?? 0;
  const total       = verify?.total_claims ?? 0;
  const verifyScore = total > 0 ? (verify?.verified ?? 0) / total : 0;
  const overall     = report?.trust_score ?? 0;

  const radarData = [
    { subject: 'Documentation', value: Math.round(docScore * 100) },
    { subject: 'Verification',  value: Math.round(verifyScore * 100) },
    { subject: 'Technologies',  value: Math.min(techCount * 10, 100) },
    { subject: 'Features',      value: Math.min(featCount * 20, 100) },
    { subject: 'Capabilities',  value: Math.min(capCount * 25, 100) },
  ];

  return (
    <div className="p-6 space-y-6 animate-in">
      <h1 className="text-2xl font-bold flex items-center gap-2">
        <ShieldCheck size={20} className="text-primary" />
        Trust Score
      </h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main gauge */}
        <div className="glass rounded-2xl p-8 flex flex-col items-center gap-4 col-span-1">
          <TrustScoreGauge score={overall} size="lg" />
          {report?.overall_assessment && (
            <p className="text-xs text-muted-foreground text-center leading-relaxed max-w-xs">
              {report.overall_assessment}
            </p>
          )}
        </div>

        {/* Radar chart */}
        <div className="glass rounded-2xl p-6 col-span-1 lg:col-span-2">
          <h2 className="text-sm font-semibold mb-4">Trust Dimensions</h2>
          <ResponsiveContainer width="100%" height={280}>
            <RadarChart data={radarData}>
              <PolarGrid stroke="hsl(var(--border))" />
              <PolarAngleAxis dataKey="subject" tick={{ fontSize: 11, fill: 'hsl(var(--muted-foreground))' }} />
              <Radar name="Score" dataKey="value" stroke="hsl(var(--primary))"
                     fill="hsl(var(--primary))" fillOpacity={0.2} />
              <Tooltip contentStyle={{ background: 'hsl(var(--card))', border: '1px solid hsl(var(--border))', borderRadius: 8 }} />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Component scores */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
        <MetricsCard label="Documentation Coverage" value={`${Math.round(docScore * 100)}%`} icon={BookOpen} color="primary" loading={isAnalyzing} />
        <MetricsCard label="Tech Detected"           value={techCount}                        icon={Cpu}      color="violet"  loading={isAnalyzing} />
        <MetricsCard label="Features Extracted"      value={featCount}                        icon={Layers}   color="emerald" loading={isAnalyzing} />
        <MetricsCard label="Capabilities"            value={capCount}                         icon={Zap}      color="amber"   loading={isAnalyzing} />
        <MetricsCard label="Verification Rate"        value={`${Math.round(verifyScore * 100)}%`} icon={ShieldCheck} color="emerald" loading={isAnalyzing} />
      </div>

      {/* Risk factors & strengths */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {report?.strengths?.length ? (
          <div className="glass rounded-2xl p-6">
            <h2 className="text-sm font-semibold text-emerald-400 mb-3">Strengths</h2>
            <ul className="space-y-2">
              {report.strengths.map((s, i) => (
                <li key={i} className="text-sm text-muted-foreground flex items-start gap-2">
                  <ShieldCheck size={12} className="text-emerald-400 mt-0.5 shrink-0" />
                  {typeof s === 'string' ? s : (s as any).message ?? JSON.stringify(s)}
                </li>
              ))}
            </ul>
          </div>
        ) : null}

        {report?.risk_factors?.length ? (
          <div className="glass rounded-2xl p-6">
            <h2 className="text-sm font-semibold text-red-400 mb-3">Risk Factors</h2>
            <ul className="space-y-2">
              {report.risk_factors.map((r, i) => (
                <li key={i} className="text-sm text-muted-foreground flex items-start gap-2">
                  <span className="w-2 h-2 rounded-full bg-red-400 mt-1.5 shrink-0" />
                  {typeof r === 'string' ? r : (r as any).message ?? JSON.stringify(r)}
                </li>
              ))}
            </ul>
          </div>
        ) : null}
      </div>
    </div>
  );
}
