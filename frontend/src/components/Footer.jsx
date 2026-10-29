import React, { useState, useEffect } from 'react';
import { 
  ExternalLink, 
  Phone, 
  ShieldCheck, 
  HeartHandshake, 
  ArrowUp, 
  CheckCircle2, 
  FileText, 
  X,
  Compass,
  Landmark,
  AlertTriangle
} from 'lucide-react';
import BrandLogo from './BrandLogo';

export default function Footer({ language = 'en', onNavigate }) {
  const [activeModal, setActiveModal] = useState(null); // 'privacy' | 'terms' | 'methodology' | null

  // Close modal on Escape key
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') setActiveModal(null);
    };
    if (activeModal) {
      window.addEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'hidden';
    }
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = '';
    };
  }, [activeModal]);

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleNavClick = (tabKey) => {
    if (onNavigate) {
      onNavigate(tabKey);
      scrollToTop();
    }
  };

  const isHindi = language === 'hi';

  return (
    <footer style={{
      position: 'relative',
      zIndex: 1001,
      background: 'var(--bg-surface)',
      borderTop: '1px solid var(--border-subtle)',
      marginTop: 'auto',
      padding: '2.5rem 0 1.5rem',
      color: 'var(--text-secondary)',
      fontSize: '0.8rem',
    }}>
      <div className="max-w-content" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
        
        {/* Top Trust & Highlight Banner */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
          gap: '1rem',
          padding: '1rem 1.25rem',
          background: 'var(--bg-surface-elevated)',
          border: '1px solid var(--border-subtle)',
          borderRadius: '12px',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div style={{
              width: '32px',
              height: '32px',
              borderRadius: '8px',
              background: 'var(--pill-bg)',
              color: 'var(--terracotta-600)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0,
            }}>
              <ShieldCheck size={18} />
            </div>
            <div>
              <div style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--text-main)' }}>
                {isHindi ? '100% सत्यापित डेटा' : '100% Verified Data'}
              </div>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                {isHindi ? 'PMBI व NPPA आधिकारिक राजपत्र' : 'Sourced from PMBI & NPPA Gazette'}
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div style={{
              width: '32px',
              height: '32px',
              borderRadius: '8px',
              background: '#f0fdf4',
              color: 'var(--green-700)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0,
            }}>
              <HeartHandshake size={18} />
            </div>
            <div>
              <div style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--text-main)' }}>
                {isHindi ? 'निःशुल्क सार्वजनिक सेवा' : 'Non-Commercial Public Service'}
              </div>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                {isHindi ? 'विज्ञापन-मुक्त और डेटा-सुरक्षित' : 'Zero Ad Tracking & DPDP Compliant'}
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div style={{
              width: '32px',
              height: '32px',
              borderRadius: '8px',
              background: 'var(--pill-bg)',
              color: 'var(--terracotta-600)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0,
            }}>
              <Phone size={18} />
            </div>
            <div>
              <div style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--text-main)' }}>
                PMBJP Toll-Free
              </div>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                <a href="tel:18001808080" style={{ color: 'var(--terracotta-600)', fontWeight: 700 }}>
                  1800-180-8080
                </a> (Govt. Helpline)
              </div>
            </div>
          </div>
        </div>

        {/* Main 4 Columns */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
          gap: '2rem',
        }}>
          {/* Column 1: Brand & Mission */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <BrandLogo size={24} />
              <span style={{ fontSize: '1.15rem', fontWeight: 800, color: 'var(--terracotta-600)', letterSpacing: '-0.02em' }}>
                GenericMeds<span style={{ color: 'var(--text-main)' }}>AI</span>
              </span>
            </div>
            <p style={{ margin: 0, color: 'var(--text-muted)', lineHeight: 1.6, fontSize: '0.78rem' }}>
              {isHindi
                ? 'भारत का सत्यापित जेनेरिक दवा खोज, साल्ट संरचना समानता और पीएमबीजेपी मूल्य तुलना मंच। नागरिकों के स्वास्थ्य खर्च को कम करने हेतु समर्पित।'
                : "India's verified generic medicine discovery, salt composition equivalence, and PMBJP price comparison platform. Dedicated to reducing out-of-pocket healthcare expenses."}
            </p>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem', marginTop: '0.25rem' }}>
              <span style={{
                fontSize: '0.7rem',
                padding: '0.2rem 0.55rem',
                background: 'var(--bg-surface-elevated)',
                border: '1px solid var(--border-subtle)',
                borderRadius: '6px',
                color: 'var(--text-secondary)',
                fontWeight: 600,
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.35rem',
              }}>
                <CheckCircle2 size={12} color="var(--green-700)" />
                <span>Made for India</span>
              </span>
              <span style={{
                fontSize: '0.7rem',
                padding: '0.2rem 0.55rem',
                background: 'var(--bg-surface-elevated)',
                border: '1px solid var(--border-subtle)',
                borderRadius: '6px',
                color: 'var(--text-secondary)',
                fontWeight: 600,
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.35rem',
              }}>
                <ShieldCheck size={12} color="var(--terracotta-600)" />
                <span>DPDP 2023 Safe</span>
              </span>
            </div>
          </div>

          {/* Column 2: Quick Platform Navigation */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <h4 style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--text-main)', margin: '0 0 0.2rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <Compass size={14} color="var(--terracotta-600)" />
              <span>{isHindi ? 'प्लेटफ़ॉर्म नेविगेशन' : 'Platform Features'}</span>
            </h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem', fontSize: '0.78rem' }}>
              <button
                onClick={() => handleNavClick('home')}
                style={{ background: 'none', border: 'none', padding: 0, textAlign: 'left', color: 'var(--text-secondary)', cursor: 'pointer' }}
                onMouseEnter={(e) => e.target.style.color = 'var(--terracotta-600)'}
                onMouseLeave={(e) => e.target.style.color = 'var(--text-secondary)'}
              >
                {isHindi ? 'दवा खोज एवं मूल्य तुलना' : 'Medicine Search & Price Comparison'}
              </button>
              <button
                onClick={() => handleNavClick('kendras')}
                style={{ background: 'none', border: 'none', padding: 0, textAlign: 'left', color: 'var(--text-secondary)', cursor: 'pointer' }}
                onMouseEnter={(e) => e.target.style.color = 'var(--terracotta-600)'}
                onMouseLeave={(e) => e.target.style.color = 'var(--text-secondary)'}
              >
                {isHindi ? 'जन औषधि केंद्र खोजक' : 'PMBJP Kendra Locator (10,000+ Kendras)'}
              </button>
              <button
                onClick={() => handleNavClick('groups')}
                style={{ background: 'none', border: 'none', padding: 0, textAlign: 'left', color: 'var(--text-secondary)', cursor: 'pointer' }}
                onMouseEnter={(e) => e.target.style.color = 'var(--terracotta-600)'}
                onMouseLeave={(e) => e.target.style.color = 'var(--text-secondary)'}
              >
                {isHindi ? 'चिकित्सीय दवा श्रेणियां' : 'Therapeutic Drug Categories'}
              </button>
              <button
                onClick={() => handleNavClick('guidelines')}
                style={{ background: 'none', border: 'none', padding: 0, textAlign: 'left', color: 'var(--text-secondary)', cursor: 'pointer' }}
                onMouseEnter={(e) => e.target.style.color = 'var(--terracotta-600)'}
                onMouseLeave={(e) => e.target.style.color = 'var(--text-secondary)'}
              >
                {isHindi ? 'नैदानिक एवं विनियामक दिशानिर्देश' : 'Clinical Substitution Guidelines'}
              </button>
              <button
                onClick={() => handleNavClick('sources')}
                style={{ background: 'none', border: 'none', padding: 0, textAlign: 'left', color: 'var(--text-secondary)', cursor: 'pointer' }}
                onMouseEnter={(e) => e.target.style.color = 'var(--terracotta-600)'}
                onMouseLeave={(e) => e.target.style.color = 'var(--text-secondary)'}
              >
                {isHindi ? 'सत्यापित सरकारी डेटा स्रोत' : 'Statutory & Government Data Sources'}
              </button>
              <button
                onClick={() => handleNavClick('chat')}
                style={{ background: 'none', border: 'none', padding: 0, textAlign: 'left', color: 'var(--terracotta-600)', fontWeight: 600, cursor: 'pointer' }}
              >
                {isHindi ? 'एआई स्वास्थ्य सहायक' : 'AI Medicine Assistant ↗'}
              </button>
            </div>
          </div>

          {/* Column 3: Statutory & Govt Portals */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <h4 style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--text-main)', margin: '0 0 0.2rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <Landmark size={14} color="var(--terracotta-600)" />
              <span>{isHindi ? 'वैधानिक व सरकारी पोर्टल' : 'Statutory Portals'}</span>
            </h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem', fontSize: '0.78rem' }}>
              <a href="https://janaushadhi.gov.in" target="_blank" rel="noopener noreferrer" style={{ color: 'var(--text-secondary)' }}>
                PMBI Jan Aushadhi (PMBJP) ↗
              </a>
              <a href="https://nppaindia.nic.in" target="_blank" rel="noopener noreferrer" style={{ color: 'var(--text-secondary)' }}>
                NPPA Pharma Sahi Daam ↗
              </a>
              <a href="https://abdm.gov.in" target="_blank" rel="noopener noreferrer" style={{ color: 'var(--text-secondary)' }}>
                Ayushman Bharat Digital Mission (ABDM) ↗
              </a>
              <a href="https://cdsco.gov.in" target="_blank" rel="noopener noreferrer" style={{ color: 'var(--text-secondary)' }}>
                CDSCO Drug Controller General ↗
              </a>
              <a href="https://chemicals.gov.in" target="_blank" rel="noopener noreferrer" style={{ color: 'var(--text-secondary)' }}>
                Ministry of Chemicals & Fertilizers ↗
              </a>
            </div>
          </div>

          {/* Column 4: Emergency Helplines */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <h4 style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--text-main)', margin: '0 0 0.2rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <Phone size={14} color="var(--terracotta-600)" />
              <span>{isHindi ? 'आपातकालीन हेल्पलाइन' : 'Emergency & Helplines'}</span>
            </h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem', fontSize: '0.78rem' }}>
              <div>
                National Emergency: <a href="tel:112" style={{ color: 'var(--terracotta-600)', fontWeight: 700 }}>112</a> (24x7)
              </div>
              <div>
                Ambulance Helpline: <a href="tel:108" style={{ color: 'var(--terracotta-600)', fontWeight: 700 }}>108</a> (Medical)
              </div>
              <div>
                PMBJP Toll-Free: <a href="tel:18001808080" style={{ color: 'var(--terracotta-600)', fontWeight: 700 }}>1800-180-8080</a>
              </div>
              <div>
                Tele-MANAS (Mental Health): <a href="tel:14416" style={{ color: 'var(--text-secondary)', fontWeight: 600 }}>14416</a>
              </div>
              <div>
                National Health Portal: <a href="https://www.nhp.gov.in" target="_blank" rel="noopener noreferrer" style={{ color: 'var(--text-secondary)' }}>nhp.gov.in ↗</a>
              </div>
            </div>
          </div>
        </div>

        {/* Legal & Medical Disclaimer Banner */}
        <div style={{
          padding: '1rem 1.25rem',
          background: 'var(--bg-surface-elevated)',
          border: '1px solid var(--border-subtle)',
          borderRadius: '10px',
          fontSize: '0.75rem',
          color: 'var(--text-muted)',
          lineHeight: 1.6,
          display: 'flex',
          gap: '0.75rem',
          alignItems: 'flex-start',
        }}>
          <AlertTriangle size={18} color="var(--terracotta-600)" style={{ flexShrink: 0, marginTop: '2px' }} />
          <div>
            <strong style={{ color: 'var(--text-main)' }}>
              {isHindi ? 'कानूनी एवं चिकित्सीय अस्वीकरण (Legal & Medical Disclaimer): ' : 'Legal & Medical Disclaimer: '}
            </strong>
            {isHindi
              ? 'GenericMeds AI एक सार्वजनिक सूचना एवं मूल्य पारदर्शिता मंच है। यह मंच कोई चिकित्सीय निदान, नुस्खा या दवाओं की सीधी बिक्री प्रदान नहीं करता है। किसी भी दवा के विकल्प या साल्ट को बदलने से पहले हमेशा पंजीकृत चिकित्सक (RMP) अथवा योग्य फार्मासिस्ट से परामर्श अवश्य लें।'
              : 'GenericMeds AI is a non-commercial digital public information platform designed solely for educational price transparency. It does not provide clinical diagnoses, medical advice, or commercial pharmaceutical sales. Medicine prices, pack sizes, and store stocks are subject to official government notifications and local pharmacy inventory. Never alter, substitute, or discontinue prescribed medications without explicit consultation with a registered medical practitioner (RMP).'}
          </div>
        </div>

        {/* Bottom Copyright & Policy Links */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '1rem',
          borderTop: '1px solid var(--border-subtle)',
          paddingTop: '1.25rem',
          fontSize: '0.75rem',
          color: 'var(--text-dim)',
        }}>
          <div>
            © {new Date().getFullYear()} GenericMeds AI • {isHindi ? 'भारतीय नागरिकों हेतु सस्ती स्वास्थ्य सेवा पहल' : 'In Public Interest for Indian Healthcare Accessibility'}
          </div>

          {/* Interactive Policy Modal Buttons & Scroll to Top */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem', flexWrap: 'wrap' }}>
            <button
              onClick={() => setActiveModal('privacy')}
              style={{
                background: 'none',
                border: 'none',
                padding: 0,
                color: 'var(--text-secondary)',
                fontSize: '0.75rem',
                cursor: 'pointer',
                textDecoration: 'underline',
              }}
              onMouseEnter={(e) => e.target.style.color = 'var(--terracotta-600)'}
              onMouseLeave={(e) => e.target.style.color = 'var(--text-secondary)'}
            >
              {isHindi ? 'गोपनीयता नीति' : 'Privacy Policy'}
            </button>

            <button
              onClick={() => setActiveModal('terms')}
              style={{
                background: 'none',
                border: 'none',
                padding: 0,
                color: 'var(--text-secondary)',
                fontSize: '0.75rem',
                cursor: 'pointer',
                textDecoration: 'underline',
              }}
              onMouseEnter={(e) => e.target.style.color = 'var(--terracotta-600)'}
              onMouseLeave={(e) => e.target.style.color = 'var(--text-secondary)'}
            >
              {isHindi ? 'उपयोग की शर्तें' : 'Terms of Use'}
            </button>

            <button
              onClick={() => setActiveModal('methodology')}
              style={{
                background: 'none',
                border: 'none',
                padding: 0,
                color: 'var(--text-secondary)',
                fontSize: '0.75rem',
                cursor: 'pointer',
                textDecoration: 'underline',
              }}
              onMouseEnter={(e) => e.target.style.color = 'var(--terracotta-600)'}
              onMouseLeave={(e) => e.target.style.color = 'var(--text-secondary)'}
            >
              {isHindi ? 'डेटा पद्धति' : 'Data Methodology'}
            </button>

            <button
              onClick={scrollToTop}
              title={isHindi ? 'शीर्ष पर जाएं' : 'Back to top'}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.3rem',
                padding: '0.3rem 0.6rem',
                borderRadius: '6px',
                background: 'var(--bg-surface-elevated)',
                border: '1px solid var(--border-subtle)',
                color: 'var(--text-secondary)',
                fontSize: '0.72rem',
                fontWeight: 600,
                cursor: 'pointer',
              }}
              onMouseEnter={(e) => e.target.style.color = 'var(--terracotta-600)'}
              onMouseLeave={(e) => e.target.style.color = 'var(--text-secondary)'}
            >
              <span>{isHindi ? 'ऊपर जाएं' : 'Top'}</span>
              <ArrowUp size={12} />
            </button>
          </div>
        </div>
      </div>

      {/* Policy & Governance Modals */}
      {activeModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0, 0, 0, 0.55)',
          backdropFilter: 'blur(4px)',
          zIndex: 9999,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '1.25rem',
        }} onClick={() => setActiveModal(null)}>
          <div
            onClick={(e) => e.stopPropagation()}
            style={{
              background: 'var(--bg-surface)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '16px',
              maxWidth: '640px',
              width: '100%',
              maxHeight: '85vh',
              overflowY: 'auto',
              padding: '1.75rem',
              boxShadow: '0 20px 40px rgba(0,0,0,0.2)',
              position: 'relative',
              display: 'flex',
              flexDirection: 'column',
              gap: '1rem',
            }}
          >
            {/* Modal Header */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '0.75rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <FileText size={20} color="var(--terracotta-600)" />
                <h3 style={{ margin: 0, fontSize: '1.15rem', fontWeight: 700, color: 'var(--text-main)' }}>
                  {activeModal === 'privacy' && (isHindi ? 'गोपनीयता नीति (Privacy Policy)' : 'Privacy Policy')}
                  {activeModal === 'terms' && (isHindi ? 'उपयोग की शर्तें (Terms of Use)' : 'Terms of Use')}
                  {activeModal === 'methodology' && (isHindi ? 'डेटा स्रोत एवं सत्यापन पद्धति' : 'Data Verification Methodology')}
                </h3>
              </div>
              <button
                onClick={() => setActiveModal(null)}
                style={{
                  background: 'none',
                  border: 'none',
                  cursor: 'pointer',
                  color: 'var(--text-muted)',
                  padding: '4px',
                  borderRadius: '6px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <X size={20} />
              </button>
            </div>

            {/* Modal Content */}
            <div style={{ fontSize: '0.84rem', lineHeight: 1.65, color: 'var(--text-secondary)' }}>
              {activeModal === 'privacy' && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  <p>
                    <strong>1. Zero Personal Health Data Collection:</strong> GenericMeds AI is engineered on a privacy-by-default architecture. We do not require account sign-ups, phone numbers, or email addresses to search for generic medicines.
                  </p>
                  <p>
                    <strong>2. Prescription Data:</strong> Search queries and medicine names entered into the search bar or AI assistant are processed in transient memory to generate salt matches and are not stored in any persistent profile.
                  </p>
                  <p>
                    <strong>3. Geolocation & Kendra Discovery:</strong> When you use the "Detect Location" feature on the PMBJP Kendra Locator, your coordinates are processed strictly in your local browser to calculate radial distances. Geolocation data is never logged or transmitted to third parties.
                  </p>
                  <p>
                    <strong>4. Compliance with Indian DPDP Act 2023:</strong> This platform adheres strictly to the principles of data minimization and purpose limitation under India's Digital Personal Data Protection Act, 2023.
                  </p>
                </div>
              )}

              {activeModal === 'terms' && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  <p>
                    <strong>1. Public Information Service:</strong> GenericMeds AI provides publicly accessible pricing and salt equivalence data solely for consumer education, price awareness, and public health literacy.
                  </p>
                  <p>
                    <strong>2. No Commercial Pharmacy Operations:</strong> This platform does not sell, ship, warehouse, or distribute pharmaceutical products. All PMBJP generic medicines must be procured through government-authorized Jan Aushadhi Kendras or licensed retail pharmacies.
                  </p>
                  <p>
                    <strong>3. Doctor Consultation is Mandatory:</strong> While generic formulations contain identical active pharmaceutical ingredients (APIs), dosage strengths, and therapeutic efficacy, you must consult your treating doctor or registered pharmacist prior to altering any prescription.
                  </p>
                  <p>
                    <strong>4. Price Variations:</strong> Government ceiling prices (NPPA) and Jan Aushadhi prices (PMBI) are updated per official revisions; users should verify retail pack MRP at the point of dispensing.
                  </p>
                </div>
              )}

              {activeModal === 'methodology' && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  <p>
                    <strong>1. PMBI Product Master Synchronization:</strong> Generic formulations and ceiling rates are mapped against the Pharmaceuticals & Medical Devices Bureau of India (PMBI) official Jan Aushadhi catalog.
                  </p>
                  <p>
                    <strong>2. NPPA DPCO Price Ceilings:</strong> Branded medicine maximum retail prices (MRPs) are checked against the National Pharmaceutical Pricing Authority (NPPA) Drugs (Prices Control) Order notifications to determine consumer savings.
                  </p>
                  <p>
                    <strong>3. Chemical Salt Equivalence:</strong> Equivalence is calculated by matching active pharmaceutical ingredients (APIs), therapeutic dosage strength (e.g. 500mg, 650mg), and drug release formulation (e.g., Immediate Release vs Sustained Release).
                  </p>
                  <p>
                    <strong>4. Kendra Geocoding:</strong> Jan Aushadhi Kendra addresses, district registries, and PIN code mappings are indexed from official Department of Pharmaceuticals open registers.
                  </p>
                </div>
              )}
            </div>

            {/* Modal Footer */}
            <div style={{ display: 'flex', justifyContent: 'flex-end', borderTop: '1px solid var(--border-subtle)', paddingTop: '0.75rem' }}>
              <button
                onClick={() => setActiveModal(null)}
                style={{
                  padding: '0.45rem 1.1rem',
                  borderRadius: '8px',
                  background: 'var(--terracotta-600)',
                  color: '#ffffff',
                  border: 'none',
                  fontSize: '0.82rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                }}
              >
                {isHindi ? 'बंद करें (Close)' : 'Close'}
              </button>
            </div>
          </div>
        </div>
      )}
    </footer>
  );
}
