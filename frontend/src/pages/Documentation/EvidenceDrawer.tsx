import { DocumentationClaim, FeatureFinding, EvidenceItem } from '@/types/api';
import { CheckCircle2, AlertTriangle, XCircle, HelpCircle, X, FileCode2, ArrowDown } from 'lucide-react';
import { useEffect, useState } from 'react';

interface EvidenceDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  data: DocumentationClaim | FeatureFinding | null;
  type: 'claim' | 'feature' | null;
}

const EvidenceSnippet = ({ item }: { item: EvidenceItem }) => (
  <div className="mt-3 bg-muted/30 border border-border rounded-lg overflow-hidden">
    <div className="flex items-center gap-2 px-3 py-2 bg-muted/50 border-b border-border text-xs text-muted-foreground font-medium">
      <FileCode2 size={14} />
      <span>{item.source.file_path}</span>
      {item.source.line_number && <span className="opacity-70">: line {item.source.line_number}</span>}
      <div className="flex-1" />
      <span className="px-2 py-0.5 rounded-full bg-primary/10 text-primary text-[10px] font-bold tracking-wider uppercase">
        {item.evidence_type || 'SOURCE CODE'}
      </span>
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

export default function EvidenceDrawer({ isOpen, onClose, data, type }: EvidenceDrawerProps) {
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

  if (!data) return null;

  const title = type === 'claim' ? (data as DocumentationClaim).claim_text : (data as FeatureFinding).feature;
  const status = type === 'claim' ? (data as DocumentationClaim).verdict : (data as FeatureFinding).status;
  const reasoning = type === 'claim' ? (data as DocumentationClaim).reasoning : (data as FeatureFinding).reasoning;
  const chain = data.provenance_chain || (type === 'feature' ? (data as FeatureFinding).evidence?.[0] : null);
  const claimText = type === 'claim' ? (data as DocumentationClaim).claim_text : null;
  const isMissingDocs = status === 'MISSING_DOCUMENTATION';
  const isContradicted = status === 'CONTRADICTED';
  const isVerified = status === 'VERIFIED';

  let StatusIcon = HelpCircle;
  let statusColor = 'text-slate-500';
  let statusBg = 'bg-slate-100';
  let humanStatus: string = status;

  if (isVerified) {
    StatusIcon = CheckCircle2;
    statusColor = 'text-emerald-600';
    statusBg = 'bg-emerald-50';
    humanStatus = 'VERIFIED';
  } else if (isMissingDocs) {
    StatusIcon = AlertTriangle;
    statusColor = 'text-amber-600';
    statusBg = 'bg-amber-50';
    humanStatus = 'MISSING DOCUMENTATION';
  } else if (isContradicted) {
    StatusIcon = XCircle;
    statusColor = 'text-rose-600';
    statusBg = 'bg-rose-50';
    humanStatus = 'CONTRADICTED';
  }

  const allEvidence = chain?.sequence || [];

  return (
    <>
      {/* Backdrop */}
      <div 
        className={`fixed inset-0 bg-background/80 backdrop-blur-sm z-40 transition-opacity duration-300 ${isOpen ? 'opacity-100 pointer-events-auto' : 'opacity-0 pointer-events-none'}`}
        onClick={handleBackdropClick}
      />
      
      {/* Drawer */}
      <div className={`fixed inset-y-0 right-0 w-full md:w-[600px] bg-background border-l border-border shadow-2xl z-50 transform transition-transform duration-300 ease-in-out flex flex-col ${isOpen ? 'translate-x-0' : 'translate-x-full'}`}>
        
        {/* Header */}
        <div className="flex items-start justify-between p-6 border-b border-border bg-muted/20">
          <div>
            <div className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md ${statusBg} ${statusColor} font-bold text-xs tracking-wider mb-3 border border-current/10`}>
              <StatusIcon size={14} />
              {humanStatus}
            </div>
            <h2 className="text-xl font-bold text-foreground leading-tight">{title}</h2>
          </div>
          <button 
            onClick={onClose}
            className="p-2 hover:bg-muted rounded-full transition-colors text-muted-foreground hover:text-foreground"
          >
            <X size={20} />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-8">
          
          {/* Documentation Block */}
          <div>
            <h4 className="text-xs font-bold text-muted-foreground uppercase tracking-wider mb-3 border-b border-border pb-2">Documentation</h4>
            <div className="p-4 bg-muted/20 rounded-lg border border-border">
              {claimText ? (
                <p className="text-sm text-foreground italic">"{claimText}"</p>
              ) : (
                <div className="flex items-center gap-2 text-muted-foreground">
                  <AlertTriangle size={16} />
                  <span className="text-sm italic">No matching documentation claim found.</span>
                </div>
              )}
            </div>
          </div>

          <div className="flex justify-center text-muted-foreground/50">
            <ArrowDown size={24} />
          </div>

          {/* Repository Code Block */}
          <div>
            <h4 className="text-xs font-bold text-muted-foreground uppercase tracking-wider mb-3 border-b border-border pb-2">Repository Code</h4>
            {allEvidence.length > 0 ? (
              <div className="space-y-4">
                {allEvidence.map((item, idx) => (
                  <EvidenceSnippet key={idx} item={item} />
                ))}
              </div>
            ) : (
              <div className="p-4 bg-muted/20 rounded-lg border border-border border-dashed text-sm text-muted-foreground">
                No code evidence snippets provided by the verification engine.
              </div>
            )}
          </div>

          <div className="flex justify-center text-muted-foreground/50">
            <ArrowDown size={24} />
          </div>

          {/* Evidence Assessment Block */}
          <div>
            <h4 className="text-xs font-bold text-muted-foreground uppercase tracking-wider mb-3 border-b border-border pb-2">Evidence Assessment</h4>
            <div className={`p-5 rounded-xl border ${statusBg.replace('bg-', 'border-')} ${statusBg}`}>
              <div className="flex items-center gap-3 mb-4">
                <div className={`p-2 rounded-full bg-white/60 dark:bg-black/20 ${statusColor}`}>
                  <StatusIcon size={24} />
                </div>
                <div>
                  <h5 className={`font-bold ${statusColor}`}>
                    {isVerified && 'Code supports documentation'}
                    {isMissingDocs && 'Documentation gap detected'}
                    {isContradicted && 'Conflict detected'}
                    {!isVerified && !isMissingDocs && !isContradicted && 'Insufficient evidence'}
                  </h5>
                  <p className="text-xs text-muted-foreground mt-0.5 uppercase tracking-wider font-semibold">Verdict: {humanStatus}</p>
                </div>
              </div>
              
              {reasoning && (
                <div className="mt-4 pt-4 border-t border-black/5 dark:border-white/5">
                  <h6 className={`text-xs font-bold uppercase tracking-wider mb-2 opacity-70 ${statusColor}`}>Reasoning</h6>
                  <p className={`text-sm leading-relaxed ${statusColor} opacity-90`}>{reasoning}</p>
                </div>
              )}
            </div>
          </div>

        </div>
      </div>
    </>
  );
}
