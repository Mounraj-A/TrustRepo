import { ReasoningStep } from '@/types/api';
import { ArrowRight, FileText, FileCode2, Scale, CheckCircle2, XCircle, AlertTriangle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface ReasoningStepCardProps {
  step: ReasoningStep;
}

export default function ReasoningStepCard({ step }: ReasoningStepCardProps) {
  const navigate = useNavigate();

  const type = step.step_type.toUpperCase();
  let StepIcon = FileText;
  let color = 'text-slate-600';
  let border = 'border-slate-200';
  let bg = 'bg-slate-50';

  if (type.includes('DOCUMENTATION')) {
    StepIcon = FileText;
    color = 'text-purple-600';
    border = 'border-purple-200';
    bg = 'bg-purple-50';
  } else if (type.includes('REPOSITORY') || type.includes('CODE')) {
    StepIcon = FileCode2;
    color = 'text-blue-600';
    border = 'border-blue-200';
    bg = 'bg-blue-50';
  } else if (type.includes('COMPARISON')) {
    StepIcon = Scale;
    color = 'text-orange-600';
    border = 'border-orange-200';
    bg = 'bg-orange-50';
  } else if (type.includes('VERDICT') || type.includes('VERIFICATION')) {
    StepIcon = CheckCircle2;
    color = 'text-emerald-600';
    border = 'border-emerald-200';
    bg = 'bg-emerald-50';
  } else if (type.includes('CONTRADICTION')) {
    StepIcon = XCircle;
    color = 'text-rose-600';
    border = 'border-rose-200';
    bg = 'bg-rose-50';
  }

  const handleViewEvidence = (evId: string) => {
    // Navigate to Evidence Explorer with the evidence id as a query parameter
    navigate(`/dashboard/evidence?id=${evId}`);
  };

  return (
    <div className={`rounded-xl border ${border} overflow-hidden bg-card shadow-sm`}>
      <div className={`px-4 py-3 flex items-center gap-2 border-b ${border} ${bg}`}>
        <StepIcon size={16} className={color} />
        <span className={`text-xs font-bold uppercase tracking-wider ${color}`}>
          {step.step_type.replace('_', ' ')}
        </span>
      </div>
      
      <div className="p-4 space-y-3">
        <h4 className="font-semibold text-sm text-foreground">
          {step.title}
        </h4>
        
        {step.description && (
          <p className="text-sm text-muted-foreground leading-relaxed">
            {step.description}
          </p>
        )}

        {(step.source || step.source_file) && (
          <div className="bg-muted/30 rounded-md p-3 border border-border mt-2">
            <div className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground mb-1">Source</div>
            <div className="font-mono text-xs text-foreground break-all">
              {step.source_file || step.source}
            </div>
            {step.line_start && (
              <div className="font-mono text-[10px] text-muted-foreground mt-1">
                Lines {step.line_start}{step.line_end ? `–${step.line_end}` : ''}
              </div>
            )}
          </div>
        )}
        
        {step.result && (
          <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-muted text-xs font-semibold text-foreground border border-border">
            Result: {step.result}
          </div>
        )}

        {step.evidence_ids && step.evidence_ids.length > 0 && (
          <div className="mt-4 pt-4 border-t border-border space-y-2">
            {step.evidence_ids.map(evId => (
              <div key={evId} className="flex items-center justify-between">
                <div className="text-xs font-mono text-muted-foreground">
                  Evidence ID: {evId}
                </div>
                <button 
                  onClick={() => handleViewEvidence(evId)}
                  className="flex items-center gap-1 text-xs font-bold text-primary hover:text-primary/80 transition-colors"
                >
                  View Evidence <ArrowRight size={12} />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
