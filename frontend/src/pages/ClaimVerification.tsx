import { useAnalysisStore } from '@/store';
import EmptyState from '@/components/EmptyState';
import VerificationTable from '@/components/VerificationTable';
import MetricsCard from '@/components/MetricsCard';
import { ClipboardCheck, CheckCircle2, XCircle, AlertTriangle, HelpCircle } from 'lucide-react';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts';

export default function ClaimVerification() {
  const { analysisResult, isAnalyzing } = useAnalysisStore();
  if (!analysisResult && !isAnalyzing) return <EmptyState />;

  const verify = analysisResult?.verification_summary;
  const claims = analysisResult?.report?.claims ?? [];

  const pieData = verify ? [
    { name: 'Verified',     value: verify.verified,            color: '#10b981' },
    { name: 'Partial',      value: verify.partially_verified,  color: '#f59e0b' },
    { name: 'Refuted',      value: verify.refuted,             color: '#ef4444' },
    { name: 'Insufficient', value: verify.insufficient,        color: '#64748b' },
  ].filter(d => d.value > 0) : [];

  return (
    <div className="p-6 space-y-6 animate-in">
      <h1 className="text-2xl font-bold flex items-center gap-2">
        <ClipboardCheck size={20} className="text-primary" />
        Claim Verification
      </h1>

      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4">
        <MetricsCard label="Total Claims"  value={verify?.total_claims}       icon={ClipboardCheck} loading={isAnalyzing} />
        <MetricsCard label="Verified"      value={verify?.verified}           icon={CheckCircle2}   color="emerald" loading={isAnalyzing} />
        <MetricsCard label="Partial"       value={verify?.partially_verified} icon={AlertTriangle}  color="amber"   loading={isAnalyzing} />
        <MetricsCard label="Refuted"       value={verify?.refuted}            icon={XCircle}        color="red"     loading={isAnalyzing} />
        <MetricsCard label="Insufficient"  value={verify?.insufficient}       icon={HelpCircle}     loading={isAnalyzing} />
      </div>

      {pieData.length > 0 && (
        <div className="glass rounded-2xl p-6">
          <h2 className="text-sm font-semibold mb-4">Verdict Distribution</h2>
          <div className="flex items-center gap-8">
            <ResponsiveContainer width={200} height={200}>
              <PieChart>
                <Pie data={pieData} cx="50%" cy="50%" innerRadius={55} outerRadius={90}
                     paddingAngle={3} dataKey="value">
                  {pieData.map((d) => <Cell key={d.name} fill={d.color} stroke="transparent" />)}
                </Pie>
                <Tooltip contentStyle={{ background: 'hsl(var(--card))', border: '1px solid hsl(var(--border))', borderRadius: 8 }} />
              </PieChart>
            </ResponsiveContainer>
            <div className="space-y-2">
              {pieData.map((d) => (
                <div key={d.name} className="flex items-center gap-2 text-sm">
                  <span className="w-3 h-3 rounded-sm shrink-0" style={{ background: d.color }} />
                  <span className="text-muted-foreground">{d.name}</span>
                  <span className="font-mono font-bold ml-auto">{d.value}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      <div className="glass rounded-2xl p-6">
        <h2 className="text-sm font-semibold mb-4">Claims ({claims.length})</h2>
        {claims.length > 0
          ? <VerificationTable claims={claims} />
          : <p className="text-sm text-muted-foreground">
              {verify?.total_claims
                ? `${verify.total_claims} claims were processed. Enable detailed claim export in Settings.`
                : 'No claims extracted from documentation.'}
            </p>
        }
      </div>
    </div>
  );
}
