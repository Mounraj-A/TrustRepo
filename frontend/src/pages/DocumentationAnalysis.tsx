import { useAnalysisStore } from '@/store';
import EmptyState from '@/components/EmptyState';
import { BookOpen, FileText, AlertTriangle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import MetricsCard from '@/components/MetricsCard';

export default function DocumentationAnalysis() {
  const { analysisResult, isAnalyzing } = useAnalysisStore();
  if (!analysisResult && !isAnalyzing) return <EmptyState />;

  const report = analysisResult?.report;
  const markdown = analysisResult?.markdown ?? '';
  const verify = analysisResult?.verification_summary;
  const coverage = report?.documentation_coverage ?? 0;

  return (
    <div className="p-6 space-y-6 animate-in">
      <h1 className="text-2xl font-bold flex items-center gap-2">
        <BookOpen size={20} className="text-primary" />
        Documentation Analysis
      </h1>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricsCard label="Coverage"    value={`${Math.round(coverage * 100)}%`}      icon={BookOpen}    loading={isAnalyzing} />
        <MetricsCard label="Claims"      value={verify?.total_claims}                  icon={FileText}    color="violet" loading={isAnalyzing} />
        <MetricsCard label="Verified"    value={verify?.verified}                      icon={BookOpen}    color="emerald" loading={isAnalyzing} />
        <MetricsCard label="Missing"     value={verify?.insufficient}                  icon={AlertTriangle} color="amber" loading={isAnalyzing} />
      </div>

      {markdown ? (
        <div className="glass rounded-2xl p-6">
          <h2 className="text-sm font-semibold mb-4">Repository Trust Report (Markdown)</h2>
          <div className="prose prose-invert prose-sm max-w-none
                          prose-headings:text-foreground prose-headings:font-bold
                          prose-p:text-muted-foreground prose-li:text-muted-foreground
                          prose-code:text-primary prose-code:bg-muted/60
                          prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded
                          prose-pre:bg-muted/60 prose-pre:border prose-pre:border-border
                          prose-a:text-primary">
            <ReactMarkdown>{markdown}</ReactMarkdown>
          </div>
        </div>
      ) : (
        <div className="glass rounded-2xl p-6">
          <p className="text-muted-foreground text-sm">
            {report?.repository_name
              ? 'No markdown report generated for this repository.'
              : 'Run an analysis to see documentation insights.'}
          </p>
        </div>
      )}
    </div>
  );
}
