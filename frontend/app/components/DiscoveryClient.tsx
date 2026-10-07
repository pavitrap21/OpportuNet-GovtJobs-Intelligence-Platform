'use client';

import Link from 'next/link';
import { useMemo, useState } from 'react';
import { type Recruitment } from '../recruitments/data';

export default function DiscoveryClient({
  initialItems,
}: {
  initialItems: Recruitment[];
}) {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedOrg, setSelectedOrg] = useState('ALL');
  const [selectedEdu, setSelectedEdu] = useState('ALL');

  const filteredItems = useMemo(() => {
    return initialItems.filter((item) => {
      // Query filter
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const matchesTitle = item.title.toLowerCase().includes(q);
        const matchesOrg = (item.organization_name || item.organization_id).toLowerCase().includes(q);
        const matchesPost = item.posts.some((p) => p.title.toLowerCase().includes(q) || (p.department && p.department.toLowerCase().includes(q)));
        if (!matchesTitle && !matchesOrg && !matchesPost) return false;
      }

      // Organization filter
      if (selectedOrg !== 'ALL') {
        if (item.organization_id !== selectedOrg) return false;
      }

      // Education filter
      if (selectedEdu !== 'ALL') {
        if ((item.required_education_level || '').toUpperCase() !== selectedEdu) return false;
      }

      return true;
    });
  }, [initialItems, searchQuery, selectedOrg, selectedEdu]);

  return (
    <div className="discovery-container">
      {/* FILTER BAR */}
      <div className="filter-toolbar">
        <div className="search-box">
          <span className="search-icon">🔍</span>
          <input
            type="text"
            placeholder="Search by keyword, post, ministry, or exam (e.g. IAS, Bank, Railway)..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          {searchQuery && (
            <button className="clear-btn" onClick={() => setSearchQuery('')}>
              ✕
            </button>
          )}
        </div>

        <div className="filter-chips">
          <label className="filter-label">Organization:</label>
          <button
            className={`chip ${selectedOrg === 'ALL' ? 'active' : ''}`}
            onClick={() => setSelectedOrg('ALL')}
          >
            All Organizations
          </button>
          <button
            className={`chip ${selectedOrg === 'org_ssc' ? 'active' : ''}`}
            onClick={() => setSelectedOrg('org_ssc')}
          >
            SSC
          </button>
          <button
            className={`chip ${selectedOrg === 'org_upsc' ? 'active' : ''}`}
            onClick={() => setSelectedOrg('org_upsc')}
          >
            UPSC
          </button>
          <button
            className={`chip ${selectedOrg === 'org_ibps' ? 'active' : ''}`}
            onClick={() => setSelectedOrg('org_ibps')}
          >
            IBPS (Banking)
          </button>
          <button
            className={`chip ${selectedOrg === 'org_rrb' ? 'active' : ''}`}
            onClick={() => setSelectedOrg('org_rrb')}
          >
            RRB (Railways)
          </button>
          <button
            className={`chip ${selectedOrg === 'org_tspsc' ? 'active' : ''}`}
            onClick={() => setSelectedOrg('org_tspsc')}
          >
            Telangana (TSPSC)
          </button>
        </div>
      </div>

      <div className="discovery-meta-row">
        <span className="result-count">
          Showing <strong>{filteredItems.length}</strong> verified public sector recruitment{filteredItems.length === 1 ? '' : 's'}
        </span>
        {(searchQuery || selectedOrg !== 'ALL' || selectedEdu !== 'ALL') && (
          <button
            className="text-link reset-link"
            onClick={() => {
              setSearchQuery('');
              setSelectedOrg('ALL');
              setSelectedEdu('ALL');
            }}
          >
            Reset Filters ✕
          </button>
        )}
      </div>

      {filteredItems.length === 0 ? (
        <div className="notice">
          No recruitments match your current filters. Try searching with a different term or resetting the filters.
        </div>
      ) : (
        <div className="recruitment-grid">
          {filteredItems.map((recruitment) => (
            <RecruitmentCard key={recruitment.id} recruitment={recruitment} />
          ))}
        </div>
      )}
    </div>
  );
}

function RecruitmentCard({ recruitment }: { recruitment: Recruitment }) {
  const post = recruitment.posts[0];
  const sourceCount = recruitment.official_sources.length;

  return (
    <article className="recruitment-card">
      <div className="card-topline">
        <span className="status-pill status-verified">✓ VERIFIED OFFICIAL</span>
        <span className="org-badge">
          {recruitment.organization_name || recruitment.organization_id}
        </span>
      </div>

      <h3>{recruitment.title}</h3>
      <p className="post-title">{post?.title ?? 'Recruitment details'}</p>

      <div className="card-facts">
        <span>
          <span aria-hidden="true">⌖</span> {post?.location_type ?? 'All India'}
        </span>
        <span>
          <span aria-hidden="true">▤</span>{' '}
          {post?.vacancies == null
            ? 'Vacancies in notice'
            : `${post.vacancies.toLocaleString('en-IN')} Vacancies`}
        </span>
        <span>
          <span aria-hidden="true">⏱</span>{' '}
          {recruitment.application_deadline
            ? `Deadline: ${new Date(recruitment.application_deadline).toLocaleDateString('en-IN', {
                day: 'numeric',
                month: 'short',
              })}`
            : 'Check notice'}
        </span>
      </div>

      {post?.salary_text && (
        <div className="card-salary">
          <strong>Pay:</strong> {post.salary_text}
        </div>
      )}

      <div className="card-bottom">
        <span className="source-count">
          {sourceCount} official source doc{sourceCount === 1 ? '' : 's'}
        </span>
        <Link
          className="button button-dark button-sm"
          href={`/recruitments/${encodeURIComponent(recruitment.id)}`}
        >
          Check Eligibility ↗
        </Link>
      </div>
    </article>
  );
}
