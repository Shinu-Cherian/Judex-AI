import { useEffect } from 'react';
import Lenis from 'lenis';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

let lenisInstance = null;

// Module-level accessor so nav links / section-snap logic elsewhere can drive
// scroll position through Lenis instead of raw window.scrollTo (which Lenis
// would otherwise fight/override on its next animation frame).
export function getLenis() {
  return lenisInstance;
}

export function scrollToEl(target, opts = {}) {
  const lenis = getLenis();
  if (lenis) {
    lenis.scrollTo(target, { duration: 1.1, easing: (t) => 1 - Math.pow(1 - t, 3), ...opts });
  } else if (typeof target !== 'string' && target?.scrollIntoView) {
    target.scrollIntoView({ behavior: 'smooth' });
  } else if (typeof target === 'string') {
    document.querySelector(target)?.scrollIntoView({ behavior: 'smooth' });
  }
}

// Physics-based smooth scrolling (Lenis), kept in sync with GSAP's ScrollTrigger
// so scroll-scrubbed animations stay perfectly in sync with the smoothed scroll.
export default function useSmoothScroll() {
  useEffect(() => {
    const lenis = new Lenis({
      duration: 1.1,
      easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
      smoothWheel: true,
      autoRaf: true, // Lenis drives its own RAF loop; we just keep ScrollTrigger synced to it below
    });

    lenisInstance = lenis;
    lenis.on('scroll', ScrollTrigger.update);
    gsap.ticker.lagSmoothing(0);
    if (import.meta.env.DEV) window.__lenis = lenis; // dev-only debug hook, stripped from prod builds

    return () => {
      lenis.destroy();
      lenisInstance = null;
    };
  }, []);
}
