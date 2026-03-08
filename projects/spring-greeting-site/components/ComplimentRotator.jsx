'use client';

import { useEffect, useMemo, useState } from 'react';

export default function ComplimentRotator({ compliments, rotateMinutes = 5 }) {
  const safeCompliments = useMemo(
    () => (Array.isArray(compliments) && compliments.length ? compliments : ['Светлой весны и тёплых дней.']),
    [compliments]
  );

  const [index, setIndex] = useState(() => Math.floor(Math.random() * safeCompliments.length));
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    const duration = Math.max(1, rotateMinutes) * 60 * 1000;

    const timer = setInterval(() => {
      setVisible(false);

      setTimeout(() => {
        setIndex((prev) => {
          if (safeCompliments.length === 1) return prev;

          let next = prev;
          while (next === prev) {
            next = Math.floor(Math.random() * safeCompliments.length);
          }
          return next;
        });
        setVisible(true);
      }, 420);
    }, duration);

    return () => clearInterval(timer);
  }, [rotateMinutes, safeCompliments]);

  return (
    <p
      className={`min-h-[72px] text-lg leading-relaxed text-[#6b5575] transition-opacity duration-500 ${
        visible ? 'opacity-100' : 'opacity-0'
      }`}
    >
      {safeCompliments[index]}
    </p>
  );
}
