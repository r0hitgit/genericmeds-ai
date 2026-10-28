import React from 'react';
import { Pill, ExternalLink, Phone } from 'lucide-react';
import BrandLogo from './BrandLogo';

export default function Footer({ language }) {
  return (
    <footer style={{
      background: 'var(--bg-surface)',
      borderTop: '1px solid var(--border-subtle)',
      marginTop: 'auto',
      padding: '2.5rem 0 1.5rem',
      color: 'var(--text-secondary)',
      fontSize: '0.8rem',
    }}>
      <div className="max-w-content" style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
        {/* Main Columns */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
          gap: '2rem',
        }}>
          {/* Brand Info matching MedBridgeAi / GenericMeds style */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <BrandLogo size={24} />
              <span style={{ fontSize: '1.15rem', fontWeight: 800, color: 'var(--terracotta-600)', letterSpacing: '-0.02em' }}>
                GenericMeds<span style={{ color: 'var(--text-main)' }}>AI</span>
              </span>
            </div>
            <p style={{ margin: 0, color: 'var(--text-muted)', lineHeight: 1.6, fontSize: '0.8rem' }}>
              India's verified generic medicine discovery and PMBJP price comparison platform. Dedicated to reducing out-of-pocket healthcare expenses.
            </p>
          </div>

          {/* Emergency & Official Links */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
            <h4 style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--text-main)', margin: '0 0 0.2rem' }}>
              Emergency Helplines
            </h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem', fontSize: '0.78rem' }}>
              <div>National Emergency: <a href="tel:112" style={{ color: 'var(--terracotta-600)', fontWeight: 600 }}>112</a></div>
              <div>Ambulance Helpline: <a href="tel:108" style={{ color: 'var(--terracotta-600)', fontWeight: 600 }}>108</a></div>
              <div>National Health Portal: <a href="https://www.nhp.gov.in" target="_blank" rel="noopener noreferrer" style={{ color: 'var(--text-secondary)' }}>nhp.gov.in ↗</a></div>
            </div>
          </div>

          {/* Statutory Portals */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
            <h4 style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--text-main)', margin: '0 0 0.2rem' }}>
              Statutory Portals
            </h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem', fontSize: '0.78rem' }}>
              <a href="https://janaushadhi.gov.in" target="_blank" rel="noopener noreferrer" style={{ color: 'var(--text-secondary)' }}>
                PMBI Jan Aushadhi (PMBJP) ↗
              </a>
              <a href="https://nppaindia.nic.in" target="_blank" rel="noopener noreferrer" style={{ color: 'var(--text-secondary)' }}>
                NPPA Pharma Sahi Daam ↗
              </a>
              <a href="/docs" target="_blank" rel="noopener noreferrer" style={{ color: 'var(--terracotta-600)', fontWeight: 600 }}>
                Interactive FastAPI Swagger API Docs ↗
              </a>
            </div>
          </div>
        </div>

        {/* Disclaimer */}
        <div style={{
          padding: '0.85rem 1rem',
          background: 'var(--bg-surface-elevated)',
          border: '1px solid var(--border-subtle)',
          borderRadius: '8px',
          fontSize: '0.74rem',
          color: 'var(--text-muted)',
          lineHeight: 1.5,
        }}>
          <strong>Legal & Medical Disclaimer:</strong> GenericMeds AI is a public information platform and does not provide clinical diagnoses, medical advice, or commercial pharmaceutical sales. Medicine prices and store inventories are subject to official government revisions and local pharmacy availability. Never alter or substitute prescribed medication without consulting a registered medical practitioner.
        </div>

        {/* Bottom copyright */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '0.5rem',
          borderTop: '1px solid var(--border-subtle)',
          paddingTop: '0.85rem',
          fontSize: '0.74rem',
          color: 'var(--text-dim)',
        }}>
          <div>
            © {new Date().getFullYear()} GenericMeds AI
          </div>
          <div>
            Public Service Healthcare Accessibility
          </div>
        </div>
      </div>
    </footer>
  );
}
