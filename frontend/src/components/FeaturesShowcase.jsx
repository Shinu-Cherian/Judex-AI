import React, { useRef } from 'react';
import { motion, useInView } from 'framer-motion';
import {
  Scale, Link2, ShieldCheck, Eye, Sparkles, History, Network, FolderArchive,
} from 'lucide-react';

const FEATURES = [
  {
    icon: Scale,
    title: 'Four AI Reviewers, One Verdict',
    desc: "Your code gets reviewed from four different angles at once -- security, performance, and quality -- then a senior judge weighs all three opinions into a single, weighted verdict. No single blind spot.",
    accent: '#818cf8',
  },
  {
    icon: ShieldCheck,
    title: 'Your Own Security Playbook',
    desc: "Set your company's security rules once -- Fintech, Healthcare, Startup, or Enterprise -- and every future review checks against them automatically, tailored to whatever you paste in.",
    accent: '#6bcf9f',
  },
  {
    icon: Sparkles,
    title: 'One-Click Fixes',
    desc: 'Generate a ready-to-review security patch instantly, with a clear before/after diff. Turn on Autopilot to fix an entire project at once, with a certificate proving exactly what changed.',
    accent: '#f0c060',
  },
  {
    icon: Link2,
    title: 'Backed by Real Standards',
    desc: "Every issue we flag is grounded in a real, named industry standard -- not just an AI's opinion. Click straight through to see exactly which rule was broken.",
    accent: '#818cf8',
  },
  {
    icon: Eye,
    title: 'See the Reasoning, Not Just a Verdict',
    desc: 'Every result is double-checked against itself before it reaches you -- so you get the full reasoning behind a decision, not just a pass/fail badge.',
    accent: '#c7d2fe',
  },
  {
    icon: History,
    title: 'It Remembers What Worked Before',
    desc: 'Every finding is matched against how similar issues were resolved in the past -- so recommendations come with real precedent, not generic advice.',
    accent: '#f59e6a',
  },
  {
    icon: Network,
    title: 'Know the Ripple Effect',
    desc: 'See exactly what else in your codebase is affected before you touch a single flagged function -- mapped visually, heat-ranked by risk.',
    accent: '#ff6b6b',
  },
  {
    icon: FolderArchive,
    title: 'Audit a Whole Project at Once',
    desc: 'Upload your entire project and get one repository-wide health score across every file and every language -- not just one snippet at a time.',
    accent: '#6bcf9f',
  },
];

function FeatureCard({ f, i }) {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: '-40px' });
  const Icon = f.icon;

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 24 }}
      animate={inView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.5, delay: (i % 4) * 0.06, ease: [0.22, 1, 0.36, 1] }}
      className="card feature-card"
      style={{
        padding: '26px',
        display: 'flex',
        flexDirection: 'column',
        gap: '14px',
      }}
    >
      <div style={{
        width: '40px', height: '40px', borderRadius: '10px',
        background: `${f.accent}18`, border: `1px solid ${f.accent}35`,
        display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
      }}>
        <Icon size={19} style={{ color: f.accent }} />
      </div>
      <div>
        <div style={{ fontFamily: 'Outfit, sans-serif', fontSize: '15px', fontWeight: 700, color: 'var(--text-heading)', marginBottom: '8px' }}>
          {f.title}
        </div>
        <div style={{ fontSize: '13px', color: 'var(--text-body)', lineHeight: 1.65 }}>
          {f.desc}
        </div>
      </div>
    </motion.div>
  );
}

export default function FeaturesShowcase() {
  return (
    <div>
      <div style={{ textAlign: 'center', marginBottom: '48px' }}>
        <div className="label" style={{ marginBottom: '12px' }}>FEATURES</div>
        <h2 style={{
          fontFamily: 'Outfit, sans-serif',
          fontSize: 'clamp(28px, 4vw, 42px)',
          fontWeight: 700,
          letterSpacing: '-0.02em',
          lineHeight: 1.2,
          marginBottom: '14px',
        }}>
          Everything a single AI can't do alone
        </h2>
        <p style={{ fontSize: '14px', color: 'var(--text-body)', maxWidth: '560px', margin: '0 auto', lineHeight: 1.7 }}>
          Judex AI isn't one prompt -- it's a complete review process, from first read to final fix.
        </p>
      </div>

      <div className="bento-grid">
        {FEATURES.map((f, i) => <FeatureCard key={f.title} f={f} i={i} />)}
      </div>
    </div>
  );
}
