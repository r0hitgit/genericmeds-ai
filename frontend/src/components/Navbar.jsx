import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

export default function Navbar({
  activeTab,
  setActiveTab,
  language,
  setLanguage,
  theme,
  setTheme,
  sandboxCount,
}) {
  const [healthStatus, setHealthStatus] = useState({ online: false, checking: true });
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    let isMounted = true;
    const checkBackend = async () => {
      try {
        const res = await api.getHealth();
        if (isMounted) {
          setHealthStatus({
            online: res.status === 'online',
            service: res.service,
            version: res.version,
            db: res.database,
            checking: false,
          });
        }
      } catch (err) {
        if (isMounted) {
          setHealthStatus({ online: false, checking: false });
        }
      }
    };
    checkBackend();
    const interval = setInterval(checkBackend, 30000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  const navItems = [
    { id: 'search', label: language === 'hi' ? 'दवा खोजें' : 'Medicine Search', icon: '💊' },
    { id: 'sandbox', label: language === 'hi' ? 'मूल्य तुलना' : 'Price Sandbox', icon: '⚖️', badge: sandboxCount },
    { id: 'kendras', label: language === 'hi' ? 'जन औषधि केंद्र' : 'Nearby Kendras', icon: '🏥' },
    { id: 'groups', label: language === 'hi' ? '68 समूह' : '68 Groups', icon: '🏷️' },
    { id: 'guidelines', label: language === 'hi' ? 'वितरण नियम' : 'Clinical Rules', icon: '🔬' },
    { id: 'chat', label: language === 'hi' ? 'AI सहायक' : 'AI Assistant', icon: '🤖' },
    { id: 'sources', label: language === 'hi' ? 'डेटा स्रोत' : 'Data Sources', icon: '🏛️' },
  ];

  return (
    <header style={{ position: 'sticky', top: 0, zIndex: 50, borderBottom: '1px solid var(--border-subtle)', background: 'var(--bg-glass)', backdropFilter: 'blur(16px)' }}>
      {/* Medical Safety Advisory Alert */}
      <div className="disclaimer-banner">
        <div className="max-w-content" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '0.75rem', flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ fontSize: '1.05rem' }}>⚠️</span>
            <span>
              <strong>{language === 'hi' ? 'चिकित्सा सूचना:' : 'Medical Notice:'}</strong>{' '}
              {language === 'hi'
                ? 'यह मंच केवल दवा जानकारी और मूल्य तुलना के लिए है, चिकित्सीय सलाह नहीं। डॉक्टर के परामर्श बिना दवा न बदलें।'
                : 'GenericMeds AI provides verified generic alternatives and statutory price comparisons, NOT medical advice. Always consult your doctor or registered pharmacist.'}
            </span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 600, fontSize: '0.75rem' }}>
            <span>{language === 'hi' ? 'आपातकाल? कॉल करें:' : 'Emergency Hotline:'}</span>
            <a href="tel:112" style={{ background: 'var(--amber-500)', color: '#000', padding: '0.15rem 0.5rem', borderRadius: '4px', textDecoration: 'none' }}>112 / 108</a>
          </div>
        </div>
      </div>

      {/* Main Navbar Bar */}
      <div className="max-w-content" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.75rem 1rem', gap: '1rem' }}>
        {/* Brand Logo */}
        <div
          onClick={() => setActiveTab('search')}
          style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', cursor: 'pointer', userSelect: 'none' }}
        >
          <div style={{
            width: '42px',
            height: '42px',
            borderRadius: '12px',
            background: 'linear-gradient(135deg, var(--teal-600) 0%, var(--teal-800) 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#fff',
            fontSize: '1.4rem',
            boxShadow: 'var(--glow-accent)',
          }}>
            💊
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <span style={{ fontSize: '1.25rem', fontWeight: 800, letterSpacing: '-0.02em', color: 'var(--text-main)' }}>
                GenericMeds
              </span>
              <span style={{
                background: 'linear-gradient(135deg, var(--teal-500) 0%, var(--teal-700) 100%)',
                color: '#fff',
                fontSize: '0.68rem',
                fontWeight: 800,
                padding: '0.15rem 0.45rem',
                borderRadius: '9999px',
                letterSpacing: '0.05em',
              }}>
                AI
              </span>
            </div>
            <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', margin: 0, fontWeight: 500 }}>
              PMBJP & NPPA Generic Discovery
            </p>
          </div>
        </div>

        {/* Desktop Navigation Links */}
        <nav style={{ display: 'none', alignItems: 'center', gap: '0.35rem' }} className="desktop-nav">
          {navItems.map((item) => {
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                id={`nav-tab-${item.id}`}
                onClick={() => setActiveTab(item.id)}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '0.4rem',
                  padding: '0.45rem 0.85rem',
                  borderRadius: '0.65rem',
                  fontSize: '0.82rem',
                  fontWeight: isActive ? 700 : 500,
                  color: isActive ? 'var(--teal-600)' : 'var(--text-secondary)',
                  background: isActive ? 'var(--bg-surface-elevated)' : 'transparent',
                  border: isActive ? '1px solid var(--border-medium)' : '1px solid transparent',
                  transition: 'all var(--transition-fast)',
                }}
              >
                <span>{item.icon}</span>
                <span>{item.label}</span>
                {item.badge > 0 && (
                  <span style={{
                    background: 'var(--teal-600)',
                    color: '#fff',
                    fontSize: '0.65rem',
                    fontWeight: 800,
                    padding: '0.1rem 0.4rem',
                    borderRadius: '9999px',
                  }}>
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>

        {/* Utilities: Lang, Theme, Backend Status, Swagger */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
          {/* Backend Status Pill */}
          <div
            title={healthStatus.online ? 'FastAPI Backend Online' : 'Connecting to FastAPI...'}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.35rem',
              padding: '0.3rem 0.6rem',
              borderRadius: '9999px',
              fontSize: '0.72rem',
              fontWeight: 600,
              background: healthStatus.online ? 'rgba(16, 185, 129, 0.12)' : 'rgba(239, 68, 68, 0.12)',
              color: healthStatus.online ? 'var(--emerald-600)' : 'var(--rose-600)',
              border: `1px solid ${healthStatus.online ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`,
            }}
          >
            <span style={{
              width: '7px',
              height: '7px',
              borderRadius: '50%',
              backgroundColor: healthStatus.online ? 'var(--emerald-500)' : 'var(--rose-500)',
              display: 'inline-block',
            }} />
            <span style={{ display: 'none' }} className="status-text sm-inline">
              {healthStatus.online ? 'API Live' : 'API Connecting'}
            </span>
          </div>

          {/* Language Switcher */}
          <div style={{
            display: 'flex',
            background: 'var(--bg-surface-elevated)',
            border: '1px solid var(--border-subtle)',
            borderRadius: '0.5rem',
            padding: '2px',
          }}>
            <button
              onClick={() => setLanguage('en')}
              style={{
                padding: '0.25rem 0.55rem',
                borderRadius: '0.35rem',
                fontSize: '0.74rem',
                fontWeight: 600,
                background: language === 'en' ? 'var(--bg-surface)' : 'transparent',
                color: language === 'en' ? 'var(--teal-600)' : 'var(--text-muted)',
                boxShadow: language === 'en' ? '0 1px 3px rgba(0,0,0,0.1)' : 'none',
              }}
            >
              EN
            </button>
            <button
              onClick={() => setLanguage('hi')}
              style={{
                padding: '0.25rem 0.55rem',
                borderRadius: '0.35rem',
                fontSize: '0.74rem',
                fontWeight: 600,
                background: language === 'hi' ? 'var(--bg-surface)' : 'transparent',
                color: language === 'hi' ? 'var(--teal-600)' : 'var(--text-muted)',
                boxShadow: language === 'hi' ? '0 1px 3px rgba(0,0,0,0.1)' : 'none',
              }}
            >
              हिंदी
            </button>
          </div>

          {/* Theme Toggle (Dark / Light) */}
          <button
            onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
            title="Toggle Dark / Light theme"
            aria-label="Toggle theme"
            style={{
              width: '34px',
              height: '34px',
              borderRadius: '0.5rem',
              background: 'var(--bg-surface-elevated)',
              border: '1px solid var(--border-subtle)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '1rem',
              color: 'var(--text-main)',
            }}
          >
            {theme === 'dark' ? '☀️' : '🌙'}
          </button>

          {/* Swagger API External Link */}
          <a
            href="/docs"
            target="_blank"
            rel="noopener noreferrer"
            title="Interactive Swagger OpenAPI Docs"
            style={{
              padding: '0.35rem 0.65rem',
              borderRadius: '0.5rem',
              border: '1px solid var(--border-medium)',
              fontSize: '0.75rem',
              fontWeight: 600,
              color: 'var(--text-secondary)',
              background: 'var(--bg-surface)',
              display: 'none',
              alignItems: 'center',
              gap: '0.25rem',
            }}
            className="swagger-btn"
          >
            <span>Swagger</span>
            <span>↗</span>
          </a>

          {/* Mobile Menu Hamburger */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            style={{
              width: '36px',
              height: '36px',
              borderRadius: '0.5rem',
              background: 'var(--bg-surface-elevated)',
              border: '1px solid var(--border-subtle)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '1.2rem',
              color: 'var(--text-main)',
            }}
            className="mobile-hamburger"
          >
            {mobileMenuOpen ? '✕' : '☰'}
          </button>
        </div>
      </div>

      {/* Mobile Drawer Navigation */}
      {mobileMenuOpen && (
        <div style={{
          padding: '0.75rem 1rem',
          background: 'var(--bg-surface)',
          borderTop: '1px solid var(--border-subtle)',
          display: 'flex',
          flexDirection: 'column',
          gap: '0.35rem',
        }}>
          {navItems.map((item) => (
            <button
              key={item.id}
              onClick={() => {
                setActiveTab(item.id);
                setMobileMenuOpen(false);
              }}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '0.65rem 0.85rem',
                borderRadius: '0.5rem',
                fontSize: '0.88rem',
                fontWeight: activeTab === item.id ? 700 : 500,
                color: activeTab === item.id ? 'var(--teal-600)' : 'var(--text-main)',
                background: activeTab === item.id ? 'var(--bg-surface-elevated)' : 'transparent',
              }}
            >
              <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <span>{item.icon}</span>
                <span>{item.label}</span>
              </span>
              {item.badge > 0 && (
                <span style={{
                  background: 'var(--teal-600)',
                  color: '#fff',
                  fontSize: '0.7rem',
                  fontWeight: 700,
                  padding: '0.1rem 0.5rem',
                  borderRadius: '9999px',
                }}>
                  {item.badge}
                </span>
              )}
            </button>
          ))}
          <a
            href="/docs"
            target="_blank"
            rel="noopener noreferrer"
            style={{
              padding: '0.65rem 0.85rem',
              fontSize: '0.85rem',
              color: 'var(--teal-600)',
              fontWeight: 600,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
            }}
          >
            <span>Interactive Swagger API</span>
            <span>↗</span>
          </a>
        </div>
      )}

      <style>{`
        @media (min-width: 900px) {
          .desktop-nav { display: flex !important; }
          .mobile-hamburger { display: none !important; }
          .sm-inline { display: inline !important; }
          .swagger-btn { display: inline-flex !important; }
        }
      `}</style>
    </header>
  );
}
