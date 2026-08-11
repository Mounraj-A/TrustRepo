// ============================================================
// App Configuration — Central source of truth for all constants
// ============================================================

export const CONFIG = {
  API_BASE: '/api',
  BACKEND_URL: 'http://127.0.0.1:8000',
  APP_NAME: 'TrustRepo',
  APP_DESCRIPTION: 'Enterprise Repository Intelligence Platform',
  APP_VERSION: '3.0.0',
  DEFAULT_TIMEOUT_MS: 120_000,
  MAX_RETRIES: 3,
  RETRY_DELAY_MS: 1_000,
} as const;

export const VERDICT_CONFIG = {
  VERIFIED: {
    label: 'Verified',
    color: 'text-emerald-400',
    bg: 'bg-emerald-500/10',
    border: 'border-emerald-500/30',
    icon: 'CheckCircle2',
  },
  CONTRADICTED: {
    label: 'Contradicted',
    color: 'text-red-400',
    bg: 'bg-red-500/10',
    border: 'border-red-500/30',
    icon: 'XCircle',
  },
  MISSING_DOCUMENTATION: {
    label: 'Missing Docs',
    color: 'text-amber-400',
    bg: 'bg-amber-500/10',
    border: 'border-amber-500/30',
    icon: 'AlertTriangle',
  },
  UNSUPPORTED: {
    label: 'Unsupported',
    color: 'text-slate-400',
    bg: 'bg-slate-500/10',
    border: 'border-slate-500/30',
    icon: 'HelpCircle',
  },
  INSUFFICIENT_EVIDENCE: {
    label: 'Insufficient',
    color: 'text-amber-400',
    bg: 'bg-amber-500/10',
    border: 'border-amber-500/30',
    icon: 'AlertCircle',
  },
} as const;

export const LAYER_CONFIG: Record<string, { label: string; description: string; icon: string }> = {
  '2A: Document Understanding': {
    label: 'Document Understanding',
    description: 'Parse, section, and extract claims from documentation',
    icon: 'FileText',
  },
  '2B: Code Understanding': {
    label: 'Code Understanding',
    description: 'Build AST, UIR, symbols, and relationships',
    icon: 'Code2',
  },
  '3: Knowledge Graph': {
    label: 'Knowledge Graph',
    description: 'Build in-memory graph, detect technologies, extract features',
    icon: 'GitGraph',
  },
  '4: Evidence Retrieval': {
    label: 'Evidence Retrieval',
    description: 'Collect evidence for each claim',
    icon: 'Search',
  },
  '5: Investigation': {
    label: 'Multi-Agent Investigation',
    description: 'Run reasoning agents across code, docs, and graph',
    icon: 'Brain',
  },
  '6: Verification': {
    label: 'Verification Summary',
    description: 'Compute final verdicts and trust scores',
    icon: 'ShieldCheck',
  },
  '7: Report Generation': {
    label: 'Report Generation',
    description: 'Generate final structured trust report',
    icon: 'BarChart3',
  },
};

export const NAV_ITEMS = [
  { path: '/dashboard', label: 'Dashboard', icon: 'LayoutDashboard', group: 'Overview' },
  { path: '/dashboard/repository', label: 'Repository Explorer', icon: 'FolderTree', group: 'Overview' },
  { path: '/dashboard/code', label: 'Code Intelligence', icon: 'Code2', group: 'Analysis' },
  { path: '/dashboard/graph', label: 'Knowledge Graph', icon: 'GitGraph', group: 'Analysis' },
  { path: '/dashboard/technologies', label: 'Technologies', icon: 'Cpu', group: 'Intelligence' },
  { path: '/dashboard/features', label: 'Semantic Features', icon: 'Layers', group: 'Intelligence' },
  { path: '/dashboard/capabilities', label: 'Capabilities', icon: 'Zap', group: 'Intelligence' },
  { path: '/dashboard/architecture', label: 'Architecture', icon: 'Building2', group: 'Intelligence' },
  { path: '/dashboard/documentation', label: 'Documentation', icon: 'BookOpen', group: 'Verification' },
  { path: '/dashboard/claims', label: 'Claim Verification', icon: 'ClipboardCheck', group: 'Verification' },
  { path: '/dashboard/evidence', label: 'Evidence Explorer', icon: 'Search', group: 'Verification' },
  { path: '/dashboard/reasoning', label: 'Reasoning Explorer', icon: 'Brain', group: 'Verification' },
  { path: '/dashboard/trust-score', label: 'Trust Score', icon: 'ShieldCheck', group: 'Results' },
  { path: '/dashboard/benchmarks', label: 'Benchmark Results', icon: 'BarChart3', group: 'Results' },
  { path: '/dashboard/runtime', label: 'Runtime Dashboard', icon: 'Activity', group: 'DevOps' },
  { path: '/dashboard/system-health', label: 'System Health', icon: 'Server', group: 'DevOps' },
  { path: '/dashboard/api-inspector', label: 'API Inspector', icon: 'Terminal', group: 'DevOps' },
  { path: '/dashboard/settings', label: 'Settings', icon: 'Settings', group: 'System' },
] as const;
