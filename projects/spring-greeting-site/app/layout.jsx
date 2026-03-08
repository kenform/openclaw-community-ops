import './globals.css';

export const metadata = {
  title: 'Весеннее поздравление',
  description: 'Нежный мини-лендинг поздравление с праздником весны'
};

export default function RootLayout({ children }) {
  return (
    <html lang="ru">
      <body>{children}</body>
    </html>
  );
}
