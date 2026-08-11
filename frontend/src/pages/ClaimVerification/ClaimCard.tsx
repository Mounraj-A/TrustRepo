import { DocumentationClaim } from '@/types/api';
import { CheckCircle2, AlertTriangle, XCircle, HelpCircle, ArrowRight } from 'lucide-react';

interface ClaimCardProps {
  claim: DocumentationClaim;
  onClick: () => void;
}

export default function ClaimCard({ claim, onClick }: ClaimCardProps) {
  const isVerified = claim.verdict === 'VERIFIED';
  const isContradicted = claim.verdict === 'CONTRADICTED';
  const isUnsupported = claim.verdict === 'UNSUPPORTED'; // Using unsupported for partial
  const isInsufficient = claim.verdict === 'INSUFFICIENT_EVIDENCE';

  let StatusIcon = HelpCircle;
  let statusColor = 'text-slate-500';
  let statusBg = 'bg-slate-50';
  let borderColor = 'border-slate-200 dark:border-slate-800';
  let humanStatus = 'UNKNOWN';

  if (isVerified) {
    StatusIcon = CheckCircle2;
    statusColor = 'text-emerald-600';
    statusBg = 'bg-emerald-50';
    borderColor = 'border-emerald-200 dark:border-emerald-900/50';
    humanStatus = 'VERIFIED';
  } else if (isContradicted) {
    StatusIcon = XCircle;
    statusColor = 'text-rose-600';
    statusBg = 'bg-rose-50';
    borderColor = 'border-rose-200 dark:border-rose-900/50';
    humanStatus = 'REFUTED';
  } else if (isUnsupported) {
    StatusIcon = AlertTriangle;
    statusColor = 'text-amber-600';
    statusBg = 'bg-amber-50';
    borderColor = 'border-amber-200 dark:border-amber-900/50';
    humanStatus = 'PARTIAL';
  } else if (isInsufficient) {
    StatusIcon = HelpCircle;
    statusColor = 'text-indigo-600';
    statusBg = 'bg-indigo-50';
    borderColor = 'border-indigo-200 dark:border-indigo-900/50';
    humanStatus = 'INSUFFICIENT';
  }

  // The backend types allow undefined for these fields, so check existence
  const hasEvidenceCount = typeof claim.evidence_count === 'number';
  const hasConfidence = typeof claim.confidence === 'number';

  return (
    <div 
      className={`glass rounded-xl overflow-hidden mb-4 border ${borderColor} hover:shadow-md transition-all cursor-pointer group flex flex-col md:flex-row`}
      onClick={onClick}
    >
      {/* Left side: Status Color block (optional, or just use top banner) */}
      
      <div className="flex-1 p-5 md:p-6 flex flex-col justify-between">
        <div className="space-y-3">
          <div className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md ${statusBg} ${statusColor} font-bold text-[10px] uppercase tracking-wider border border-current/10`}>
            <StatusIcon size={14} />
            {humanStatus}
          </div>
          
          <h3 className="font-medium text-foreground text-base leading-snug">{claim.claim_text}</h3>
        </div>

        <div className="flex flex-wrap items-center gap-4 mt-4 text-sm">
          {hasEvidenceCount && (
            <div className="text-muted-foreground flex items-center gap-1.5">
              <span className="font-semibold text-foreground">Evidence</span>
              <span>·</span>
              <span>{claim.evidence_count} {claim.evidence_count === 1 ? 'source' : 'sources'}</span>
            </div>
          )}
          {hasConfidence && (
            <div className={`px-2.5 py-1 rounded-md text-[10px] font-bold ${statusBg} ${statusColor} shrink-0 border border-current/10`}>
              Confidence: {Math.round((claim.confidence ?? claim.trust_score ?? 0) * 100)}%
            </div>
          )}
        </div>
      </div>

      <div className={`p-4 md:p-6 md:w-48 border-t md:border-t-0 md:border-l ${borderColor} bg-muted/10 flex flex-col items-end justify-end md:justify-center`}>
         <button className={`flex items-center gap-1.5 text-sm font-semibold transition-colors ${statusColor} group-hover:opacity-80`}>
          View Evidence <ArrowRight size={16} className="transition-transform group-hover:translate-x-1" />
        </button>
      </div>
    </div>
  );
}
