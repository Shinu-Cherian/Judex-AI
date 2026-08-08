import React, { useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle2, Loader2, Clock, Gavel, ShieldCheck, Zap, Code2 } from 'lucide-react';

const MODELS = [
  {
    title: 'Security Inspector',
    sub: 'Groq Llama 3.3 70B',
    task: 'Scanning for injection flaws, secrets, auth issues & CVE patterns...',
    Icon: ShieldCheck,
    color: 'var(--risk-critical)',
    colorBg: 'rgba(255,107,107,0.08)',
    colorBorder: 'rgba(255,107,107,0.25)',
  },
  {
    title: 'Performance Inspector',
    sub: 'Mistral Small',
    task: 'Evaluating complexity, blocking calls, memory leaks & bottlenecks...',
    Icon: Zap,
    color: 'var(--risk-medium)',
    colorBg: 'rgba(240,192,96,0.08)',
    colorBorder: 'rgba(240,192,96,0.25)',
  },
  {
    title: 'Code Quality Inspector',
    sub: 'Gemini 2.0 Flash',
    task: 'Checking type safety, docs, error handling & language best practices...',
    Icon: Code2,
    color: '#6bcf9f',
    colorBg: 'rgba(107,207,159,0.08)',
    colorBorder: 'rgba(107,207,159,0.25)',
  },
  {
    title: 'Chief Judge Verdict Synthesizer',
    sub: 'GPT-4o-mini',
    task: 'Cross-examining 3 inspector reports, calculating weighted consensus...',
    Icon: Gavel,
    color: '#a080c0',
    colorBg: 'rgba(160,128,192,0.08)',
    colorBorder: 'rgba(160,128,192,0.25)',
  },
];

// Rotating thinking phrases per model to show while waiting
const THINKING_PHRASES = {
  0: ['Scanning SQL patterns...', 'Checking auth flows...', 'Detecting hardcoded secrets...', 'Reviewing access controls...'],
  1: ['Measuring complexity...', 'Tracing I/O blocks...', 'Checking memory usage...', 'Evaluating loop bounds...'],
  2: ['Reading type hints...', 'Checking docstrings...', 'Reviewing error handling...', 'Verifying naming conventions...'],
  3: ['Reading 3 inspector reports...', 'Weighing confidence scores...', 'Synthesizing consensus...', 'Generating final verdict...'],
};

