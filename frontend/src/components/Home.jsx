import React, { useState } from 'react';
import {
  Search,
  ShieldCheck,
  ArrowUpRight,
  Plus,
  X,
  AlertCircle,
  Building2,
  TrendingDown,
  Sparkles,
  MapPin
} from 'lucide-react';
import AlternativeComparisonModal from './AlternativeComparisonModal';

export default function Home({
  language,
  searchQuery,
  setSearchQuery,
  searchResults,
  searchLoading,
  searchError,
  onExecuteSearch,
  onAddToSandbox,
  onLocateStores,
  setActiveTab,
  onClearSearch,
}) {
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

  const handleSubmit = (e) => {
    e.preventDefault();
    onExecuteSearch(searchQuery);
  };

  const handleQuickSearch = (term) => {
    setSearchQuery(term);
    onExecuteSearch(term);
  };

  return (
    <section className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '2.5rem' }}>
      {/* Hero Header Area matching screenshot */}
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

        {/* Single Search Bar (Only one bar as requested, with no city/pincode bar) */}
        <form
          onSubmit={handleSubmit}
          style={{
            background: 'var(--bg-surface)',
            border: '1px solid var(--border-subtle)',
            borderRadius: '16px',
            padding: '8px 10px',
            boxShadow: 'var(--card-shadow)',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            maxWidth: '820px',
            position: 'relative',
          }}
        >
          <div style={{ flex: 1, position: 'relative', display: 'flex', alignItems: 'center' }}>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Treatment, e.g. Dolo 650, Augmentin, Pan 40"
              style={{
                width: '100%',
                padding: '11px 14px',
                borderRadius: '8px',
                border: 'none',
                background: 'transparent',
                color: 'var(--text-main)',
                fontSize: '0.92rem',
                outline: 'none',
                fontWeight: 500,
              }}
            />
            {searchQuery && (
              <button
                type="button"
                onClick={() => {
                  setSearchQuery('');
                  if (onClearSearch) onClearSearch();
                }}
                style={{
                  position: 'absolute',
                  right: '8px',
                  color: 'var(--text-dim)',
                  display: 'flex',
                  alignItems: 'center',
                  background: 'none',
                  border: 'none',
                }}
              >
                <X size={15} />
              </button>
            )}
          </div>

          <button
            type="submit"
            disabled={searchLoading}
            className="btn-primary"
            style={{
              padding: '11px 24px',
              fontSize: '0.88rem',
              whiteSpace: 'nowrap',
              borderRadius: '8px',
              flexShrink: 0,
            }}
          >
            <Search size={16} />
            <span>{searchLoading ? 'Searching...' : 'Find medicines'}</span>
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

      {/* RESULTS DISPLAYED JUST BELOW THE SEARCH BAR (as explicitly requested) */}
      {searchLoading && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '1rem' }}>
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="clean-card" style={{ height: '180px', opacity: 0.5 }} />
          ))}
        </div>
      )}

      {searchError && (
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
          <span>{searchError}</span>
        </div>
      )}

      {!searchLoading && searchResults && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '0.75rem', flexWrap: 'wrap', gap: '0.5rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
              <h2 style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--text-main)', margin: 0 }}>
                Search Results for "{searchResults.query || searchQuery}"
              </h2>
              {onClearSearch && (
                <button
                  type="button"
                  onClick={onClearSearch}
                  style={{
                    fontSize: '0.74rem',
                    color: 'var(--terracotta-600)',
                    fontWeight: 600,
                    textDecoration: 'underline',
                    background: 'none',
                    border: 'none',
                    cursor: 'pointer',
                    padding: '2px 6px',
                  }}
                >
                  Clear Results
                </button>
              )}
            </div>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>
              {searchResults.total} medicines found
            </span>
          </div>

          {searchResults.items.length === 0 ? (
            <div style={{
              padding: '2.5rem 1.5rem',
              textAlign: 'center',
              background: 'var(--bg-surface)',
              borderRadius: '12px',
              border: '1px solid var(--border-subtle)',
            }}>
              <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-main)', margin: '0 0 0.5rem' }}>
                No verified medicines found matching "{searchQuery}"
              </h3>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', maxWidth: '440px', margin: '0 auto' }}>
                Please verify the brand name or active salt spelling (e.g., Paracetamol, Dolo 650, Augmentin).
              </p>
            </div>
          ) : (
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))',
              gap: '1rem',
            }}>
              {searchResults.items.map((med) => {
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

      {/* 4 Value Proposition Cards matching screenshot */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
        gap: '1rem',
      }}>
        <div
          onClick={() => setActiveTab('medicines')}
          className="clean-card clean-card-interactive"
          style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', cursor: 'pointer' }}
        >
          <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-main)', margin: 0 }}>
            Verified Jan Aushadhi
          </h3>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', margin: 0, lineHeight: 1.5 }}>
            Accreditation and active ingredient composition checked before listing.
          </p>
        </div>

        <div
          onClick={() => setActiveTab('sandbox')}
          className="clean-card clean-card-interactive"
          style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', cursor: 'pointer' }}
        >
          <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-main)', margin: 0 }}>
            All-inclusive savings
          </h3>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', margin: 0, lineHeight: 1.5 }}>
            Save up to 80% with standardized government ceiling prices against branded MRPs.
          </p>
        </div>

        <div
          onClick={() => setActiveTab('chat')}
          className="clean-card clean-card-interactive"
          style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', cursor: 'pointer' }}
        >
          <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-main)', margin: 0 }}>
            AI report summary
          </h3>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', margin: 0, lineHeight: 1.5 }}>
            Plain-language summary of your medicine salts, reviewed by clinical protocols.
          </p>
        </div>

        <div
          onClick={() => setActiveTab('kendras')}
          className="clean-card clean-card-interactive"
          style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', cursor: 'pointer' }}
        >
          <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-main)', margin: 0 }}>
            Nearby Kendra locator
          </h3>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', margin: 0, lineHeight: 1.5 }}>
            Locate authorized PMBJP pharmacies near you with GPS coordinates.
          </p>
        </div>
      </div>

      {/* "How it works" 4-Step Section matching screenshot */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-main)', margin: 0 }}>
          How it works
        </h2>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
          gap: '1rem',
        }}>
          <div className="clean-card" style={{ padding: '1.1rem 1.25rem' }}>
            <span style={{ fontSize: '0.74rem', color: 'var(--text-dim)', fontWeight: 600 }}>1</span>
            <div style={{ fontSize: '0.92rem', fontWeight: 700, color: 'var(--text-main)', marginTop: '0.2rem' }}>
              Search medicine
            </div>
          </div>

          <div className="clean-card" style={{ padding: '1.1rem 1.25rem' }}>
            <span style={{ fontSize: '0.74rem', color: 'var(--text-dim)', fontWeight: 600 }}>2</span>
            <div style={{ fontSize: '0.92rem', fontWeight: 700, color: 'var(--text-main)', marginTop: '0.2rem' }}>
              Compare options
            </div>
          </div>

          <div className="clean-card" style={{ padding: '1.1rem 1.25rem' }}>
            <span style={{ fontSize: '0.74rem', color: 'var(--text-dim)', fontWeight: 600 }}>3</span>
            <div style={{ fontSize: '0.92rem', fontWeight: 700, color: 'var(--text-main)', marginTop: '0.2rem' }}>
              Locate store
            </div>
          </div>

          <div className="clean-card" style={{ padding: '1.1rem 1.25rem' }}>
            <span style={{ fontSize: '0.74rem', color: 'var(--text-dim)', fontWeight: 600 }}>4</span>
            <div style={{ fontSize: '0.92rem', fontWeight: 700, color: 'var(--text-main)', marginTop: '0.2rem' }}>
              Save with support
            </div>
          </div>
        </div>
      </div>

      {/* Alternatives Comparison Modal */}
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
