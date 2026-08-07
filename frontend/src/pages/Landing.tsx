import { motion, useScroll, useTransform } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import {
  ArrowRight, ShieldCheck, Database, FileCode2, GitGraph,
  Search, CheckCircle2, Zap, BrainCircuit, Activity, Layers, Workflow,
  FileText, Network, BarChart4, Box, Cpu
} from 'lucide-react';
import { useEffect, useState } from 'react';

// --- Shared Animation Variants ---
const fadeUp = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.6, ease: 'easeOut' } }
} as any;

const staggerContainer = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.1 } }
} as any;

// --- Animated Counter Component ---
function AnimatedCounter({ value, label }: { value: number, label: string }) {
  const [count, setCount] = useState(0);

  useEffect(() => {
    let start = 0;
    const duration = 2000;
    const increment = value / (duration / 16);

    const timer = setInterval(() => {
      start += increment;
      if (start >= value) {
        setCount(value);
        clearInterval(timer);
      } else {
        setCount(Math.floor(start));
      }
    }, 16);

    return () => clearInterval(timer);
  }, [value]);

  return (
    <div className="flex flex-col items-center p-6 card-secondary hover:border-primary/20 transition-colors">
      <div className="text-4xl font-extrabold text-primary mb-2 tabular-nums">
        {count.toLocaleString()}{value > 1000 ? '+' : ''}
      </div>
      <div className="text-sm text-foreground-muted font-medium">{label}</div>
    </div>
  );
}

