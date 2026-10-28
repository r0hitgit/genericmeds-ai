import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

export default function ClinicalGuidelines({ language }) {
  const [guidelines, setGuidelines] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedClass, setSelectedClass] = useState('');

  useEffect(() => {
    let isMounted = true;
    const fetchGuidelines = async () => {
      setLoading(true);
      try {
        const data = await api.getGuidelines(selectedClass || undefined);
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
  }, [selectedClass]);

  return (
    <section className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '1rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ fontSize: '1.5rem' }}>🔬</span>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--text-main)', margin: 0 }}>
              {language === 'hi' ? 'दवा वितरण नियम व सुरक्षा दिशानिर्देश' : 'Molecule Price Discovery & Safe Dispensing Rules'}
            </h2>
          </div>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', margin: '0.25rem 0 0' }}>
            Authoritative Schedule H/H1, Cold-Chain, Narrow Therapeutic Index (NTI), and prescription dispensing protocols.
          </p>
        </div>

        <span style={{ background: 'rgba(59, 130, 246, 0.1)', color: 'var(--blue-600)', border: '1px solid rgba(59, 130, 246, 0.25)', padding: '0.35rem 0.85rem', borderRadius: '9999px', fontSize: '0.78rem', fontWeight: 800 }}>
          {guidelines.length} Clinical Protocols
        </span>
      </div>

      {/* Loading & Error */}
      {loading && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '1rem' }}>
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="skeleton" style={{ height: '160px', borderRadius: '1rem' }} />
          ))}
        </div>
      )}

      {error && (
        <div style={{ padding: '1rem', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: '0.75rem', color: 'var(--rose-600)', fontSize: '0.85rem' }}>
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* Guidelines Grid */}
      {!loading && !error && (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))',
          gap: '1.25rem',
        }}>
          {guidelines.map((g) => (
            <div
              key={g.id || g.active_ingredient}
              className="glass-card-interactive"
              style={{
                padding: '1.25rem',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                gap: '0.85rem',
              }}
            >
              <div>
                <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '0.5rem' }}>
                  <div>
                    <h3 style={{ fontSize: '1.05rem', fontWeight: 800, color: 'var(--text-main)', margin: 0 }}>
                      {g.active_ingredient}
                    </h3>
                    <span style={{ fontSize: '0.74rem', color: 'var(--text-muted)', fontWeight: 500 }}>
                      {g.therapeutic_class}
                    </span>
                  </div>

                  {g.price_diff_pct && (
                    <span style={{
                      fontSize: '0.7rem',
                      fontWeight: 800,
                      background: 'var(--disclaimer-bg)',
                      color: 'var(--disclaimer-text)',
                      border: '1px solid var(--disclaimer-border)',
                      padding: '0.15rem 0.5rem',
                      borderRadius: '0.35rem',
                    }}>
                      {g.price_diff_pct}
                    </span>
                  )}
                </div>

                <div style={{
                  background: 'var(--disclaimer-bg)',
                  border: '1px solid var(--disclaimer-border)',
                  color: 'var(--disclaimer-text)',
                  padding: '0.75rem',
                  borderRadius: '0.5rem',
                  fontSize: '0.78rem',
                  lineHeight: 1.45,
                  marginTop: '0.75rem',
                }}>
                  <strong>⚠️ Safe Dispensing Rule:</strong> {g.dispensing_rule}
                </div>
              </div>

              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                borderTop: '1px solid var(--border-subtle)',
                paddingTop: '0.65rem',
                fontSize: '0.72rem',
                color: 'var(--text-dim)',
              }}>
                <span>Forms: {g.strengths_forms || 'Standard Oral / Topical'}</span>
                {g.reference_url && (
                  <a
                    href={g.reference_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{ color: 'var(--teal-600)', fontWeight: 600, display: 'inline-flex', alignItems: 'center', gap: '0.2rem' }}
                  >
                    <span>Reference</span>
                    <span>↗</span>
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
