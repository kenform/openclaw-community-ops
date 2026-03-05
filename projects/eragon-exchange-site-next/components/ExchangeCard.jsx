export default function ExchangeCard({ item }) {
  return (
    <article className={`gate reveal ${item.highlight ? 'highlighted' : ''}`}>
      <span className="rune" aria-hidden="true" />
      <span className="sigil" aria-hidden="true">{item.sigil}</span>
      <h3>{item.name}</h3>
      <p>{item.desc}</p>
      <a
        className="btn btn-ghost"
        href={item.href}
        target="_blank"
        rel="noopener noreferrer"
      >
        Войти в гильдию
      </a>
      {item.note ? <p className="note">{item.note}</p> : null}
    </article>
  );
}
