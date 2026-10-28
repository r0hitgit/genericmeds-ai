import React, { useState, useEffect } from 'react';
import {
  Scale,
  Trash2,
  Plus,
  AlertCircle,
  TrendingDown,
  Layers
} from 'lucide-react';
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
    <section className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '0.75rem' }}>
        <div>
          <h2 style={{ fontSize: '1.35rem', fontWeight: 700, color: 'var(--text-main)', margin: 0 }}>
            {language === 'hi' ? 'दवा मूल्य तुलना सैंडबॉक्स' : 'Price Comparison Sandbox'}
          </h2>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', margin: '0.2rem 0 0' }}>
            Compare normalized per-tablet unit prices and calculate potential savings across multiple products.
          </p>
        </div>

        {sandboxItems.length > 0 && (
          <button
            onClick={onClearSandbox}
            className="btn-secondary"
            style={{ fontSize: '0.78rem', padding: '0.4rem 0.85rem' }}
          >
            <Trash2 size={13} />
            <span>Clear Sandbox ({sandboxItems.length})</span>
          </button>
        )}
      </div>

      {/* Preset Buttons */}
      <div style={{
        background: 'var(--bg-surface)',
        border: '1px solid var(--border-subtle)',
        borderRadius: '10px',
        padding: '0.75rem 1rem',
        display: 'flex',
        alignItems: 'center',
        gap: '0.5rem',
        flexWrap: 'wrap',
      }}>
        <span style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
          Quick presets:
        </span>
        <button
          onClick={() => loadPreset('Paracetamol')}
          className="btn-secondary"
          style={{ padding: '0.35rem 0.75rem', fontSize: '0.76rem' }}
        >
          Paracetamol 650 (Dolo vs PMBJP)
        </button>
        <button
          onClick={() => loadPreset('Amoxicillin Clavulanic')}
          className="btn-secondary"
          style={{ padding: '0.35rem 0.75rem', fontSize: '0.76rem' }}
        >
          Augmentin 625 Duo vs Generic
        </button>
        <button
          onClick={() => loadPreset('Metformin')}
          className="btn-secondary"
          style={{ padding: '0.35rem 0.75rem', fontSize: '0.76rem' }}
        >
          Glycomet 500 SR vs Generic
        </button>
      </div>

      {/* Selected Items Tray */}
      {sandboxItems.length === 0 ? (
        <div style={{
          padding: '3rem 1.5rem',
          textAlign: 'center',
          background: 'var(--bg-surface)',
          borderRadius: '12px',
          border: '1px dashed var(--border-medium)',
        }}>
          <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-main)', margin: '0 0 0.4rem' }}>
            Your comparison sandbox is empty
          </h3>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', maxWidth: '420px', margin: '0 auto' }}>
            Click "+ Sandbox" on any medicine card or choose one of the quick presets above to calculate price differences.
          </p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '1rem' }}>
            {sandboxItems.map((med) => (
              <div
                key={med.id}
                className="clean-card"
                style={{
                  padding: '1rem 1.25rem',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  gap: '0.75rem',
                  position: 'relative',
                }}
              >
                <button
                  onClick={() => onRemoveFromSandbox(med.id)}
                  title="Remove"
                  style={{
                    position: 'absolute',
                    top: '0.75rem',
                    right: '0.75rem',
                    color: 'var(--text-dim)',
                    padding: '2px',
                  }}
                >
                  <Trash2 size={14} />
                </button>

                <div>
                  <span className={med.is_jan_aushadhi ? 'badge badge-generic' : 'badge badge-brand'}>
                    {med.is_jan_aushadhi ? 'PMBJP Jan Aushadhi' : 'Branded MRP'}
                  </span>
                  <h4 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-main)', marginTop: '0.35rem', marginBottom: '0.15rem' }}>
                    {med.brand_name}
                  </h4>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    {med.dosage_form} • {med.pack_size} {med.pack_unit}
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', borderTop: '1px solid var(--border-subtle)', paddingTop: '0.5rem' }}>
                  <span style={{ fontSize: '1.15rem', fontWeight: 800, color: 'var(--text-main)' }}>
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
            <div style={{ padding: '0.75rem 1rem', background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)', borderRadius: '8px', color: 'var(--text-muted)', fontSize: '0.78rem' }}>
              Please add at least one more medicine to compute the price difference and unit savings.
            </div>
          )}
        </div>
      )}

      {/* Comparison Calculation Matrix */}
      {!comparing && comparisonResult && (
        <div className="clean-card" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '0.75rem' }}>
            <div>
              <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-main)', margin: 0 }}>
                Unit Price & Savings Matrix
              </h3>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', margin: '0.15rem 0 0' }}>
                Normalized per-unit statutory comparison
              </p>
            </div>
            {comparisonResult.max_savings_percentage && (
              <span className="badge badge-savings" style={{ fontSize: '0.8rem', padding: '0.35rem 0.75rem' }}>
                <TrendingDown size={14} />
                <span>Max Savings: {comparisonResult.max_savings_percentage}%</span>
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
                  <th>Potential Savings</th>
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
                    <td style={{ fontWeight: 700, color: 'var(--terracotta-600)' }}>
                      ₹{item.unit_price_inr} / unit
                    </td>
                    <td>
                      {item.savings_vs_highest_pct ? (
                        <span style={{ color: 'var(--green-700)', fontWeight: 800 }}>
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
              padding: '0.75rem 1rem',
              background: 'var(--disclaimer-bg)',
              border: '1px solid var(--disclaimer-border)',
              borderRadius: '8px',
              color: 'var(--disclaimer-text)',
              fontSize: '0.76rem',
              display: 'flex',
              gap: '0.4rem',
              alignItems: 'center',
            }}>
              <AlertCircle size={15} />
              <span>{comparisonResult.cautionary_notice}</span>
            </div>
          )}
        </div>
      )}
    </section>
  );
}
