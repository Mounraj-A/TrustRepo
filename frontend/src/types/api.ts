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
  report: RepositoryReport;
  markdown: string;
  code_metrics: CodeMetrics;
  graph_metrics: GraphMetrics;
  verification_summary: VerificationSummary;
  execution_trace: LayerTrace[];
  code_intelligence: CodeIntelligence;
  file_tree?: FileTreeNode[];
  detail?: string;
  message?: string;
}

export interface FileTreeNode {
  name: string;
  type: 'file' | 'directory';
  path?: string;
  language?: string;
  size?: number;
  children?: FileTreeNode[];
}

export interface DocumentationCoverage {
  detected_features: number;
  documented_features: number;
  verified_features: number;
  contradicted_features: number;
  missing_features: number;
  coverage_percentage: number;
}

export interface UndocumentedFeature {
  feature_name: string;
  status: string;
  evidence_chain?: EvidenceChain;
  reason: string;
  documentation_analysis: string;
  verdict: string;
  confidence: number;
  recommendation: string;
}

export interface DocumentationSummary {
  documentation_sources: string[];
  total_candidates: number;
  confirmed_features: number;
  documented_features: number;
  missing_documentation: number;
  contradicted: number;
  insufficient_evidence: number;
  total_claims: number;
  verified_claims: number;
  contradicted_claims: number;
  coverage_percentage: number;
  coverage_score: number | null;
}

export interface Recommendation {
  priority: string;
  message: string;
}

export interface TrustAssessment {
  score: number;
  status: string;
  details: string;
}

export interface RepositoryMetadata {
  repository_url: string;
  commit_sha: string;
  branch: string;
  languages: string[];
  frameworks: string[];
  source_files_count: number;
  documentation_sources: string[];
  claims_analyzed: number;
  features_investigated: number;
  analysis_date: string;
  verification_version: string;
}

export interface UnifiedEvidenceItem {
  evidence_id: string;
  evidence_type: string;
  source_file?: string;
  line_range?: string;
  snippet?: string;
  linked_claim?: {
    claim_id: string;
    claim_text: string;
    verdict: string;
  };
  reasoning?: string;
  provenance_chain?: EvidenceChain | null;
}

export interface EvidenceSummary {
  total_evidence: number;
  linked_claims: number;
  source_files: number;
}

export interface RepositoryReport {
  metadata: RepositoryMetadata;
  summary: DocumentationSummary;
  documentation_claims: DocumentationClaim[];
  feature_findings: FeatureFinding[];
  architecture_findings?: ArchitectureFinding[];
  contradictions: any[]; // Map if needed
  recommendations: Recommendation[];
  trust_assessment: TrustAssessment | null;
  evidence_summary: EvidenceSummary;
  unified_evidence: UnifiedEvidenceItem[];
}

export interface FeatureReference {
  id: string;
  name: string;
}

export interface ArchitectureFinding {
  id: string;
  name: string;
  status: string;
  supporting_features: FeatureReference[];
  evidence: EvidenceChain[];
  reasoning?: string;
  provenance_chain?: EvidenceChain;
}

// ── Verification ─────────────────────────────────────────────
export interface EvidenceSource {
  repository_id: string;
  repository_relative_path: string;
  file_path: string;
  line_number?: number;
  column?: number;
}

export interface EvidenceItem {
  id: string;
  source: EvidenceSource;
  node_type: string;
  symbol_kind: string;
  symbol: string;
  qualified_name: string;
  evidence_type: string;
  code_snippet: string;
  evidence_strength: string;
}

export interface EvidenceChain {
  chain_id: string;
  chain_type: string;
  sequence: EvidenceItem[];
  graph_path: string;
  confidence: number;
  reasoning_trace: string;
}

export interface EvidenceSearchStep {
  strategy: string;
  source: string;
  query_description?: string;
  matches: number;
  status: string;
  explanation?: string;
}

export interface EvidenceRetrievalTrace {
  strategies_attempted: string[];
  strategies_succeeded: string[];
  strategies_failed: string[];
  searches: EvidenceSearchStep[];
  candidate_count: number;
  matched_entities: number;
  evidence_items_created: number;
  evidence_items_rejected: number;
  rejection_reasons: string[];
  conclusion?: string;
}

export interface DocumentationSearchResult {
  searched_sources: string[];
  searched_terms: string[];
  matches: string[];
  search_method: string;
  found: boolean;
  search_timestamp: string;
}

export interface ReasoningStep {
  step_id: string;
  step_type: string;
  title: string;
  description?: string;
  source?: string;
  source_file?: string;
  line_start?: number;
  line_end?: number;
  evidence_ids?: string[];
  result?: string;
}

export interface ReasoningTrace {
  claim_id: string;
  steps: ReasoningStep[];
  final_verdict?: string;
  explanation?: string;
}

export interface DocumentationClaim {
  claim_id: string;
  claim_text: string;
  verdict: string;
  verification_category?: string;
  source_file?: string;
  line_range?: string;
  trust_score?: number;
  confidence?: number;
  confidence_breakdown?: Record<string, number>;
  evidence_count?: number;
  evidence_quality?: number;
  evidence_diversity?: number;
  expected_features?: string[];
  observed_features?: string[];
  missing_features?: string[];
  unsupported_features?: string[];
  contradicted_features?: string[];
  reasoning?: string;
  reasoning_trace?: ReasoningTrace | null;
  provenance_chain?: EvidenceChain | null;
  recommendation?: string;
}

export interface FeatureFinding {
  feature: string;
  category: string;
  candidate_source: string;
  status: 'VERIFIED' | 'CONTRADICTED' | 'MISSING_DOCUMENTATION' | 'UNSUPPORTED' | 'INSUFFICIENT_EVIDENCE';
  evidence: EvidenceChain[];
  evidence_count: number;
  evidence_quality: number;
  evidence_diversity: number;
  documentation_search: DocumentationSearchResult | null;
  retrieval_trace: EvidenceRetrievalTrace | null;
  confidence: number | null;
  reasoning: string;
  reasoning_trace: string[];
  provenance_chain: EvidenceChain | null;
  recommendation: string | null;
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
