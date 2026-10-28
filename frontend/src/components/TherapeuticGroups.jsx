import React, { useState, useEffect } from 'react';
import { Tag, Search, ArrowUpRight, Layers } from 'lucide-react';
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
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '0.75rem' }}>
        <div>
          <h2 style={{ fontSize: '1.35rem', fontWeight: 700, color: 'var(--text-main)', margin: 0 }}>
            {language === 'hi' ? '68 चिकित्सीय समूह निर्देशिका' : '68 Reconciled PMBI Therapeutic Groups'}
          </h2>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', margin: '0.2rem 0 0' }}>
            Explore standardized classifications across {totalProductsCount.toLocaleString()} Jan Aushadhi generic products.
          </p>
        </div>

        <span style={{ fontSize: '0.8rem', color: 'var(--terracotta-600)', fontWeight: 600 }}>
          {groups.length} Standardized Groups
        </span>
      </div>

      {/* Filter Bar */}
      <div style={{ maxWidth: '380px', width: '100%', position: 'relative', display: 'flex', alignItems: 'center' }}>
        <input
          type="text"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          placeholder="Filter groups (e.g. Cardiovascular, Antibiotic)..."
          className="form-input"
          style={{ paddingLeft: '2rem', fontSize: '0.82rem' }}
        />
        <Search size={14} color="var(--text-dim)" style={{ position: 'absolute', left: '10px' }} />
      </div>

      {/* Groups Grid */}
      {!loading && !error && (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))',
          gap: '0.85rem',
        }}>
          {filteredGroups.map((g) => (
            <div
              key={g.name}
              onClick={() => onSelectGroup && onSelectGroup(g.name)}
              className="clean-card-interactive"
              style={{
                padding: '1rem 1.15rem',
                cursor: 'pointer',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                gap: '0.65rem',
              }}
            >
              <h3 style={{ fontSize: '0.92rem', fontWeight: 700, color: 'var(--text-main)', margin: 0 }}>
                {g.name}
              </h3>

              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                fontSize: '0.72rem',
                borderTop: '1px solid var(--border-subtle)',
                paddingTop: '0.45rem',
                color: 'var(--text-muted)',
              }}>
                <span style={{ fontWeight: 600, color: 'var(--terracotta-600)' }}>
                  {g.total_products} Products
                </span>
                <span style={{ display: 'flex', alignItems: 'center', gap: '0.2rem' }}>
                  <span>View</span>
                  <ArrowUpRight size={11} />
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
