import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'GovJobs Intelligence Platform',
  description: 'Evidence-backed government recruitment intelligence for India',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
