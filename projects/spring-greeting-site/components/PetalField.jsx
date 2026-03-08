'use client';

import { useMemo } from 'react';

const PETALS_COUNT = 12;

export default function PetalField() {
  const petals = useMemo(
    () =>
      Array.from({ length: PETALS_COUNT }, (_, i) => ({
        id: i,
        left: `${(i * 100) / PETALS_COUNT + Math.random() * 6}%`,
        size: 8 + Math.random() * 12,
        delay: `${Math.random() * 8}s`,
        duration: `${14 + Math.random() * 12}s`,
        drift: `${-24 + Math.random() * 48}px`,
        opacity: 0.2 + Math.random() * 0.4
      })),
    []
  );

  return (
    <div className="pointer-events-none fixed inset-0 overflow-hidden" aria-hidden="true">
      {petals.map((petal) => (
        <span
          key={petal.id}
          className="petal"
          style={{
            left: petal.left,
            width: petal.size,
            height: petal.size * 0.72,
            animationDelay: petal.delay,
            animationDuration: petal.duration,
            opacity: petal.opacity,
            ['--drift']: petal.drift
          }}
        />
      ))}
    </div>
  );
}
