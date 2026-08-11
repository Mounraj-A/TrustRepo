import { DocumentationClaim, EvidenceItem } from '@/types/api';
import { CheckCircle2, AlertTriangle, XCircle, HelpCircle, X, FileCode2, ArrowDown, FileText } from 'lucide-react';
import { useEffect, useState } from 'react';

interface ClaimEvidenceDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  claim: DocumentationClaim | null;
}

const EvidenceSnippet = ({ item }: { item: EvidenceItem }) => (
  <div className="bg-muted/30 border border-border rounded-lg overflow-hidden">
    <div className="flex items-center gap-2 px-3 py-2 bg-muted/50 border-b border-border text-xs text-muted-foreground font-medium">
      <FileCode2 size={14} />
      <span>{item.source.file_path}</span>
      {item.source.line_number && <span className="opacity-70">: line {item.source.line_number}</span>}
    </div>
    {item.code_snippet && (
      <div className="p-3 overflow-x-auto">
        <pre className="text-xs font-mono text-foreground m-0 p-0 bg-transparent border-0">
          <code>{item.code_snippet}</code>
        </pre>
      </div>
    )}
  </div>
);

export default function ClaimEvidenceDrawer({ isOpen, onClose, claim }: ClaimEvidenceDrawerProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  if (!mounted) return null;

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) onClose();
  };

  if (!claim) return null;

  const isVerified = claim.verdict === 'VERIFIED';
  const isContradicted = claim.verdict === 'CONTRADICTED';
  const isUnsupported = claim.verdict === 'UNSUPPORTED';
  const isInsufficient = claim.verdict === 'INSUFFICIENT_EVIDENCE';

  let StatusIcon = HelpCircle;
  let statusColor = 'text-slate-500';
  let statusBg = 'bg-slate-50';
  let borderColor = 'border-slate-200 dark:border-slate-800';
  let humanStatus = 'UNKNOWN';
  let verificationMessage = 'Insufficient evidence supplied by backend';

  if (isVerified) {
    StatusIcon = CheckCircle2;
    statusColor = 'text-emerald-600';
    statusBg = 'bg-emerald-50';
    borderColor = 'border-emerald-200 dark:border-emerald-900/50';
    humanStatus = 'VERIFIED';
    verificationMessage = 'Evidence supports the claim';
  } else if (isContradicted) {
    StatusIcon = XCircle;
    statusColor = 'text-rose-600';
    statusBg = 'bg-rose-50';
    borderColor = 'border-rose-200 dark:border-rose-900/50';
    humanStatus = 'REFUTED';
    verificationMessage = 'Evidence conflicts with claim';
  } else if (isUnsupported) {
    StatusIcon = AlertTriangle;
    statusColor = 'text-amber-600';
    statusBg = 'bg-amber-50';
    borderColor = 'border-amber-200 dark:border-amber-900/50';
    humanStatus = 'PARTIALLY VERIFIED';
    verificationMessage = 'Evidence partially supports claim';
  } else if (isInsufficient) {
    StatusIcon = HelpCircle;
    statusColor = 'text-indigo-600';
    statusBg = 'bg-indigo-50';
    borderColor = 'border-indigo-200 dark:border-indigo-900/50';
    humanStatus = 'INSUFFICIENT';
    verificationMessage = 'Insufficient evidence';
  }

  const allEvidence = claim.provenance_chain?.sequence || [];

  return (
    <>
      <div 
        className={`fixed inset-0 bg-background/80 backdrop-blur-sm z-40 transition-opacity duration-300 ${isOpen ? 'opacity-100 pointer-events-auto' : 'opacity-0 pointer-events-none'}`}
        onClick={handleBackdropClick}
      />
      
      <div className={`fixed inset-y-0 right-0 w-full md:w-[500px] bg-background border-l border-border shadow-2xl z-50 transform transition-transform duration-300 ease-in-out flex flex-col ${isOpen ? 'translate-x-0' : 'translate-x-full'}`}>
        
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-border bg-muted/20">
          <div className="flex items-center gap-2">
            <h2 className="text-lg font-bold text-foreground">CLAIM VERIFICATION</h2>
            <div className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md ${statusBg} ${statusColor} font-bold text-[10px] uppercase tracking-wider border ${borderColor}`}>
              <StatusIcon size={12} />
              {humanStatus}
            </div>
          </div>
          <button 
            onClick={onClose}
            className="p-2 hover:bg-muted rounded-full transition-colors text-muted-foreground hover:text-foreground"
          >
            <X size={20} />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          
          {/* CLAIM Block */}
          <div>
            <h4 className="text-xs font-bold text-muted-foreground uppercase tracking-wider mb-2">CLAIM</h4>
            <div className="text-base text-foreground font-medium">"{claim.claim_text}"</div>
          </div>

          <div className="flex justify-center text-muted-foreground/30">
            <ArrowDown size={20} />
          </div>

          {/* DOCUMENTATION Block */}
          <div>
            <h4 className="text-xs font-bold text-muted-foreground uppercase tracking-wider mb-2 flex items-center gap-1.5">
              <FileText size={14} /> Documentation
            </h4>
            <div className="p-4 bg-muted/20 rounded-lg border border-border">
              {claim.source_file ? (
                <div className="space-y-2 text-sm text-foreground">
                  <div className="font-medium text-primary">{claim.source_file}</div>
                  {claim.line_range && <div className="text-muted-foreground text-xs font-mono">Lines {claim.line_range}</div>}
                  {/* We don't have the raw doc snippet in the current API, so we skip it to not fabricate data. */}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground italic">No specific documentation location provided.</p>
              )}
            </div>
          </div>

          <div className="flex justify-center text-muted-foreground/30">
            <ArrowDown size={20} />
          </div>

          {/* REPOSITORY EVIDENCE Block */}
          <div>
            <h4 className="text-xs font-bold text-muted-foreground uppercase tracking-wider mb-2 flex items-center gap-1.5">
              <FileCode2 size={14} /> Repository Evidence
            </h4>
            {allEvidence.length > 0 ? (
              <div className="space-y-4">
                {allEvidence.map((item, idx) => (
                  <EvidenceSnippet key={idx} item={item} />
                ))}
              </div>
            ) : (
              <div className="p-4 bg-muted/20 rounded-lg border border-border border-dashed text-sm text-muted-foreground">
                No sufficient evidence supplied by backend
              </div>
            )}
          </div>

          <div className="flex justify-center text-muted-foreground/30">
            <ArrowDown size={20} />
          </div>

          {/* VERIFICATION Block */}
          <div>
            <h4 className="text-xs font-bold text-muted-foreground uppercase tracking-wider mb-2">VERIFICATION</h4>
            <div className={`flex items-center gap-2 text-sm font-bold ${statusColor}`}>
              <StatusIcon size={16} /> {verificationMessage}
            </div>
          </div>
          
          <div className="flex justify-center text-muted-foreground/30">
            <ArrowDown size={20} />
          </div>

          {/* VERDICT & REASONING Block */}
          <div>
            <div className={`p-4 rounded-xl border ${statusBg} ${borderColor}`}>
              <h4 className={`text-xs font-bold uppercase tracking-wider mb-1 ${statusColor}`}>VERDICT</h4>
              <div className={`text-lg font-bold mb-4 ${statusColor}`}>{humanStatus}</div>
              
              {claim.reasoning && (
            <div className="space-y-4">
              <h3 className="text-sm font-bold uppercase tracking-wider text-muted-foreground">Reasoning Trace</h3>
              <div className="bg-muted/40 rounded-xl p-5 text-sm text-foreground leading-relaxed">
                {claim.reasoning}
              </div>
            </div>
          )}  </div>
          </div>

        </div>
      </div>
    </>
  );
}
