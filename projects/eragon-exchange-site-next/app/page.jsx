import ExchangeCard from '../components/ExchangeCard';
import { exchanges } from '../components/exchange-data';

export default function HomePage() {
  return (
    <>
      <div className="noise" aria-hidden="true" />

      <header className="hero">
        <div className="hero-inner">
          <p className="kicker">Elven AI Lab • Codex</p>
          <h1>
            Врата Бирж
            <br />
            для Всадника
          </h1>
          <p className="subtitle">
            Выбери гильдию, открой доступ и заходи в рынок через проверенные маршруты.
          </p>
          <a href="#gates" className="btn btn-primary">Открыть врата</a>
        </div>
      </header>

      <main>
        <section id="gates" className="section gates">
          {exchanges.map((item) => (
            <ExchangeCard key={item.id} item={item} />
          ))}
        </section>

        <section className="section oath">
          <h2>Клятва Всадника</h2>
          <p>Один вход — одна стратегия. Один риск — один лимит. Один план — без импровизации.</p>
        </section>
      </main>

      <footer>
        <p>🌿 Elven AI Lab</p>
      </footer>
    </>
  );
}
