import { useState } from 'react';
import { Search, Loader2, GitBranch } from 'lucide-react';
import { useAnalysis } from '@/hooks/useAnalysis';
import { useAnalysisStore } from '@/store';
import { cn } from '@/lib/utils';

export default function AnalyzeBar() {
  const { repositoryUrl, isAnalyzing } = useAnalysisStore();
  const { analyze } = useAnalysis();
  const [url, setUrl] = useState(repositoryUrl);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = url.trim();
    if (!trimmed || isAnalyzing) return;
    analyze(trimmed);
  };

  return (
    <form onSubmit={handleSubmit} className="flex items-center gap-2 w-full max-w-2xl">
      <div className="relative flex-1">
        <GitBranch
          size={14}
          className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground"
        />
        <input
          type="text"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://github.com/owner/repo  or  D:\path\to\repo"
          disabled={isAnalyzing}
          className={cn(
            'w-full pl-8 pr-3 py-2 text-sm rounded-lg border bg-background/60',
            'border-border focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary',
            'placeholder:text-muted-foreground/50 transition-all duration-200',
            'disabled:opacity-60 disabled:cursor-not-allowed'
          )}
        />
      </div>
      <button
        type="submit"
        disabled={isAnalyzing || !url.trim()}
        className={cn(
          'flex items-center gap-2 px-4 py-2 text-sm font-semibold rounded-lg transition-all duration-200',
          'gradient-trust text-white shadow-lg shadow-primary/20',
          'hover:opacity-90 active:scale-95',
          'disabled:opacity-50 disabled:cursor-not-allowed disabled:active:scale-100'
        )}
      >
        {isAnalyzing ? (
          <>
            <Loader2 size={14} className="animate-spin" />
            Analyzing…
          </>
        ) : (
          <>
            <Search size={14} />
            Analyze
          </>
        )}
      </button>
    </form>
  );
}