export default function ExecutionLoader({ onComplete }) {
  // activeStep: -1 = loading started, 0-3 = current running model, 4 = all done
  const [activeStep, setActiveStep] = useState(0);
  const [thinkingIdx, setThinkingIdx] = useState(0);
  const [elapsedSecs, setElapsedSecs] = useState(0);
  const completedRef = useRef(false);
  const apiFinishedRef = useRef(false);

  // Advance thinking phrase every 1.8s
  useEffect(() => {
    const t = setInterval(() => {
      setThinkingIdx(i => i + 1);
    }, 1800);
    return () => clearInterval(t);
  }, []);

  // Elapsed time counter
  useEffect(() => {
    const t = setInterval(() => setElapsedSecs(s => s + 1), 1000);
    return () => clearInterval(t);
  }, []);

  // 10-second total multi-agent inspection pacing (2.5s per inspector node)
  useEffect(() => {
    if (activeStep < 3) {
      const t = setTimeout(() => {
        setActiveStep(s => s + 1);
      }, 2500);
      return () => clearTimeout(t);
    }
  }, [activeStep]);

  // Wait for both: 10s animation completed AND backend API finished
  useEffect(() => {
    window.__judexApiDone = () => {
      apiFinishedRef.current = true;
    };
    return () => { delete window.__judexApiDone; };
  }, []);

  useEffect(() => {
    if (activeStep >= 3 && !completedRef.current) {
      const checkDone = setInterval(() => {
        if (apiFinishedRef.current && !completedRef.current) {
          completedRef.current = true;
          clearInterval(checkDone);
          setTimeout(() => { if (onComplete) onComplete(); }, 800);
        }
      }, 300);
      return () => clearInterval(checkDone);
    }
  }, [activeStep, onComplete]);

  const progressPct = Math.round(((activeStep + 1) / 4) * 100);

  return (
    <motion.div
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -14 }}
      transition={{ duration: 0.35 }}
      className="card"
      style={{ padding: '28px', marginBottom: '24px' }}
    >
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
        <div style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: '11px', letterSpacing: '0.1em', color: 'var(--text-muted)' }}>
          JUDEX AI — LIVE 4-LLM EXECUTION
        </div>
        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: '10px', color: 'var(--text-faint)', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <Clock size={10} /> {elapsedSecs}s
          </span>
          <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: '11px', color: 'var(--text-heading)', fontWeight: 600 }}>
            {progressPct}%
          </span>
        </div>
      </div>

      <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '20px', fontFamily: 'JetBrains Mono, monospace' }}>
        Running 4 AI models across independent inspection domains. Results appear when all complete.
      </div>

      {/* Progress bar */}
      <div style={{ width: '100%', height: '3px', background: 'var(--border-subtle)', borderRadius: '999px', overflow: 'hidden', marginBottom: '24px' }}>
        <motion.div
          animate={{ width: `${progressPct}%` }}
          transition={{ duration: 0.5, ease: 'easeOut' }}
          style={{ height: '100%', background: 'var(--text-heading)', borderRadius: '999px' }}
        />
      </div>

      {/* Model rows */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {MODELS.map((model, idx) => {
          const isDone = activeStep > idx;
          const isCurrent = activeStep === idx;
          const isPending = activeStep < idx;
          const Icon = model.Icon;
          const phrase = THINKING_PHRASES[idx][thinkingIdx % THINKING_PHRASES[idx].length];

          return (
            <motion.div
              key={idx}
              animate={{
                borderColor: isCurrent ? model.colorBorder : isDone ? 'rgba(107,207,159,0.2)' : 'var(--border-subtle)',
                backgroundColor: isCurrent ? model.colorBg : isDone ? 'rgba(107,207,159,0.03)' : 'transparent',
              }}
              transition={{ duration: 0.25 }}
              style={{
                display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                padding: '14px 18px', borderRadius: '10px',
                border: '1px solid var(--border-subtle)',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: '14px' }}>
                {/* Icon / status */}
                <div style={{ marginTop: '2px', flexShrink: 0 }}>
                  {isDone ? (
                    <CheckCircle2 size={18} style={{ color: '#6bcf9f' }} />
                  ) : isCurrent ? (
                    <Loader2 size={18} style={{ color: model.color }} className="spin-icon" />
                  ) : (
                    <Icon size={18} style={{ color: 'var(--text-faint)' }} />
                  )}
                </div>

                <div>
                  {/* Top Line: Primary Heading (Security Inspector, Performance Inspector, etc.) */}
                  <div style={{
                    fontSize: '15px', fontWeight: 700, fontFamily: 'Outfit, sans-serif',
                    color: isPending ? 'var(--text-faint)' : '#ffffff',
                    marginBottom: '3px', letterSpacing: '-0.01em'
                  }}>
                    {model.title}
                  </div>

                  {/* Bottom Line: Subheading (Groq Llama 3.3 70B, Mistral Small, etc.) */}
                  <div style={{
                    fontSize: '12px', fontFamily: 'JetBrains Mono, monospace',
                    color: isPending ? 'var(--text-faint)' : isCurrent ? model.color : '#6bcf9f',
                    marginBottom: '6px', opacity: isPending ? 0.6 : 0.95, fontWeight: 600
                  }}>
                    {model.sub}
                  </div>

                  <AnimatePresence mode="wait">
                    <motion.div
                      key={isCurrent ? phrase : isDone ? 'done' : 'pending'}
                      initial={{ opacity: 0, y: 4 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -4 }}
                      transition={{ duration: 0.2 }}
                      style={{ fontSize: '11px', fontFamily: 'JetBrains Mono, monospace', color: isPending ? 'var(--text-faint)' : 'var(--text-muted)' }}
                    >
                      {isDone ? '✓ Analysis complete' : isCurrent ? phrase : model.task}
                    </motion.div>
                  </AnimatePresence>
                </div>
              </div>

              {/* Status badge */}
              <div style={{ flexShrink: 0 }}>
                {isDone && (
                  <span style={{
                    fontSize: '10px', fontFamily: 'JetBrains Mono, monospace', fontWeight: 600,
                    padding: '3px 10px', borderRadius: '999px',
                    background: 'rgba(107,207,159,0.12)', color: '#6bcf9f',
                    border: '1px solid rgba(107,207,159,0.3)',
                  }}>
                    DONE
                  </span>
                )}
                {isCurrent && (
                  <span style={{
                    fontSize: '10px', fontFamily: 'JetBrains Mono, monospace', fontWeight: 600,
                    padding: '3px 10px', borderRadius: '999px',
                    background: model.colorBg, color: model.color,
                    border: `1px solid ${model.colorBorder}`,
                  }}>
                    RUNNING...
                  </span>
                )}
                {isPending && (
                  <span style={{
                    fontSize: '10px', fontFamily: 'JetBrains Mono, monospace',
                    color: 'var(--text-faint)', padding: '3px 10px', borderRadius: '999px',
                    border: '1px solid var(--border-subtle)',
                  }}>
                    QUEUED
                  </span>
                )}
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Bottom status */}
      <div style={{
        marginTop: '20px', padding: '10px 14px',
        background: 'var(--bg-input)', borderRadius: '8px',
        display: 'flex', alignItems: 'center', justifyContent: 'space-between'
      }}>
        <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: '10px', color: 'var(--text-muted)' }}>
          {activeStep < 3
            ? `${activeStep + 1} of 4 models running — results shown when all complete`
            : 'Chief Judge synthesizing final verdict...'}
        </span>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <div style={{ width: '6px', height: '6px', borderRadius: '50%', background: 'var(--risk-low)', animation: 'pulse-dot 1.5s ease-in-out infinite' }} />
          <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: '10px', color: 'var(--risk-low)' }}>LIVE</span>
        </div>
      </div>
    </motion.div>
  );
}
