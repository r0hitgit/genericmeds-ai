import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

export default function KendraLocator({ language }) {
  const [method, setMethod] = useState('gps'); // 'gps' | 'manual'
  const [radiusKm, setRadiusKm] = useState(10);
  const [gpsLoading, setGpsLoading] = useState(false);
  const [gpsStatus, setGpsStatus] = useState('');
  const [lastCoords, setLastCoords] = useState(null);

  // Manual search form fields
  const [pincode, setPincode] = useState('');
  const [stateName, setStateName] = useState('');
  const [district, setDistrict] = useState('');
  const [filter24x7, setFilter24x7] = useState(false);

  // Results state
  const [loading, setLoading] = useState(false);
  const [kendras, setKendras] = useState([]);
  const [resultsHeader, setResultsHeader] = useState('Verified Kendra Directory');
  const [resultsBadge, setResultsBadge] = useState('All Major Hubs');
  const [error, setError] = useState(null);
  const [widerRadiusSuggested, setWiderRadiusSuggested] = useState(null);

  // Load initial directory
  useEffect(() => {
    loadAllKendras();
  }, []);

  const loadAllKendras = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getAllKendras({ limit: 30, is_24x7: filter24x7 ? true : undefined });
      setKendras(data || []);
      setResultsHeader('Verified Jan Aushadhi Kendra Directory');
      setResultsBadge('Pan-India Verified Hubs');
      setWiderRadiusSuggested(null);
    } catch (err) {
      setError(err.message || 'Failed to load Kendras.');
    } finally {
      setLoading(false);
    }
  };

  const handleUseLocation = () => {
    if (!navigator.geolocation) {
      setGpsStatus('Geolocation is not supported by your browser. Please use manual search.');
      return;
    }

    setGpsLoading(true);
    setGpsStatus('Requesting browser location permission...');
    setError(null);

    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        const { latitude, longitude } = pos.coords;
        setLastCoords({ lat: latitude, lon: longitude });
        setGpsStatus(`GPS acquired. Searching stores within ${radiusKm} km...`);

        try {
          setLoading(true);
          const data = await api.getNearbyKendras(latitude, longitude, radiusKm, 30);
          setKendras(data.kendras || []);
          setResultsHeader(`Nearby Jan Aushadhi Kendras (Within ${radiusKm} km)`);
          setResultsBadge(`${data.total_found} Stores Near You`);
          setWiderRadiusSuggested(data.wider_radius_suggested);
          setGpsStatus('');
        } catch (err) {
          setError(err.message || 'Error searching nearby Kendras.');
        } finally {
          setLoading(false);
          setGpsLoading(false);
        }
      },
      (err) => {
        setGpsLoading(false);
        let msg = 'Location permission denied. Please enter your PIN code or District below.';
        if (err.code === err.POSITION_UNAVAILABLE) msg = 'Location unavailable. Please use manual search.';
        if (err.code === err.TIMEOUT) msg = 'Location request timed out. Please try again or use manual search.';
        setGpsStatus(msg);
      },
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 60000 }
    );
  };

  const handleManualSearch = async (e) => {
    e.preventDefault();
    if (!pincode.trim() && !stateName.trim() && !district.trim()) {
      setError('Please provide at least a PIN code, District, or State.');
      return;
    }

    if (pincode && !/^[1-9][0-9]{5}$/.test(pincode.trim())) {
      setError('PIN code must be a 6-digit Indian postal code starting with digits 1-9.');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const data = await api.searchKendrasManual({
        pincode: pincode.trim(),
        state: stateName.trim(),
        district: district.trim(),
        limit: 30,
      });

      setKendras(data.kendras || []);
      const title = pincode
        ? `Jan Aushadhi Kendras in PIN ${pincode}`
        : `Jan Aushadhi Kendras in ${district || stateName}`;
      setResultsHeader(title);
      setResultsBadge(`${data.total} Stores Found`);
      setWiderRadiusSuggested(null);
    } catch (err) {
      setError(err.message || 'Manual search failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleWiderSearch = (newRadius) => {
    setRadiusKm(newRadius);
    if (lastCoords) {
      setLoading(true);
      api.getNearbyKendras(lastCoords.lat, lastCoords.lon, newRadius, 30)
        .then((data) => {
          setKendras(data.kendras || []);
          setResultsHeader(`Nearby Jan Aushadhi Kendras (Within ${newRadius} km)`);
          setResultsBadge(`${data.total_found} Stores Near You`);
          setWiderRadiusSuggested(data.wider_radius_suggested);
        })
        .catch((err) => setError(err.message))
        .finally(() => setLoading(false));
    } else {
      handleUseLocation();
    }
  };

  return (
    <section className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
      {/* Header and Banner */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.75rem', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '0.75rem' }}>
          <div>
            <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.35rem', background: 'rgba(13, 148, 136, 0.1)', color: 'var(--teal-600)', padding: '0.2rem 0.6rem', borderRadius: '9999px', fontSize: '0.72rem', fontWeight: 700, marginBottom: '0.25rem' }}>
              🏛️ Pradhan Mantri Bhartiya Janaushadhi Pariyojana (PMBJP)
            </div>
            <h2 style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--text-main)', margin: 0 }}>
              {language === 'hi' ? 'निकटतम जन औषधि केंद्र खोजें' : 'Find Nearby Jan Aushadhi Kendras'}
            </h2>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', margin: '0.2rem 0 0' }}>
              Locate verified government generic medicine stores across India using GPS or postal code search.
            </p>
          </div>

          <a
            href="https://janaushadhi.gov.in/locate-kendra"
            target="_blank"
            rel="noopener noreferrer"
            className="btn-outline-teal"
            style={{ fontSize: '0.78rem' }}
          >
            <span>Official PMBI Locator</span>
            <span>↗</span>
          </a>
        </div>

        {/* Mandatory Inventory Stock Disclaimer Banner */}
        <div style={{
          padding: '0.85rem 1.25rem',
          background: 'var(--disclaimer-bg)',
          border: '1px solid var(--disclaimer-border)',
          borderRadius: '0.85rem',
          color: 'var(--disclaimer-text)',
          fontSize: '0.78rem',
          lineHeight: 1.5,
          display: 'flex',
          gap: '0.5rem',
        }}>
          <span style={{ fontSize: '1rem' }}>⚠️</span>
          <div>
            <strong>Mandatory Notice & Stock Availability Disclaimer:</strong> Kendra listings help you find nearby Jan Aushadhi stores but do not guarantee that a particular generic medicine is in stock today. Please confirm medicine availability, current batch MRPs, and operating hours directly with the Kendra using the provided phone or location.
          </div>
        </div>
      </div>

      {/* Dual Search Method Selector */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
        gap: '1.25rem',
      }}>
        {/* Method 1: GPS Device Location */}
        <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', gap: '1rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
              <span style={{ fontSize: '0.72rem', fontWeight: 800, textTransform: 'uppercase', color: 'var(--teal-600)', letterSpacing: '0.05em' }}>
                Option 1: Device GPS
              </span>
              <span style={{ fontSize: '0.7rem', color: 'var(--text-dim)', fontWeight: 600 }}>
                Explicit Permission Only
              </span>
            </div>
            <h3 style={{ fontSize: '1.05rem', fontWeight: 800, color: 'var(--text-main)', margin: '0 0 0.35rem' }}>
              Find Nearest Stores Around Me
            </h3>
            <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
              Uses browser geolocation to calculate exact aerial and road distances via the Haversine formula. Coordinates are never logged or stored.
            </p>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.8rem' }}>
              <label htmlFor="gps-radius-select" style={{ fontWeight: 600, color: 'var(--text-secondary)' }}>
                Search Radius:
              </label>
              <select
                id="gps-radius-select"
                value={radiusKm}
                onChange={(e) => setRadiusKm(Number(e.target.value))}
                style={{
                  background: 'var(--bg-surface)',
                  border: '1px solid var(--border-medium)',
                  borderRadius: '0.5rem',
                  padding: '0.35rem 0.65rem',
                  fontSize: '0.8rem',
                  color: 'var(--text-main)',
                  outline: 'none',
                }}
              >
                <option value={5}>5 km</option>
                <option value={10}>10 km (Recommended)</option>
                <option value={25}>25 km</option>
                <option value={50}>50 km</option>
              </select>
            </div>

            <button
              onClick={handleUseLocation}
              disabled={gpsLoading}
              className="btn-primary"
              id="gps-location-btn"
              style={{ width: '100%', padding: '0.75rem', fontSize: '0.88rem' }}
            >
              <span>{gpsLoading ? 'Acquiring GPS...' : '📍 Use My Current Location'}</span>
            </button>

            {gpsStatus && (
              <div style={{ fontSize: '0.76rem', color: 'var(--teal-600)', textAlign: 'center', minHeight: '1.2rem', fontWeight: 500 }}>
                {gpsStatus}
              </div>
            )}
          </div>
        </div>

        {/* Method 2: Manual Search */}
        <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', gap: '1rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
              <span style={{ fontSize: '0.72rem', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-dim)', letterSpacing: '0.05em' }}>
                Option 2: Postal Search
              </span>
              <span style={{ fontSize: '0.7rem', color: 'var(--emerald-600)', fontWeight: 600 }}>
                No GPS Required
              </span>
            </div>
            <h3 style={{ fontSize: '1.05rem', fontWeight: 800, color: 'var(--text-main)', margin: '0 0 0.35rem' }}>
              Search by PIN Code, District, or State
            </h3>
            <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
              Locate registered Jan Aushadhi pharmacies across all Indian postal zones and hospital complexes.
            </p>
          </div>

          <form onSubmit={handleManualSearch} style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem' }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(100px, 1fr))', gap: '0.5rem' }}>
              <div>
                <label style={{ fontSize: '0.72rem', fontWeight: 600, color: 'var(--text-muted)', display: 'block', marginBottom: '0.2rem' }}>
                  PIN Code (6 digits)
                </label>
                <input
                  type="text"
                  maxLength={6}
                  value={pincode}
                  onChange={(e) => setPincode(e.target.value)}
                  placeholder="e.g. 110029"
                  className="form-input"
                  style={{ padding: '0.45rem 0.65rem', fontSize: '0.8rem' }}
                />
              </div>

              <div>
                <label style={{ fontSize: '0.72rem', fontWeight: 600, color: 'var(--text-muted)', display: 'block', marginBottom: '0.2rem' }}>
                  District / City
                </label>
                <input
                  type="text"
                  value={district}
                  onChange={(e) => setDistrict(e.target.value)}
                  placeholder="e.g. New Delhi"
                  className="form-input"
                  style={{ padding: '0.45rem 0.65rem', fontSize: '0.8rem' }}
                />
              </div>

              <div>
                <label style={{ fontSize: '0.72rem', fontWeight: 600, color: 'var(--text-muted)', display: 'block', marginBottom: '0.2rem' }}>
                  State
                </label>
                <input
                  type="text"
                  value={stateName}
                  onChange={(e) => setStateName(e.target.value)}
                  placeholder="e.g. Delhi, Maharashtra"
                  className="form-input"
                  style={{ padding: '0.45rem 0.65rem', fontSize: '0.8rem' }}
                />
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '0.5rem', marginTop: '0.25rem' }}>
              <button
                type="button"
                onClick={loadAllKendras}
                style={{ fontSize: '0.75rem', color: 'var(--teal-600)', textDecoration: 'underline' }}
              >
                Reset / Show All
              </button>

              <button type="submit" className="btn-secondary" style={{ padding: '0.5rem 1rem', fontSize: '0.82rem' }}>
                <span>Search Kendras</span>
                <span>🔍</span>
              </button>
            </div>
          </form>
        </div>
      </div>

      {/* Filter 24x7 Open toggle */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <h3 style={{ fontSize: '1.15rem', fontWeight: 800, color: 'var(--text-main)', margin: 0 }}>
            {resultsHeader}
          </h3>
          <span style={{ background: 'var(--bg-surface-elevated)', border: '1px solid var(--border-medium)', color: 'var(--text-secondary)', padding: '0.2rem 0.65rem', borderRadius: '9999px', fontSize: '0.72rem', fontWeight: 700 }}>
            {resultsBadge}
          </span>
        </div>

        <label style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.78rem', color: 'var(--text-secondary)', cursor: 'pointer' }}>
          <input
            type="checkbox"
            checked={filter24x7}
            onChange={(e) => {
              setFilter24x7(e.target.checked);
              loadAllKendras();
            }}
            style={{ accentColor: 'var(--teal-600)' }}
          />
          <span>24x7 Operational Only</span>
        </label>
      </div>

      {/* Loading & Error States */}
      {loading && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '1rem' }}>
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="skeleton" style={{ height: '180px', borderRadius: '1rem' }} />
          ))}
        </div>
      )}

      {error && (
        <div style={{ padding: '1rem', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: '0.75rem', color: 'var(--rose-600)', fontSize: '0.85rem' }}>
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* Zero results recommendation */}
      {!loading && !error && kendras.length === 0 && (
        <div style={{
          padding: '2.5rem',
          textAlign: 'center',
          background: 'var(--bg-surface)',
          borderRadius: '1rem',
          border: '1px solid var(--border-subtle)',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: '0.75rem',
        }}>
          <div style={{ fontSize: '2.5rem' }}>🏥</div>
          <h4 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-main)', margin: 0 }}>
            No Jan Aushadhi Kendras found matching your query
          </h4>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', maxWidth: '440px', margin: 0 }}>
            No registered store was found within this radius or postal zone in our directory.
          </p>
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', justifyContent: 'center', marginTop: '0.5rem' }}>
            {widerRadiusSuggested && (
              <button
                onClick={() => handleWiderSearch(widerRadiusSuggested)}
                className="btn-primary"
                style={{ fontSize: '0.8rem' }}
              >
                Widen Search to {widerRadiusSuggested} km ↗
              </button>
            )}
            <button onClick={loadAllKendras} className="btn-secondary" style={{ fontSize: '0.8rem' }}>
              View All Registered Hubs
            </button>
          </div>
        </div>
      )}

      {/* Kendra Cards Grid */}
      {!loading && kendras.length > 0 && (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))',
          gap: '1.25rem',
        }}>
          {kendras.map((k) => {
            const distance = k.distance_km !== null && k.distance_km !== undefined ? `${k.distance_km} km away` : null;

            return (
              <div
                key={k.id}
                className="glass-card-interactive"
                style={{
                  padding: '1.25rem',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  gap: '0.85rem',
                }}
              >
                <div>
                  <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '0.5rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', flexWrap: 'wrap' }}>
                      <span style={{ fontSize: '0.68rem', fontWeight: 800, background: 'rgba(13, 148, 136, 0.1)', color: 'var(--teal-600)', padding: '0.15rem 0.5rem', borderRadius: '4px', border: '1px solid rgba(13, 148, 136, 0.2)' }}>
                        {k.official_kendra_code || k.kendra_code || 'PMBJP'}
                      </span>
                      {k.is_24x7 && (
                        <span style={{ fontSize: '0.68rem', fontWeight: 700, background: 'rgba(16, 185, 129, 0.15)', color: 'var(--emerald-600)', padding: '0.15rem 0.5rem', borderRadius: '4px' }}>
                          24x7 Open
                        </span>
                      )}
                    </div>

                    {distance && (
                      <span style={{ fontSize: '0.74rem', fontWeight: 800, background: 'var(--teal-600)', color: '#fff', padding: '0.2rem 0.6rem', borderRadius: '9999px', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                        <span>📍</span>
                        <span>{distance}</span>
                      </span>
                    )}
                  </div>

                  <h4 style={{ fontSize: '1.05rem', fontWeight: 800, color: 'var(--text-main)', marginTop: '0.5rem', marginBottom: '0.25rem' }}>
                    {k.kendra_name || k.hospital_name}
                  </h4>

                  <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', display: 'flex', flexDirection: 'column', gap: '0.25rem', marginTop: '0.35rem' }}>
                    <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.35rem' }}>
                      <span style={{ color: 'var(--text-dim)' }}>📍</span>
                      <span>
                        {k.address || k.location}, {k.city}, {k.state} - <strong>{k.pincode}</strong>
                      </span>
                    </div>

                    {k.opening_hours && (
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', color: 'var(--text-muted)' }}>
                        <span>🕒</span>
                        <span>Hours: {k.opening_hours}</span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Bottom Bar: Call, Directions, Disclaimer */}
                <div style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: '0.75rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  <div style={{ fontSize: '0.68rem', color: 'var(--amber-600)', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                    <span>⚠️</span>
                    <span>{k.stock_status || 'Medicine stock unconfirmed; please call store'}</span>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '0.5rem' }}>
                    <span style={{ fontSize: '0.68rem', color: 'var(--text-dim)' }}>
                      PMBI Verified
                    </span>

                    <div style={{ display: 'flex', gap: '0.4rem' }}>
                      {k.phone && (
                        <a
                          href={`tel:${k.phone}`}
                          style={{
                            padding: '0.35rem 0.65rem',
                            borderRadius: '0.5rem',
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
                          <span>📞</span>
                          <span>Call</span>
                        </a>
                      )}

                      {k.directions_url && (
                        <a
                          href={k.directions_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="btn-primary"
                          style={{
                            padding: '0.35rem 0.75rem',
                            fontSize: '0.75rem',
                          }}
                        >
                          <span>Directions ↗</span>
                        </a>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}
