// ============================================================
// TrustRepo — Complete TypeScript Type Definitions
// Maps 1:1 to backend TrustRepoContext and API DTOs
// ============================================================

// ── Core API Response ────────────────────────────────────────
export interface AnalysisRequest {
  repository_url: string;
}

export interface AnalysisResponse {
  status: 'completed' | 'error' | 'running';
  processing_time_seconds: number;
  report: TrustReport;
  markdown: string;
  code_metrics: CodeMetrics;
  graph_metrics: GraphMetrics;
  verification_summary: VerificationSummary;
  execution_trace: LayerTrace[];
  code_intelligence: CodeIntelligence;
  detail?: string;
  message?: string;
}

// ── Trust Report ─────────────────────────────────────────────
export interface TrustReport {
  repository_name: string;
  repository_url: string;
  analysis_timestamp: string;
  trust_score: number;
  overall_assessment: string;
  documentation_coverage: number;
  claims?: ClaimVerification[];
  technology_summary?: string;
  feature_summary?: string;
  architecture_summary?: string;
  recommendations?: Array<string | { priority?: string; message?: string; [key: string]: any }>;
  risk_factors?: Array<string | { severity?: string; message?: string; [key: string]: any }>;
  strengths?: Array<string | { message?: string; [key: string]: any }>;
}

// ── Verification ─────────────────────────────────────────────
export interface ClaimVerification {
  claim_id: string;
  claim_text: string;
  verdict: 'VERIFIED' | 'CONTRADICTION' | 'MISSING_DOCUMENTATION' | 'UNSUPPORTED_DOCUMENTATION' | 'PARTIAL_DOCUMENTATION';
  trust_score: number;
  confidence: number;
  reasoning_trace: string[];
  evidence_count?: number;
  recommendation?: string;
}

export interface VerificationSummary {
  total_claims: number;
  verified: number;
  refuted: number;
  partially_verified: number;
  insufficient: number;
}

// ── Code Metrics ─────────────────────────────────────────────
export interface CodeMetrics {
  source_files: number;
  parsed_files: number;
  ast_nodes: number;
  uir_files: number;
  symbols: number;
  relationships: number;
}

// ── Graph Metrics ─────────────────────────────────────────────
export interface GraphMetrics {
  nodes: number;
  edges: number;
  raw_nodes?: any[];
  raw_edges?: any[];
  technologies: string[];
  technology_categories: Record<string, string[]>;
  features: string[];
  capabilities: string[];
  architectures: string[];
  evidence_chain_count: number;
  analytics: GraphAnalytics;
  schema_validation: SchemaValidation;
}

export interface GraphAnalytics {
  cycle_detected?: boolean;
  cycle_count?: number;
  node_count?: number;
  edge_count?: number;
  critical_nodes?: number;
  communities?: number;
  schema_validation?: SchemaValidation;
}

export interface SchemaValidation {
  is_valid: boolean;
  node_count: number;
  edge_count: number;
  missing_required_properties: number;
  duplicate_nodes: number;
  isolated_nodes: number;
  density_score: number;
  integrity_score: number;
  warnings: string[];
  errors: string[];
}

// ── Execution Trace (Runtime Dashboard) ──────────────────────
export interface LayerTrace {
  layer: string;
  status: 'OK' | 'FAILED' | 'SKIPPED' | 'PENDING';
  time_s: number;
  objects_created: number;
  evidence_count: number;
  warnings: string[];
  errors: string[];
  details: Record<string, unknown>;
}

// ── Code Intelligence Mode ────────────────────────────────────
export interface CodeIntelligence {
  mode?: string;
  detected_components?: string[];
  missing_documentation?: string[];
  recommendations?: string[];
}

// ── App State ─────────────────────────────────────────────────
export type ThemeMode = 'dark' | 'light';

export interface AppSettings {
  backendUrl: string;
  theme: ThemeMode;
  showRawJson: boolean;
  maxRetries: number;
  timeout: number;
}

// ── API Error ─────────────────────────────────────────────────
export interface ApiError {
  status: number;
  message: string;
  detail?: string;
  code?: string;
}

// ── Health ────────────────────────────────────────────────────
export interface HealthStatus {
  backend: boolean;
  neo4j: boolean;
  pipeline: boolean;
  version?: string;
  uptime?: number;
}
