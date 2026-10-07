'use client';

import { useState } from 'react';
import { getApiBaseUrl, type AssistantResponse } from '../recruitments/data';

export default function AssistantDrawer({
  recruitmentId,
  recruitmentTitle,
}: {
  recruitmentId: string;
  recruitmentTitle: string;
}) {
  const [isOpen, setIsOpen] = useState(false);
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<AssistantResponse | null>(null);
  const [error, setError] = useState('');

  const suggestedPrompts = [
    'What is the last date to apply?',
    'What is the age limit and relaxation for OBC/SC/ST?',
    'What are the minimum educational qualifications?',
    'What is the pay scale and total vacancies?',
  ];

  async function askQuestion(queryText: string) {
    if (!queryText.trim()) return;
    setLoading(true);
    setError('');
    setQuestion(queryText);

    try {
      const res = await fetch(`${getApiBaseUrl()}/v1/assistant/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          recruitment_id: recruitmentId,
          question: queryText,
        }),
      });
      const data = await res.json();
      if (!res.ok) {
        setError(data.detail ?? 'Unable to process query');
      } else {
        setResponse(data as AssistantResponse);
      }
    } catch {
      setError(`Could not connect to the API at ${getApiBaseUrl()}.`);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="copilot-widget">
      <div className="copilot-header-bar" onClick={() => setIsOpen(!isOpen)}>
        <div className="copilot-title">
          <span className="copilot-icon">✦</span>
          <div>
            <strong>Recruitment Copilot</strong>
            <small>Ask questions about this sample recruitment</small>
          </div>
        </div>
        <button
          className="button button-outline button-sm"
          type="button"
          aria-expanded={isOpen}
          onClick={(e) => {
            e.stopPropagation();
            setIsOpen(!isOpen);
          }}
        >
          {isOpen ? 'Close Assistant ✕' : 'Open Assistant ↗'}
        </button>
      </div>

      {isOpen && (
        <div className="copilot-body">
          <p className="copilot-intro">
            Ask any question about <strong>{recruitmentTitle}</strong>. Answers use sample data and may not match the current official notification.
          </p>

          <div className="suggested-prompts">
            <span className="prompts-label">SUGGESTED QUESTIONS:</span>
            <div className="prompts-list">
              {suggestedPrompts.map((p, idx) => (
                <button
                  key={idx}
                  type="button"
                  className="prompt-chip"
                  onClick={() => askQuestion(p)}
                  disabled={loading}
                >
                  {p}
                </button>
              ))}
            </div>
          </div>

          <form
            className="copilot-form"
            onSubmit={(e) => {
              e.preventDefault();
              askQuestion(question);
            }}
          >
            <input
              type="text"
              placeholder="Ask about age, qualifications, dates, syllabus..."
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              disabled={loading}
            />
            <button className="button button-primary" type="submit" disabled={loading || !question.trim()}>
              {loading ? 'Searching…' : 'Ask Copilot'}
            </button>
          </form>

          {error && <p className="notice notice-error">{error}</p>}

          {response && (
            <div className="copilot-answer-card">
              <div className="answer-topline">
                <span className="badge badge-verified">
                  DEMO ANSWER · UNVERIFIED
                </span>
                {response.last_verified_at && (
                  <span className="verified-timestamp">
                    Sample timestamp {new Date(response.last_verified_at).toLocaleDateString('en-IN')}
                  </span>
                )}
              </div>

              <div className="answer-content">
                {response.answer.split('\n\n').map((paragraph, i) => (
                  <p key={i}>{paragraph}</p>
                ))}
              </div>

              {response.citations.length > 0 && (
                <div className="answer-citations">
                  <span className="citations-header">SAMPLE SOURCE REFERENCES</span>
                  {response.citations.map((c, i) => (
                    <div className="citation-box" key={i}>
                      <div className="citation-meta">
                        <strong>{c.document_title || 'Official Document'}</strong>
                        {c.page && <span>Page {c.page}</span>}
                        {c.section && <span>{c.section}</span>}
                      </div>
                      {c.quote && <p className="citation-quote">“{c.quote}”</p>}
                      {c.url && (
                        <a href={c.url} target="_blank" rel="noreferrer" className="citation-link">
                          Open listed source ↗
                        </a>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
