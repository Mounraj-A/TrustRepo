import { DocumentationClaim } from '@/types/api';
import { CheckCircle2, AlertTriangle, XCircle, HelpCircle } from 'lucide-react';

interface ReasoningClaimCardProps {
  claim: DocumentationClaim;
  isSelected: boolean;
  onClick: () => void;
}

export default function ReasoningClaimCard({ claim, isSelected, onClick }: ReasoningClaimCardProps) {
  
  const v = claim.verdict.toUpperCase();
  let VerdictIcon = HelpCircle;
  let verdictColor = 'text-slate-500';
  let verdictBg = 'bg-slate-50';
  let verdictBorder = 'border-slate-200';
  let verdictText = 'UNKNOWN';

  if (v === 'VERIFIED') {
    VerdictIcon = CheckCircle2;
    verdictColor = 'text-emerald-600';
    verdictBg = 'bg-emerald-50';
    verdictBorder = 'border-emerald-200';
    verdictText = 'VERIFIED';
  } else if (v === 'PARTIALLY_VERIFIED' || v === 'UNSUPPORTED') {
    VerdictIcon = AlertTriangle;
    verdictColor = 'text-amber-600';
    verdictBg = 'bg-amber-50';
    verdictBorder = 'border-amber-200';
    verdictText = 'PARTIAL';
  } else if (v === 'CONTRADICTED') {
    VerdictIcon = XCircle;
    verdictColor = 'text-rose-600';
    verdictBg = 'bg-rose-50';
    verdictBorder = 'border-rose-200';
    verdictText = 'CONTRADICTED';
  } else if (v === 'MISSING_DOCUMENTATION') {
    VerdictIcon = AlertTriangle;
    verdictColor = 'text-orange-600';
    verdictBg = 'bg-orange-50';
    verdictBorder = 'border-orange-200';
    verdictText = 'MISSING DOCS';
  } else if (v === 'INSUFFICIENT_EVIDENCE') {
    VerdictIcon = HelpCircle;
    verdictColor = 'text-indigo-600';
    verdictBg = 'bg-indigo-50';
    verdictBorder = 'border-indigo-200';
    verdictText = 'INSUFFICIENT';
  }

  const stepCount = claim.reasoning_trace?.steps?.length;

  return (
    <div 
      onClick={onClick}
      className={`p-4 rounded-xl cursor-pointer border transition-all duration-200 
        ${isSelected ? `border-primary shadow-md bg-background scale-[1.02]` : 'border-border bg-card hover:bg-muted/50 hover:border-primary/30'}
      `}
    >
      <div className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider border ${verdictBg} ${verdictBorder} ${verdictColor} mb-3`}>
        <VerdictIcon size={12} />
        {verdictText}
      </div>
      
      <p className="text-sm text-foreground font-medium line-clamp-3 leading-snug">
        {claim.claim_text}
      </p>
      
      {stepCount !== undefined && stepCount > 0 && (
        <div className="mt-3 text-xs text-muted-foreground font-semibold">
          {stepCount} reasoning steps
        </div>
      )}
    </div>
  );
}
