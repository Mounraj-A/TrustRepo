import { UnifiedEvidenceItem } from '@/types/api';
import { X, ExternalLink, Link2, GitGraph, FileCode2, FileText, Settings, FlaskConical, HelpCircle, CheckCircle2, AlertTriangle, XCircle } from 'lucide-react';
import { useEffect } from 'react';

interface EvidenceDetailsDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  evidence: UnifiedEvidenceItem | null;
}

export default function EvidenceDetailsDrawer({ isOpen, onClose, evidence }: EvidenceDetailsDrawerProps) {
  
  // Handle escape key
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, [onClose]);

  if (!evidence) return null;

  const type = evidence.evidence_type.toUpperCase();
  let TypeIcon = HelpCircle;
  let typeColor = 'text-pink-600';
  let typeBg = 'bg-pink-50';
  let typeBorder = 'border-pink-200';

  if (type.includes('DOCUMENTATION')) {
    TypeIcon = FileText;
    typeColor = 'text-purple-600';
    typeBg = 'bg-purple-50';
    typeBorder = 'border-purple-200';
  } else if (type.includes('CODE') || type.includes('REPOSITORY')) {
    TypeIcon = FileCode2;
    typeColor = 'text-blue-600';
    typeBg = 'bg-blue-50';
    typeBorder = 'border-blue-200';
  } else if (type.includes('TEST')) {
    TypeIcon = FlaskConical;
    typeColor = 'text-emerald-600';
    typeBg = 'bg-emerald-50';
    typeBorder = 'border-emerald-200';
  } else if (type.includes('CONFIG')) {
    TypeIcon = Settings;
    typeColor = 'text-orange-600';
    typeBg = 'bg-orange-50';
    typeBorder = 'border-orange-200';
  }

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
    <>
      {/* Backdrop */}
      <div 
        className={`fixed inset-0 bg-background/80 backdrop-blur-sm z-40 transition-opacity duration-300 ${isOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'}`}
        onClick={onClose}
      />
      
      {/* Drawer */}
      <div className={`fixed inset-y-0 right-0 w-full max-w-2xl bg-card border-l border-border z-50 shadow-2xl flex flex-col transition-transform duration-300 ease-out ${isOpen ? 'translate-x-0' : 'translate-x-full'}`}>
        
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-border bg-muted/20">
          <h2 className="text-xl font-bold flex items-center gap-2">
            <TypeIcon className={typeColor} size={24} />
            Evidence Details
          </h2>
          <button 
            onClick={onClose}
            className="p-2 hover:bg-muted rounded-full transition-colors"
          >
            <X size={20} className="text-muted-foreground" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-8 pb-20">
          
          {/* 1. Evidence Source block */}
          <div className="space-y-4">
            <h3 className="text-sm font-bold uppercase tracking-wider text-muted-foreground">Source</h3>
            <div className={`rounded-xl border ${typeBorder} overflow-hidden`}>
              <div className={`px-4 py-3 border-b ${typeBorder} ${typeBg} flex items-center gap-2`}>
                <TypeIcon size={16} className={typeColor} />
                <span className={`text-sm font-bold ${typeColor}`}>{type}</span>
              </div>
              <div className="p-4 bg-card space-y-4">
                
                {evidence.source_file ? (
                  <div>
                    <div className="flex items-center gap-2 font-mono text-sm text-foreground break-all">
                      <ExternalLink size={14} className="text-muted-foreground shrink-0" />
                      {evidence.source_file}
                    </div>
                    {evidence.line_range && (
                      <div className="text-xs text-muted-foreground mt-1 ml-6 font-mono">
                        Lines {evidence.line_range}
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-sm text-muted-foreground italic">No repository file provided.</div>
                )}
                
                {evidence.snippet ? (
                  <div className="mt-4 rounded-md border border-border bg-muted/30 overflow-hidden">
                    <pre className="p-4 text-sm font-mono text-foreground overflow-x-auto">
                      <code>{evidence.snippet}</code>
                    </pre>
                  </div>
                ) : (
                  <div className="mt-4 p-4 rounded-md border border-dashed border-border bg-muted/10 text-center text-sm text-muted-foreground italic">
                    No code snippet available
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* 2. Linked Claim */}
          {evidence.linked_claim && (
            <div className="space-y-4">
              <h3 className="text-sm font-bold uppercase tracking-wider text-muted-foreground">Linked Claim</h3>
              <div className="glass rounded-xl p-5 border-l-4 border-l-primary/50">
                <div className="flex items-start gap-3">
                  <Link2 className="text-primary mt-1 shrink-0" size={18} />
                  <div>
                    <p className="text-base font-medium text-foreground leading-relaxed">
                      "{evidence.linked_claim.claim_text}"
                    </p>
                    {VerdictIcon && (
                      <div className={`mt-3 inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold uppercase tracking-wider border bg-background/50 ${verdictColor.replace('text-', 'border-').replace('600', '200')} ${verdictColor}`}>
                        <VerdictIcon size={14} />
                        {verdictText}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* 3. Reasoning */}
          {evidence.reasoning && (
            <div className="space-y-4">
              <h3 className="text-sm font-bold uppercase tracking-wider text-muted-foreground">Verification Reasoning</h3>
              <div className="bg-muted/40 rounded-xl p-5 text-sm text-foreground leading-relaxed">
                {evidence.reasoning}
              </div>
            </div>
          )}

          {/* 4. Provenance */}
          <div className="space-y-4">
            <h3 className="text-sm font-bold uppercase tracking-wider text-muted-foreground">Provenance Chain</h3>
            
            {evidence.provenance_chain ? (
              <div className="glass rounded-xl p-5 space-y-4">
                <div className="flex items-center gap-2 text-sm font-semibold mb-2">
                  <GitGraph size={16} className="text-muted-foreground" />
                  Backend Execution Trace
                </div>
                
                <div className="pl-4 border-l-2 border-primary/20 space-y-6 py-2 relative">
                  
                  {/* Sequence items */}
                  {evidence.provenance_chain.sequence?.map((item, idx) => (
                    <div key={idx} className="relative">
                      <div className="absolute -left-[21px] top-1 w-2.5 h-2.5 rounded-full bg-primary/40 border-2 border-background" />
                      <div className="text-xs font-bold text-muted-foreground uppercase tracking-wider mb-1">
                        {item.node_type || item.evidence_type}
                      </div>
                      <div className="text-sm font-mono text-foreground break-all">
                        {item.symbol || item.qualified_name || "Unknown node"}
                      </div>
                    </div>
                  ))}
                  
                  {/* Verdict node */}
                  <div className="relative">
                    <div className="absolute -left-[21px] top-1 w-2.5 h-2.5 rounded-full bg-primary border-2 border-background" />
                    <div className="text-xs font-bold text-muted-foreground uppercase tracking-wider mb-1">
                      VERDICT
                    </div>
                    <div className="text-sm font-medium">
                      Trust Score: {Math.round((evidence.provenance_chain?.confidence || 0) * 100)}%
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-sm text-muted-foreground italic bg-muted/20 p-4 rounded-xl border border-dashed border-border">
                Provenance information not provided by backend for this evidence.
              </div>
            )}
          </div>

        </div>
      </div>
    </>
  );
}
