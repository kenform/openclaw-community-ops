import './globals.css';

export const metadata = {
  title: 'Elven Exchange Codex',
  description: 'Fantasy-style exchange gateway with referral links.',
};

export default function RootLayout({ children }) {
  return (
    <html lang="ru">
      <body>{children}</body>
    </html>
  );
}
