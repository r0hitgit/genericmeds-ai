import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

export default function DataSources({ language }) {
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let isMounted = true;
    const fetchSources = async () => {
      try {
        const data = await api.getSources();
        if (isMounted) {
          setSources(data || []);
          setLoading(false);
        }
      } catch (err) {
        if (isMounted) {
          setError(err.message || 'Failed to fetch statutory sources.');
          setLoading(false);
        }
      }
    };
    fetchSources();
    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <section className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '1rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ fontSize: '1.5rem' }}>🏛️</span>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--text-main)', margin: 0 }}>
              {language === 'hi' ? 'सत्यापित सरकारी व वैधानिक डेटा स्रोत' : 'Official Statutory & Government Data Sources'}
            </h2>
          </div>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', margin: '0.25rem 0 0' }}>
            Full data provenance and synchronization logs from official Indian statutory authorities.
          </p>
        </div>

        <span style={{ background: 'rgba(16, 185, 129, 0.1)', color: 'var(--emerald-600)', border: '1px solid rgba(16, 185, 129, 0.25)', padding: '0.35rem 0.85rem', borderRadius: '9999px', fontSize: '0.78rem', fontWeight: 800 }}>
          Statutory Compliance
        </span>
      </div>

      {loading && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '1rem' }}>
          {[1, 2, 3].map((i) => (
            <div key={i} className="skeleton" style={{ height: '140px', borderRadius: '1rem' }} />
          ))}
        </div>
      )}

      {error && (
        <div style={{ padding: '1rem', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: '0.75rem', color: 'var(--rose-600)', fontSize: '0.85rem' }}>
          <strong>Error:</strong> {error}
        </div>
      )}

      {!loading && !error && (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
          gap: '1.25rem',
        }}>
          {sources.map((s) => (
            <div
              key={s.id || s.source_name}
              className="glass-card-interactive"
              style={{
                padding: '1.25rem',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                gap: '1rem',
              }}
            >
              <div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.4rem' }}>
                  <span style={{ fontSize: '0.7rem', fontWeight: 800, textTransform: 'uppercase', color: 'var(--teal-600)', letterSpacing: '0.04em' }}>
                    {s.source_type}
                  </span>
                  <span style={{
                    fontSize: '0.68rem',
                    fontWeight: 700,
                    padding: '0.15rem 0.45rem',
                    borderRadius: '4px',
                    background: s.is_fresh ? 'rgba(16, 185, 129, 0.15)' : 'rgba(245, 158, 11, 0.15)',
                    color: s.is_fresh ? 'var(--emerald-600)' : 'var(--amber-600)',
                  }}>
                    {s.is_fresh ? 'Verified Fresh' : 'Under Review'}
                  </span>
                </div>

                <h3 style={{ fontSize: '1.05rem', fontWeight: 800, color: 'var(--text-main)', margin: '0 0 0.35rem' }}>
                  {s.source_name}
                </h3>

                <p style={{ fontSize: '0.76rem', color: 'var(--text-secondary)', margin: 0 }}>
                  {s.description || 'Statutory regulatory and public pharmaceutical pricing catalogue.'}
                </p>
              </div>

              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                borderTop: '1px solid var(--border-subtle)',
                paddingTop: '0.75rem',
                fontSize: '0.75rem',
              }}>
                <span style={{ fontWeight: 700, color: 'var(--text-main)' }}>
                  {s.medicine_count !== undefined ? `${s.medicine_count.toLocaleString()} Products` : 'Active'}
                </span>

                <a
                  href={s.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn-outline-teal"
                  style={{ fontSize: '0.74rem', padding: '0.3rem 0.65rem' }}
                >
                  <span>Official Portal</span>
                  <span>↗</span>
                </a>
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
