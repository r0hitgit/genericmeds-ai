import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

export default function TherapeuticGroups({ onSelectGroup, language }) {
  const [groups, setGroups] = useState([]);
  const [filter, setFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let isMounted = true;
    const fetchGroups = async () => {
      try {
        const data = await api.getTherapeuticGroups();
        if (isMounted) {
          setGroups(data || []);
          setLoading(false);
        }
      } catch (err) {
        if (isMounted) {
          setError(err.message || 'Failed to fetch therapeutic groups.');
          setLoading(false);
        }
      }
    };
    fetchGroups();
    return () => {
      isMounted = false;
    };
  }, []);

  const filteredGroups = groups.filter((g) =>
    g.name.toLowerCase().includes(filter.toLowerCase())
  );

  const totalProductsCount = groups.reduce((acc, g) => acc + (g.total_products || 0), 0);

  return (
    <section className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '1rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ fontSize: '1.5rem' }}>🏷️</span>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--text-main)', margin: 0 }}>
              {language === 'hi' ? '68 चिकित्सीय समूह निर्देशिका' : '68 Reconciled PMBI Therapeutic Groups'}
            </h2>
          </div>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', margin: '0.25rem 0 0' }}>
            Explore complete clinical classifications across {totalProductsCount.toLocaleString()} Jan Aushadhi generic products.
          </p>
        </div>

        <span style={{ background: 'rgba(13, 148, 136, 0.1)', color: 'var(--teal-600)', border: '1px solid rgba(13, 148, 136, 0.25)', padding: '0.35rem 0.85rem', borderRadius: '9999px', fontSize: '0.78rem', fontWeight: 800 }}>
          {groups.length} Standardized Groups
        </span>
      </div>

      {/* Filter Bar */}
      <div style={{ maxWidth: '420px', width: '100%' }}>
        <input
          type="text"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          placeholder="Filter classifications (e.g. Cardiovascular, Antibiotic, Vitamins)..."
          className="form-input"
          style={{ fontSize: '0.85rem', padding: '0.65rem 1rem' }}
        />
      </div>

      {/* Loading & Error */}
      {loading && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '1rem' }}>
          {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
            <div key={i} className="skeleton" style={{ height: '100px', borderRadius: '0.75rem' }} />
          ))}
        </div>
      )}

      {error && (
        <div style={{ padding: '1rem', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: '0.75rem', color: 'var(--rose-600)', fontSize: '0.85rem' }}>
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* Groups Grid */}
      {!loading && !error && (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
          gap: '1rem',
        }}>
          {filteredGroups.map((g) => (
            <div
              key={g.name}
              onClick={() => onSelectGroup && onSelectGroup(g.name)}
              className="glass-card-interactive"
              style={{
                padding: '1.1rem',
                cursor: 'pointer',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                gap: '0.75rem',
              }}
            >
              <div>
                <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-main)', margin: 0 }}>
                  {g.name}
                </h3>
              </div>

              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                fontSize: '0.72rem',
                borderTop: '1px solid var(--border-subtle)',
                paddingTop: '0.5rem',
                color: 'var(--text-muted)',
              }}>
                <span style={{ fontWeight: 700, color: 'var(--teal-600)' }}>
                  {g.total_products} Products
                </span>
                <span style={{ color: 'var(--text-dim)' }}>
                  {g.priced_products} Priced • Click to View ↗
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
