import { ReasoningTrace } from '@/types/api';
import ReasoningStepCard from './ReasoningStepCard';
import { GitCommit } from 'lucide-react';

interface ReasoningTimelineProps {
  trace: ReasoningTrace | null;
}

export default function ReasoningTimeline({ trace }: ReasoningTimelineProps) {
  if (!trace || !trace.steps || trace.steps.length === 0) {
    return (
      <div className="p-8 border border-dashed border-border rounded-xl bg-muted/20 text-center">
        <h3 className="text-sm font-bold uppercase tracking-wider text-muted-foreground mb-2">
          Reasoning Trace
        </h3>
        <p className="text-foreground font-medium mb-1">
          No reasoning trace was produced for this claim.
        </p>
        <p className="text-sm text-muted-foreground">
          The backend returned the claim and verdict, but no structured reasoning steps were available.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      
      {trace.explanation && (
        <div className="p-4 rounded-xl bg-muted/40 text-sm text-foreground leading-relaxed border border-border">
          {trace.explanation}
        </div>
      )}

      <div className="pt-2">
        <h3 className="text-xs font-bold uppercase tracking-wider text-muted-foreground mb-6 flex items-center gap-2">
          <GitCommit size={16} />
          Verification Path
        </h3>
        
        <div className="relative pl-6 space-y-8 border-l-2 border-primary/20 ml-2">
          {trace.steps.map((step, idx) => {
            const isLast = idx === trace.steps.length - 1;
            return (
              <div key={step.step_id} className="relative">
                {/* Timeline node */}
                <div className={`absolute -left-[31px] top-4 w-4 h-4 rounded-full border-4 border-background ${isLast ? 'bg-primary' : 'bg-primary/50'}`} />
                <ReasoningStepCard step={step} />
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
