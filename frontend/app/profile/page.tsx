'use client';

import Link from 'next/link';
import { useEffect, useState, type FormEvent } from 'react';
import {
  getApiBaseUrl,
  type CandidateProfile,
  type ProfileEvaluationItem,
} from '../recruitments/data';

export default function ProfilePage() {
  const [profile, setProfile] = useState<CandidateProfile>({
    date_of_birth: '1995-06-12',
    gender: 'F',
    category: 'GENERAL',
    domicile_state: 'Telangana',
    preferred_states: ['Telangana', 'India'],
    education_level: 'GRADUATE',
    degree_name: 'B.Tech',
    specialization: 'Computer Science',
    experience_years: 2.0,
  });

  const [evaluations, setEvaluations] = useState<ProfileEvaluationItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    async function loadData() {
      try {
        const [profRes, evalRes] = await Promise.all([
          fetch(`${getApiBaseUrl()}/v1/profile`),
          fetch(`${getApiBaseUrl()}/v1/profile/evaluations`),
        ]);

        if (profRes.ok) {
          const profData = await profRes.json();
          setProfile({
            date_of_birth: profData.date_of_birth || '',
            gender: profData.gender || 'F',
            category: profData.category || 'GENERAL',
            domicile_state: profData.domicile_state || 'Telangana',
            preferred_states: profData.preferred_states || ['Telangana', 'India'],
            education_level: profData.education_level || 'GRADUATE',
            degree_name: profData.degree_name || 'B.Tech',
            specialization: profData.specialization || 'Computer Science',
            experience_years: Number(profData.experience_years ?? 2.0),
          });
        }

        if (evalRes.ok) {
          const evalData = await evalRes.json();
          setEvaluations(evalData.items || []);
        }
      } catch {
        setError('Could not connect to the backend server at ' + getApiBaseUrl());
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, []);

  async function handleSave(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setSaving(true);
    setSaveSuccess(false);
    setError('');

    try {
      const res = await fetch(`${getApiBaseUrl()}/v1/profile`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...profile,
          experience_years: Number(profile.experience_years),
        }),
      });

      if (!res.ok) {
        const data = await res.json();
        setError(data.detail || 'Failed to update profile');
      } else {
        setSaveSuccess(true);
        // Refresh evaluations with updated profile
        const evalRes = await fetch(`${getApiBaseUrl()}/v1/profile/evaluations`);
        if (evalRes.ok) {
          const evalData = await evalRes.json();
          setEvaluations(evalData.items || []);
        }
      }
    } catch {
      setError('Could not connect to the backend server.');
    } finally {
      setSaving(false);
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
          <Link href="/saved">Saved & Reminders</Link>
          <Link className="active" href="/profile">
            Candidate Profile
          </Link>
        </nav>
        <Link className="button button-outline header-action" href="/">
          ← Back to Discover
        </Link>
      </header>

      <div className="breadcrumb">
        <Link href="/">Discover</Link>
        <span aria-hidden="true">/</span>
        <span>Candidate Profile & Eligibility Matrix</span>
      </div>

      <section className="profile-hero">
        <div>
          <span className="status-pill status-verified">PERSONALIZED INTELLIGENCE</span>
          <h1>Candidate Profile</h1>
          <p className="detail-summary">
            Configure your date of birth, caste/reservation category, domicile, and qualifications. The deterministic engine calculates your match status across all central and state recruitments with category relaxations.
          </p>
        </div>
      </section>

      {error && <div className="notice notice-error">{error}</div>}

      <div className="profile-layout">
        {/* PROFILE EDIT FORM */}
        <section className="profile-card">
          <div className="section-title">
            <div>
              <p className="eyebrow">YOUR DETAILS</p>
              <h2>Profile Information</h2>
            </div>
          </div>

          <form onSubmit={handleSave} className="profile-form">
            <div className="form-group-row">
              <label>
                Date of Birth
                <input
                  type="date"
                  required
                  value={profile.date_of_birth || ''}
                  onChange={(e) =>
                    setProfile({ ...profile, date_of_birth: e.target.value })
                  }
                />
              </label>

              <label>
                Gender
                <select
                  value={profile.gender}
                  onChange={(e) => setProfile({ ...profile, gender: e.target.value })}
                >
                  <option value="F">Female</option>
                  <option value="M">Male</option>
                  <option value="OTHER">Other</option>
                </select>
              </label>
            </div>

            <div className="form-group-row">
              <label>
                Social / Reservation Category
                <select
                  value={profile.category}
                  onChange={(e) =>
                    setProfile({ ...profile, category: e.target.value })
                  }
                >
                  <option value="GENERAL">General / Unreserved</option>
                  <option value="OBC">OBC (Non-Creamy Layer) [+3 yrs relaxation]</option>
                  <option value="SC">SC (Scheduled Caste) [+5 yrs relaxation]</option>
                  <option value="ST">ST (Scheduled Tribe) [+5 yrs relaxation]</option>
                  <option value="EWS">EWS (Economically Weaker Section)</option>
                  <option value="PWBD">PwBD / Divyangjan [+10 yrs relaxation]</option>
                </select>
              </label>

              <label>
                Domicile State
                <select
                  value={profile.domicile_state}
                  onChange={(e) =>
                    setProfile({ ...profile, domicile_state: e.target.value })
                  }
                >
                  <option value="Telangana">Telangana (Local 95% Quota)</option>
                  <option value="Andhra Pradesh">Andhra Pradesh</option>
                  <option value="Maharashtra">Maharashtra</option>
                  <option value="Karnataka">Karnataka</option>
                  <option value="Delhi">Delhi</option>
                  <option value="Other">Other States</option>
                </select>
              </label>
            </div>

            <div className="form-group-row">
              <label>
                Highest Educational Level
                <select
                  value={profile.education_level}
                  onChange={(e) =>
                    setProfile({ ...profile, education_level: e.target.value })
                  }
                >
                  <option value="SCHOOL">10th / Matriculation</option>
                  <option value="HIGHER_SECONDARY">12th / Intermediate</option>
                  <option value="DIPLOMA">Diploma</option>
                  <option value="GRADUATE">Graduate (Degree)</option>
                  <option value="POSTGRADUATE">Postgraduate (Master&apos;s)</option>
                  <option value="DOCTORATE">Doctorate (Ph.D)</option>
                </select>
              </label>

              <label>
                Degree / Qualification Name
                <input
                  type="text"
                  placeholder="e.g. B.Tech, B.Sc, B.Com, BA"
                  value={profile.degree_name}
                  onChange={(e) =>
                    setProfile({ ...profile, degree_name: e.target.value })
                  }
                />
              </label>
            </div>

            <div className="form-group-row">
              <label>
                Specialization / Major
                <input
                  type="text"
                  placeholder="e.g. Computer Science, Civil, Commerce"
                  value={profile.specialization}
                  onChange={(e) =>
                    setProfile({ ...profile, specialization: e.target.value })
                  }
                />
              </label>

              <label>
                Experience (Years)
                <input
                  type="number"
                  min="0"
                  max="60"
                  step="0.5"
                  value={profile.experience_years}
                  onChange={(e) =>
                    setProfile({
                      ...profile,
                      experience_years: Number(e.target.value),
                    })
                  }
                />
              </label>
            </div>

            <div className="form-actions">
              <button
                className="button button-primary"
                type="submit"
                disabled={saving}
              >
                {saving ? 'Saving changes…' : 'Save Profile & Recalculate Matches'}
              </button>
              {saveSuccess && (
                <span className="success-tag">✓ Profile updated and matches recalculated</span>
              )}
            </div>
          </form>
        </section>

        {/* LIVE EVALUATIONS MATRIX */}
        <section className="matches-section">
          <div className="section-title">
            <div>
              <p className="eyebrow">DETERMINISTIC RESULTS</p>
              <h2>My Recruitment Matches</h2>
            </div>
            <span className="engine-label">AUTOMATED ENGINE v2.0</span>
          </div>

          {loading ? (
            <p className="muted">Evaluating eligibility across all recruitments…</p>
          ) : evaluations.length === 0 ? (
            <div className="notice">No evaluations available.</div>
          ) : (
            <div className="evaluations-grid">
              {evaluations.map((item, idx) => (
                <div className="match-card" key={idx}>
                  <div className="match-card-top">
                    <div>
                      <span className="match-recruitment-name">
                        {item.recruitment_title}
                      </span>
                      <h3>{item.job_post_title}</h3>
                    </div>
                    <span className={`result-badge status-${item.result.toLowerCase()}`}>
                      {item.result.replaceAll('_', ' ')}
                    </span>
                  </div>

                  <div className="match-reasons-summary">
                    {item.reasons.map((r, rIdx) => (
                      <div className="match-reason-item" key={rIdx}>
                        <span className={`reason-pill reason-${r.status.toLowerCase()}`}>
                          {r.status === 'PASS' && '✓'}
                          {r.status === 'CHECK_FAILED' && '✗'}
                          {r.status === 'NEEDS_VERIFICATION' && '⚠'}
                          {r.status === 'INSUFFICIENT_DATA' && '?'} {r.rule_type}
                        </span>
                        <p>{r.message}</p>
                      </div>
                    ))}
                  </div>

                  <div className="match-card-footer">
                    <Link
                      className="button button-outline button-sm"
                      href={`/recruitments/${encodeURIComponent(item.recruitment_id)}`}
                    >
                      View Notice & Evidence Citations ↗
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>

      <footer className="site-footer">
        <span>Civic Careers · Verified Indian Public Sector Intelligence</span>
        <span>Deterministic eligibility evaluation based on official reference dates.</span>
      </footer>
    </main>
  );
}
