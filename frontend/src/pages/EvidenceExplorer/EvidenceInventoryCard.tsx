import { UnifiedEvidenceItem } from '@/types/api';
import { ArrowRight, FileCode2, FileText, FlaskConical, Settings, HelpCircle, CheckCircle2, AlertTriangle, XCircle } from 'lucide-react';

interface EvidenceInventoryCardProps {
  evidence: UnifiedEvidenceItem;
  onClick: () => void;
}

export default function EvidenceInventoryCard({ evidence, onClick }: EvidenceInventoryCardProps) {
  // Determine Evidence Type styling
  const type = evidence.evidence_type.toUpperCase();
  let TypeIcon = HelpCircle;
  let typeColor = 'text-pink-600';
  let typeBg = 'bg-pink-50';
  let typeBorder = 'border-pink-200 dark:border-pink-900/50';

  if (type.includes('DOCUMENTATION')) {
    TypeIcon = FileText;
    typeColor = 'text-purple-600';
    typeBg = 'bg-purple-50';
    typeBorder = 'border-purple-200 dark:border-purple-900/50';
  } else if (type.includes('CODE') || type.includes('REPOSITORY')) {
    TypeIcon = FileCode2;
    typeColor = 'text-blue-600';
    typeBg = 'bg-blue-50';
    typeBorder = 'border-blue-200 dark:border-blue-900/50';
  } else if (type.includes('TEST')) {
    TypeIcon = FlaskConical;
    typeColor = 'text-emerald-600';
    typeBg = 'bg-emerald-50';
    typeBorder = 'border-emerald-200 dark:border-emerald-900/50';
  } else if (type.includes('CONFIG')) {
    TypeIcon = Settings;
    typeColor = 'text-orange-600';
    typeBg = 'bg-orange-50';
    typeBorder = 'border-orange-200 dark:border-orange-900/50';
  }

  // Determine Linked Claim Verdict styling
  let VerdictIcon = null;
  let verdictColor = 'text-slate-500';
  let verdictText = 'UNKNOWN';

  if (evidence.linked_claim) {
    const v = evidence.linked_claim.verdict;
    if (v === 'VERIFIED') {
      VerdictIcon = CheckCircle2;
      verdictColor = 'text-emerald-600';
      verdictText = 'VERIFIED';
    } else if (v === 'UNSUPPORTED' || v === 'PARTIALLY_VERIFIED') {
      VerdictIcon = AlertTriangle;
      verdictColor = 'text-amber-600';
      verdictText = 'PARTIAL';
    } else if (v === 'CONTRADICTED') {
      VerdictIcon = XCircle;
      verdictColor = 'text-rose-600';
      verdictText = 'REFUTED';
    } else if (v === 'INSUFFICIENT_EVIDENCE') {
      VerdictIcon = HelpCircle;
      verdictColor = 'text-indigo-600';
      verdictText = 'INSUFFICIENT';
    } else if (v === 'MISSING_DOCUMENTATION') {
      VerdictIcon = AlertTriangle;
      verdictColor = 'text-orange-600';
      verdictText = 'MISSING DOCUMENTATION';
    }
  }

  return (
    <div 
      className={`glass rounded-xl overflow-hidden mb-4 border ${typeBorder} hover:shadow-md transition-all cursor-pointer group flex flex-col h-full`}
      onClick={onClick}
    >
      {/* Header */}
      <div className={`px-4 py-2 flex items-center justify-between border-b ${typeBorder} ${typeBg}`}>
        <div className="flex items-center gap-2">
          <TypeIcon size={16} className={typeColor} />
          <span className={`text-xs font-bold tracking-wider ${typeColor}`}>{type}</span>
        </div>
        
        {evidence.linked_claim && VerdictIcon && (
          <div className={`flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-wider ${verdictColor}`}>
            <VerdictIcon size={12} />
            {verdictText}
          </div>
        )}
      </div>

      <div className="p-5 flex-1 flex flex-col justify-between">
        
        {/* Source Info */}
        <div className="space-y-4">
          <div>
            {evidence.source_file ? (
              <h3 className="font-semibold text-sm text-foreground truncate" title={evidence.source_file}>
                {evidence.source_file.split('/').pop()}
              </h3>
            ) : (
              <h3 className="font-semibold text-sm text-muted-foreground italic">No repository file</h3>
            )}
            
            {evidence.line_range && (
              <div className="text-xs text-muted-foreground font-mono mt-1">
                Lines {evidence.line_range}
              </div>
            )}
          </div>

          {/* Snippet */}
          <div className="bg-muted/30 border border-border rounded-lg overflow-hidden relative">
            {evidence.snippet ? (
              <div className="p-3 overflow-hidden">
                <pre className="text-[11px] font-mono text-foreground line-clamp-4 m-0 p-0 bg-transparent border-0 break-all whitespace-pre-wrap">
                  <code>{evidence.snippet}</code>
                </pre>
              </div>
            ) : (
              <div className="p-3 text-xs text-muted-foreground italic text-center py-6">
                No snippet provided
              </div>
            )}
          </div>
        </div>

        {/* Footer Area */}
        <div className="mt-5 pt-4 border-t border-border flex flex-col gap-3">
          {evidence.linked_claim && (
            <div>
              <div className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider mb-1">Linked Claim</div>
              <p className="text-xs text-foreground line-clamp-2 leading-relaxed">
                "{evidence.linked_claim.claim_text}"
              </p>
            </div>
          )}

          <div className="flex justify-end mt-2">
            <button className={`flex items-center gap-1.5 text-xs font-semibold ${typeColor} group-hover:opacity-80 transition-opacity`}>
              View Details <ArrowRight size={14} className="transition-transform group-hover:translate-x-1" />
            </button>
          </div>
        </div>

      </div>
    </div>
  );
}
