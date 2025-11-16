import type { Metadata } from 'next';
import '../src/index.css';

export const metadata: Metadata = {
  title: 'Grid Game',
  description: 'Grid Game Application',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

