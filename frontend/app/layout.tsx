import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'GovJobs Intelligence Platform · Public Demo',
  description: 'Public demo using sample recruitment data. Verify all facts with official notices.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <aside className="public-demo-banner" role="note">
          <strong>PUBLIC DEMO · SAMPLE DATA</strong>
          <span>Recruitment dates, eligibility, citations, and vacancies may be outdated or inaccurate. Do not use this demo to make application decisions; verify every detail in the current official notice. Eligibility inputs are used for calculation only; profile edits, saves, and reminders are disabled and not stored.</span>
        </aside>
        {children}
      </body>
    </html>
  );
}
