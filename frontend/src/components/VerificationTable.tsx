import { cn, verdictColor } from '@/lib/utils';
import { CheckCircle2, XCircle, AlertCircle, HelpCircle, TrendingUp, TrendingDown } from 'lucide-react';
import { motion } from 'framer-motion';
import type { ClaimVerification } from '@/types/api';
import { VERDICT_CONFIG } from '@/config/app';

interface VerificationTableProps {
  claims: ClaimVerification[];
  className?: string;
}

export default function VerificationTable({ claims, className }: VerificationTableProps) {
  if (!claims?.length) {
    return (
      <div className="text-center py-10 text-muted-foreground text-sm">
        No claims to display.
      </div>
    );
  }

  return (
    <div className={cn('space-y-3', className)}>
      {claims.map((claim, idx) => {
        const cfg = VERDICT_CONFIG[claim.verdict] ?? VERDICT_CONFIG.INSUFFICIENT_EVIDENCE;
        const VerdictIcon =
          claim.verdict === 'VERIFIED' ? CheckCircle2 :
          claim.verdict === 'REFUTED'  ? XCircle :
          claim.verdict === 'PARTIALLY_VERIFIED' ? AlertCircle :
          HelpCircle;

        return (
          <motion.div
            key={claim.claim_id}
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.25, delay: idx * 0.04 }}
            className={cn('glass rounded-xl p-4 border', cfg.border)}
          >
            {/* Header */}
            <div className="flex items-start gap-3">
              <div className={cn('p-1.5 rounded-lg shrink-0 mt-0.5', cfg.bg)}>
                <VerdictIcon size={14} className={cfg.color} />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium leading-snug">{claim.claim_text}</p>
                <div className="flex items-center gap-3 mt-1.5 flex-wrap">
                  <span className={cn('status-badge', cfg.bg, cfg.color)}>
                    {cfg.label}
                  </span>
                  <span className="text-xs text-muted-foreground">
                    Confidence: <span className="font-medium text-foreground">{Math.round((claim.confidence ?? 0) * 100)}%</span>
                  </span>
                  {claim.trust_score > 0 && (
                    <span className="text-xs text-muted-foreground flex items-center gap-1">
                      Score:
                      <span className={cn('font-medium', verdictColor(claim.verdict))}>
                        {Math.round(claim.trust_score * 100)}%
                      </span>
                    </span>
                  )}
                </div>
              </div>
            </div>

            {/* Reasoning trace */}
            {claim.reasoning_trace?.length > 0 && (
              <div className="mt-3 ml-10 space-y-1">
                {claim.reasoning_trace.slice(0, 3).map((step, i) => (
                  <p key={i} className="text-xs text-muted-foreground flex items-start gap-1.5">
                    <span className="text-primary shrink-0 font-mono">{i + 1}.</span>
                    {step}
                  </p>
                ))}
              </div>
            )}

            {/* Recommendation */}
            {claim.recommendation && (
              <div className="mt-2 ml-10 flex items-start gap-1.5">
                <TrendingUp size={12} className="text-primary shrink-0 mt-0.5" />
                <p className="text-xs text-muted-foreground/80 italic">{claim.recommendation}</p>
              </div>
            )}
          </motion.div>
        );
      })}
    </div>
  );
}
