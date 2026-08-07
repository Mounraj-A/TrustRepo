import { useAnalysisStore } from '@/store';
import EmptyState from '@/components/EmptyState';
import { Server, Cpu, HardDrive, Database, Activity } from 'lucide-react';

export default function SystemHealth() {
  const { analysisResult, isAnalyzing } = useAnalysisStore();
  
  if (!analysisResult && !isAnalyzing) return <EmptyState />;

  const trace = analysisResult?.execution_trace || [];

  return (
    <div className="p-6 space-y-6 animate-in">
      <h1 className="text-2xl font-bold flex items-center gap-2">
        <Server size={20} className="text-primary" />
        System Health & Telemetry
      </h1>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {/* Placeholders for real metrics */}
        <div className="glass p-4 rounded-xl">
          <p className="text-sm text-muted-foreground flex items-center gap-2"><Cpu size={14} /> Peak CPU Load</p>
          <p className="text-2xl font-bold mt-2">12%</p>
        </div>
        <div className="glass p-4 rounded-xl">
          <p className="text-sm text-muted-foreground flex items-center gap-2"><HardDrive size={14} /> Peak RAM</p>
          <p className="text-2xl font-bold mt-2">142 MB</p>
        </div>
        <div className="glass p-4 rounded-xl">
          <p className="text-sm text-muted-foreground flex items-center gap-2"><Database size={14} /> Objects Cached</p>
          <p className="text-2xl font-bold mt-2">1,204</p>
        </div>
        <div className="glass p-4 rounded-xl">
          <p className="text-sm text-muted-foreground flex items-center gap-2"><Activity size={14} /> Pipeline Status</p>
          <p className="text-2xl font-bold mt-2 text-emerald-400">Stable</p>
        </div>
      </div>
      <div className="glass p-6 rounded-2xl border border-border/50">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Activity size={16} /> Layer Telemetry
          </h2>
          <div className="space-y-2">
            {trace.map((t, idx) => (
                <div key={idx} className="flex justify-between items-center p-3 bg-muted/20 rounded-lg border border-border/30">
                    <span className="font-mono text-sm">{t.layer}</span>
                    <span className="font-mono text-xs text-muted-foreground">{t.time_s}s</span>
                </div>
            ))}
          </div>
      </div>
    </div>
  );
}
