'use client';

import { useState, type FormEvent } from 'react';
import { getApiBaseUrl, type EvaluationResult } from '../recruitments/data';

export default function EligibilityChecker({
  jobPostId,
  initialDob = '',
  initialCategory = 'GENERAL',
  initialDomicile = 'Telangana',
}: {
  jobPostId: string;
  initialDob?: string;
  initialCategory?: string;
  initialDomicile?: string;
}) {
  const [dateOfBirth, setDateOfBirth] = useState(initialDob);
  const [category, setCategory] = useState(initialCategory);
  const [domicileState, setDomicileState] = useState(initialDomicile);
  const [educationLevel, setEducationLevel] = useState('GRADUATE');
  const [experienceYears, setExperienceYears] = useState('0');
  const [evaluation, setEvaluation] = useState<EvaluationResult | null>(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function evaluate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError('');
    setEvaluation(null);

    try {
      const response = await fetch(`${getApiBaseUrl()}/v1/eligibility/evaluate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          job_post_id: jobPostId,
          profile: {
            date_of_birth: dateOfBirth || null,
            category: category,
            domicile_state: domicileState,
            education_level: educationLevel,
            experience_years: Number(experienceYears),
          },
        }),
      });
      const body = await response.json();
      if (!response.ok) {
        setError(body.detail ?? `Eligibility check failed (HTTP ${response.status}).`);
        return;
      }
      setEvaluation(body as EvaluationResult);
    } catch {
      setError(`Could not connect to the API at ${getApiBaseUrl()}.`);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="eligibility-panel" aria-labelledby="eligibility-heading">
      <div className="eligibility-heading">
        <div>
          <p className="eyebrow">DETERMINISTIC EVALUATION</p>
          <h2 id="eligibility-heading">Check your eligibility</h2>
        </div>
        <span className="engine-label">RULE ENGINE · v2.0</span>
      </div>
      <p className="muted">
        Compares your inputs against illustrative sample rules. Do not use this result to decide whether to apply.
      </p>

      <form className="eligibility-form" onSubmit={evaluate}>
        <div className="form-group-row">
          <label>
            Date of birth
            <input
              type="date"
              value={dateOfBirth}
              onChange={(e) => setDateOfBirth(e.target.value)}
            />
          </label>
          <label>
            Category
            <select value={category} onChange={(e) => setCategory(e.target.value)}>
              <option value="GENERAL">General / Unreserved</option>
              <option value="OBC">OBC (Non-Creamy Layer)</option>
              <option value="SC">SC (Scheduled Caste)</option>
              <option value="ST">ST (Scheduled Tribe)</option>
              <option value="EWS">EWS (Economically Weaker)</option>
              <option value="PWBD">PwBD / Divyangjan</option>
            </select>
          </label>
        </div>

        <div className="form-group-row">
          <label>
            Domicile state
            <select value={domicileState} onChange={(e) => setDomicileState(e.target.value)}>
              <option value="Telangana">Telangana</option>
              <option value="Andhra Pradesh">Andhra Pradesh</option>
              <option value="Maharashtra">Maharashtra</option>
              <option value="Delhi">Delhi</option>
              <option value="Other">Other States</option>
            </select>
          </label>
          <label>
            Highest qualification
            <select value={educationLevel} onChange={(e) => setEducationLevel(e.target.value)}>
              <option value="SCHOOL">10th / Matriculation</option>
              <option value="HIGHER_SECONDARY">12th / Intermediate</option>
              <option value="DIPLOMA">Diploma</option>
              <option value="GRADUATE">Graduate (Degree)</option>
              <option value="POSTGRADUATE">Postgraduate</option>
              <option value="DOCTORATE">Doctorate (Ph.D)</option>
            </select>
          </label>
        </div>

        <label>
          Relevant experience (years)
          <input
            type="number"
            min="0"
            max="60"
            step="0.5"
            value={experienceYears}
            onChange={(e) => setExperienceYears(e.target.value)}
          />
        </label>

        <button className="button button-primary" type="submit" disabled={loading}>
          {loading ? 'Evaluating criteria…' : 'Run Deterministic Check'}
        </button>
      </form>

      {error && <p className="notice notice-error" role="alert">{error}</p>}

      {evaluation && (
        <div className="evaluation-result" aria-live="polite">
          <div className="evaluation-summary">
            <span className={`result-badge status-${evaluation.result.toLowerCase()}`}>
              {evaluation.result.replaceAll('_', ' ')}
            </span>
            <div>
              <strong>
                {evaluation.result === 'ELIGIBLE' && '✓ This profile matches the demo rules shown.'}
                {evaluation.result === 'LIKELY_ELIGIBLE' && '✓ This profile matches some sample rules; confirm the official notice.'}
                {evaluation.result === 'NOT_ELIGIBLE' && '✗ This sample check found a rule mismatch; verify the notice.'}
                {evaluation.result === 'INSUFFICIENT_DATA' && '⚠ Required profile information is missing.'}
              </strong>
              <small>Illustrative calculation only; the sample rules may be outdated or inaccurate.</small>
            </div>
          </div>

          <ul className="reason-list">
            {evaluation.reasons.map((reason, idx) => (
              <li key={idx}>
                <span className={`reason-status reason-${reason.status.toLowerCase()}`}>
                  {reason.status.replaceAll('_', ' ')}
                </span>
                <div>
                  <strong>{reason.rule_type.replaceAll('_', ' ')}</strong>
                  <p>{reason.message}</p>
                  {reason.source_quote && (
                    <blockquote className="evidence-quote">
                      <span className="quote-badge">OFFICIAL EVIDENCE</span>
                      <span>“{reason.source_quote}”</span>
                      {reason.page && <small>Page {reason.page}</small>}
                    </blockquote>
                  )}
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}
