# Eragon Exchange Site (Next.js)

## Запуск
```bash
cd projects/eragon-exchange-site-next
npm install
npm run dev
```

Открой: `http://localhost:3000`

## Прод
```bash
npm run build
npm run start
```

## Deploy
- **Vercel:** проект готов, есть `vercel.json`
- **Netlify:** проект готов, есть `netlify.toml` + Next plugin

## Что внутри
- App Router (`app/`)
- Компонент карточки биржи
- Данные бирж в `components/exchange-data.js` (удобно менять ссылки)
