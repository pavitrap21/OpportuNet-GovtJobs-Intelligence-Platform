'use client';

import Link from 'next/link';
import { useState, type FormEvent } from 'react';
import { getApiBaseUrl } from '../recruitments/data';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const [previewMode, setPreviewMode] = useState(false);
  const [loading, setLoading] = useState(false);

  async function signIn(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setMessage('');
    try {
      const response = await fetch(`${getApiBaseUrl()}/v1/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });
      const body = await response.json();
      setMessage(body.detail ?? `Sign in is unavailable (HTTP ${response.status}).`);
    } catch {
      setMessage(`Could not connect to the API at ${getApiBaseUrl()}.`);
    } finally {
      setLoading(false);
    }
  }

  function continuePreview() {
    window.sessionStorage.setItem('govjobs-preview-mode', 'true');
    setPreviewMode(true);
  }

  return (
    <main className="login-shell">
      <header className="site-header login-header">
        <Link className="brand" href="/"><span className="brand-mark">CC</span><span>Civic Careers<small>RECRUITMENT INTELLIGENCE</small></span></Link>
        <Link className="text-link" href="/">← Back to discovery</Link>
      </header>
      <section className="login-layout">
        <div className="login-story">
          <p className="eyebrow">YOUR NEXT STEP, MADE CLEARER</p>
          <h1>Keep your public-service search in focus.</h1>
          <p>Save opportunities, track your profile checks, and keep the source information close at hand.</p>
          <div className="login-value"><span>01</span><div><strong>One candidate profile</strong><small>Review age, education and experience against preview criteria.</small></div></div>
          <div className="login-value"><span>02</span><div><strong>Evidence in view</strong><small>Find source links and see when verification is missing.</small></div></div>
        </div>
        <section className="login-card">
          <div className="login-card-heading"><span className="brand-mark">CC</span><p className="eyebrow">CANDIDATE ACCESS</p><h2>Sign in</h2><p className="muted">Authentication is not configured in this local preview.</p></div>
          <form className="login-form" onSubmit={signIn}>
            <label>Email address<input type="email" autoComplete="email" required value={email} onChange={(event) => setEmail(event.target.value)} placeholder="you@example.com" /></label>
            <label>Password<input type="password" autoComplete="current-password" required value={password} onChange={(event) => setPassword(event.target.value)} placeholder="Enter your password" /></label>
            <button className="button button-dark button-full" disabled={loading}>{loading ? 'Checking…' : 'Sign in'}</button>
          </form>
          {message && <p className="login-message" role="status">{message}</p>}
          <div className="login-divider"><span>OR</span></div>
          <button className="button button-outline button-full" type="button" onClick={continuePreview}>Continue in preview mode <span aria-hidden="true">→</span></button>
          {previewMode && <div className="preview-session" role="status"><strong>Preview mode enabled for this tab.</strong><p>No account was created and no personal details were saved.</p><Link className="text-link" href="/">Continue to opportunities →</Link></div>}
          <p className="fine-print login-footnote">Do not enter a real password here. This preview does not create accounts or store credentials.</p>
        </section>
      </section>
    </main>
  );
}
