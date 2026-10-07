'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import {
  getApiBaseUrl,
  type Recruitment,
  type ReminderItem,
} from '../recruitments/data';

export default function SavedPage() {
  const [savedItems, setSavedItems] = useState<Recruitment[]>([]);
  const [reminders, setReminders] = useState<ReminderItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [reminderRecruitmentId, setReminderRecruitmentId] = useState('');
  const [reminderType, setReminderType] = useState<'DEADLINE' | 'EXAM_DATE' | 'DOCUMENT_CHECK'>('DEADLINE');
  const [reminderDate, setReminderDate] = useState('');
  const [creatingReminder, setCreatingReminder] = useState(false);

  useEffect(() => {
    async function loadData() {
      try {
        const [savedRes, remRes] = await Promise.all([
          fetch(`${getApiBaseUrl()}/v1/saved`),
          fetch(`${getApiBaseUrl()}/v1/reminders`),
        ]);

        if (savedRes.ok) {
          const sData = await savedRes.json();
          setSavedItems(sData.items || []);
          if (sData.items && sData.items.length > 0) {
            setReminderRecruitmentId(sData.items[0].id);
          }
        }
        if (remRes.ok) {
          const rData = await remRes.json();
          setReminders(rData.items || []);
        }
      } catch {
        setError('Could not connect to backend server at ' + getApiBaseUrl());
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, []);

  async function handleUnsave(recruitmentId: string) {
    try {
      const res = await fetch(`${getApiBaseUrl()}/v1/recruitments/${recruitmentId}/save`, {
        method: 'DELETE',
      });
      if (res.ok) {
        setSavedItems((prev) => prev.filter((item) => item.id !== recruitmentId));
      }
    } catch {
      alert('Failed to unsave recruitment.');
    }
  }

  async function handleDeleteReminder(reminderId: string) {
    try {
      const res = await fetch(`${getApiBaseUrl()}/v1/reminders/${reminderId}`, {
        method: 'DELETE',
      });
      if (res.ok) {
        setReminders((prev) => prev.filter((r) => r.id !== reminderId));
      }
    } catch {
      alert('Failed to delete reminder.');
    }
  }

  async function handleCreateReminder(e: React.FormEvent) {
    e.preventDefault();
    if (!reminderRecruitmentId || !reminderDate) return;
    setCreatingReminder(true);

    try {
      const res = await fetch(`${getApiBaseUrl()}/v1/reminders`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          recruitment_id: reminderRecruitmentId,
          event_type: reminderType,
          scheduled_for: new Date(reminderDate).toISOString(),
        }),
      });

      if (res.ok) {
        const newRem = await res.json();
        setReminders((prev) => [...prev, newRem]);
        setReminderDate('');
      } else {
        alert('Failed to create reminder.');
      }
    } catch {
      alert('Network error while scheduling reminder.');
    } finally {
      setCreatingReminder(false);
    }
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
          <Link className="active" href="/saved">
            Saved & Reminders
          </Link>
          <Link href="/profile">Candidate Profile</Link>
        </nav>
        <Link className="button button-dark header-action" href="/profile">
          My Profile <span aria-hidden="true">→</span>
        </Link>
      </header>

      <div className="breadcrumb">
        <Link href="/">Discover</Link>
        <span aria-hidden="true">/</span>
        <span>Saved Opportunities & Reminders</span>
      </div>

      <section className="profile-hero">
        <div>
          <span className="status-pill status-verified">PERSONAL TRACKER</span>
          <h1>Saved Opportunities & Reminders</h1>
          <p className="detail-summary">
            Track key application deadlines, exam dates, and saved recruitments in one place. Never miss an official closing date or admit card release.
          </p>
        </div>
      </section>

      {error && <div className="notice notice-error">{error}</div>}

      <div className="saved-layout">
        {/* SAVED RECRUITMENTS */}
        <section className="saved-main">
          <div className="section-title">
            <div>
              <p className="eyebrow">SAVED OPPORTUNITIES</p>
              <h2>My Tracked Recruitments ({savedItems.length})</h2>
            </div>
          </div>

          {loading ? (
            <p className="muted">Loading saved opportunities…</p>
          ) : savedItems.length === 0 ? (
            <div className="notice">
              You haven&apos;t saved any recruitments yet.{' '}
              <Link className="text-link" href="/">
                Browse open opportunities on the Discover page →
              </Link>
            </div>
          ) : (
            <div className="saved-list">
              {savedItems.map((recruitment) => {
                const post = recruitment.posts[0];
                return (
                  <article className="saved-card" key={recruitment.id}>
                    <div className="saved-card-header">
                      <div>
                        <span className="org-pill">
                          {recruitment.organization_name || recruitment.organization_id}
                        </span>
                        <h3>{recruitment.title}</h3>
                        <p className="post-subtitle">{post?.title}</p>
                      </div>
                      <button
                        className="button button-outline button-sm"
                        onClick={() => handleUnsave(recruitment.id)}
                        title="Remove from saved"
                      >
                        Unsave ✕
                      </button>
                    </div>

                    <div className="card-facts">
                      <span>
                        <span aria-hidden="true">⏱</span>{' '}
                        {recruitment.application_deadline
                          ? `Deadline: ${new Date(
                              recruitment.application_deadline
                            ).toLocaleDateString('en-IN', {
                              day: 'numeric',
                              month: 'short',
                              year: 'numeric',
                            })}`
                          : 'No deadline'}
                      </span>
                      <span>
                        <span aria-hidden="true">▤</span>{' '}
                        {post?.vacancies
                          ? `${post.vacancies.toLocaleString('en-IN')} Vacancies`
                          : 'Vacancies in notice'}
                      </span>
                      <span>
                        <span aria-hidden="true">⌖</span> {post?.location_type || 'All India'}
                      </span>
                    </div>

                    <div className="saved-card-actions">
                      {recruitment.official_apply_url && (
                        <a
                          className="button button-primary button-sm"
                          href={recruitment.official_apply_url}
                          target="_blank"
                          rel="noreferrer"
                        >
                          Apply on Official Portal ↗
                        </a>
                      )}
                      <Link
                        className="button button-outline button-sm"
                        href={`/recruitments/${encodeURIComponent(recruitment.id)}`}
                      >
                        View Full Notice & Citations →
                      </Link>
                    </div>
                  </article>
                );
              })}
            </div>
          )}
        </section>

        {/* REMINDERS SIDEBAR */}
        <aside className="reminders-sidebar">
          <div className="section-title">
            <div>
              <p className="eyebrow">ACTIVE ALERTS</p>
              <h2>Scheduled Reminders ({reminders.length})</h2>
            </div>
          </div>

          {/* ADD REMINDER FORM */}
          <form className="reminder-form" onSubmit={handleCreateReminder}>
            <strong>Set a Deadline Reminder</strong>
            <label>
              Select Recruitment
              <select
                value={reminderRecruitmentId}
                onChange={(e) => setReminderRecruitmentId(e.target.value)}
                required
              >
                {savedItems.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.title}
                  </option>
                ))}
              </select>
            </label>

            <label>
              Event Type
              <select
                value={reminderType}
                onChange={(e) => setReminderType(e.target.value as any)}
              >
                <option value="DEADLINE">Application Deadline</option>
                <option value="EXAM_DATE">Examination Date</option>
                <option value="DOCUMENT_CHECK">Document Verification</option>
              </select>
            </label>

            <label>
              Alert Date & Time
              <input
                type="datetime-local"
                required
                value={reminderDate}
                onChange={(e) => setReminderDate(e.target.value)}
              />
            </label>

            <button
              className="button button-primary button-full"
              type="submit"
              disabled={creatingReminder || !reminderRecruitmentId || !reminderDate}
            >
              {creatingReminder ? 'Scheduling…' : 'Schedule Reminder'}
            </button>
          </form>

          {/* LIST OF REMINDERS */}
          <div className="reminders-list">
            {reminders.length === 0 ? (
              <p className="muted">No deadline reminders scheduled.</p>
            ) : (
              reminders.map((rem) => (
                <div className="reminder-item" key={rem.id}>
                  <div>
                    <span className="badge badge-deadline">{rem.event_type}</span>
                    <p className="reminder-target">
                      {savedItems.find((s) => s.id === rem.recruitment_id)?.title ||
                        rem.recruitment_id}
                    </p>
                    <small className="reminder-time">
                      Scheduled for{' '}
                      {new Date(rem.scheduled_for).toLocaleString('en-IN', {
                        day: 'numeric',
                        month: 'short',
                        year: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </small>
                  </div>
                  <button
                    className="delete-rem-btn"
                    title="Delete reminder"
                    onClick={() => handleDeleteReminder(rem.id)}
                  >
                    ✕
                  </button>
                </div>
              ))
            )}
          </div>
        </aside>
      </div>

      <footer className="site-footer">
        <span>Civic Careers · Public Demo · Sample recruitment data</span>
        <span>Always verify exact application closing times with the organizing body.</span>
      </footer>
    </main>
  );
}
