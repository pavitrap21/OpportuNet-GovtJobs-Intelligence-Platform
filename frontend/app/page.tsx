import Link from 'next/link';
import DiscoveryClient from './components/DiscoveryClient';
import { apiGet, type Recruitment } from './recruitments/data';

export const dynamic = 'force-dynamic';

export default async function HomePage() {
  const response = await apiGet<{ items: Recruitment[]; total: number }>('/v1/recruitments');
  const items = response.ok ? response.data.items : [];

  return (
    <main className="app-shell">
      <header className="site-header">
        <Link className="brand" href="/" aria-label="Civic Careers home">
          <span className="brand-mark">CC</span>
          <span>
            Civic Careers<small>RECRUITMENT INTELLIGENCE</small>
          </span>
        </Link>
        <nav className="main-nav" aria-label="Main navigation">
          <Link className="active" href="/">
            Discover
          </Link>
          <Link href="/saved">Saved & Reminders</Link>
          <Link href="/profile">Candidate Profile</Link>
        </nav>
        <Link className="button button-dark header-action" href="/profile">
          Candidate Profile <span aria-hidden="true">↗</span>
        </Link>
      </header>

      <section className="hero">
        <div className="hero-copy">
          <p className="eyebrow">
            <span className="live-dot" /> INDIA · PUBLIC SECTOR RECRUITMENT INTELLIGENCE
          </p>
          <h1>
            A clearer way to explore<br />
            <em>public service aspirants.</em>
          </h1>
          <p className="hero-description">
            Explore sample listings from SSC, UPSC, IBPS, RRB, and Telangana. This public preview is not a live feed and its recruitment data has not been verified.
          </p>
          <div className="hero-actions">
            <a className="button button-primary" href="#opportunities">
              Explore Sample Recruitments <span aria-hidden="true">↓</span>
            </a>
            <Link className="button button-outline" href="/profile">
              Check Profile Match <span aria-hidden="true">→</span>
            </Link>
          </div>
          <div className="trust-note">
            <span className="shield-icon" aria-hidden="true">
              ✓
            </span>{' '}
            Illustrative rules only · Verify dates and eligibility in current official notices
          </div>
        </div>

        <aside className="hero-panel" aria-label="Platform principles">
          <span className="panel-kicker">SAMPLE ECOSYSTEMS</span>
          <h2>Central & State Public Recruitments</h2>
          <div className="principle">
            <span>01</span>
            <div>
              <strong>Central Bodies</strong>
              <small>Staff Selection Commission (SSC) & Union Public Service Commission (UPSC).</small>
            </div>
          </div>
          <div className="principle">
            <span>02</span>
            <div>
              <strong>Banking & Railways</strong>
              <small>IBPS CRP Probationary Officers & RRB Centralized Railway recruitments.</small>
            </div>
          </div>
          <div className="principle">
            <span>03</span>
            <div>
              <strong>State Civil Services</strong>
              <small>Telangana Public Service Commission (TSPSC Group-I) with local reservation quotas.</small>
            </div>
          </div>
          <p className="preview-caption">
            SAMPLE DATA · NOT A LIVE VERIFIED SERVICE
          </p>
        </aside>
      </section>

      <section className="section-heading" id="opportunities">
        <div>
          <p className="eyebrow">DISCOVERY & INTELLIGENCE</p>
          <h2>Explore Opportunities</h2>
          <p className="muted">
            Filter across central ministries, railways, public sector banking, and state administration.
          </p>
        </div>
      </section>

      {!response.ok ? (
        <div className="notice notice-error" role="alert">
          <strong>Recruitment Service Offline</strong>
          <p>{response.error}</p>
          <p>The sample recruitment service is currently unavailable.</p>
        </div>
      ) : (
        <DiscoveryClient initialItems={items} />
      )}

      <footer className="site-footer">
        <span>Civic Careers · Public Demo</span>
        <span>Always verify exact post terms and submit applications on official recruitment portals.</span>
      </footer>
    </main>
  );
}
