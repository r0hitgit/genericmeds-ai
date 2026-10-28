import React, { useState, useEffect } from 'react';
import { FlaskConical, AlertCircle, ExternalLink } from 'lucide-react';
import { api } from '../services/api';

export default function ClinicalGuidelines({ language }) {
  const [guidelines, setGuidelines] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let isMounted = true;
    const fetchGuidelines = async () => {
      setLoading(true);
      try {
        const data = await api.getGuidelines();
        if (isMounted) {
          setGuidelines(data || []);
          setLoading(false);
        }
      } catch (err) {
        if (isMounted) {
          setError(err.message || 'Failed to load clinical guidelines.');
          setLoading(false);
        }
      }
    };
    fetchGuidelines();
    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <section className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '0.75rem' }}>
        <div>
          <h2 style={{ fontSize: '1.35rem', fontWeight: 700, color: 'var(--text-main)', margin: 0 }}>
            {language === 'hi' ? 'दवा वितरण नियम व सुरक्षा दिशानिर्देश' : 'Safe Dispensing Protocols & Guidelines'}
          </h2>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', margin: '0.2rem 0 0' }}>
            Authoritative Schedule H/H1, Cold-Chain, and Narrow Therapeutic Index (NTI) rules.
          </p>
        </div>

        <span style={{ fontSize: '0.8rem', color: 'var(--terracotta-600)', fontWeight: 600 }}>
          {guidelines.length} Clinical Protocols
        </span>
      </div>

      {/* Guidelines Grid */}
      {!loading && !error && (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
          gap: '1rem',
        }}>
          {guidelines.map((g) => (
            <div
              key={g.id || g.active_ingredient}
              className="clean-card"
              style={{
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                gap: '0.75rem',
              }}
            >
              <div>
                <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '0.5rem' }}>
                  <div>
                    <h3 style={{ fontSize: '1.02rem', fontWeight: 700, color: 'var(--text-main)', margin: 0 }}>
                      {g.active_ingredient}
                    </h3>
                    <span style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>
                      {g.therapeutic_class}
                    </span>
                  </div>

                  {g.price_diff_pct && (
                    <span className="badge badge-savings">
                      {g.price_diff_pct}
                    </span>
                  )}
                </div>

                <div style={{
                  background: 'var(--disclaimer-bg)',
                  border: '1px solid var(--disclaimer-border)',
                  color: 'var(--disclaimer-text)',
                  padding: '0.65rem 0.85rem',
                  borderRadius: '6px',
                  fontSize: '0.76rem',
                  lineHeight: 1.45,
                  marginTop: '0.65rem',
                  display: 'flex',
                  gap: '0.35rem',
                  alignItems: 'flex-start',
                }}>
                  <AlertCircle size={14} style={{ flexShrink: 0, marginTop: '2px' }} />
                  <div>
                    <strong>Rule:</strong> {g.dispensing_rule}
                  </div>
                </div>
              </div>

              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                borderTop: '1px solid var(--border-subtle)',
                paddingTop: '0.55rem',
                fontSize: '0.72rem',
                color: 'var(--text-dim)',
              }}>
                <span>Forms: {g.strengths_forms || 'Oral / Topical'}</span>
                {g.reference_url && (
                  <a
                    href={g.reference_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{ color: 'var(--terracotta-600)', fontWeight: 600, display: 'inline-flex', alignItems: 'center', gap: '0.2rem' }}
                  >
                    <span>Reference</span>
                    <ExternalLink size={11} />
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
