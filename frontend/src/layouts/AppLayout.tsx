import { useEffect } from 'react';
import { Outlet, NavLink, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  LayoutDashboard, FolderTree, Code2, GitGraph, Cpu, Layers, Zap,
  Building2, BookOpen, ClipboardCheck, Search, ShieldCheck, Activity,
  Terminal, Settings, ChevronLeft, ChevronRight, Circle, CheckCircle2,
  AlertCircle, Menu, Brain, Server, BarChart3
} from 'lucide-react';
import { cn, formatDuration, scoreColor } from '@/lib/utils';
import { useAnalysisStore, useUIStore } from '@/store';
import { useHealth } from '@/hooks/useAnalysis';
import { NAV_ITEMS } from '@/config/app';
import AnalyzeBar from '@/components/AnalyzeBar';

const ICON_MAP: Record<string, React.ComponentType<{ className?: string; size?: number }>> = {
  LayoutDashboard, FolderTree, Code2, GitGraph, Cpu, Layers, Zap,
  Building2, BookOpen, ClipboardCheck, Search, ShieldCheck, Activity,
  Terminal, Settings, Brain, Server, BarChart3,
};

const NAV_GROUPS = ['Overview', 'Analysis', 'Intelligence', 'Verification', 'Results', 'DevOps', 'System'];

export default function AppLayout() {
  const { sidebarOpen, toggleSidebar } = useUIStore();
  const { analysisResult, health } = useAnalysisStore();
  const { mutate: ping } = useHealth();
  const location = useLocation();

  // Health check on mount
  useEffect(() => { ping(); }, []);

  const score = analysisResult?.report?.trust_score;
  const repoName = analysisResult?.report?.repository_name;

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      {/* ── Sidebar ─────────────────────────────────────────────── */}
      <motion.aside
        initial={false}
        animate={{ width: sidebarOpen ? 260 : 60 }}
        transition={{ duration: 0.25, ease: 'easeInOut' }}
        className="relative flex flex-col border-r border-border bg-card/50 backdrop-blur-sm shrink-0 z-20"
      >
        {/* Logo */}
        <div className="flex items-center gap-3 px-4 py-4 border-b border-border min-h-[56px]">
          <div className="w-7 h-7 rounded-lg gradient-trust flex items-center justify-center shrink-0">
            <ShieldCheck size={14} className="text-white" />
          </div>
          <AnimatePresence>
            {sidebarOpen && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.15 }}
              >
                <p className="text-sm font-bold tracking-tight gradient-text">TrustRepo</p>
                <p className="text-[10px] text-muted-foreground">v3.0 Intelligence Platform</p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto py-3 px-2 space-y-4">
          {NAV_GROUPS.map((group) => {
            const items = NAV_ITEMS.filter((i) => i.group === group);
            if (!items.length) return null;
            return (
              <div key={group}>
                {sidebarOpen && (
                  <p className="text-[10px] uppercase tracking-widest text-muted-foreground/50 px-3 mb-1 font-semibold">
                    {group}
                  </p>
                )}
                {items.map((item) => {
                  const Icon = ICON_MAP[item.icon];
                  return (
                    <NavLink
                      key={item.path}
                      to={item.path}
                      className={({ isActive }) =>
                        cn('nav-item', isActive && 'active')
                      }
                      title={!sidebarOpen ? item.label : undefined}
                    >
                      {Icon && <Icon size={16} className="shrink-0" />}
                      <AnimatePresence>
                        {sidebarOpen && (
                          <motion.span
                            initial={{ opacity: 0, x: -4 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0 }}
                            transition={{ duration: 0.15 }}
                            className="truncate"
                          >
                            {item.label}
                          </motion.span>
                        )}
                      </AnimatePresence>
                    </NavLink>
                  );
                })}
              </div>
            );
          })}
        </nav>

        {/* Sidebar footer — status + score */}
        {sidebarOpen && (
          <div className="border-t border-border px-3 py-3 space-y-2">
            <div className="flex items-center gap-2">
              <Circle
                size={8}
                className={cn('shrink-0', health?.backend ? 'text-emerald-400 fill-emerald-400' : 'text-red-400 fill-red-400')}
              />
              <span className="text-xs text-muted-foreground truncate">
                {health?.backend ? 'Backend Connected' : 'Backend Offline'}
              </span>
            </div>
            {score !== undefined && (
              <div className="text-xs text-muted-foreground">
                Trust Score: <span className={cn('font-bold', scoreColor(score))}>{Math.round(score * 100)}%</span>
              </div>
            )}
            {repoName && (
              <p className="text-[10px] text-muted-foreground/60 truncate">{repoName}</p>
            )}
          </div>
        )}

        {/* Collapse button */}
        <button
          onClick={toggleSidebar}
          className="absolute -right-3 top-1/2 -translate-y-1/2 w-6 h-6 rounded-full bg-card border border-border
                     flex items-center justify-center text-muted-foreground hover:text-foreground
                     hover:border-primary/40 transition-all duration-200 z-30"
        >
          {sidebarOpen ? <ChevronLeft size={12} /> : <ChevronRight size={12} />}
        </button>
      </motion.aside>

      {/* ── Main Content ─────────────────────────────────────────── */}
      <div className="flex flex-col flex-1 min-w-0">
        {/* Header */}
        <header className="flex items-center gap-4 px-6 border-b border-border bg-card/50 backdrop-blur-sm min-h-[56px] shrink-0">
          <button
            onClick={toggleSidebar}
            className="md:hidden p-1.5 rounded-lg hover:bg-accent transition-colors"
          >
            <Menu size={16} />
          </button>

          <div className="flex-1">
            <AnalyzeBar />
          </div>

          {/* Header right — status indicators */}
          {analysisResult && (
            <div className="hidden md:flex items-center gap-3 text-xs text-muted-foreground shrink-0">
              <span className="flex items-center gap-1.5">
                <CheckCircle2 size={12} className="text-emerald-400" />
                {formatDuration(analysisResult.processing_time_seconds)}
              </span>
              {analysisResult.code_metrics?.source_files > 0 && (
                <span>{analysisResult.code_metrics.source_files} files</span>
              )}
            </div>
          )}
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-auto">
          <AnimatePresence mode="wait">
            <motion.div
              key={location.pathname}
              initial={{ opacity: 0, y: 4 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="h-full"
            >
              <Outlet />
            </motion.div>
          </AnimatePresence>
        </main>
      </div>
    </div>
  );
}
