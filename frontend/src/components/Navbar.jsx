import React, { useState, useEffect } from 'react';
import {
  Home,
  Pill,
  Search,
  Scale,
  MapPin,
  Tag,
  FlaskConical,
  Bot,
  Landmark,
  Sun,
  Moon,
  ExternalLink,
  Menu,
  X,
  AlertCircle
} from 'lucide-react';
import { api } from '../services/api';
import BrandLogo from './BrandLogo';

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
    { id: 'home', label: language === 'hi' ? 'मुख्य पृष्ठ' : 'Home', icon: Home },
    { id: 'medicines', label: language === 'hi' ? 'दवाएं' : 'Medicines', icon: Search },
    { id: 'sandbox', label: language === 'hi' ? 'तुलना' : 'Compare', icon: Scale, badge: sandboxCount },
    { id: 'kendras', label: language === 'hi' ? 'केंद्र' : 'Kendras', icon: MapPin },
    { id: 'groups', label: language === 'hi' ? 'समूह' : 'Groups', icon: Tag },
    { id: 'guidelines', label: language === 'hi' ? 'नियम' : 'Rules', icon: FlaskConical },
    { id: 'chat', label: language === 'hi' ? 'सहायक' : 'Assistant', icon: Bot },
    { id: 'sources', label: language === 'hi' ? 'डेटा स्रोत' : 'Sources', icon: Landmark },
  ];

  return (
    <header style={{
      position: 'sticky',
      top: 0,
      zIndex: 1001,
      backgroundColor: 'var(--bg-surface)',
      borderBottom: '1px solid var(--border-subtle)',
    }}>
      {/* Top Advisory Strip */}
      <div style={{
        background: 'var(--disclaimer-bg)',
        borderBottom: '1px solid var(--disclaimer-border)',
        color: 'var(--disclaimer-text)',
        fontSize: '0.74rem',
        padding: '0.35rem 0',
      }}>
        <div className="max-w-content" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '0.75rem', flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <AlertCircle size={14} color="var(--terracotta-600)" />
            <span>
              <strong>{language === 'hi' ? 'चिकित्सा सूचना:' : 'Medical Notice:'}</strong>{' '}
              {language === 'hi'
                ? 'यह मंच दवा जानकारी और मूल्य तुलना के लिए है, चिकित्सीय सलाह नहीं।'
                : 'GenericMeds AI provides verified generic alternatives and PMBJP price comparisons, NOT medical advice.'}
            </span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.72rem' }}>
            <span>{language === 'hi' ? 'आपातकाल:' : 'Emergency:'}</span>
            <a href="tel:112" style={{ fontWeight: 700, color: 'var(--terracotta-600)' }}>112 / 108</a>
          </div>
        </div>
      </div>

      {/* Main Navbar */}
      <div className="max-w-content" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: '64px' }}>
        {/* Brand Logo matching favicon */}
        <div
          onClick={() => setActiveTab('home')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.65rem',
            cursor: 'pointer',
            userSelect: 'none',
          }}
        >
          <BrandLogo size={28} />
          <span style={{
            fontSize: '1.25rem',
            fontWeight: 800,
            color: 'var(--terracotta-600)',
            letterSpacing: '-0.02em',
          }}>
            GenericMeds<span style={{ color: 'var(--text-main)' }}>AI</span>
          </span>
        </div>

        {/* Centered Clean Text Navigation Links - HOME AND MEDICINES ARE NOW COMPLETELY SEPARATE */}
        <nav style={{ display: 'none', alignItems: 'center', gap: '1.5rem' }} className="desktop-nav">
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
                  gap: '0.35rem',
                  padding: '0.4rem 0',
                  fontSize: '0.84rem',
                  fontWeight: isActive ? 600 : 500,
                  color: isActive ? 'var(--terracotta-600)' : 'var(--text-secondary)',
                  borderBottom: isActive ? '2px solid var(--terracotta-600)' : '2px solid transparent',
                  transition: 'all var(--transition-fast)',
                }}
              >
                <span>{item.label}</span>
                {item.badge > 0 && (
                  <span style={{
                    background: 'var(--terracotta-600)',
                    color: '#fff',
                    fontSize: '0.62rem',
                    fontWeight: 700,
                    padding: '0.1rem 0.35rem',
                    borderRadius: '9999px',
                    marginLeft: '2px',
                  }}>
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>

        {/* Right side utilities: Status, Lang, Theme */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          {/* Language Switcher */}
          <div style={{
            display: 'flex',
            border: '1px solid var(--border-subtle)',
            borderRadius: '6px',
            overflow: 'hidden',
          }}>
            <button
              onClick={() => setLanguage('en')}
              style={{
                padding: '0.2rem 0.45rem',
                fontSize: '0.72rem',
                fontWeight: 600,
                background: language === 'en' ? 'var(--bg-surface-elevated)' : 'transparent',
                color: language === 'en' ? 'var(--terracotta-600)' : 'var(--text-muted)',
              }}
            >
              EN
            </button>
            <button
              onClick={() => setLanguage('hi')}
              style={{
                padding: '0.2rem 0.45rem',
                fontSize: '0.72rem',
                fontWeight: 600,
                background: language === 'hi' ? 'var(--bg-surface-elevated)' : 'transparent',
                color: language === 'hi' ? 'var(--terracotta-600)' : 'var(--text-muted)',
              }}
            >
              हिंदी
            </button>
          </div>

          {/* Theme Switcher with Lucide Icon */}
          <button
            onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
            title="Toggle Theme"
            aria-label="Toggle Theme"
            style={{
              width: '32px',
              height: '32px',
              borderRadius: '8px',
              border: '1px solid var(--border-subtle)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--text-secondary)',
            }}
          >
            {theme === 'dark' ? <Sun size={15} /> : <Moon size={15} />}
          </button>


          {/* Mobile menu hamburger */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            style={{
              width: '34px',
              height: '34px',
              borderRadius: '8px',
              border: '1px solid var(--border-subtle)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--text-main)',
            }}
            className="mobile-hamburger"
          >
            {mobileMenuOpen ? <X size={18} /> : <Menu size={18} />}
          </button>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div style={{
          padding: '1rem',
          background: 'var(--bg-surface)',
          borderTop: '1px solid var(--border-subtle)',
          display: 'flex',
          flexDirection: 'column',
          gap: '0.5rem',
        }}>
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
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
                  padding: '0.6rem 0.85rem',
                  borderRadius: '6px',
                  fontSize: '0.86rem',
                  fontWeight: activeTab === item.id ? 600 : 500,
                  color: activeTab === item.id ? 'var(--terracotta-600)' : 'var(--text-main)',
                  background: activeTab === item.id ? 'var(--bg-surface-elevated)' : 'transparent',
                }}
              >
                <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <Icon size={16} color={activeTab === item.id ? 'var(--terracotta-600)' : 'var(--text-muted)'} />
                  <span>{item.label}</span>
                </span>
                {item.badge > 0 && (
                  <span style={{
                    background: 'var(--terracotta-600)',
                    color: '#fff',
                    fontSize: '0.65rem',
                    fontWeight: 700,
                    padding: '0.1rem 0.45rem',
                    borderRadius: '9999px',
                  }}>
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}

        </div>
      )}

      <style>{`
        @media (min-width: 880px) {
          .desktop-nav { display: flex !important; }
          .mobile-hamburger { display: none !important; }
        }
      `}</style>
    </header>
  );
}
