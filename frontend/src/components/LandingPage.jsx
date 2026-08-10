import React, { useRef, useEffect, useState } from 'react';
import { motion, useInView } from 'framer-motion';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { ArrowRight, CheckCircle2, Loader2 } from 'lucide-react';
import MagneticButton from './MagneticButton';
import FeaturesShowcase from './FeaturesShowcase';
import PipelineDetail from './PipelineDetail';
import ComparisonSplit from './ComparisonSplit';
import useSectionSnap from '../hooks/useSectionSnap';

gsap.registerPlugin(ScrollTrigger);

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
    { role: 'Chief Judge Verdict Synthesizer', model: 'DeepSeek-R1 Distill 70B' },
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

export default function LandingPage({ onLaunchAnalyzer }) {
  const heroRef = useRef(null);
  useSectionSnap('.snap-section');

  useEffect(() => {
    const ctx = gsap.context(() => {
      // Hero drifts up and fades slightly as the user scrolls past it -- cinematic depth.
      gsap.to(heroRef.current, {
        yPercent: -12,
        opacity: 0.5,
        ease: 'none',
        scrollTrigger: { trigger: heroRef.current, start: 'top top', end: 'bottom top', scrub: true },
      });
    });
    return () => ctx.revert();
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', paddingTop: '0' }}>

      {/* ═══════════════ SECTION: HOME ═══════════════ */}
      <section id="home" className="snap-section" style={{ paddingTop: '20px' }}>

        {/* ── HERO — Full-width split layout ── */}
        <div ref={heroRef} style={{ position: 'relative', padding: '60px 0 60px', overflow: 'hidden' }}>
          <div className="hero-bg">
            <div className="hero-grid" />
          </div>

          <div className="hero-two-col" style={{
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
                <MagneticButton onClick={onLaunchAnalyzer} className="btn-primary" style={{ height: '50px', padding: '0 32px', fontSize: '15px' }}>
                  Launch Analyzer <ArrowRight size={16} />
                </MagneticButton>
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
        </div>

        {/* ── STATS ROW ── */}
        <Reveal delay={0}>
          <div className="stats-row" style={{ marginTop: '60px' }}>
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
      </section>

      {/* ═══════════════ SECTION: FEATURES ═══════════════ */}
      <section id="features" className="snap-section">
        <Reveal>
          <FeaturesShowcase />
        </Reveal>
      </section>

      {/* ═══════════════ SECTION: HOW IT WORKS ═══════════════ */}
      <section id="how-it-works" className="snap-section">
        <Reveal>
          <PipelineDetail />
        </Reveal>

        {/* ── ENTERPRISE RELIABILITY — COMPARISON ── */}
        <div style={{ marginTop: '80px' }}>
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

          <ComparisonSplit />
        </div>

        {/* ── CTA ── */}
        <Reveal>
          <div className="cta-glow-wrap" style={{ marginTop: '80px' }}>
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
              <MagneticButton onClick={onLaunchAnalyzer} className="btn-primary" style={{ height: '52px', padding: '0 40px', fontSize: '15px' }}>
                Open Judex AI Analyzer <ArrowRight size={16} />
              </MagneticButton>
            </div>
          </div>
        </Reveal>
      </section>

      {/* small footer gap */}
      <div style={{ height: '20px' }} />
    </div>
  );
}
