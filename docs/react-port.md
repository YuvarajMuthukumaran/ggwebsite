# If you move to Next.js: the three requested Framer Motion pieces

Stack: Next.js 14 (app router), Tailwind, `framer-motion`, `lenis`, `lucide-react`, Radix/shadcn for Tabs, Accordion, Dialog.

Tokens (tailwind.config): cream `#F6EFE4`, oat `#EFE4D2`, sage `#3F6B57`, forest `#25352E`, ink `#26332D`, clay `#A85A40`, blush `#EFD2C3`, gold `#C9A24B`.
Warm shadow: `shadow-[0_22px_50px_-24px_rgba(120,80,50,0.30)]`. Glass: `bg-[#FFFAF2]/70 backdrop-blur-xl backdrop-saturate-125 border border-[#E6DBC9] rounded-full`.
Organic radius: `rounded-[2rem_2.5rem_2rem_3rem]`. Fonts: Fraunces (display), Figtree (UI).

## 1. Breathing orb
```tsx
"use client";
import { motion, useReducedMotion } from "framer-motion";
export function BreathingOrb() {
  const still = useReducedMotion();
  return (
    <motion.div aria-hidden
      className="pointer-events-none absolute right-[6%] top-[6%] aspect-square w-[min(560px,60vw)] rounded-full
                 bg-[radial-gradient(closest-side,rgba(239,210,195,.95),rgba(201,162,75,.22)_58%,transparent_74%)]"
      animate={still ? undefined : { scale: [0.9, 1.08, 0.9], opacity: [0.7, 1, 0.7] }}
      transition={{ duration: 10, repeat: Infinity, ease: [0.45, 0, 0.25, 1] }} />
  );
}
```
## 2. Scroll-triggered card entrance
```tsx
"use client";
import { motion } from "framer-motion";
export function RevealCard({ i = 0, children }: { i?: number; children: React.ReactNode }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 28, scale: 0.97 }}
      whileInView={{ opacity: 1, y: 0, scale: 1 }}
      viewport={{ once: true, margin: "-80px" }}
      transition={{ type: "spring", stiffness: 70, damping: 18, mass: 0.9, delay: i * 0.08 }}
      className="rounded-[2rem] border border-[#E6DBC9] bg-[#FFFBF5]/80 p-6 shadow-[0_22px_50px_-24px_rgba(120,80,50,0.30)]">
      {children}
    </motion.div>
  );
}
```
## 3. Magnetic button
```tsx
"use client";
import { useRef } from "react";
import { motion, useMotionValue, useSpring } from "framer-motion";
export function MagneticButton({ children }: { children: React.ReactNode }) {
  const ref = useRef<HTMLButtonElement>(null);
  const x = useSpring(useMotionValue(0), { stiffness: 150, damping: 15, mass: 0.2 });
  const y = useSpring(useMotionValue(0), { stiffness: 150, damping: 15, mass: 0.2 });
  const move = (e: React.PointerEvent) => {
    const r = ref.current!.getBoundingClientRect();
    x.set((e.clientX - (r.left + r.width / 2)) * 0.25);
    y.set((e.clientY - (r.top + r.height / 2)) * 0.25);
  };
  return (
    <motion.button ref={ref} style={{ x, y }} onPointerMove={move}
      onPointerLeave={() => { x.set(0); y.set(0); }} whileTap={{ scale: 0.97 }}
      className="rounded-full bg-[#3F6B57] px-6 py-3 font-medium text-white shadow-[0_16px_30px_-12px_rgba(63,107,87,.55)]">
      {children}
    </motion.button>
  );
}
```
Lenis: `new Lenis({ lerp: 0.08 })` in a client provider. The current static site deliberately keeps native scrolling (see README v6), so add Lenis only if you accept that trade-off, and disable it under `prefers-reduced-motion`.
