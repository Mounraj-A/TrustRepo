import { ShieldCheck, GitBranch, Search } from 'lucide-react';
import { motion } from 'framer-motion';

export default function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center h-full min-h-[60vh] p-8 text-center animate-in">
      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.5, ease: 'backOut' }}
        className="relative mb-8"
      >
        <div className="w-24 h-24 rounded-3xl gradient-trust flex items-center justify-center shadow-2xl shadow-primary/30">
          <ShieldCheck size={40} className="text-white" />
        </div>
        <div className="absolute -top-2 -right-2 w-8 h-8 rounded-full bg-card border-2 border-border flex items-center justify-center">
          <GitBranch size={14} className="text-muted-foreground" />
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="space-y-3 max-w-md"
      >
        <h2 className="text-2xl font-bold gradient-text">TrustRepo Intelligence Platform</h2>
        <p className="text-muted-foreground">
          Enter a repository URL above to begin evidence-based analysis.
          Every claim, technology, and feature will be backed by parser-level evidence.
        </p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="mt-10 grid grid-cols-1 sm:grid-cols-3 gap-4 w-full max-w-2xl"
      >
        {[
          { icon: Search, title: 'Evidence-Based', desc: 'Every insight backed by parser evidence' },
          { icon: GitBranch, title: 'Multi-Language', desc: 'Java, Python, JavaScript, TypeScript' },
          { icon: ShieldCheck, title: 'Trust Scoring', desc: 'Claim verification with confidence scores' },
        ].map(({ icon: Icon, title, desc }) => (
          <div key={title} className="glass rounded-xl p-4 text-left">
            <div className="p-2 bg-primary/10 rounded-lg w-fit mb-3">
              <Icon size={16} className="text-primary" />
            </div>
            <p className="text-sm font-semibold">{title}</p>
            <p className="text-xs text-muted-foreground mt-1">{desc}</p>
          </div>
        ))}
      </motion.div>
    </div>
  );
}
