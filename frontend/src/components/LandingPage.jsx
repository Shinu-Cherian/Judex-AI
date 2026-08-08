import React, { useRef, useEffect, useState } from 'react';
import { motion, useInView } from 'framer-motion';
import {
  ArrowRight, Cpu, ShieldCheck, Zap, Network, Layers,
  CheckCircle2, Loader2
} from 'lucide-react';

/* ─── Reusable scroll-reveal wrapper ─── */
function Reveal({ children, delay = 0, y = 28 }) {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: '-60px' });
  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y }}
      animate={inView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.55, ease: [0.22, 1, 0.36, 1], delay }}
    >
      {children}
    </motion.div>
  );
}

/* ─── Animated counter ─── */
function Counter({ to, suffix = '' }) {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true });
  const [val, setVal] = useState(0);

  useEffect(() => {
    if (!inView) return;
    let start = 0;
    const end = parseFloat(to);
    if (start === end) return;
    const duration = 900;
    const step = end / (duration / 16);
    const timer = setInterval(() => {
      start += step;
      if (start >= end) { setVal(end); clearInterval(timer); }
      else setVal(Math.floor(start));
    }, 16);
    return () => clearInterval(timer);
  }, [inView, to]);

  return <span ref={ref}>{val}{suffix}</span>;
}

/* ─── Infinite Looping Live Execution Card ─── */
function InfiniteExecutionCard() {
  const [activeStep, setActiveStep] = useState(0);

  const models = [
    { role: 'Security Inspector', model: 'Groq Llama 3.3 70B' },
    { role: 'Performance Inspector', model: 'Mistral Small' },
    { role: 'Code Quality Inspector', model: 'Gemini 2.0 Flash' },
    { role: 'Chief Judge Verdict Synthesizer', model: 'GPT-4o-mini' },
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveStep((prev) => (prev + 1) % 5);
    }, 1400);

    return () => clearInterval(interval);
  }, []);

  const progressPct = Math.min(100, Math.round((activeStep / 4) * 100));

  return (
    <div style={{
      background: 'var(--bg-card)',
      border: '1px solid var(--border-subtle)',
      borderRadius: '16px',
      padding: '28px',
      boxShadow: '0 20px 60px rgba(0,0,0,0.5)',
    }}>
      {/* Header of card */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: '11px', letterSpacing: '0.1em', color: 'var(--text-muted)' }}>
          LIVE 4-LLM EXECUTION
        </div>
        <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
          <div style={{ width: '7px', height: '7px', borderRadius: '50%', background: 'var(--risk-low)', boxShadow: '0 0 8px var(--risk-low)' }} />
          <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: '10px', color: 'var(--risk-low)' }}>
            {activeStep === 4 ? 'VERDICT READY' : 'RUNNING...'}
          </span>
        </div>
      </div>

      {/* Model rows */}
      {models.map((item, i) => {
        const isDone = activeStep > i;
        const isCurrent = activeStep === i;
        const isPending = activeStep < i;

        return (
          <motion.div
            key={i}
            animate={{
              scale: isCurrent ? 1.01 : 1,
              borderColor: isCurrent ? 'rgba(255,243,230,0.25)' : 'var(--border-subtle)',
              backgroundColor: isCurrent ? 'rgba(255,243,230,0.06)' : isDone ? 'rgba(107,207,159,0.03)' : 'var(--bg-input)',
            }}
            transition={{ duration: 0.25 }}
            style={{
              display: 'flex', alignItems: 'center', justifyContent: 'space-between',
              padding: '12px 16px', borderRadius: '10px', marginBottom: '8px',
              border: '1px solid var(--border-subtle)',
            }}
          >
            <div>
              <div style={{
                fontSize: '14px', fontWeight: 700,
                color: isPending ? 'var(--text-muted)' : '#ffffff',
                fontFamily: 'Outfit, sans-serif'
              }}>
                {item.role}
              </div>
              <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontFamily: 'JetBrains Mono, monospace', marginTop: '2px' }}>
                {item.model}
              </div>
            </div>

            <div>
              {isDone && (
                <span style={{
                  fontSize: '10px', fontFamily: 'JetBrains Mono, monospace', fontWeight: 600,
                  padding: '3px 10px', borderRadius: '999px',
                  background: 'rgba(107,207,159,0.1)', color: 'var(--risk-low)',
                  border: '1px solid rgba(107,207,159,0.3)', display: 'inline-flex', alignItems: 'center', gap: '4px'
                }}>
                  <CheckCircle2 size={10} /> DONE
                </span>
              )}
              {isCurrent && (
                <span style={{
                  fontSize: '10px', fontFamily: 'JetBrains Mono, monospace', fontWeight: 600,
                  padding: '3px 10px', borderRadius: '999px',
                  background: 'rgba(255,243,230,0.12)', color: 'var(--text-heading)',
                  border: '1px solid rgba(255,243,230,0.3)', display: 'inline-flex', alignItems: 'center', gap: '4px'
                }}>
                  <Loader2 size={10} className="spin-icon" /> RUNNING...
                </span>
              )}
              {isPending && (
                <span style={{
                  fontSize: '10px', fontFamily: 'JetBrains Mono, monospace', fontWeight: 500,
                  padding: '3px 10px', borderRadius: '999px',
                  color: 'var(--text-faint)', border: '1px solid var(--border-subtle)'
                }}>
                  QUEUED
                </span>
              )}
            </div>
          </motion.div>
        );
      })}

      {/* Dynamic progress bar */}
      <div style={{ marginTop: '20px', height: '3px', background: 'var(--border-subtle)', borderRadius: '999px', overflow: 'hidden' }}>
        <motion.div
          animate={{ width: `${progressPct}%` }}
          transition={{ duration: 0.35, ease: 'easeInOut' }}
          style={{ height: '100%', background: 'var(--text-heading)', borderRadius: '999px' }}
        />
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '10px' }}>
        <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: '10px', color: 'var(--text-muted)' }}>
          {activeStep === 4 ? '4 / 4 models complete — Consensus Verdict' : `${activeStep} / 4 models complete`}
        </span>
        <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: '10px', color: 'var(--text-heading)', fontWeight: 600 }}>
          {progressPct}%
        </span>
      </div>
    </div>
  );
}

