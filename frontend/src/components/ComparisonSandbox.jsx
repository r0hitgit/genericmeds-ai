import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

export default function ComparisonSandbox({
  sandboxItems,
  onRemoveFromSandbox,
  onClearSandbox,
  onAddMedicine,
  language,
}) {
  const [comparing, setComparing] = useState(false);
  const [comparisonResult, setComparisonResult] = useState(null);
  const [error, setError] = useState(null);

  const runComparison = async (items = sandboxItems) => {
    if (items.length < 2) {
      setComparisonResult(null);
      return;
    }
    setComparing(true);
    setError(null);
    try {
      const ids = items.map((i) => i.id);
      const res = await api.comparePrices(ids);
      setComparisonResult(res);
    } catch (err) {
      setError(err.message || 'Comparison failed.');
    } finally {
      setComparing(false);
    }
  };

  useEffect(() => {
    if (sandboxItems.length >= 2) {
      runComparison();
    } else {
      setComparisonResult(null);
    }
  }, [sandboxItems]);

  const loadPreset = async (queryTerm) => {
    try {
      setComparing(true);
      const res = await api.searchMedicines(queryTerm, 4, 0, false);
      if (res.items.length >= 2) {
        onClearSandbox();
        res.items.slice(0, 3).forEach((m) => onAddMedicine(m));
      }
    } catch (err) {
      setError('Could not load preset medicines: ' + err.message);
    } finally {
      setComparing(false);
    }
  };

  return (
    <section className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem', borderBottom: '1px solid var(--border-subtle)', pb: '1rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ fontSize: '1.5rem' }}>⚖️</span>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--text-main)', margin: 0 }}>
              {language === 'hi' ? 'दवा मूल्य तुलना सैंडबॉक्स' : 'Medicine Price Comparison Sandbox'}
            </h2>
          </div>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', margin: '0.25rem 0 0' }}>
            {language === 'hi'
              ? 'विभिन्न ब्रांड और जन औषधि दवाओं के प्रति-यूनिट मूल्य और संभावित बचत की तुलना करें।'
              : 'Add 2 or more medicines to calculate exact unit price differences, package price deltas, and potential statutory savings.'}
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          {sandboxItems.length > 0 && (
            <button
              onClick={onClearSandbox}
              style={{
                padding: '0.45rem 0.85rem',
                borderRadius: '0.55rem',
                border: '1px solid var(--border-medium)',
                background: 'var(--bg-surface-elevated)',
                fontSize: '0.78rem',
                fontWeight: 600,
                color: 'var(--rose-600)',
              }}
            >
              Clear All ({sandboxItems.length})
            </button>
          )}
        </div>
      </div>

      {/* Preset Quick Loaders */}
      <div style={{
        background: 'var(--bg-surface-elevated)',
        padding: '0.85rem 1.25rem',
        borderRadius: '0.75rem',
        border: '1px solid var(--border-subtle)',
        display: 'flex',
        alignItems: 'center',
        gap: '0.75rem',
        flexWrap: 'wrap',
      }}>
        <span style={{ fontSize: '0.78rem', fontWeight: 700, color: 'var(--text-secondary)' }}>
          Quick Comparison Presets:
        </span>
        <button
          onClick={() => loadPreset('Paracetamol')}
          style={{
            background: 'var(--bg-surface)',
            border: '1px solid var(--border-medium)',
            padding: '0.35rem 0.75rem',
            borderRadius: '0.5rem',
            fontSize: '0.75rem',
            fontWeight: 600,
            color: 'var(--teal-600)',
          }}
        >
          💊 Paracetamol 650 (Dolo vs PMBJP)
        </button>
        <button
          onClick={() => loadPreset('Amoxicillin Clavulanic')}
          style={{
            background: 'var(--bg-surface)',
            border: '1px solid var(--border-medium)',
            padding: '0.35rem 0.75rem',
            borderRadius: '0.5rem',
            fontSize: '0.75rem',
            fontWeight: 600,
            color: 'var(--teal-600)',
          }}
        >
          💊 Augmentin 625 Duo vs Generic
        </button>
        <button
          onClick={() => loadPreset('Metformin')}
          style={{
            background: 'var(--bg-surface)',
            border: '1px solid var(--border-medium)',
            padding: '0.35rem 0.75rem',
            borderRadius: '0.5rem',
            fontSize: '0.75rem',
            fontWeight: 600,
            color: 'var(--teal-600)',
          }}
        >
          💊 Glycomet 500 SR vs Generic
        </button>
      </div>

      {/* Selected Items Tray */}
      {sandboxItems.length === 0 ? (
        <div style={{
          padding: '3rem 1.5rem',
          textAlign: 'center',
          background: 'var(--bg-surface)',
          borderRadius: '1rem',
          border: '1.5px dashed var(--border-medium)',
        }}>
          <div style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>📦</div>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-main)' }}>
            Your Comparison Sandbox is empty
          </h3>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', maxWidth: '440px', margin: '0.35rem auto 1rem' }}>
            Click "+ Sandbox" on any medicine card or select one of the quick comparison presets above to start comparing prices.
          </p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '1rem' }}>
            {sandboxItems.map((med) => (
              <div
                key={med.id}
                style={{
                  background: 'var(--bg-surface)',
                  borderRadius: '0.85rem',
                  border: '1px solid var(--border-subtle)',
                  padding: '1rem',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  gap: '0.5rem',
                  position: 'relative',
                  boxShadow: 'var(--card-shadow)',
                }}
              >
                <button
                  onClick={() => onRemoveFromSandbox(med.id)}
                  title="Remove from sandbox"
                  style={{
                    position: 'absolute',
                    top: '0.75rem',
                    right: '0.75rem',
                    width: '24px',
                    height: '24px',
                    borderRadius: '50%',
                    background: 'var(--bg-surface-elevated)',
                    border: '1px solid var(--border-medium)',
                    fontSize: '0.75rem',
                    color: 'var(--text-dim)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  ✕
                </button>

                <div>
                  <div style={{ paddingRight: '1.75rem' }}>
                    <span className={med.is_jan_aushadhi ? 'badge badge-generic' : 'badge badge-brand'}>
                      {med.is_jan_aushadhi ? 'PMBJP Jan Aushadhi' : 'Branded MRP'}
                    </span>
                    <h4 style={{ fontSize: '1rem', fontWeight: 800, color: 'var(--text-main)', marginTop: '0.35rem' }}>
                      {med.brand_name}
                    </h4>
                  </div>
                  <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>
                    {med.dosage_form} • {med.pack_size} {med.pack_unit}
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', borderTop: '1px solid var(--border-subtle)', paddingTop: '0.5rem' }}>
                  <span style={{ fontSize: '1.1rem', fontWeight: 800, color: 'var(--text-main)' }}>
                    {med.latest_price ? `₹${med.latest_price.amount_inr}` : 'Unverified'}
                  </span>
                  {med.latest_price?.unit_price_inr && (
                    <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                      ₹{med.latest_price.unit_price_inr} / unit
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>

          {sandboxItems.length < 2 && (
            <div style={{ padding: '0.75rem 1rem', background: 'var(--disclaimer-bg)', border: '1px solid var(--disclaimer-border)', borderRadius: '0.5rem', color: 'var(--disclaimer-text)', fontSize: '0.78rem' }}>
              ℹ️ Please add at least one more medicine to compute the price difference and unit savings.
            </div>
          )}
        </div>
      )}

      {/* Comparison Calculation View */}
      {comparing && (
        <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
          <div style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>🔄</div>
          <p style={{ fontWeight: 600 }}>Calculating unit price savings matrix...</p>
        </div>
      )}

      {error && (
        <div style={{ padding: '1rem', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: '0.75rem', color: 'var(--rose-600)', fontSize: '0.85rem' }}>
          <strong>Comparison calculation error:</strong> {error}
        </div>
      )}

      {!comparing && comparisonResult && (
        <div style={{
          background: 'var(--bg-surface)',
          borderRadius: '1rem',
          border: '1px solid var(--border-subtle)',
          padding: '1.5rem',
          display: 'flex',
          flexDirection: 'column',
          gap: '1.25rem',
          boxShadow: 'var(--card-shadow)',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '0.75rem' }}>
            <div>
              <h3 style={{ fontSize: '1.15rem', fontWeight: 800, color: 'var(--text-main)', margin: 0 }}>
                Unit Price & Package Deltas
              </h3>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', margin: '0.2rem 0 0' }}>
                Normalized per-tablet / per-capsule / per-ml statutory comparison
              </p>
            </div>
            {comparisonResult.max_savings_percentage && (
              <span className="badge badge-savings" style={{ fontSize: '0.85rem', padding: '0.4rem 0.85rem' }}>
                Maximum Savings: {comparisonResult.max_savings_percentage}%
              </span>
            )}
          </div>

          <div className="data-table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Medicine</th>
                  <th>Classification</th>
                  <th>Pack Size</th>
                  <th>Package Price</th>
                  <th>Calculated Unit Price</th>
                  <th>Potential Savings vs Baseline</th>
                </tr>
              </thead>
              <tbody>
                {comparisonResult.items && comparisonResult.items.map((item, idx) => (
                  <tr key={item.medicine_id || idx}>
                    <td style={{ fontWeight: 700, color: 'var(--text-main)' }}>
                      {item.brand_name}
                    </td>
                    <td>
                      <span className={item.is_jan_aushadhi ? 'badge badge-generic' : 'badge badge-brand'}>
                        {item.is_jan_aushadhi ? 'PMBJP Generic' : 'Branded MRP'}
                      </span>
                    </td>
                    <td>{item.pack_size} {item.pack_unit}</td>
                    <td style={{ fontWeight: 700 }}>₹{item.package_price_inr}</td>
                    <td style={{ fontWeight: 800, color: 'var(--teal-600)' }}>
                      ₹{item.unit_price_inr} / unit
                    </td>
                    <td>
                      {item.savings_vs_highest_pct ? (
                        <span style={{ color: 'var(--emerald-600)', fontWeight: 800 }}>
                          Save {item.savings_vs_highest_pct}% (₹{item.unit_savings_vs_highest_inr}/unit)
                        </span>
                      ) : (
                        <span style={{ color: 'var(--text-dim)' }}>Baseline (Highest)</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {comparisonResult.cautionary_notice && (
            <div style={{
              padding: '0.85rem 1rem',
              background: 'var(--disclaimer-bg)',
              border: '1px solid var(--disclaimer-border)',
              borderRadius: '0.75rem',
              color: 'var(--disclaimer-text)',
              fontSize: '0.76rem',
            }}>
              <strong>Clinical Equivalence Notice:</strong> {comparisonResult.cautionary_notice}
            </div>
          )}
        </div>
      )}
    </section>
  );
}
