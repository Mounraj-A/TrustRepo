import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { AnalysisResponse, HealthStatus, ThemeMode } from '@/types/api';

// ── Analysis Store ────────────────────────────────────────────
interface AnalysisState {
  repositoryUrl: string;
  isAnalyzing: boolean;
  analysisResult: AnalysisResponse | null;
  error: string | null;
  health: HealthStatus | null;

  setRepositoryUrl: (url: string) => void;
  setAnalyzing: (v: boolean) => void;
  setResult: (result: AnalysisResponse) => void;
  setError: (err: string | null) => void;
  setHealth: (h: HealthStatus) => void;
  reset: () => void;
}

export const useAnalysisStore = create<AnalysisState>()((set) => ({
  repositoryUrl: '',
  isAnalyzing: false,
  analysisResult: null,
  error: null,
  health: null,

  setRepositoryUrl: (url) => set({ repositoryUrl: url }),
  setAnalyzing: (v) => set({ isAnalyzing: v }),
  setResult: (result) => set({ analysisResult: result, error: null, isAnalyzing: false }),
  setError: (err) => set({ error: err, isAnalyzing: false }),
  setHealth: (h) => set({ health: h }),
  reset: () => set({ analysisResult: null, error: null, isAnalyzing: false }),
}));

// ── Settings Store ────────────────────────────────────────────
interface SettingsState {
  theme: ThemeMode;
  backendUrl: string;
  timeout: number;
  maxRetries: number;
  showRawJson: boolean;
  setTheme: (t: ThemeMode) => void;
  setBackendUrl: (url: string) => void;
  setTimeout: (ms: number) => void;
  setMaxRetries: (n: number) => void;
  toggleRawJson: () => void;
}

export const useSettingsStore = create<SettingsState>()(
  persist(
    (set) => ({
      theme: 'dark',
      backendUrl: 'http://127.0.0.1:8000',
      timeout: 120000,
      maxRetries: 3,
      showRawJson: false,
      setTheme: (t) => set({ theme: t }),
      setBackendUrl: (url) => set({ backendUrl: url }),
      setTimeout: (ms) => set({ timeout: ms }),
      setMaxRetries: (n) => set({ maxRetries: n }),
      toggleRawJson: () => set((s) => ({ showRawJson: !s.showRawJson })),
    }),
    { name: 'trustrepo-settings' }
  )
);

// ── UI Store ─────────────────────────────────────────────────
interface UIState {
  sidebarOpen: boolean;
  activeSearch: string;
  setSidebarOpen: (v: boolean) => void;
  toggleSidebar: () => void;
  setSearch: (q: string) => void;
}

export const useUIStore = create<UIState>()((set) => ({
  sidebarOpen: true,
  activeSearch: '',
  setSidebarOpen: (v) => set({ sidebarOpen: v }),
  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
  setSearch: (q) => set({ activeSearch: q }),
}));
