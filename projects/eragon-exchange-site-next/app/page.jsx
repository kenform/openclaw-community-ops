'use client';

import { useEffect } from 'react';
import ExchangeCard from '../components/ExchangeCard';
import { exchanges } from '../components/exchange-data';

export default function HomePage() {
  useEffect(() => {
    const onMove = (e) => {
      const x = (e.clientX / window.innerWidth - 0.5) * 14;
      const y = (e.clientY / window.innerHeight - 0.5) * 10;
      document.documentElement.style.setProperty('--mx', `${x}px`);
      document.documentElement.style.setProperty('--my', `${y}px`);
    };

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) entry.target.classList.add('in');
        });
      },
      { threshold: 0.14 }
    );

    document.querySelectorAll('.reveal').forEach((el) => observer.observe(el));
    window.addEventListener('mousemove', onMove, { passive: true });

    return () => {
      window.removeEventListener('mousemove', onMove);
      observer.disconnect();
    };
  }, []);
  return (
    <>
      <div className="noise" aria-hidden="true" />
      <div className="orb orb-a" aria-hidden="true" />
      <div className="orb orb-b" aria-hidden="true" />
      <div className="orb orb-c" aria-hidden="true" />
      <div className="sparkles" aria-hidden="true" />

      <header className="hero reveal">
        <div className="dragon-wrap" aria-hidden="true">
          <div className="dragon dragon-body" />
          <div className="dragon dragon-wing wing-left" />
          <div className="dragon dragon-wing wing-right" />
          <div className="dragon dragon-head" />
          <div className="dragon-eye" />
        </div>

        <div className="hero-inner">
          <p className="kicker">Elven AI Lab • Codex</p>
          <h1>
            Сапфировые Врата
            <br />
            для Всадника
          </h1>
          <p className="subtitle">
            Выбери гильдию, открой доступ и заходи в рынок через проверенные маршруты.
            Сила дракона — в дисциплине и ясном плане.
          </p>
          <a href="#gates" className="btn btn-primary">Открыть врата</a>
        </div>
      </header>

      <main>
        <section id="gates" className="section gates reveal">
          {exchanges.map((item) => (
            <ExchangeCard key={item.id} item={item} />
          ))}
        </section>

        <section className="section oath reveal">
          <h2>Клятва Всадника</h2>
          <p>Один вход — одна стратегия. Один риск — один лимит. Один план — без импровизации.</p>
        </section>
      </main>

      <footer className="reveal">
        <p>🌿 Elven AI Lab</p>
      </footer>
    </>
  );
}
