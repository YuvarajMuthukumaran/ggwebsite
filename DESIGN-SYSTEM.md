# v9 Warm Calm: design system and roadmap

## What changed in this zip
- `assets/css/calm.css` re-points the existing tokens (`--blue`, `--tint`, `--ink`...) to a warm palette, so every section recolours with no markup change. It also adds paper grain, drifting hero light, a shrinking glass nav and softer shadows.
- `assets/js/calm.js` adds the **Breathe & Ground** widget (4 in, 4 hold, 6 out; Esc closes; reduced-motion safe).
- Stack is unchanged (vanilla, no build). Roadmap below covers a Next.js port if you want one.

## Palette
| Role | Hex |
|---|---|
| Cream (page) | `#FBF6EC` |
| Sand (bands) | `#F4ECDD` / `#E9DDC7` |
| Sage (primary) / deep | `#5B7C65` / `#3C5A47` |
| Terracotta (accent) | `#C77B5D` |
| Blush | `#F3D9CC` |
| Soft gold | `#C9A96A` |
| Forest ink / muted | `#2A3A33` / `#6B7A70` |
| Footer forest | `#27362E` |

White text on `#5B7C65` is about 4.6:1 (AA for body text). Use terracotta for accents and large text only.

## Type
Fraunces (soft serif) for headlines, Inter for UI and body. For rounder UI, try Nunito or DM Sans for labels. Body 16-18px at 1.65 line height, headlines at -0.02em tracking.

## Tailwind recipes (for a React port)
```
warm card   : rounded-[28px] bg-[#FFFDF8]/80 backdrop-blur-md border border-[#E8DECD] shadow-[0_18px_40px_-18px_rgba(120,84,50,.22)]
glass nav   : bg-[#FBF6EC]/70 backdrop-blur-xl border border-white/70 rounded-full
organic blob: rounded-[58%_42%_47%_53%/52%_46%_54%_48%]
glow button : bg-gradient-to-b from-[#6A8D74] to-[#5B7C65] shadow-[inset_0_1px_0_rgba(255,255,255,.25),0_10px_24px_-12px_rgba(60,90,71,.6)]
```

## Framer Motion snippets
```tsx
// 1. Breathing orb (hero background)
import { motion } from "framer-motion";
export const BreathingOrb = () => (
  <motion.div aria-hidden
    className="pointer-events-none absolute left-1/2 top-1/3 h-[520px] w-[520px] -translate-x-1/2 rounded-full
               bg-[radial-gradient(circle_at_35%_30%,#FFF,#F5CDB8_45%,#CFE0CB)] blur-3xl"
    animate={{ scale: [1, 1.14, 1], opacity: [0.55, 0.8, 0.55] }}
    transition={{ duration: 10, ease: "easeInOut", repeat: Infinity }} />
);

// 2. Scroll-triggered spring card
export const Reveal = ({ children, i = 0 }) => (
  <motion.div
    initial={{ opacity: 0, y: 32, scale: 0.97 }}
    whileInView={{ opacity: 1, y: 0, scale: 1 }}
    viewport={{ once: true, margin: "-80px" }}
    transition={{ type: "spring", stiffness: 70, damping: 18, delay: i * 0.08 }}>
    {children}
  </motion.div>
);

// 3. Magnetic button
import { useRef } from "react";
import { motion, useMotionValue, useSpring } from "framer-motion";
export function Magnetic({ children }) {
  const ref = useRef<HTMLDivElement>(null);
  const x = useSpring(useMotionValue(0), { stiffness: 150, damping: 15, mass: 0.2 });
  const y = useSpring(useMotionValue(0), { stiffness: 150, damping: 15, mass: 0.2 });
  const move = (e: React.MouseEvent) => {
    const r = ref.current!.getBoundingClientRect();
    x.set((e.clientX - (r.left + r.width / 2)) * 0.25);
    y.set((e.clientY - (r.top + r.height / 2)) * 0.25);
  };
  return (
    <motion.div ref={ref} style={{ x, y }} onMouseMove={move}
      onMouseLeave={() => { x.set(0); y.set(0); }}
      whileTap={{ scale: 0.97 }} className="inline-block">
      {children}
    </motion.div>
  );
}
```
Wrap each in `useReducedMotion()` and skip the animation when it returns true.

## Roadmap
1. Review the warm palette (this zip) and tune the sage/terracotta balance.
2. Replace the placeholder reviews and press links (see README, v7).
3. Add a multi-step booking form (Who is it for, Concern, Preferred time, Confirm) with a progress bar.
4. Add a crisis-resources banner to the footer (verify local helpline numbers before publishing).
5. Optional: port to Next.js + Tailwind + Framer Motion + Lenis using the snippets above.
