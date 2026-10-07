import Link from 'next/link';
import { notFound } from 'next/navigation';
import AssistantDrawer from '../../components/AssistantDrawer';
import EligibilityChecker from '../../components/EligibilityChecker';
import { apiGet, type EvidenceFragment, type Recruitment } from '../data';

export const dynamic = 'force-dynamic';

export default async function RecruitmentDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const decodedId = decodeURIComponent(id);

  const [recruitmentRes, evidenceRes] = await Promise.all([
    apiGet<Recruitment>(`/v1/recruitments/${encodeURIComponent(decodedId)}`),
    apiGet<{ items: EvidenceFragment[] }>(`/v1/recruitments/${encodeURIComponent(decodedId)}/evidence`),
  ]);

  if (!recruitmentRes.ok && recruitmentRes.status === 404) {
    notFound();
  }

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
          <Link href="/">Discover</Link>
          <Link href="/saved">Saved & Reminders</Link>
          <Link href="/profile">Candidate Profile</Link>
        </nav>
        <Link className="button button-dark header-action" href="/profile">
          My Profile <span aria-hidden="true">→</span>
        </Link>
      </header>

      {!recruitmentRes.ok ? (
        <div className="notice notice-error detail-error" role="alert">
          <h1>Recruitment details unavailable</h1>
          <p>{recruitmentRes.error}</p>
          <Link className="text-link" href="/">
            Return to discovery →
          </Link>
        </div>
      ) : (
        <RecruitmentDetails
          recruitment={recruitmentRes.data}
          evidenceItems={evidenceRes.ok ? evidenceRes.data.items : []}
        />
      )}

      <footer className="site-footer">
        <span>Civic Careers · Verified Indian Public Sector Intelligence</span>
        <span>Always confirm application steps and deadlines on the official portal.</span>
      </footer>
    </main>
  );
}

