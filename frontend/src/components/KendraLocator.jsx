import React, { useState, useEffect } from 'react';
import {
  MapPin,
  Navigation,
  Search,
  Phone,
  ExternalLink,
  Clock,
  AlertCircle,
  RotateCcw
} from 'lucide-react';
import { api } from '../services/api';

export default function KendraLocator({ language }) {
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
      setResultsBadge('Pan-India Hubs');
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
    <section className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Header */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.75rem', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '0.75rem' }}>
          <div>
            <div className="hero-pill-badge" style={{ marginBottom: '0.35rem' }}>
              <span>Pradhan Mantri Bhartiya Janaushadhi Pariyojana</span>
            </div>
            <h2 style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--text-main)', margin: 0 }}>
              {language === 'hi' ? 'निकटतम जन औषधि केंद्र खोजें' : 'Find Nearby Jan Aushadhi Kendras'}
            </h2>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', margin: '0.2rem 0 0' }}>
              Locate verified government generic medicine pharmacies across India with GPS or postal search.
            </p>
          </div>

          <a
            href="https://janaushadhi.gov.in/locate-kendra"
            target="_blank"
            rel="noopener noreferrer"
            className="btn-pill-outline"
            style={{ fontSize: '0.78rem' }}
          >
            <span>Official PMBI Locator</span>
            <ExternalLink size={12} />
          </a>
        </div>

        {/* Stock Disclaimer */}
        <div style={{
          padding: '0.75rem 1rem',
          background: 'var(--disclaimer-bg)',
          border: '1px solid var(--disclaimer-border)',
          borderRadius: '8px',
          color: 'var(--disclaimer-text)',
          fontSize: '0.76rem',
          display: 'flex',
          gap: '0.4rem',
          alignItems: 'flex-start',
        }}>
          <AlertCircle size={15} style={{ flexShrink: 0, marginTop: '2px' }} />
          <div>
            <strong>Mandatory Stock Disclaimer:</strong> Store listings help locate nearby Jan Aushadhi stores but do not guarantee real-time inventory. Please call the store to verify availability before traveling.
          </div>
        </div>
      </div>

      {/* Dual Search Options matching clean card layout */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
        gap: '1.25rem',
      }}>
        {/* Option 1: GPS */}
        <div className="clean-card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between', gap: '1rem' }}>
          <div>
            <span style={{ fontSize: '0.7rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--terracotta-600)', letterSpacing: '0.04em' }}>
              Option 1: Device GPS
            </span>
            <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-main)', margin: '0.25rem 0' }}>
              Find Closest Stores Near Me
            </h3>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
              Uses browser location to calculate direct aerial distance. Coordinates are never saved or logged.
            </p>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.8rem' }}>
              <label htmlFor="radius-select" style={{ color: 'var(--text-secondary)', fontWeight: 500 }}>
                Radius:
              </label>
              <select
                id="radius-select"
                value={radiusKm}
                onChange={(e) => setRadiusKm(Number(e.target.value))}
                style={{
                  background: 'var(--bg-surface)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: '6px',
                  padding: '4px 8px',
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
              style={{ width: '100%', padding: '0.65rem' }}
            >
              <Navigation size={15} />
              <span>{gpsLoading ? 'Acquiring GPS...' : 'Use My Current Location'}</span>
            </button>

            {gpsStatus && (
              <div style={{ fontSize: '0.75rem', color: 'var(--terracotta-600)', textAlign: 'center' }}>
                {gpsStatus}
              </div>
            )}
          </div>
        </div>

        {/* Option 2: Postal Search */}
        <div className="clean-card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between', gap: '1rem' }}>
          <div>
            <span style={{ fontSize: '0.7rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-dim)', letterSpacing: '0.04em' }}>
              Option 2: Postal Search
            </span>
            <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-main)', margin: '0.25rem 0' }}>
              Search by PIN Code or District
            </h3>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
              Search across all registered government stores without granting GPS permissions.
            </p>
          </div>

          <form onSubmit={handleManualSearch} style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(90px, 1fr))', gap: '0.4rem' }}>
              <div>
                <input
                  type="text"
                  maxLength={6}
                  value={pincode}
                  onChange={(e) => setPincode(e.target.value)}
                  placeholder="PIN (e.g. 110029)"
                  className="form-input"
                  style={{ padding: '0.45rem 0.65rem', fontSize: '0.8rem' }}
                />
              </div>

              <div>
                <input
                  type="text"
                  value={district}
                  onChange={(e) => setDistrict(e.target.value)}
                  placeholder="District / City"
                  className="form-input"
                  style={{ padding: '0.45rem 0.65rem', fontSize: '0.8rem' }}
                />
              </div>

              <div>
                <input
                  type="text"
                  value={stateName}
                  onChange={(e) => setStateName(e.target.value)}
                  placeholder="State"
                  className="form-input"
                  style={{ padding: '0.45rem 0.65rem', fontSize: '0.8rem' }}
                />
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: '0.25rem' }}>
              <button
                type="button"
                onClick={loadAllKendras}
                style={{ fontSize: '0.75rem', color: 'var(--terracotta-600)', textDecoration: 'underline' }}
              >
                Reset
              </button>

              <button type="submit" className="btn-secondary" style={{ padding: '0.45rem 0.85rem', fontSize: '0.78rem' }}>
                <Search size={13} />
                <span>Search</span>
              </button>
            </div>
          </form>
        </div>
      </div>

      {/* Kendra Results Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-main)', margin: 0 }}>
            {resultsHeader}
          </h3>
          <span style={{ fontSize: '0.76rem', color: 'var(--text-muted)', fontWeight: 600 }}>
            {resultsBadge}
          </span>
        </div>

        <label style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.76rem', color: 'var(--text-secondary)', cursor: 'pointer' }}>
          <input
            type="checkbox"
            checked={filter24x7}
            onChange={(e) => {
              setFilter24x7(e.target.checked);
              loadAllKendras();
            }}
            style={{ accentColor: 'var(--terracotta-600)' }}
          />
          <span>24x7 Operational Only</span>
        </label>
      </div>

      {/* Cards Grid */}
      {!loading && kendras.length > 0 && (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))',
          gap: '1rem',
        }}>
          {kendras.map((k) => {
            const distance = k.distance_km !== null && k.distance_km !== undefined ? `${k.distance_km} km away` : null;

            return (
              <div
                key={k.id}
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
                    <span style={{ fontSize: '0.68rem', fontWeight: 700, background: 'var(--bg-surface-elevated)', color: 'var(--text-secondary)', padding: '0.15rem 0.5rem', borderRadius: '4px', border: '1px solid var(--border-subtle)' }}>
                      {k.official_kendra_code || k.kendra_code || 'PMBJP'}
                    </span>

                    {distance && (
                      <span style={{ fontSize: '0.74rem', fontWeight: 700, color: 'var(--terracotta-600)', display: 'flex', alignItems: 'center', gap: '0.2rem' }}>
                        <MapPin size={12} />
                        <span>{distance}</span>
                      </span>
                    )}
                  </div>

                  <h4 style={{ fontSize: '1.02rem', fontWeight: 700, color: 'var(--text-main)', marginTop: '0.4rem', marginBottom: '0.25rem' }}>
                    {k.kendra_name || k.hospital_name}
                  </h4>

                  <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', display: 'flex', flexDirection: 'column', gap: '0.2rem' }}>
                    <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.35rem' }}>
                      <MapPin size={13} color="var(--text-dim)" style={{ flexShrink: 0, marginTop: '2px' }} />
                      <span>
                        {k.address || k.location}, {k.city}, {k.state} - <strong>{k.pincode}</strong>
                      </span>
                    </div>

                    {k.opening_hours && (
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', color: 'var(--text-muted)', fontSize: '0.74rem' }}>
                        <Clock size={12} />
                        <span>Hours: {k.opening_hours}</span>
                      </div>
                    )}
                  </div>
                </div>

                <div style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: '0.65rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <span style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>
                    PMBI Verified
                  </span>

                  <div style={{ display: 'flex', gap: '0.35rem' }}>
                    {k.phone && (
                      <a
                        href={`tel:${k.phone}`}
                        className="btn-secondary"
                        style={{ padding: '0.3rem 0.65rem', fontSize: '0.74rem' }}
                      >
                        <Phone size={12} />
                        <span>Call</span>
                      </a>
                    )}

                    {k.directions_url && (
                      <a
                        href={k.directions_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="btn-primary"
                        style={{ padding: '0.3rem 0.75rem', fontSize: '0.74rem' }}
                      >
                        <span>Directions</span>
                        <ExternalLink size={12} />
                      </a>
                    )}
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
