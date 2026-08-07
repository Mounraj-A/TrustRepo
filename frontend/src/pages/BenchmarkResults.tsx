import EmptyState from '@/components/EmptyState';
import { BarChart3, AlertCircle } from 'lucide-react';

export default function BenchmarkResults() {
  return (
    <div className="p-6 space-y-6 animate-in">
      <h1 className="text-2xl font-bold flex items-center gap-2">
        <BarChart3 size={20} className="text-primary" />
        Benchmark Results
      </h1>
      
      <div className="glass p-8 rounded-2xl border border-amber-500/20 bg-amber-500/5 text-center flex flex-col items-center justify-center">
        <AlertCircle size={48} className="text-amber-400 mb-4" />
        <h2 className="text-xl font-bold mb-2">Benchmark Suite Pending</h2>
        <p className="text-muted-foreground max-w-lg">
          The Benchmark Engine (`benchmark_engine.py`) has not yet been executed on the full dataset (React, Angular, Spring Boot, etc.).
          Once completed, Precision, Recall, F1, Accuracy, and Confusion Matrices will appear here.
        </p>
      </div>
    </div>
  );
}