export default function Landing() {
  const navigate = useNavigate();
  const { scrollY } = useScroll();
  const y = useTransform(scrollY, [0, 500], [0, 150]);

  return (
    <div className="min-h-screen bg-[#F8FAFC] text-slate-900 selection:bg-indigo-500/30 font-sans overflow-x-hidden">

      {/* --- Navigation --- */}
      <nav className="fixed top-0 left-0 right-0 h-16 bg-white/80 backdrop-blur-xl border-b border-slate-200 z-50 transition-all flex items-center justify-center">
        <div className="max-w-7xl w-full px-6 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center shadow-lg shadow-indigo-600/20">
              <ShieldCheck size={18} className="text-white" />
            </div>
            <span className="font-bold text-lg tracking-tight">TrustRepo</span>
          </div>
          <div className="hidden md:flex items-center gap-8 text-sm font-medium text-slate-600">
            <a href="#features" className="hover:text-indigo-600 transition-colors">Features</a>
            <a href="#architecture" className="hover:text-indigo-600 transition-colors">Architecture</a>
            <a href="#explainable" className="hover:text-indigo-600 transition-colors">Explainable AI</a>
            <a href="#research" className="hover:text-indigo-600 transition-colors">Research</a>
          </div>
          <div className="flex items-center gap-4">
            <button className="hidden md:flex items-center gap-2 text-sm font-medium text-slate-600 hover:text-slate-900 transition-colors">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4" /><path d="M9 18c-4.51 2-5-2-7-2" /></svg>
              GitHub
            </button>
            <button
              onClick={() => navigate('/dashboard')}
              className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-all shadow-md shadow-indigo-600/20 active:scale-95 flex items-center gap-2"
            >
              Analyze Repository <ArrowRight size={16} />
            </button>
          </div>
        </div>
      </nav>

      <main className="pt-32 pb-24">
        {/* --- Hero Section --- */}
        <section className="max-w-7xl mx-auto px-6 mb-32 relative">
          <motion.div
            initial="hidden"
            animate="visible"
            variants={staggerContainer}
            className="text-center max-w-4xl mx-auto z-10 relative"
          >
            <motion.div variants={fadeUp} className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-50 border border-indigo-100 text-indigo-600 text-xs font-semibold uppercase tracking-wider mb-8">
              <SparklesIcon /> Research-Grade Platform
            </motion.div>

            <motion.h1 variants={fadeUp} className="text-3xl md:text-5xl font-extrabold tracking-tight text-slate-900 leading-[1.1] mb-8">
              Independent Evidence-Based <br className="hidden md:block" />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-cyan-500">
                Repository Intelligence
              </span>
            </motion.h1>

            <motion.p variants={fadeUp} className="text-lg md:text-xl text-slate-600 mb-10 leading-relaxed max-w-3xl mx-auto">
              TrustRepo automatically analyzes GitHub repositories using static analysis, knowledge graphs, semantic reasoning, and explainable AI. <br /><br />
              Instead of relying solely on documentation, TrustRepo verifies repository claims against the actual source code and produces deterministic evidence-backed reports.
            </motion.p>

            <motion.div variants={fadeUp} className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <button onClick={() => navigate('/dashboard')} className="w-full sm:w-auto px-8 py-4 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-medium shadow-xl shadow-indigo-600/20 transition-all flex items-center justify-center gap-2 text-lg active:scale-95">
                Analyze Repository <ArrowRight size={18} />
              </button>
              {/* <a href="#architecture" className="w-full sm:w-auto px-8 py-4 bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 rounded-xl font-medium shadow-sm transition-all flex items-center justify-center gap-2 text-lg">
                View Architecture
              </a> */}
            </motion.div>
          </motion.div>

          {/* Hero Illustration Background Elements */}
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[800px] bg-gradient-to-br from-indigo-500/10 to-cyan-500/10 blur-3xl -z-10 rounded-full pointer-events-none" />
        </section>

        {/* --- TrustRepo Pipeline Visualization --- */}
        <section className="py-24 bg-white border-y border-slate-100 overflow-hidden">
          <div className="max-w-7xl mx-auto px-6 mb-16 text-center">
            <h2 className="text-3xl font-bold tracking-tight text-slate-900 mb-4">The Verification Pipeline</h2>
            <p className="text-slate-600">A deterministic, multi-layered approach to repository intelligence.</p>
          </div>

          <div className="relative max-w-7xl mx-auto px-6">
            <div className="absolute left-6 right-6 top-1/2 h-0.5 bg-gradient-to-r from-indigo-100 via-indigo-300 to-emerald-100 -translate-y-1/2 -z-10 hidden lg:block" />

            <motion.div
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: "-100px" }}
              variants={staggerContainer}
              className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-4 lg:gap-6"
            >
              {[
                { icon: Search, label: "Discovery" },
                { icon: FileCode2, label: "Parser & AST" },
                { icon: Layers, label: "Canonical UIR" },
                { icon: Network, label: "Knowledge Graph" },
                { icon: BrainCircuit, label: "Semantic Registry" },
                { icon: Search, label: "Evidence Retrieval" },
                { icon: Workflow, label: "Verification" },
                { icon: FileText, label: "Trust Report" }
              ].map((step, i) => (
                <motion.div key={i} variants={fadeUp} className="flex flex-col items-center">
                  <div className="w-14 h-14 rounded-2xl bg-white border border-slate-200 shadow-sm flex items-center justify-center mb-4 z-10 group hover:border-indigo-400 hover:shadow-md hover:shadow-indigo-500/10 transition-all">
                    <step.icon size={24} className="text-slate-700 group-hover:text-indigo-600 transition-colors" />
                  </div>
                  <span className="text-xs font-semibold text-slate-600 text-center uppercase tracking-wide">{step.label}</span>
                </motion.div>
              ))}
            </motion.div>
          </div>
        </section>

        {/* --- Why TrustRepo? --- */}
        <section id="features" className="py-24 max-w-7xl mx-auto px-6">
          <div className="mb-16">
            <h2 className="text-3xl font-bold tracking-tight text-slate-900 mb-4">Why TrustRepo?</h2>
            <p className="text-slate-600 max-w-2xl text-lg">A paradigm shift from heuristic static analysis to deterministic, evidence-based repository intelligence.</p>
          </div>

          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={staggerContainer}
            className="grid grid-cols-1 md:grid-cols-2 gap-8"
          >
            {[
              { icon: FileCode2, title: "Code First", desc: "TrustRepo analyzes the actual source code rather than relying only on documentation or human claims." },
              { icon: BrainCircuit, title: "Explainable AI", desc: "Every decision includes deterministic evidence and reasoning. No black-box hallucinations." },
              { icon: Network, title: "Knowledge Graph", desc: "Repository intelligence is represented as an interconnected graph mapping claims to implementations." },
              { icon: Activity, title: "Research Platform", desc: "Designed for software engineering research, providing rigorous metrics and confidence scores." }
            ].map((f, i) => (
              <motion.div key={i} variants={fadeUp} className="p-8 rounded-3xl bg-white border border-slate-200 shadow-sm hover:shadow-xl hover:shadow-indigo-500/5 hover:-translate-y-1 transition-all duration-300">
                <div className="w-12 h-12 rounded-xl bg-[#EEF2FF] flex items-center justify-center mb-6">
                  <f.icon size={24} className="text-[#4F46E5]" />
                </div>
                <h3 className="text-xl font-bold text-slate-900 mb-3">{f.title}</h3>
                <p className="text-slate-600 leading-relaxed">{f.desc}</p>
              </motion.div>
            ))}
          </motion.div>
        </section>

        {/* --- Core Features Bento Grid --- */}
        <section className="py-24 bg-slate-50 border-y border-slate-100">
          <div className="max-w-7xl mx-auto px-6">
            <div className="mb-16 text-center">
              <h2 className="text-3xl font-bold tracking-tight text-slate-900 mb-4">Core Capabilities</h2>
              <p className="text-slate-600">Enterprise-grade tools for deep codebase comprehension.</p>
            </div>

            <motion.div
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true }}
              variants={staggerContainer}
              className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4"
            >
              {[
                { label: "Repository Discovery", icon: Search },
                { label: "AST Analysis", icon: GitGraph },
                { label: "Canonical UIR", icon: Layers },
                { label: "Semantic Symbols", icon: Box },
                { label: "Technology Detection", icon: Cpu },
                { label: "Feature Extraction", icon: Zap },
                { label: "Capability Detection", icon: Activity },
                { label: "Architecture Detection", icon: Workflow },
                { label: "Knowledge Graph", icon: Network },
                { label: "Evidence Ranking", icon: BarChart4 },
                { label: "Reasoning Engine", icon: BrainCircuit },
                { label: "Verification Engine", icon: ShieldCheck }
              ].map((c, i) => (
                <motion.div key={i} variants={fadeUp} className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-4 hover:border-indigo-300 transition-colors">
                  <c.icon size={20} className="text-indigo-500 shrink-0" />
                  <span className="text-sm font-semibold text-slate-700">{c.label}</span>
                </motion.div>
              ))}
            </motion.div>
          </div>
        </section>

        {/* --- Explainable AI Example --- */}
        <section id="explainable" className="py-24 max-w-7xl mx-auto px-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
            <motion.div
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true }}
              variants={fadeUp}
            >
              <h2 className="text-3xl font-bold tracking-tight text-slate-900 mb-6">Explainable AI & Deterministic Evidence</h2>
              <p className="text-slate-600 text-lg mb-8 leading-relaxed">
                We don't trust LLMs to make blind decisions. TrustRepo uses multi-agent reasoning strictly bound by deterministic evidence retrieved from the AST-backed Knowledge Graph.
              </p>

              <ul className="space-y-4">
                {[
                  "Multi-source evidence fusion (Imports, AST, Dependencies)",
                  "Confidence Engine calculating rigorous probability",
                  "Graph-based contradiction detection",
                  "Line-level traceability for every claim"
                ].map((item, i) => (
                  <li key={i} className="flex items-start gap-3">
                    <CheckCircle2 size={20} className="text-[#10B981] shrink-0 mt-0.5" />
                    <span className="text-slate-700">{item}</span>
                  </li>
                ))}
              </ul>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="bg-white rounded-3xl border border-slate-200 shadow-2xl shadow-indigo-900/5 p-8 relative overflow-hidden"
            >
              <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-indigo-500 to-cyan-400" />

              <div className="mb-6 flex justify-between items-start">
                <div>
                  <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Claim Verification</p>
                  <p className="text-lg font-bold text-slate-900">"The application uses React for the frontend."</p>
                </div>
                <div className="bg-emerald-50 text-emerald-600 px-3 py-1 rounded-full text-xs font-bold border border-emerald-200">
                  VERIFIED
                </div>
              </div>

              <div className="space-y-4 mb-6">
                <div className="bg-slate-50 rounded-xl p-4 border border-slate-100">
                  <p className="text-xs font-bold text-slate-500 uppercase mb-2">Evidence Retrieved</p>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-sm text-slate-700"><CheckCircle2 size={14} className="text-emerald-500" /> <code>package.json</code> contains "react" dependency</div>
                    <div className="flex items-center gap-2 text-sm text-slate-700"><CheckCircle2 size={14} className="text-emerald-500" /> <code>App.tsx</code> utilizes React hooks</div>
                    <div className="flex items-center gap-2 text-sm text-slate-700"><CheckCircle2 size={14} className="text-emerald-500" /> <code>main.tsx</code> invokes ReactDOM.render</div>
                  </div>
                </div>
              </div>

              <div className="flex items-center justify-between border-t border-slate-100 pt-4">
                <div>
                  <p className="text-xs font-bold text-slate-500 uppercase mb-1">Confidence Score</p>
                  <p className="text-2xl font-black text-indigo-600">98.5%</p>
                </div>
                <div className="text-right">
                  <p className="text-xs font-bold text-slate-500 uppercase mb-1">Reasoning</p>
                  <p className="text-sm text-slate-700 max-w-[200px]">Three independent AST sources confirm the presence of React.</p>
                </div>
              </div>
            </motion.div>
          </div>
        </section>

        {/* --- Statistics --- */}
        <section className="py-24 bg-white">
          <div className="max-w-7xl mx-auto px-6">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              <AnimatedCounter value={12042} label="Repositories Analyzed" />
              <AnimatedCounter value={895000} label="Graph Nodes Generated" />
              <AnimatedCounter value={45} label="Technologies Supported" />
              <AnimatedCounter value={320500} label="Claims Verified" />
            </div>
          </div>
        </section>

        {/* --- Call to Action --- */}
        {/* <section className="py-32 relative overflow-hidden">
          <div className="absolute inset-0 bg-indigo-600 -z-20" />
          <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-10 -z-10 mix-blend-overlay" />

          <div className="max-w-4xl mx-auto px-6 text-center text-white relative z-10">
            <h2 className="text-4xl md:text-5xl font-extrabold tracking-tight mb-6">Ready to verify your repository?</h2>
            <p className="text-indigo-100 text-lg md:text-xl mb-10 max-w-2xl mx-auto">
              Generate deterministic, evidence-backed repository intelligence in seconds. Stop guessing, start verifying.
            </p>
            <button
              onClick={() => navigate('/dashboard')}
              className="px-10 py-5 bg-white text-indigo-600 hover:bg-slate-50 rounded-2xl font-bold shadow-2xl transition-all hover:scale-105 active:scale-95 text-lg inline-flex items-center gap-3"
            >
              Analyze Repository <ArrowRight size={20} />
            </button>
          </div>
        </section> */}
      </main>

      {/* --- Footer --- */}
      <footer className="bg-white border-t border-slate-200 py-12">
        <div className="max-w-7xl mx-auto px-6 flex flex-col items-center justify-center gap-4">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded bg-indigo-600 flex items-center justify-center">
              <ShieldCheck size={14} className="text-white" />
            </div>
            <span className="font-bold text-slate-900">TrustRepo</span>
          </div>
          <div className="text-sm text-slate-400">
            &copy; {new Date().getFullYear()} TrustRepo Research. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  );
}

function SparklesIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z" />
    </svg>
  );
}
