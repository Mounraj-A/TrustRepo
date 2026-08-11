import { DocumentationClaim, FeatureFinding } from '@/types/api';
import { CheckCircle2, AlertTriangle, XCircle, HelpCircle, ArrowRight } from 'lucide-react';

interface EvidenceCardProps {
  type: 'claim' | 'feature';
  data: DocumentationClaim | FeatureFinding;
  onClick: () => void;
}

export default function EvidenceCard({ type, data, onClick }: EvidenceCardProps) {
  const title = type === 'claim' ? (data as DocumentationClaim).claim_text : (data as FeatureFinding).feature;
  const status = type === 'claim' ? (data as DocumentationClaim).verdict : (data as FeatureFinding).status;
  const chain = data.provenance_chain || (type === 'feature' ? (data as FeatureFinding).evidence?.[0] : null);
  const evidenceCount = chain?.sequence?.length || (type === 'claim' ? (data as DocumentationClaim).evidence_count : (data as FeatureFinding).evidence_count) || 0;
  
  const claimText = type === 'claim' ? (data as DocumentationClaim).claim_text : null;
  const isMissingDocs = status === 'MISSING_DOCUMENTATION';
  const isContradicted = status === 'CONTRADICTED';
  const isVerified = status === 'VERIFIED';

  let StatusIcon = HelpCircle;
  let statusColor = 'text-slate-500';
  let statusBg = 'bg-slate-100';
  let borderColor = 'border-slate-200 dark:border-slate-800';
  let humanStatus: string = status;

  if (isVerified) {
    StatusIcon = CheckCircle2;
    statusColor = 'text-emerald-600';
    statusBg = 'bg-emerald-50';
    borderColor = 'border-emerald-200 dark:border-emerald-900/50';
    humanStatus = 'VERIFIED';
  } else if (isMissingDocs) {
    StatusIcon = AlertTriangle;
    statusColor = 'text-amber-600';
    statusBg = 'bg-amber-50';
    borderColor = 'border-amber-200 dark:border-amber-900/50';
    humanStatus = 'MISSING DOCUMENTATION';
  } else if (isContradicted) {
    StatusIcon = XCircle;
    statusColor = 'text-rose-600';
    statusBg = 'bg-rose-50';
    borderColor = 'border-rose-200 dark:border-rose-900/50';
    humanStatus = 'CONTRADICTED';
  }

  return (
    <div 
      className={`glass rounded-xl overflow-hidden mb-4 border ${borderColor} hover:shadow-md transition-all cursor-pointer group flex flex-col`}
      onClick={onClick}
    >
      {/* Top Banner Status */}
      <div className={`px-4 py-2 flex items-center gap-2 border-b ${borderColor} ${statusBg}`}>
        <StatusIcon size={16} className={statusColor} />
        <span className={`text-xs font-bold tracking-wider ${statusColor}`}>{humanStatus}</span>
      </div>

      <div className="p-5 flex flex-col md:flex-row gap-6 justify-between items-start md:items-center">
        
        {/* Main Content */}
        <div className="space-y-4 flex-1">
          <h3 className="font-semibold text-lg text-foreground">{title}</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Documentation Side */}
            <div>
              <div className="text-xs font-bold text-muted-foreground uppercase tracking-wider mb-1">Documentation</div>
              {claimText ? (
                <p className="text-sm text-foreground line-clamp-2 italic">"{claimText}"</p>
              ) : (
                <p className="text-sm text-muted-foreground italic">No matching documentation claim found.</p>
              )}
            </div>
            
            {/* Code Evidence Side */}
            <div>
              <div className="text-xs font-bold text-muted-foreground uppercase tracking-wider mb-1">Repository Code</div>
              <p className="text-sm text-foreground">
                {evidenceCount > 0 ? (
                  <span className="flex items-center gap-1.5">
                    <CheckCircle2 size={14} className="text-emerald-500" />
                    {evidenceCount} evidence {evidenceCount === 1 ? 'source' : 'sources'} found
                  </span>
                ) : (
                  <span className="flex items-center gap-1.5 text-muted-foreground">
                    <HelpCircle size={14} />
                    No direct code evidence linked
                  </span>
                )}
              </p>
            </div>
          </div>
        </div>

        {/* Action Button */}
        <div className="flex flex-col items-end gap-3 self-stretch justify-end md:justify-center border-t md:border-t-0 md:border-l border-border pt-4 md:pt-0 md:pl-6 w-full md:w-auto">
          <div className="text-xs font-medium text-muted-foreground mb-1 text-right">
            {isVerified && 'Code supports the documented behavior.'}
            {isMissingDocs && 'Repository capability is undocumented.'}
            {isContradicted && 'Documentation differs from repository behavior.'}
            {!isVerified && !isMissingDocs && !isContradicted && 'Insufficient evidence to verify.'}
          </div>
          <button className="flex items-center gap-1.5 text-sm font-medium text-primary hover:text-primary/80 group-hover:translate-x-1 transition-transform">
            View Evidence <ArrowRight size={16} />
          </button>
        </div>

      </div>
    </div>
  );
}
