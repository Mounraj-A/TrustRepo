import { useState } from 'react';
import { useAnalysisStore } from '@/store';
import EmptyState from '@/components/EmptyState';
import { Terminal, Copy, Check, Download } from 'lucide-react';
import { cn } from '@/lib/utils';
import { toast } from 'sonner';

export default function ApiInspector() {
  const { analysisResult } = useAnalysisStore();
  const [copied, setCopied] = useState(false);
  const [tab, setTab] = useState<'response' | 'graph' | 'trace'>('response');

  if (!analysisResult) return <EmptyState />;

  const tabs = [
    { id: 'response' as const, label: 'Full Response' },
    { id: 'graph'    as const, label: 'Graph Metrics' },
    { id: 'trace'    as const, label: 'Execution Trace' },
  ];

  const dataMap = {
    response: analysisResult,
    graph:    analysisResult.graph_metrics,
    trace:    analysisResult.execution_trace,
  };

  const jsonStr = JSON.stringify(dataMap[tab], null, 2);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(jsonStr);
    setCopied(true);
    toast.success('Copied to clipboard');
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const blob = new Blob([jsonStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `trustrepo-${tab}-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
    toast.success('Downloaded');
  };

  return (
    <div className="p-6 space-y-4 animate-in h-full flex flex-col">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Terminal size={20} className="text-primary" />
          API Inspector
        </h1>
        <div className="flex items-center gap-2">
          <button onClick={handleCopy}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg
                       bg-muted hover:bg-accent transition-colors border border-border">
            {copied ? <Check size={12} className="text-emerald-400" /> : <Copy size={12} />}
            Copy
          </button>
          <button onClick={handleDownload}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg
                       gradient-trust text-white transition-opacity hover:opacity-90">
            <Download size={12} />
            Download JSON
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-muted/40 rounded-lg p-1 w-fit">
        {tabs.map((t) => (
          <button key={t.id} onClick={() => setTab(t.id)}
            className={cn('px-3 py-1.5 text-xs font-medium rounded-md transition-all',
              tab === t.id ? 'bg-background text-foreground shadow-sm' : 'text-muted-foreground hover:text-foreground'
            )}>
            {t.label}
          </button>
        ))}
      </div>

      {/* JSON viewer */}
      <div className="glass rounded-2xl flex-1 overflow-hidden">
        <div className="flex items-center gap-2 px-4 py-2 border-b border-border bg-muted/20">
          <span className="text-xs font-mono text-muted-foreground">application/json</span>
          <span className="text-xs text-muted-foreground ml-auto">{jsonStr.length.toLocaleString()} bytes</span>
        </div>
        <pre className="overflow-auto p-4 text-xs font-mono leading-relaxed text-muted-foreground
                        max-h-[calc(100vh-320px)] scrollbar-thin">
          <code>{jsonStr}</code>
        </pre>
      </div>
    </div>
  );
}
