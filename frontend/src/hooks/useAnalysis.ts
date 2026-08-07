import { useMutation } from '@tanstack/react-query';
import { analyzeRepository, checkHealth } from '@/api/repository';
import { useAnalysisStore } from '@/store';
import { toast } from 'sonner';

// ── useAnalysis — main analysis mutation ──────────────────────
export function useAnalysis() {
  const { setResult, setError, setAnalyzing, setRepositoryUrl } = useAnalysisStore();

  const mutation = useMutation({
    mutationFn: analyzeRepository,
    onMutate: ({ repository_url }) => {
      setAnalyzing(true);
      setRepositoryUrl(repository_url);
      toast.loading('Analyzing repository…', { id: 'analysis' });
    },
    onSuccess: (data) => {
      setResult(data);
      toast.success(
        `Analysis complete in ${data.processing_time_seconds.toFixed(2)}s`,
        { id: 'analysis', duration: 5000 }
      );
    },
    onError: (err: { message?: string }) => {
      const msg = err?.message ?? 'Analysis failed';
      setError(msg);
      toast.error(msg, { id: 'analysis', duration: 8000 });
    },
  });

  return {
    analyze: (url: string) => mutation.mutate({ repository_url: url }),
    isLoading: mutation.isPending,
    error: mutation.error as { message?: string } | null,
  };
}

// ── useHealth — periodic backend health check ─────────────────
export function useHealth() {
  const { setHealth } = useAnalysisStore();

  return useMutation({
    mutationFn: checkHealth,
    onSuccess: setHealth,
  });
}
