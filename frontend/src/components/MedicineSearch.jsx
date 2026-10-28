import React, { useState, useEffect } from 'react';
import {
  Search,
  ShieldCheck,
  ArrowUpRight,
  Plus,
  X,
  CheckCircle2,
  AlertCircle,
  FileText,
  MapPin,
  TrendingDown
} from 'lucide-react';
import { api } from '../services/api';
import AlternativeComparisonModal from './AlternativeComparisonModal';

export default function MedicineSearch({
  language,
  onAddToSandbox,
  onLocateStores,
  initialQuery = '',
}) {
  const [query, setQuery] = useState(initialQuery);
  const [locationQuery, setLocationQuery] = useState('');
  const [janAushadhiOnly, setJanAushadhiOnly] = useState(false);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [selectedMedicine, setSelectedMedicine] = useState(null);

  const popularSearches = [
    'Dolo 650',
    'Augmentin 625 Duo',
    'Glycomet 500 SR',
    'Pan 40',
    'Amlopres 5',
    'Atorva 10',
    'Paracetamol',
    'Azithromycin',
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
    if (locationQuery.trim() && onLocateStores) {
      // If user provided a location in the second field, we can trigger search
      doSearch();
    } else {
      doSearch();
    }
  };

  const handleQuickSearch = (term) => {
    setQuery(term);
    doSearch(term);
  };

  return (
    <section className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '3rem' }}>
      {/* Hero Section matching screenshot layout */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        {/* Top Tagline Pill */}
        <div className="hero-pill-badge">
          <span>Trusted medicine. Transparent prices.</span>
        </div>

        {/* Hero Title */}
        <h1 style={{
          fontSize: 'clamp(2rem, 4.5vw, 3rem)',
          fontWeight: 800,
          color: 'var(--text-main)',
          lineHeight: 1.15,
          letterSpacing: '-0.025em',
          maxWidth: '750px',
          margin: 0,
        }}>
          Affordable, verified generic medicine in India
        </h1>

        {/* Hero Subtitle */}
        <p style={{
          fontSize: '1rem',
          color: 'var(--text-secondary)',
          lineHeight: 1.6,
          maxWidth: '680px',
          margin: 0,
        }}>
          Find accredited Jan Aushadhi alternatives, understand active salts with AI, and get verified price comparisons across PMBJP and NPPA.
        </p>

        {/* Search Bar Container with Dual Inputs matching the screenshot */}
        <form
          onSubmit={handleSubmit}
          style={{
            background: 'var(--bg-surface)',
            border: '1px solid var(--border-subtle)',
            borderRadius: '16px',
            padding: '10px',
            boxShadow: 'var(--card-shadow)',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            flexWrap: 'wrap',
            maxWidth: '920px',
          }}
        >
          {/* Input 1: Medicine / Brand */}
          <div style={{ flex: '1 1 280px', position: 'relative', display: 'flex', alignItems: 'center' }}>
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Treatment, e.g. Dolo 650, Augmentin, Pan 40"
              style={{
                width: '100%',
                padding: '11px 14px',
                borderRadius: '8px',
                border: '1px solid var(--border-subtle)',
                background: 'var(--bg-surface)',
                color: 'var(--text-main)',
                fontSize: '0.88rem',
                outline: 'none',
              }}
            />
            {query && (
              <button
                type="button"
                onClick={() => setQuery('')}
                style={{
                  position: 'absolute',
                  right: '10px',
                  color: 'var(--text-dim)',
                  display: 'flex',
                  alignItems: 'center',
                }}
              >
                <X size={15} />
              </button>
            )}
          </div>

          {/* Input 2: Secondary filter (PIN Code / Salt / City) */}
          <div style={{ flex: '1 1 240px', display: 'flex', alignItems: 'center' }}>
            <input
              type="text"
              value={locationQuery}
              onChange={(e) => setLocationQuery(e.target.value)}
              placeholder="City, PIN code, or salt (e.g. Paracetamol)"
              style={{
                width: '100%',
                padding: '11px 14px',
                borderRadius: '8px',
                border: '1px solid var(--border-subtle)',
                background: 'var(--bg-surface)',
                color: 'var(--text-main)',
                fontSize: '0.88rem',
                outline: 'none',
              }}
            />
          </div>

          {/* Action Button: Terracotta */}
          <button
            type="submit"
            disabled={loading}
            className="btn-primary"
            style={{
              padding: '11px 22px',
              fontSize: '0.88rem',
              whiteSpace: 'nowrap',
              borderRadius: '8px',
            }}
          >
            <Search size={16} />
            <span>{loading ? 'Searching...' : 'Find medicines'}</span>
          </button>
        </form>

        {/* Quick Suggestion Pills */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
          <span>Popular:</span>
          {popularSearches.map((term) => (
            <button
              key={term}
              onClick={() => handleQuickSearch(term)}
              style={{
                background: 'var(--bg-surface)',
                border: '1px solid var(--border-subtle)',
                borderRadius: '6px',
                padding: '3px 10px',
                fontSize: '0.78rem',
                color: 'var(--text-secondary)',
                fontWeight: 500,
                transition: 'all var(--transition-fast)',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = 'var(--terracotta-600)';
                e.currentTarget.style.color = 'var(--terracotta-600)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = 'var(--border-subtle)';
                e.currentTarget.style.color = 'var(--text-secondary)';
              }}
            >
              {term}
            </button>
          ))}
        </div>
      </div>

      {/* 4 Value Proposition Cards (matching the 4 cards in the screenshot) */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
        gap: '1rem',
      }}>
        {/* Card 1 */}
        <div className="clean-card" style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-main)', margin: 0 }}>
            Verified Jan Aushadhi
          </h3>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', margin: 0, lineHeight: 1.5 }}>
            Accreditation and active ingredient composition checked before listing.
          </p>
        </div>

        {/* Card 2 */}
        <div className="clean-card" style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-main)', margin: 0 }}>
            All-inclusive savings
          </h3>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', margin: 0, lineHeight: 1.5 }}>
            Save up to 80% with standardized government ceiling prices against branded MRPs.
          </p>
        </div>

        {/* Card 3 */}
        <div className="clean-card" style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-main)', margin: 0 }}>
            AI report summary
          </h3>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', margin: 0, lineHeight: 1.5 }}>
            Plain-language summary of your medicine salts, reviewed by clinical protocols.
          </p>
        </div>

        {/* Card 4 */}
        <div className="clean-card" style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-main)', margin: 0 }}>
            Nearby Kendra locator
          </h3>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', margin: 0, lineHeight: 1.5 }}>
            Locate authorized PMBJP pharmacies near you with GPS coordinates.
          </p>
        </div>
      </div>

      {/* "How it works" 4-Step Section (matching the screenshot) */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-main)', margin: 0 }}>
          How it works
        </h2>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
          gap: '1rem',
        }}>
          {/* Step 1 */}
          <div className="clean-card" style={{ padding: '1.1rem 1.25rem' }}>
            <span style={{ fontSize: '0.74rem', color: 'var(--text-dim)', fontWeight: 600 }}>1</span>
            <div style={{ fontSize: '0.92rem', fontWeight: 700, color: 'var(--text-main)', marginTop: '0.2rem' }}>
              Search medicine
            </div>
          </div>

          {/* Step 2 */}
          <div className="clean-card" style={{ padding: '1.1rem 1.25rem' }}>
            <span style={{ fontSize: '0.74rem', color: 'var(--text-dim)', fontWeight: 600 }}>2</span>
            <div style={{ fontSize: '0.92rem', fontWeight: 700, color: 'var(--text-main)', marginTop: '0.2rem' }}>
              Compare options
            </div>
          </div>

          {/* Step 3 */}
          <div className="clean-card" style={{ padding: '1.1rem 1.25rem' }}>
            <span style={{ fontSize: '0.74rem', color: 'var(--text-dim)', fontWeight: 600 }}>3</span>
            <div style={{ fontSize: '0.92rem', fontWeight: 700, color: 'var(--text-main)', marginTop: '0.2rem' }}>
              Locate store
            </div>
          </div>

          {/* Step 4 */}
          <div className="clean-card" style={{ padding: '1.1rem 1.25rem' }}>
            <span style={{ fontSize: '0.74rem', color: 'var(--text-dim)', fontWeight: 600 }}>4</span>
            <div style={{ fontSize: '0.92rem', fontWeight: 700, color: 'var(--text-main)', marginTop: '0.2rem' }}>
              Save with support
            </div>
          </div>
        </div>
      </div>

      {/* Search Results Area */}
      {loading && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '1rem' }}>
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="clean-card" style={{ height: '180px', opacity: 0.5 }} />
          ))}
        </div>
      )}

      {error && (
        <div style={{
          padding: '1.25rem',
          background: 'var(--disclaimer-bg)',
          border: '1px solid var(--disclaimer-border)',
          borderRadius: '10px',
          color: 'var(--terracotta-700)',
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
        }}>
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      {!loading && results && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '0.75rem' }}>
            <h2 style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--text-main)', margin: 0 }}>
              Search Results for "{query}"
            </h2>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>
              {results.total} medicines found
            </span>
          </div>

          {results.items.length === 0 ? (
            <div style={{
              padding: '3rem 1.5rem',
              textAlign: 'center',
              background: 'var(--bg-surface)',
              borderRadius: '12px',
              border: '1px solid var(--border-subtle)',
            }}>
              <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-main)', margin: '0 0 0.5rem' }}>
                No exact match found for "{query}"
              </h3>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', maxWidth: '440px', margin: '0 auto 1.25rem' }}>
                Try searching by common brand name (e.g., Dolo 650, Augmentin) or active salt (e.g., Paracetamol).
              </p>
            </div>
          ) : (
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))',
              gap: '1rem',
            }}>
              {results.items.map((med) => {
                const isJanAushadhi = med.is_jan_aushadhi;
                const price = med.latest_price ? `₹${med.latest_price.amount_inr}` : 'Price unverified';
                const unitPrice = med.latest_price?.unit_price_inr
                  ? `₹${med.latest_price.unit_price_inr} / ${med.pack_unit?.replace(/s$/, '') || 'unit'}`
                  : '';

                return (
                  <div
                    key={med.id}
                    className="clean-card-interactive"
                    style={{
                      display: 'flex',
                      flexDirection: 'column',
                      justifyContent: 'space-between',
                      gap: '0.85rem',
                    }}
                  >
                    <div>
                      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '0.5rem' }}>
                        <div>
                          <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-main)', margin: 0 }}>
                            {med.brand_name}
                          </h3>
                          {med.drug_code && (
                            <span style={{ fontSize: '0.7rem', color: 'var(--text-dim)', fontWeight: 500 }}>
                              Code: {med.drug_code}
                            </span>
                          )}
                        </div>

                        {isJanAushadhi ? (
                          <span className="badge badge-generic">
                            <ShieldCheck size={12} />
                            <span>PMBJP Kendra</span>
                          </span>
                        ) : (
                          <span className="badge badge-brand">
                            Branded MRP
                          </span>
                        )}
                      </div>

                      <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>
                        {med.dosage_form} • {med.pack_size} {med.pack_unit} • {med.release_type}
                      </div>

                      {med.ingredients && med.ingredients.length > 0 && (
                        <div style={{
                          background: 'var(--bg-surface-elevated)',
                          padding: '0.55rem 0.75rem',
                          borderRadius: '6px',
                          fontSize: '0.76rem',
                          color: 'var(--text-secondary)',
                          marginTop: '0.65rem',
                          lineHeight: 1.4,
                        }}>
                          <strong>Active salts:</strong>{' '}
                          {med.ingredients.map((i) => `${i.name} (${i.strength_value} ${i.strength_unit})`).join(', ')}
                        </div>
                      )}
                    </div>

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
                        <div style={{ fontSize: '1.15rem', fontWeight: 800, color: 'var(--text-main)' }}>
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
                          style={{
                            padding: '0.4rem 0.65rem',
                            borderRadius: '6px',
                            background: 'var(--bg-surface)',
                            border: '1px solid var(--border-subtle)',
                            fontSize: '0.74rem',
                            fontWeight: 600,
                            color: 'var(--text-secondary)',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.25rem',
                          }}
                        >
                          <Plus size={13} />
                          <span>Sandbox</span>
                        </button>

                        <button
                          onClick={() => setSelectedMedicine(med)}
                          className="btn-primary"
                          style={{
                            padding: '0.45rem 0.85rem',
                            fontSize: '0.76rem',
                            borderRadius: '6px',
                          }}
                        >
                          <span>Alternatives</span>
                          <ArrowUpRight size={13} />
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

      {/* Alternative comparison modal */}
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
