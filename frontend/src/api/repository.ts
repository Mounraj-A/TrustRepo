import { request, withRetry } from './client';
import type { AnalysisRequest, AnalysisResponse, HealthStatus } from '@/types/api';

// ── Repository Analysis ───────────────────────────────────────
export async function analyzeRepository(req: AnalysisRequest): Promise<AnalysisResponse> {
  return withRetry(() =>
    request<AnalysisResponse>({
      method: 'POST',
      url: '/repositories/analyze',
      data: req,
    })
  );
}

// ── Health Check ──────────────────────────────────────────────
export async function checkHealth(): Promise<HealthStatus> {
  try {
    const data = await request<Record<string, unknown>>({
      method: 'GET',
      url: '/repositories/',
      timeout: 5000,
    });
    return {
      backend: true,
      neo4j: true,
      pipeline: true,
      version: data?.version as string | undefined,
    };
  } catch {
    return { backend: false, neo4j: false, pipeline: false };
  }
}

// ── Repository List ───────────────────────────────────────────
export async function listRepositories(): Promise<string[]> {
  try {
    const data = await request<{ repositories?: string[] }>({
      method: 'GET',
      url: '/repositories/',
    });
    return data?.repositories ?? [];
  } catch {
    return [];
  }
}
