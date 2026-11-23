import React, { useState, useEffect } from 'react';
import { Landmark, CheckCircle2, ExternalLink } from 'lucide-react';
import { api } from '../services/api';

export default function DataSources({ language = 'en' }) {
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const isHindi = language === 'hi';

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
          setError(err.message || (isHindi ? 'वैधानिक स्रोत लोड करने में विफल।' : 'Failed to fetch statutory sources.'));
          setLoading(false);
        }
      }
    };
    fetchSources();
    return () => {
      isMounted = false;
    };
  }, [isHindi]);

  return (
    <section className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '0.75rem' }}>
        <div>
          <h2 style={{ fontSize: '1.35rem', fontWeight: 700, color: 'var(--text-main)', margin: 0 }}>
            {isHindi ? 'सत्यापित सरकारी व वैधानिक डेटा स्रोत' : 'Statutory & Government Data Sources'}
          </h2>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', margin: '0.2rem 0 0' }}>
            {isHindi
              ? 'आधिकारिक भारतीय विनियामक प्राधिकरणों से डेटा प्रामाणिकता एवं अद्यतन स्थिति।'
              : 'Data provenance and synchronization status from official Indian regulatory authorities.'}
          </p>
        </div>

        <span style={{ fontSize: '0.78rem', color: 'var(--green-700)', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
          <CheckCircle2 size={13} />
          <span>{isHindi ? 'वैधानिक अनुपालन' : 'Statutory Compliance'}</span>
        </span>
      </div>

      {!loading && !error && (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
          gap: '1rem',
        }}>
          {sources.map((s) => (
            <div
              key={s.id || s.source_name}
              className="clean-card"
              style={{
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                gap: '0.85rem',
              }}
            >
              <div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.35rem' }}>
                  <span style={{ fontSize: '0.68rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--terracotta-600)', letterSpacing: '0.04em' }}>
                    {s.source_type}
                  </span>
                  <span className="badge badge-generic" style={{ fontSize: '0.68rem' }}>
                    {s.is_fresh ? (isHindi ? 'नवीनतम' : 'Fresh') : (isHindi ? 'सक्रिय' : 'Active')}
                  </span>
                </div>

                <h3 style={{ fontSize: '1.02rem', fontWeight: 700, color: 'var(--text-main)', margin: '0 0 0.25rem' }}>
                  {s.source_name}
                </h3>

                <p style={{ fontSize: '0.76rem', color: 'var(--text-secondary)', margin: 0 }}>
                  {s.description || (isHindi ? 'वैधानिक विनियामक और सार्वजनिक फार्मास्यूटिकल मूल्य सूची।' : 'Statutory regulatory and public pharmaceutical pricing catalogue.')}
                </p>
              </div>

              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                borderTop: '1px solid var(--border-subtle)',
                paddingTop: '0.65rem',
                fontSize: '0.75rem',
              }}>
                <span style={{ fontWeight: 600, color: 'var(--text-main)' }}>
                  {s.medicine_count !== undefined ? `${s.medicine_count.toLocaleString()} ${isHindi ? 'उत्पाद' : 'Products'}` : (isHindi ? 'सक्रिय' : 'Active')}
                </span>

                <a
                  href={s.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{ color: 'var(--terracotta-600)', fontWeight: 600, display: 'inline-flex', alignItems: 'center', gap: '0.2rem', fontSize: '0.75rem' }}
                >
                  <span>{isHindi ? 'आधिकारिक पोर्टल' : 'Portal'}</span>
                  <ExternalLink size={11} />
                </a>
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