const stats = [
  { number: 4,   suffix: '',   label: 'LLMs Orchestrated' },
  { number: 3,   suffix: '',   label: 'Inspector Nodes' },
  { number: 5,   suffix: '',   label: 'Reflection Checks' },
  { number: 100, suffix: '%',  label: 'Automated Audit' },
];

const steps = [
  {
    num: '01',
    title: 'Upload or Paste',
    desc: 'Drop a file or paste code, specs, API docs, or logs into the input area.',
    icon: Layers,
  },
  {
    num: '02',
    title: 'Auto-Detection',
    desc: 'Judex AI detects content type and extracts individual functions, sections, or entries.',
    icon: Cpu,
  },
  {
    num: '03',
    title: '3 Inspector Nodes',
    desc: 'Groq Llama 3.3, Mistral Small, and Gemini 2.0 Flash run independently.',
    icon: Network,
  },
  {
    num: '04',
    title: 'Chief Judge Verdict',
    desc: 'GPT-4o-mini Synthesizes all findings into a weighted verdict with LangGraph reflection.',
    icon: ShieldCheck,
  },
];

const comparisonRows = [
  ['One model, one blind perspective', 'Cross-examined by 3 independent inspector nodes'],
  ['Hallucination-prone, no cross-check', 'Automated 5-point LangGraph reflection loop'],
  ['No awareness of what it missed', 'Explicit gap detection — missing items listed'],
  ['Opaque black-box verdict', 'Full per-model audit trail with confidence scores'],
  ['No dependency awareness', 'Ripple dependency graph maps all affected modules'],
];