function RecruitmentDetails({
  recruitment,
  evidenceItems,
}: {
  recruitment: Recruitment;
  evidenceItems: EvidenceFragment[];
}) {
  const primaryPost = recruitment.posts[0];
  const totalVacancies = recruitment.posts.reduce(
    (acc, p) => acc + (p.vacancies || 0),
    0
  );

  return (
    <>
      <div className="breadcrumb">
        <Link href="/">Discover</Link>
        <span aria-hidden="true">/</span>
        <span>{recruitment.organization_name || recruitment.organization_id}</span>
        <span aria-hidden="true">/</span>
        <span>{recruitment.title}</span>
      </div>

      <section className="detail-hero">
        <div>
          <div className="badge-row">
            <span className="status-pill status-verified">✓ VERIFIED OFFICIAL NOTICE</span>
            <span className="org-pill">
              {recruitment.organization_name || recruitment.organization_id}
            </span>
          </div>
          <h1>{recruitment.title}</h1>
          <p className="detail-summary">
            {primaryPost?.description ??
              'Official centralized public sector recruitment campaign.'}
          </p>

          <div className="hero-cta-bar">
            {recruitment.official_apply_url && (
              <a
                className="button button-primary button-lg"
                href={recruitment.official_apply_url}
                target="_blank"
                rel="noreferrer"
              >
                Apply on Official Portal ↗
              </a>
            )}
            <Link className="button button-outline" href="/saved">
              View in Saved Opportunities
            </Link>
          </div>
        </div>

        <aside className="verification-card">
          <span className="verification-icon">✓</span>
          <div>
            <strong>Official Source Backed</strong>
            <p>
              Verified against published gazette / recruitment notice.
              {recruitment.last_verified_at &&
                ` Last audited: ${new Date(
                  recruitment.last_verified_at
                ).toLocaleDateString('en-IN')}`}
            </p>
          </div>
        </aside>
      </section>

      <div className="detail-layout">
        <div className="detail-main">
          {/* IMPORTANT DATES */}
          <section className="detail-section">
            <div className="section-title">
              <div>
                <p className="eyebrow">KEY TIMELINE</p>
                <h2>Important Dates & Schedule</h2>
              </div>
            </div>
            <div className="timeline-grid">
              <div className="timeline-item">
                <span className="timeline-dot" />
                <span className="timeline-label">Application Opening</span>
                <strong>
                  {recruitment.application_start_date
                    ? new Date(recruitment.application_start_date).toLocaleDateString(
                        'en-IN',
                        { day: 'numeric', month: 'short', year: 'numeric' }
                      )
                    : 'Check notice'}
                </strong>
              </div>
              <div className="timeline-item timeline-critical">
                <span className="timeline-dot active" />
                <span className="timeline-label">Application Deadline</span>
                <strong>
                  {recruitment.application_deadline
                    ? new Date(recruitment.application_deadline).toLocaleDateString(
                        'en-IN',
                        { day: 'numeric', month: 'short', year: 'numeric' }
                      )
                    : 'Check notice'}
                </strong>
              </div>
              <div className="timeline-item">
                <span className="timeline-dot" />
                <span className="timeline-label">Examination Date</span>
                <strong>
                  {recruitment.exam_date
                    ? new Date(recruitment.exam_date).toLocaleDateString('en-IN', {
                        day: 'numeric',
                        month: 'short',
                        year: 'numeric',
                      })
                    : 'To be notified'}
                </strong>
              </div>
            </div>
          </section>

          {/* POSTS & VACANCIES */}
          <section className="detail-section">
            <div className="section-title">
              <div>
                <p className="eyebrow">POSTS & VACANCIES</p>
                <h2>Notified Posts ({recruitment.posts.length})</h2>
              </div>
              {totalVacancies > 0 && (
                <span className="total-vacancies-tag">
                  {totalVacancies.toLocaleString('en-IN')} Total Vacancies
                </span>
              )}
            </div>

            <div className="posts-container">
              {recruitment.posts.map((post) => (
                <div className="post-detail-card" key={post.id}>
                  <div className="post-header">
                    <h3>{post.title}</h3>
                    {post.vacancies && (
                      <span className="vacancies-badge">
                        {post.vacancies.toLocaleString('en-IN')} Vacancies
                      </span>
                    )}
                  </div>
                  <p>{post.description}</p>
                  <div className="overview-grid">
                    <OverviewFact
                      label="Department / Ministry"
                      value={post.department ?? 'Central / State Cadre'}
                    />
                    <OverviewFact
                      label="Location Cadre"
                      value={post.location_type ?? 'All India'}
                    />
                    <OverviewFact
                      label="Pay Scale / Matrix"
                      value={post.salary_text ?? 'Level Pay Matrix'}
                    />
                    <OverviewFact
                      label="Min. Education Level"
                      value={recruitment.required_education_level ?? 'Graduate'}
                    />
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* OFFICIAL EVIDENCE & FRAGMENTS */}
          <section className="detail-section">
            <div className="section-title">
              <div>
                <p className="eyebrow">PROVENANCE & CITATIONS</p>
                <h2>Official Source Documents & Evidence</h2>
              </div>
            </div>

            <div className="evidence-container">
              {evidenceItems.length > 0 ? (
                <div className="evidence-cards-list">
                  {evidenceItems.map((ev) => (
                    <div className="evidence-fragment-card" key={ev.id}>
                      <div className="evidence-meta">
                        <span className="evidence-badge">OFFICIAL CITATION</span>
                        <strong>{ev.section_heading}</strong>
                        {ev.page_number && (
                          <span className="page-tag">Page {ev.page_number}</span>
                        )}
                      </div>
                      <blockquote className="evidence-text">
                        “{ev.text_content}”
                      </blockquote>
                      <div className="evidence-footer">
                        <span>Source: {ev.source_title}</span>
                        {ev.url && (
                          <a
                            href={ev.url}
                            target="_blank"
                            rel="noreferrer"
                            className="text-link"
                          >
                            Open original PDF ↗
                          </a>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="source-list">
                  {recruitment.official_sources.map((source) => (
                    <a
                      className="source-item"
                      href={source.url}
                      key={source.id}
                      target="_blank"
                      rel="noreferrer"
                    >
                      <span className="source-file" aria-hidden="true">
                        ↗
                      </span>
                      <span className="source-copy">
                        <strong>{source.title}</strong>
                        <small>
                          {source.document_type.replaceAll('_', ' ')} · Version{' '}
                          {source.version_number}
                          {source.section ? ` · ${source.section}` : ''}
                          {source.page ? ` · Page ${source.page}` : ''}
                        </small>
                        <small>{source.url}</small>
                      </span>
                    </a>
                  ))}
                </div>
              )}
            </div>
          </section>

          {/* AI COPILOT */}
          <AssistantDrawer
            recruitmentId={recruitment.id}
            recruitmentTitle={recruitment.title}
          />
        </div>

        <aside className="detail-sidebar">
          {primaryPost ? (
            <EligibilityChecker jobPostId={primaryPost.id} />
          ) : (
            <div className="notice">Eligibility evaluation unavailable for this record.</div>
          )}

          <div className="side-note">
            <strong>Candidate Checklist</strong>
            <p>
              1. Verify date of birth on 10th certificate.<br />
              2. Keep category/caste certificate in central/state prescribed format.<br />
              3. Note exact closing time (23:59 IST on deadline date).
            </p>
          </div>
        </aside>
      </div>
    </>
  );
}

function OverviewFact({ label, value }: { label: string; value: string }) {
  return (
    <div className="overview-fact">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}
