import { Routes, Route, Navigate } from 'react-router-dom';
import AppLayout from '@/layouts/AppLayout';
import Landing from '@/pages/Landing';
import Dashboard from '@/pages/Dashboard';
import RepositoryExplorer from '@/pages/RepositoryExplorer';
import CodeIntelligence from '@/pages/CodeIntelligence';
import KnowledgeGraph from '@/pages/KnowledgeGraph';
import Technologies from '@/pages/Technologies';
import SemanticFeatures from '@/pages/SemanticFeatures';
import Capabilities from '@/pages/Capabilities';
import Architecture from '@/pages/Architecture';
import DocumentationAnalysis from '@/pages/DocumentationAnalysis';
import ClaimVerification from '@/pages/ClaimVerification';
import EvidenceExplorer from '@/pages/EvidenceExplorer';
import ReasoningExplorer from '@/pages/ReasoningExplorer';
import TrustScore from '@/pages/TrustScore';
import BenchmarkResults from '@/pages/BenchmarkResults';
import RuntimeDashboard from '@/pages/RuntimeDashboard';
import SystemHealth from '@/pages/SystemHealth';
import ApiInspector from '@/pages/ApiInspector';
import Settings from '@/pages/Settings';

export default function AppRouter() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/dashboard" element={<AppLayout />}>
        <Route index element={<Dashboard />} />
        <Route path="repository"      element={<RepositoryExplorer />} />
        <Route path="code"            element={<CodeIntelligence />} />
        <Route path="graph"           element={<KnowledgeGraph />} />
        <Route path="technologies"    element={<Technologies />} />
        <Route path="features"        element={<SemanticFeatures />} />
        <Route path="capabilities"    element={<Capabilities />} />
        <Route path="architecture"    element={<Architecture />} />
        <Route path="documentation"   element={<DocumentationAnalysis />} />
        <Route path="claims"          element={<ClaimVerification />} />
        <Route path="evidence"        element={<EvidenceExplorer />} />
        <Route path="reasoning"       element={<ReasoningExplorer />} />
        <Route path="trust-score"     element={<TrustScore />} />
        <Route path="benchmarks"      element={<BenchmarkResults />} />
        <Route path="runtime"         element={<RuntimeDashboard />} />
        <Route path="system-health"   element={<SystemHealth />} />
        <Route path="api-inspector"   element={<ApiInspector />} />
        <Route path="settings"        element={<Settings />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
