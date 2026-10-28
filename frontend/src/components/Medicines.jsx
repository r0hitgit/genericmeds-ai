import React, { useState } from 'react';
import {
  Search,
  ShieldCheck,
  ArrowUpRight,
  Plus,
  X,
  AlertCircle,
  Filter
} from 'lucide-react';
import AlternativeComparisonModal from './AlternativeComparisonModal';

export default function Medicines({
  language,
  searchQuery,
  setSearchQuery,
  searchResults,
  searchLoading,
  searchError,
  janAushadhiOnly,
  setJanAushadhiOnly,
  onExecuteSearch,
  onAddToSandbox,
  onLocateStores,
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
    onExecuteSearch(searchQuery, janAushadhiOnly);
  };

  const handleQuickSearch = (term) => {
    setSearchQuery(term);
    onExecuteSearch(term, janAushadhiOnly);
  };

  return (
    <section className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Header */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '1rem' }}>
        <h2 style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--text-main)', margin: 0 }}>
          {language === 'hi' ? 'सत्यापित दवा सूची व जेनेरिक खोज' : 'Medicines & Generic Formulations'}
        </h2>
        <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', margin: 0 }}>
          Search Indian brand names to discover active salt compositions and verified Jan Aushadhi alternatives.
        </p>
      </div>

      {/* Single Search Bar (Only one bar) */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
        <form
          onSubmit={handleSubmit}
          style={{
            background: 'var(--bg-surface)',
            border: '1px solid var(--border-subtle)',
            borderRadius: '12px',
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
              placeholder="Search by brand (e.g. Dolo 650, Augmentin, Pan 40) or salt (Paracetamol)..."
              style={{
                width: '100%',
                padding: '10px 14px',
                borderRadius: '8px',
                border: 'none',
                background: 'transparent',
                color: 'var(--text-main)',
                fontSize: '0.9rem',
                outline: 'none',
                fontWeight: 500,
              }}
            />
            {searchQuery && (
              <button
                type="button"
                onClick={() => setSearchQuery('')}
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
              padding: '10px 22px',
              fontSize: '0.88rem',
              whiteSpace: 'nowrap',
              borderRadius: '8px',
              flexShrink: 0,
            }}
          >
            <Search size={15} />
            <span>{searchLoading ? 'Searching...' : 'Search'}</span>
          </button>
        </form>

        {/* Filter & Suggestions */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.75rem', maxWidth: '820px' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.78rem', color: 'var(--text-secondary)', cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={janAushadhiOnly}
              onChange={(e) => {
                setJanAushadhiOnly(e.target.checked);
                if (searchQuery.trim()) onExecuteSearch(searchQuery, e.target.checked);
              }}
              style={{ accentColor: 'var(--terracotta-600)' }}
            />
            <span>Filter PMBJP Jan Aushadhi Only</span>
          </label>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', flexWrap: 'wrap', fontSize: '0.78rem', color: 'var(--text-muted)' }}>
            <span>Popular:</span>
            {popularSearches.map((term) => (
              <button
                key={term}
                onClick={() => handleQuickSearch(term)}
                style={{
                  background: 'var(--bg-surface)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: '6px',
                  padding: '2px 8px',
                  fontSize: '0.75rem',
                  color: 'var(--text-secondary)',
                  fontWeight: 500,
                }}
              >
                {term}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* RESULTS DISPLAYED DIRECTLY BELOW THE BAR */}
      {searchLoading && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '1rem' }}>
          {[1, 2, 3, 4, 5, 6].map((i) => (
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
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '0.75rem' }}>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-main)', margin: 0 }}>
              Search Results ({searchResults.total})
            </h3>
            <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
              Query: "{searchResults.query || searchQuery}"
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
                No medicines found
              </h3>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', maxWidth: '440px', margin: '0 auto' }}>
                Try searching by common brand name (e.g., Dolo 650, Augmentin) or active salt (e.g., Paracetamol).
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
                          <h4 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-main)', margin: 0 }}>
                            {med.brand_name}
                          </h4>
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
