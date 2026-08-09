import React, { useRef, useEffect } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { Search, RefreshCw, Scale, Gavel, Eye } from 'lucide-react';

gsap.registerPlugin(ScrollTrigger);

const NODES = [
  {
    num: '01', icon: Search, title: 'Look Up Standards',
    desc: "We find the real-world standards and best practices relevant to what you've pasted, so the review is grounded in actual rules, not guesswork.",
  },
  {
    num: '02', icon: RefreshCw, title: 'Double-Check Relevance',
    desc: "Before moving on, we make sure what we found actually applies -- if it doesn't, we look again until it does.",
  },
  {
    num: '03', icon: Scale, title: 'Inspect',
    desc: 'Three independent AI reviewers examine your content in parallel -- security, performance, and quality -- each backed by the standards found above.',
  },
  {
    num: '04', icon: Gavel, title: 'Chief Judge',
    desc: 'A senior AI reviewer weighs all three opinions into one final verdict, flags where they disagreed, and checks it against current best practices.',
  },
  {
    num: '05', icon: Eye, title: 'Reflect',
    desc: 'Before anything reaches you, the verdict is checked against itself one more time -- so what you see is validated, not just a raw first response.',
  },
];

export default function PipelineDetail() {
  const rowRef = useRef(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      const connectors = gsap.utils.toArray('.pipeline-connector', rowRef.current);
      connectors.forEach((c) => { c.style.transformOrigin = 'left center'; });
      gsap.fromTo(connectors, { scaleX: 0 }, {
        scaleX: 1, stagger: 0.15, ease: 'none',
        scrollTrigger: { trigger: rowRef.current, start: 'top 80%', end: 'bottom 65%', scrub: 1 },
      });
    }, rowRef);
    return () => ctx.revert();
  }, []);

  return (
    <div>
      <div style={{ textAlign: 'center', marginBottom: '48px' }}>
        <div className="label" style={{ marginBottom: '12px' }}>ARCHITECTURE</div>
        <h2 style={{
          fontFamily: 'Outfit, sans-serif',
          fontSize: 'clamp(28px, 4vw, 42px)',
          fontWeight: 700,
          letterSpacing: '-0.02em',
          lineHeight: 1.2,
          marginBottom: '14px',
        }}>
          How Judex AI Works
        </h2>
        <p style={{ fontSize: '14px', color: 'var(--text-body)', maxWidth: '560px', margin: '0 auto', lineHeight: 1.7 }}>
          Every single analysis goes through the same 5 steps, in order -- so results are consistent and explainable, not a black box.
        </p>
      </div>

      <div className="pipeline-row-5" ref={rowRef}>
        {NODES.map((step, i) => {
          const Icon = step.icon;
          return (
            <React.Fragment key={i}>
              <div className="pipeline-step">
                <div className="pipeline-num">{step.num}</div>
                <div style={{
                  width: '48px', height: '48px', borderRadius: '12px',
                  background: 'var(--accent-glow)', border: '1px solid var(--border-subtle)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                }}>
                  <Icon size={20} style={{ color: 'var(--text-heading)', opacity: 0.75 }} />
                </div>
                <div style={{ width: '170px' }}>
                  <div style={{ fontFamily: 'Outfit, sans-serif', fontSize: '14px', fontWeight: 600, color: 'var(--text-heading)', marginBottom: '6px' }}>
                    {step.title}
                  </div>
                  <div style={{ fontSize: '12px', color: 'var(--text-body)', lineHeight: 1.6 }}>
                    {step.desc}
                  </div>
                </div>
              </div>
              {i < NODES.length - 1 && <div className="pipeline-connector" />}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
}
