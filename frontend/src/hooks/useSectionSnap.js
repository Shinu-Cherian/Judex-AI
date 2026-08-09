import { useEffect } from 'react';
import { getLenis } from './useSmoothScroll';

// Gentle "proximity" section snapping: only pulls the view to the nearest
// section boundary once scrolling has actually come to rest near one --
// never fights the user mid-scroll through a tall section (Features /
// How It Works are longer than one viewport on purpose).
export default function useSectionSnap(selector = '.snap-section') {
  useEffect(() => {
    const lenis = getLenis();
    if (!lenis) return;

    let idleTimer = null;
    let isSnapping = false;
    const EDGE_ZONE = 140; // px -- only snap if resting within this distance of a section edge

    const onScroll = ({ velocity }) => {
      if (isSnapping) return;
      clearTimeout(idleTimer);
      idleTimer = setTimeout(() => {
        if (Math.abs(velocity) > 0.03) return; // still moving, not settled yet

        const sections = Array.from(document.querySelectorAll(selector));
        if (!sections.length) return;

        const scrollY = window.scrollY;
        let nearestTop = null;
        let nearestDist = Infinity;
        for (const s of sections) {
          const dist = Math.abs(s.offsetTop - scrollY);
          if (dist < nearestDist) { nearestDist = dist; nearestTop = s; }
        }

        if (nearestTop && nearestDist > 4 && nearestDist < EDGE_ZONE) {
          isSnapping = true;
          lenis.scrollTo(nearestTop, {
            duration: 0.8,
            easing: (t) => 1 - Math.pow(1 - t, 3),
            onComplete: () => { isSnapping = false; },
          });
        }
      }, 140);
    };

    lenis.on('scroll', onScroll);
    return () => {
      lenis.off('scroll', onScroll);
      clearTimeout(idleTimer);
    };
  }, [selector]);
}
