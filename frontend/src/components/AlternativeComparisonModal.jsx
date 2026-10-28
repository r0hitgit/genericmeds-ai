import React, { useState, useEffect } from 'react';
import {
  Scale,
  CheckCircle2,
  AlertCircle,
  X,
  Plus,
  MapPin,
  ArrowUpRight,
  ShieldCheck,
  TrendingDown
} from 'lucide-react';
import { api } from '../services/api';

export default function AlternativeComparisonModal({
  medicine,
  onClose,
  onAddToSandbox,
  onLocateStores,
  language,
}) {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!medicine) return;
    let isMounted = true;
    const fetchAlternatives = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await api.findAlternatives(medicine.id, 10, false);
        if (isMounted) {
          setData(res);
          setLoading(false);
        }
      } catch (err) {
        if (isMounted) {
          setError(err.message);
          setLoading(false);
        }
      }
    };
    fetchAlternatives();
    return () => {
      isMounted = false;
    };
  }, [medicine]);

  if (!medicine) return null;

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      zIndex: 100,
      background: 'rgba(28, 25, 23, 0.45)',
      backdropFilter: 'blur(4px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '1rem',
      animation: 'fadeInScale 0.15s ease-out',
    }}>
      <div style={{
        background: 'var(--bg-surface)',
        borderRadius: '14px',
        border: '1px solid var(--border-subtle)',
        maxWidth: '880px',
        width: '100%',
        maxHeight: '88vh',
        display: 'flex',
        flexDirection: 'column',
        boxShadow: 'var(--card-shadow-hover)',
        overflow: 'hidden',
      }}>
        {/* Header */}
        <div style={{
          padding: '1.25rem 1.5rem',
          borderBottom: '1px solid var(--border-subtle)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          background: 'var(--bg-surface-elevated)',
        }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
              <Scale size={18} color="var(--terracotta-600)" />
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-main)', margin: 0 }}>
                {language === 'hi' ? 'सत्यापित जेनेरिक विकल्प व मूल्य तुलना' : 'Verified Generic Alternative & Price Comparison'}
              </h3>
              <span className="badge badge-savings">
                <TrendingDown size={12} />
                <span>Save up to 80%</span>
              </span>
            </div>
            <p style={{ fontSize: '0.76rem', color: 'var(--text-muted)', margin: '0.2rem 0 0' }}>
              Identical active ingredients, strength equivalence & Jan Aushadhi pricing comparison
            </p>
          </div>

          <button
            onClick={onClose}
            aria-label="Close"
            style={{
              width: '32px',
              height: '32px',
              borderRadius: '8px',
              border: '1px solid var(--border-subtle)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--text-muted)',
              background: 'var(--bg-surface)',
            }}
          >
            <X size={16} />
          </button>
        </div>

        {/* Body */}
        <div style={{ padding: '1.5rem', overflowY: 'auto', flex: 1, display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          {/* Baseline Prescribed Medicine Card */}
          <div style={{
            background: 'var(--bg-surface-elevated)',
            border: '1px solid var(--border-subtle)',
            borderRadius: '10px',
            padding: '1rem 1.25rem',
            display: 'flex',
            flexDirection: 'column',
            gap: '0.5rem',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.5rem' }}>
              <div>
                <span style={{ fontSize: '0.68rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-dim)', letterSpacing: '0.04em' }}>
                  Baseline Prescribed Product
                </span>
                <h4 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-main)', margin: '0.1rem 0' }}>
                  {medicine.brand_name}
                </h4>
              </div>

              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: '1.15rem', fontWeight: 800, color: 'var(--text-main)' }}>
                  {medicine.latest_price ? `₹${medicine.latest_price.amount_inr}` : 'Price Unverified'}
                </div>
                {medicine.latest_price?.unit_price_inr && (
                  <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                    ₹{medicine.latest_price.unit_price_inr} / unit
                  </span>
                )}
              </div>
            </div>

            <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
              <strong>Formulation:</strong> {medicine.dosage_form} • {medicine.pack_size} {medicine.pack_unit} • {medicine.release_type}
            </div>

            {medicine.ingredients && medicine.ingredients.length > 0 && (
              <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', background: 'var(--bg-surface)', padding: '0.45rem 0.75rem', borderRadius: '6px', border: '1px solid var(--border-subtle)' }}>
                <strong>Active Salts:</strong> {medicine.ingredients.map((ing) => `${ing.name} (${ing.strength_value} ${ing.strength_unit})`).join(', ')}
              </div>
            )}
          </div>

          {loading && (
            <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
              <p style={{ fontWeight: 600, fontSize: '0.9rem' }}>Analyzing verified Jan Aushadhi & NPPA database...</p>
              <p style={{ fontSize: '0.76rem' }}>Verifying active salts, identical strengths, and potential savings...</p>
            </div>
          )}

          {error && (
            <div style={{ padding: '1rem', background: 'var(--disclaimer-bg)', border: '1px solid var(--disclaimer-border)', borderRadius: '8px', color: 'var(--terracotta-700)', fontSize: '0.82rem', display: 'flex', gap: '0.4rem', alignItems: 'center' }}>
              <AlertCircle size={16} />
              <span>{error}</span>
            </div>
          )}

          {!loading && !error && data && (
            <>
              {data.candidates.length === 0 ? (
                <div style={{ padding: '2rem', textAlign: 'center', background: 'var(--bg-surface-elevated)', borderRadius: '10px' }}>
                  <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-main)', margin: '0 0 0.35rem' }}>
                    No exact verified generic match found in current catalogue
                  </h4>
                  <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', maxWidth: '420px', margin: '0 auto' }}>
                    A generic formulation matching the exact salts and strength profile is not currently listed. Please consult a registered pharmacist.
                  </p>
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <span style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--text-secondary)' }}>
                      Verified Generic Equivalents ({data.candidates.length})
                    </span>
                    <span style={{ fontSize: '0.72rem', color: 'var(--terracotta-600)', fontWeight: 600 }}>
                      Sorted by Clinical Match & Savings
                    </span>
                  </div>

                  <div className="data-table-container">
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>Generic Alternative</th>
                          <th>Active Composition</th>
                          <th>Match Rating</th>
                          <th>Pack Price</th>
                          <th>Unit Price</th>
                          <th>Potential Savings</th>
                          <th>Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {data.candidates.map((cand, idx) => {
                          const prod = cand.product;
                          const isExact = cand.match_classification === 'EXACT_COMPOSITION_MATCH';
                          return (
                            <tr key={prod.id || idx}>
                              <td>
                                <div style={{ fontWeight: 700, color: 'var(--text-main)' }}>
                                  {prod.brand_name}
                                </div>
                                {prod.is_jan_aushadhi && (
                                  <span className="badge badge-generic" style={{ marginTop: '0.2rem' }}>
                                    <ShieldCheck size={11} />
                                    <span>PMBJP Kendra</span>
                                  </span>
                                )}
                              </td>
                              <td style={{ fontSize: '0.74rem', color: 'var(--text-secondary)', maxWidth: '200px' }}>
                                {prod.ingredients.map((i) => `${i.name} ${i.strength_value}${i.strength_unit}`).join(', ')}
                                <div style={{ color: 'var(--text-dim)', fontSize: '0.68rem' }}>{prod.dosage_form}</div>
                              </td>
                              <td>
                                {isExact ? (
                                  <span className="badge badge-generic" style={{ fontWeight: 700 }}>
                                    Exact Match
                                  </span>
                                ) : (
                                  <span className="badge badge-brand">
                                    {cand.match_classification}
                                  </span>
                                )}
                              </td>
                              <td style={{ fontWeight: 700 }}>
                                {prod.latest_price ? `₹${prod.latest_price.amount_inr}` : 'Unverified'}
                                <div style={{ fontSize: '0.68rem', color: 'var(--text-dim)', fontWeight: 400 }}>
                                  ({prod.pack_size} {prod.pack_unit})
                                </div>
                              </td>
                              <td style={{ fontWeight: 700, color: 'var(--text-main)' }}>
                                {cand.alternative_unit_price ? `₹${cand.alternative_unit_price}` : '—'}
                              </td>
                              <td>
                                {cand.savings_percentage ? (
                                  <div style={{ display: 'flex', flexDirection: 'column' }}>
                                    <span style={{ color: 'var(--green-700)', fontWeight: 800, fontSize: '0.85rem' }}>
                                      Save {cand.savings_percentage}%
                                    </span>
                                    <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>
                                      ₹{cand.unit_savings_inr} saved / unit
                                    </span>
                                  </div>
                                ) : (
                                  <span style={{ color: 'var(--text-dim)', fontSize: '0.72rem' }}>Same / Minimal</span>
                                )}
                              </td>
                              <td>
                                <div style={{ display: 'flex', gap: '0.35rem' }}>
                                  <button
                                    onClick={() => onAddToSandbox && onAddToSandbox(prod)}
                                    title="Add to Comparison Sandbox"
                                    style={{
                                      padding: '0.35rem 0.55rem',
                                      borderRadius: '6px',
                                      background: 'var(--bg-surface)',
                                      border: '1px solid var(--border-subtle)',
                                      fontSize: '0.72rem',
                                      fontWeight: 600,
                                      color: 'var(--text-secondary)',
                                      display: 'flex',
                                      alignItems: 'center',
                                      gap: '0.2rem',
                                    }}
                                  >
                                    <Plus size={11} />
                                    <span>Sandbox</span>
                                  </button>

                                  {prod.is_jan_aushadhi && onLocateStores && (
                                    <button
                                      onClick={() => {
                                        onClose();
                                        onLocateStores();
                                      }}
                                      className="btn-primary"
                                      style={{
                                        padding: '0.35rem 0.65rem',
                                        fontSize: '0.72rem',
                                        borderRadius: '6px',
                                      }}
                                    >
                                      <MapPin size={11} />
                                      <span>Find</span>
                                    </button>
                                  )}
                                </div>
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Safety notice disclaimer from server */}
              {data.safety_notice && (
                <div style={{
                  padding: '0.75rem 1rem',
                  background: 'var(--disclaimer-bg)',
                  border: '1px solid var(--disclaimer-border)',
                  borderRadius: '8px',
                  fontSize: '0.74rem',
                  color: 'var(--disclaimer-text)',
                  display: 'flex',
                  gap: '0.4rem',
                  alignItems: 'flex-start',
                }}>
                  <AlertCircle size={15} style={{ flexShrink: 0, marginTop: '2px' }} />
                  <div>
                    <strong>Clinical Safety Advisory:</strong> {data.safety_notice}
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        {/* Footer */}
        <div style={{
          padding: '0.85rem 1.5rem',
          borderTop: '1px solid var(--border-subtle)',
          display: 'flex',
          justifyContent: 'flex-end',
          gap: '0.65rem',
          background: 'var(--bg-surface)',
        }}>
          <button onClick={onClose} className="btn-secondary" style={{ padding: '0.5rem 1rem' }}>
            Close
          </button>
          {onLocateStores && (
            <button
              onClick={() => {
                onClose();
                onLocateStores();
              }}
              className="btn-primary"
              style={{ padding: '0.5rem 1.25rem' }}
            >
              <MapPin size={14} />
              <span>Locate Nearby Kendra</span>
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
