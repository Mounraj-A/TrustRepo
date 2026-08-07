import axios, { AxiosError, type AxiosRequestConfig } from 'axios';
import { CONFIG } from '@/config/app';
import type { ApiError } from '@/types/api';

// ── Axios Instance ────────────────────────────────────────────
export const apiClient = axios.create({
  baseURL: CONFIG.API_BASE,
  timeout: CONFIG.DEFAULT_TIMEOUT_MS,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
});

// ── Request Interceptor ───────────────────────────────────────
apiClient.interceptors.request.use(
  (config) => {
    console.debug(`[API] ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => Promise.reject(error)
);

// ── Response Interceptor ──────────────────────────────────────
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    const apiError: ApiError = {
      status: error.response?.status ?? 0,
      message: 'An unexpected error occurred',
      detail: undefined,
      code: error.code,
    };

    if (error.response) {
      const data = error.response.data as Record<string, unknown>;
      apiError.message = (data?.message as string) || error.message;
      apiError.detail = data?.detail as string | undefined;

      if (error.response.status === 0 || error.code === 'ERR_NETWORK') {
        apiError.message = 'Cannot connect to TrustRepo backend. Is the server running on port 8000?';
      }
    } else if (error.request) {
      apiError.message = 'No response from server. Check your network connection.';
      apiError.code = 'ERR_NETWORK';
    } else if (error.code === 'ECONNABORTED') {
      apiError.message = `Request timed out after ${CONFIG.DEFAULT_TIMEOUT_MS / 1000}s. The repository may be large.`;
      apiError.code = 'ERR_TIMEOUT';
    }

    return Promise.reject(apiError);
  }
);

// ── Retry Helper ──────────────────────────────────────────────
export async function withRetry<T>(
  fn: () => Promise<T>,
  retries: number = CONFIG.MAX_RETRIES,
  delayMs: number = CONFIG.RETRY_DELAY_MS
): Promise<T> {
  try {
    return await fn();
  } catch (error) {
    if (retries <= 0) throw error;
    const apiError = error as ApiError;
    // Don't retry on validation errors (4xx)
    if (apiError.status >= 400 && apiError.status < 500) throw error;
    await new Promise((resolve) => setTimeout(resolve, delayMs));
    return withRetry(fn, retries - 1, delayMs * 2);
  }
}

// ── Generic request wrapper ───────────────────────────────────
export async function request<T>(config: AxiosRequestConfig): Promise<T> {
  const response = await apiClient.request<T>(config);
  return response.data;
}
