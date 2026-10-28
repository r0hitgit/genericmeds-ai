import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import AlternativeComparisonModal from './AlternativeComparisonModal';

export default function MedicineSearch({
  language,
  onAddToSandbox,
  onLocateStores,
  initialQuery = '',
}) {
  const [query, setQuery] = useState(initialQuery);
  const [janAushadhiOnly, setJanAushadhiOnly] = useState(false);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [selectedMedicine, setSelectedMedicine] = useState(null);

  const popularSearches = [
    { label: 'Dolo 650', query: 'Dolo 650' },
    { label: 'Augmentin 625 Duo', query: 'Augmentin 625 Duo' },
    { label: 'Glycomet 500 SR', query: 'Glycomet 500 SR' },
    { label: 'Pan 40', query: 'Pan 40' },
    { label: 'Amlopres 5', query: 'Amlopres 5' },
    { label: 'Atorva 10', query: 'Atorva 10' },
    { label: 'Azithromycin 500', query: 'Azithromycin 500' },
    { label: 'Paracetamol', query: 'Paracetamol' },
  ];

  const doSearch = async (searchTerm = query, filterJanAushadhi = janAushadhiOnly) => {
    const trimmed = searchTerm.trim();
    if (!trimmed) return;
    setLoading(true);
    setError(null);
    try {
      const data = await api.searchMedicines(trimmed, 24, 0, filterJanAushadhi);
      setResults(data);
    } catch (err) {
      setError(err.message || 'Error occurred while querying catalogue.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (initialQuery) {
      setQuery(initialQuery);
      doSearch(initialQuery);
    }
  }, [initialQuery]);

  const handleSubmit = (e) => {
    e.preventDefault();
    doSearch();
  };

  const handleQuickSearch = (term) => {
    setQuery(term);
    doSearch(term);
  };

  return (
    <section className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Hero Header Area */}
      <div style={{ textAlign: 'center', maxWidth: '780px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <div style={{ display: 'inline-flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}>
          <span style={{
            background: 'rgba(13, 148, 136, 0.1)',
            border: '1px solid rgba(13, 148, 136, 0.3)',
            color: 'var(--teal-600)',
            fontSize: '0.74rem',
            fontWeight: 700,
            padding: '0.25rem 0.85rem',
            borderRadius: '9999px',
            textTransform: 'uppercase',
            letterSpacing: '0.04em',
          }}>
            🏛️ Official PMBJP Jan Aushadhi & NPPA Data Integration
          </span>
        </div>

        <h1 style={{
          fontSize: 'clamp(1.75rem, 4vw, 2.75rem)',
          fontWeight: 800,
          color: 'var(--text-main)',
          lineHeight: 1.15,
          letterSpacing: '-0.03em',
          margin: 0,
        }}>
          {language === 'hi' ? (
            <>सत्यापित जेनेरिक दवाएं खोजें। <span style={{ color: 'var(--teal-600)' }}>80% तक बचत करें।</span></>
          ) : (
            <>Discover Affordable Generic Medicines. <span style={{ color: 'var(--teal-600)' }}>Save up to 80%.</span></>
          )}
        </h1>

        <p style={{ fontSize: '0.95rem', color: 'var(--text-secondary)', margin: 0, lineHeight: 1.6 }}>
          {language === 'hi'
            ? 'ब्रांडेड दवाओं के सटीक सक्रिय तत्व (Active Ingredients) से प्रधानमंत्री भारतीय जन औषधि परियोजना (PMBJP) के सत्यापित जेनेरिक विकल्प और मूल्य तुलना देखें।'
            : 'Search branded medicines to discover exact composition generic formulations under Pradhan Mantri Bhartiya Janaushadhi Pariyojana (PMBJP) and compare statutory ceiling prices.'}
        </p>

        {/* Big Search Form */}
        <form
          onSubmit={handleSubmit}
          id="medicine-search-form"
          style={{
            position: 'relative',
            display: 'flex',
            alignItems: 'center',
            background: 'var(--bg-surface)',
            border: '2px solid var(--teal-600)',
            borderRadius: '1.25rem',
            boxShadow: 'var(--card-shadow-hover)',
            overflow: 'hidden',
            marginTop: '0.5rem',
          }}
        >
          <input
            id="medicine-search-input"
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={
              language === 'hi'
                ? 'दवा का नाम या सॉल्ट खोजें (उदा. Dolo 650, Augmentin 625 Duo, Pan 40)...'
                : 'Search brand (e.g. Dolo 650, Augmentin 625 Duo, Pan 40) or generic salt (Paracetamol)...'
            }
            style={{
              flex: 1,
              border: 'none',
              background: 'transparent',
              padding: '1rem 1.25rem',
              fontSize: '1rem',
              color: 'var(--text-main)',
              outline: 'none',
              fontWeight: 500,
            }}
          />

          {query && (
            <button
              type="button"
              onClick={() => setQuery('')}
              style={{
                padding: '0.5rem',
                color: 'var(--text-dim)',
                fontSize: '1rem',
              }}
              title="Clear search"
            >
              ✕
            </button>
          )}

          <button
            type="submit"
            id="search-submit-btn"
            disabled={loading}
            style={{
              background: 'var(--teal-600)',
              color: '#ffffff',
              fontWeight: 700,
              padding: '1rem 1.75rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              fontSize: '0.95rem',
              transition: 'background-color var(--transition-fast)',
            }}
          >
            <span>{loading ? 'Searching...' : 'Search'}</span>
            <span>🔍</span>
          </button>
        </form>

        {/* Search Controls: Jan Aushadhi Filter & Suggestions */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.75rem', marginTop: '0.25rem' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '0.45rem', fontSize: '0.8rem', color: 'var(--text-secondary)', cursor: 'pointer', userSelect: 'none' }}>
            <input
              id="filter-jan-aushadhi"
              type="checkbox"
              checked={janAushadhiOnly}
              onChange={(e) => {
                setJanAushadhiOnly(e.target.checked);
                if (query.trim()) doSearch(query, e.target.checked);
              }}
              style={{ accentColor: 'var(--teal-600)' }}
            />
            <span>Filter PMBJP Jan Aushadhi Only</span>
          </label>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', flexWrap: 'wrap', fontSize: '0.78rem' }}>
            <span style={{ color: 'var(--text-muted)' }}>Popular:</span>
            {popularSearches.map((s) => (
              <button
                key={s.label}
                onClick={() => handleQuickSearch(s.query)}
                style={{
                  background: 'var(--bg-surface)',
                  border: '1px solid var(--border-medium)',
                  color: 'var(--teal-600)',
                  fontWeight: 600,
                  padding: '0.2rem 0.55rem',
                  borderRadius: '0.5rem',
                  fontSize: '0.74rem',
                  transition: 'all var(--transition-fast)',
                }}
              >
                {s.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Loading Skeletons */}
      {loading && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '1rem' }}>
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="skeleton" style={{ height: '220px', borderRadius: '1rem' }} />
          ))}
        </div>
      )}

      {/* Error state */}
      {error && (
        <div style={{
          padding: '1.25rem',
          background: 'rgba(239, 68, 68, 0.1)',
          border: '1px solid rgba(239, 68, 68, 0.3)',
          borderRadius: '1rem',
          color: 'var(--rose-600)',
          textAlign: 'center',
        }}>
          <strong>Failed to load medicines:</strong> {error}
        </div>
      )}

      {/* Search Results Grid */}
      {!loading && results && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '0.75rem' }}>
            <h2 style={{ fontSize: '1.15rem', fontWeight: 800, color: 'var(--text-main)', margin: 0 }}>
              Catalogue Results for "{query}"
            </h2>
            <span style={{
              background: 'var(--bg-surface-elevated)',
              color: 'var(--text-secondary)',
              fontSize: '0.78rem',
              fontWeight: 700,
              padding: '0.25rem 0.75rem',
              borderRadius: '9999px',
              border: '1px solid var(--border-subtle)',
            }}>
              {results.total} medicines found
            </span>
          </div>

          {results.items.length === 0 ? (
            <div style={{
              padding: '3rem 1.5rem',
              textAlign: 'center',
              background: 'var(--bg-surface)',
              borderRadius: '1rem',
              border: '1px solid var(--border-subtle)',
            }}>
              <div style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>🔍</div>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-main)' }}>
                No verified medicines found matching "{query}"
              </h3>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', maxWidth: '480px', margin: '0.5rem auto 1rem' }}>
                Please check the spelling of the brand name or try searching by generic chemical composition (e.g., Paracetamol, Amoxicillin, Metformin).
              </p>
              <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'center', flexWrap: 'wrap' }}>
                <button onClick={() => handleQuickSearch('Dolo 650')} className="btn-secondary" style={{ fontSize: '0.8rem' }}>
                  Search Dolo 650
                </button>
                <button onClick={() => handleQuickSearch('Augmentin 625 Duo')} className="btn-secondary" style={{ fontSize: '0.8rem' }}>
                  Search Augmentin 625 Duo
                </button>
              </div>
            </div>
          ) : (
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))',
              gap: '1.25rem',
            }}>
              {results.items.map((med) => {
                const isJanAushadhi = med.is_jan_aushadhi;
                const price = med.latest_price ? `₹${med.latest_price.amount_inr}` : 'Price unverified';
                const unitPrice = med.latest_price?.unit_price_inr ? `₹${med.latest_price.unit_price_inr} / ${med.pack_unit?.replace(/s$/, '') || 'unit'}` : '';

                return (
                  <div
                    key={med.id}
                    className="glass-card-interactive"
                    style={{
                      padding: '1.25rem',
                      display: 'flex',
                      flexDirection: 'column',
                      justifyContent: 'space-between',
                      gap: '1rem',
                    }}
                  >
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '0.5rem' }}>
                        <div>
                          <h3 style={{ fontSize: '1.1rem', fontWeight: 800, color: 'var(--text-main)', margin: 0 }}>
                            {med.brand_name}
                          </h3>
                          {med.drug_code && (
                            <span style={{ fontSize: '0.68rem', color: 'var(--text-dim)', fontWeight: 600 }}>
                              Code: {med.drug_code}
                            </span>
                          )}
                        </div>
                        {isJanAushadhi ? (
                          <span className="badge badge-generic">
                            PMBJP Jan Aushadhi
                          </span>
                        ) : (
                          <span className="badge badge-brand">
                            Branded MRP
                          </span>
                        )}
                      </div>

                      <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 500 }}>
                        {med.dosage_form} • {med.pack_size} {med.pack_unit} • {med.release_type}
                      </div>

                      {med.ingredients && med.ingredients.length > 0 && (
                        <div style={{
                          background: 'var(--bg-surface-elevated)',
                          padding: '0.6rem 0.75rem',
                          borderRadius: '0.5rem',
                          border: '1px solid var(--border-subtle)',
                          fontSize: '0.76rem',
                          color: 'var(--text-secondary)',
                          lineHeight: 1.4,
                        }}>
                          <strong>Composition:</strong>{' '}
                          {med.ingredients.map((i) => `${i.name} (${i.strength_value} ${i.strength_unit})`).join(', ')}
                        </div>
                      )}

                      {med.manufacturer_name && (
                        <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>
                          Mfr: {med.manufacturer_name}
                        </div>
                      )}
                    </div>

                    {/* Price and Actions Bottom Bar */}
                    <div style={{
                      paddingTop: '0.75rem',
                      borderTop: '1px solid var(--border-subtle)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      flexWrap: 'wrap',
                      gap: '0.5rem',
                    }}>
                      <div>
                        <div style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--text-main)' }}>
                          {price}
                        </div>
                        {unitPrice && (
                          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                            {unitPrice}
                          </div>
                        )}
                      </div>

                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                        <button
                          onClick={() => onAddToSandbox && onAddToSandbox(med)}
                          title="Add to Comparison Sandbox"
                          style={{
                            padding: '0.45rem 0.65rem',
                            borderRadius: '0.55rem',
                            background: 'var(--bg-surface-elevated)',
                            border: '1px solid var(--border-medium)',
                            fontSize: '0.75rem',
                            fontWeight: 600,
                            color: 'var(--text-main)',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.25rem',
                          }}
                        >
                          <span>+</span>
                          <span>Sandbox</span>
                        </button>

                        <button
                          onClick={() => setSelectedMedicine(med)}
                          className="btn-primary"
                          style={{
                            padding: '0.45rem 0.85rem',
                            fontSize: '0.78rem',
                          }}
                        >
                          <span>Alternatives</span>
                          <span>↗</span>
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* Modal for Alternatives comparison */}
      {selectedMedicine && (
        <AlternativeComparisonModal
          medicine={selectedMedicine}
          onClose={() => setSelectedMedicine(null)}
          onAddToSandbox={onAddToSandbox}
          onLocateStores={onLocateStores}
          language={language}
        />
      )}
    </section>
  );
}
