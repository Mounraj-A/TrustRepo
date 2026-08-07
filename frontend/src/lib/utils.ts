import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatNumber(n: number | undefined | null): string {
  if (n === null || n === undefined) return '—';
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return n.toLocaleString();
}

export function formatDuration(seconds: number): string {
  if (seconds < 0.001) return '< 1ms';
  if (seconds < 1) return `${(seconds * 1000).toFixed(0)}ms`;
  if (seconds < 60) return `${seconds.toFixed(2)}s`;
  const m = Math.floor(seconds / 60);
  const s = (seconds % 60).toFixed(0);
  return `${m}m ${s}s`;
}

export function formatPercent(value: number, total: number): string {
  if (!total) return '0%';
  return `${Math.round((value / total) * 100)}%`;
}

export function formatScore(score: number): string {
  return `${(score * 100).toFixed(0)}`;
}

export function scoreColor(score: number): string {
  if (score >= 0.8) return 'text-emerald-400';
  if (score >= 0.6) return 'text-amber-400';
  if (score >= 0.4) return 'text-orange-400';
  return 'text-red-400';
}

export function scoreGradient(score: number): string {
  if (score >= 0.8) return 'from-emerald-500 to-green-400';
  if (score >= 0.6) return 'from-amber-500 to-yellow-400';
  if (score >= 0.4) return 'from-orange-500 to-amber-400';
  return 'from-red-500 to-rose-400';
}

export function truncate(str: string, max = 80): string {
  if (!str) return '';
  return str.length > max ? str.slice(0, max) + '…' : str;
}

export function capitalize(str: string): string {
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
}

export function extractRepoName(url: string): string {
  try {
    const parts = url.replace(/\\/g, '/').split('/');
    return parts[parts.length - 1] || url;
  } catch {
    return url;
  }
}

export function verdictColor(verdict: string): string {
  switch (verdict) {
    case 'VERIFIED': return 'text-emerald-400';
    case 'REFUTED': return 'text-red-400';
    case 'PARTIALLY_VERIFIED': return 'text-amber-400';
    default: return 'text-slate-400';
  }
}

export function statusColor(status: string): string {
  switch (status) {
    case 'OK': return 'text-emerald-400';
    case 'FAILED': return 'text-red-400';
    case 'SKIPPED': return 'text-slate-400';
    default: return 'text-amber-400';
  }
}