export default function LandingPage({ onLaunchAnalyzer }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '100px', paddingTop: '0' }}>

      {/* ─────────── HERO — Full-width split layout ─────────── */}
      <section style={{ position: 'relative', padding: '80px 0 60px', overflow: 'hidden' }}>
        {/* Animated background */}
        <div className="hero-bg">
          <div className="hero-grid" />
        </div>

        {/* Two-column split: left text, right visual */}
        <div style={{
          position: 'relative', zIndex: 1,
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: '60px',
          alignItems: 'center',
        }}>

          {/* ── LEFT COLUMN ── */}
          <motion.div
            initial={{ opacity: 0, x: -32 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
          >
            {/* Option 3 (Refined): Warm Monochromatic Command Chip */}
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1, duration: 0.4 }}
              style={{
                display: 'inline-flex', alignItems: 'center', gap: '8px',
                background: 'rgba(255, 243, 230, 0.03)',
                border: '1px solid rgba(255, 243, 230, 0.12)',
                boxShadow: 'inset 0 1px 0 rgba(255, 255, 255, 0.05)',
                borderRadius: '4px',
                padding: '6px 14px',
                marginBottom: '28px',
                fontFamily: 'JetBrains Mono, monospace',
                fontSize: '11px',
                fontWeight: 600,
                letterSpacing: '0.08em',
              }}
            >
              <span style={{ color: 'var(--text-faint)', fontWeight: 600 }}>[</span>
              <span style={{ color: 'var(--text-heading)', fontWeight: 600 }}>4-LLM MULTI-MODEL CONSENSUS ENGINE</span>
              <span style={{ color: 'var(--text-faint)', fontWeight: 600 }}>]</span>
            </motion.div>

            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.15, duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
              style={{
                fontFamily: 'Outfit, sans-serif',
                fontSize: 'clamp(38px, 4.5vw, 62px)',
                fontWeight: 800,
                color: 'var(--text-heading)',
                lineHeight: 1.08,
                letterSpacing: '-0.03em',
                marginBottom: '20px',
              }}
            >
              Every angle.<br />One verdict.
            </motion.h1>

            <motion.p
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.28, duration: 0.6 }}
              style={{
                fontSize: '16px', color: 'var(--text-body)', lineHeight: 1.75,
                marginBottom: '36px', maxWidth: '460px',
              }}
            >
              Autonomous evaluation panel that detects hidden security vulnerabilities, performance bottlenecks, and compliance risks across code, APIs, infrastructure logs, and system specifications.
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.38, duration: 0.5 }}
            >
              <button onClick={onLaunchAnalyzer} className="btn-primary" style={{ height: '50px', padding: '0 32px', fontSize: '15px' }}>
                Launch Analyzer <ArrowRight size={16} />
              </button>
            </motion.div>
          </motion.div>

          {/* ── RIGHT COLUMN — Visual Live LLM panel card ── */}
          <motion.div
            initial={{ opacity: 0, x: 32 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1], delay: 0.15 }}
          >
            <InfiniteExecutionCard />
          </motion.div>

        </div>
      </section>

      {/* ─────────── STATS ROW ─────────── */}
      <Reveal delay={0}>
        <div className="stats-row">
          {stats.map((s, i) => (
            <div className="stat-cell" key={i}>
              <div className="stat-number">
                <Counter to={s.number} suffix={s.suffix} />
              </div>
              <div className="stat-label">{s.label}</div>
            </div>
          ))}
        </div>
      </Reveal>

      {/* ─────────── HOW IT WORKS — PIPELINE ─────────── */}
      <section>
        <Reveal>
          <div style={{ textAlign: 'center', marginBottom: '56px' }}>
            <div className="label" style={{ marginBottom: '12px' }}>ARCHITECTURE</div>
            <h2 style={{
              fontFamily: 'Outfit, sans-serif',
              fontSize: 'clamp(28px, 4vw, 40px)',
              fontWeight: 700,
              letterSpacing: '-0.02em',
              lineHeight: 1.2,
            }}>
              How Judex AI Works
            </h2>
          </div>
        </Reveal>

        <div className="pipeline-row">
          {steps.map((step, i) => {
            const Icon = step.icon;
            return (
              <React.Fragment key={i}>
                <Reveal delay={i * 0.08}>
                  <div className="pipeline-step">
                    <div className="pipeline-num">{step.num}</div>
                    <div
                      style={{
                        width: '48px', height: '48px', borderRadius: '12px',
                        background: 'var(--accent-glow)', border: '1px solid var(--border-subtle)',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                      }}
                    >
                      <Icon size={22} style={{ color: 'var(--text-heading)', opacity: 0.7 }} />
                    </div>
                    <div>
                      <div style={{ fontFamily: 'Outfit, sans-serif', fontSize: '15px', fontWeight: 600, color: 'var(--text-heading)', marginBottom: '6px' }}>
                        {step.title}
                      </div>
                      <div style={{ fontSize: '13px', color: 'var(--text-body)', lineHeight: 1.6, maxWidth: '180px' }}>
                        {step.desc}
                      </div>
                    </div>
                  </div>
                </Reveal>
                {i < steps.length - 1 && (
                  <div className="pipeline-connector" />
                )}
              </React.Fragment>
            );
          })}
        </div>
      </section>

      {/* ─────────── ENTERPRISE RELIABILITY — COMPARISON ─────────── */}
      <section>
        <Reveal>
          <div style={{ textAlign: 'center', marginBottom: '48px' }}>
            <div className="label" style={{ marginBottom: '12px' }}>ENTERPRISE RELIABILITY</div>
            <h2 style={{
              fontFamily: 'Outfit, sans-serif',
              fontSize: 'clamp(26px, 4vw, 38px)',
              fontWeight: 700,
              letterSpacing: '-0.02em',
              lineHeight: 1.25,
            }}>
              Why single-model AI<br />fails at complex engineering
            </h2>
          </div>
        </Reveal>

        <Reveal delay={0.1}>
          <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
            <table className="comparison-table">
              <thead>
                <tr>
                  <th style={{ width: '50%' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <Zap size={14} />
                      Single LLM Prompt
                    </div>
                  </th>
                  <th style={{ width: '50%' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <CheckCircle2 size={14} />
                      Judex AI — 4-Model Panel
                    </div>
                  </th>
                </tr>
              </thead>
              <tbody>
                {comparisonRows.map(([bad, good], i) => (
                  <tr key={i}>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
                        <span style={{ color: 'var(--risk-critical)', opacity: 0.5, marginTop: '1px', flexShrink: 0 }}>—</span>
                        {bad}
                      </div>
                    </td>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
                        <CheckCircle2 size={14} style={{ color: 'var(--risk-low)', marginTop: '2px', flexShrink: 0 }} />
                        <span><strong>{good}</strong></span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Reveal>
      </section>

      {/* ─────────── CTA ─────────── */}
      <Reveal>
        <div className="cta-glow-wrap">
          <div
            className="card"
            style={{
              padding: '64px 40px',
              textAlign: 'center',
              background: 'var(--bg-card-raised)',
              animation: 'glow-pulse 4s ease-in-out infinite',
              borderColor: 'rgba(255,243,230,0.12)',
            }}
          >
            <div className="label" style={{ marginBottom: '16px' }}>GET STARTED</div>
            <h2 style={{
              fontFamily: 'Outfit, sans-serif',
              fontSize: 'clamp(26px, 4vw, 40px)',
              fontWeight: 700,
              letterSpacing: '-0.02em',
              marginBottom: '16px',
            }}>
              Ready to run the panel?
            </h2>
            <p style={{ fontSize: '15px', color: 'var(--text-body)', marginBottom: '36px', maxWidth: '480px', margin: '0 auto 36px' }}>
              Paste your code, specs, API contract, or security logs and watch four AI models tear it apart.
            </p>
            <button onClick={onLaunchAnalyzer} className="btn-primary" style={{ height: '52px', padding: '0 40px', fontSize: '15px' }}>
              Open Judex AI Analyzer <ArrowRight size={16} />
            </button>
          </div>
        </div>
      </Reveal>

      {/* small footer gap */}
      <div style={{ height: '20px' }} />
    </div>
  );
}
