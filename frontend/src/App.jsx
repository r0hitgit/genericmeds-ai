import React, { useState, useEffect } from 'react';
import { Pill } from 'lucide-react';
import Navbar from './components/Navbar';
import MedicineSearch from './components/MedicineSearch';
import ComparisonSandbox from './components/ComparisonSandbox';
import KendraLocator from './components/KendraLocator';
import TherapeuticGroups from './components/TherapeuticGroups';
import ClinicalGuidelines from './components/ClinicalGuidelines';
import AIChatAssistant from './components/AIChatAssistant';
import DataSources from './components/DataSources';
import Footer from './components/Footer';

export default function App() {
  const [activeTab, setActiveTab] = useState('search');
  const [language, setLanguage] = useState(() => localStorage.getItem('gm_lang') || 'en');
  const [theme, setTheme] = useState(() => localStorage.getItem('gm_theme') || 'light');
  const [sandboxItems, setSandboxItems] = useState(() => {
    try {
      const saved = localStorage.getItem('gm_sandbox');
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });
  const [searchInitialQuery, setSearchInitialQuery] = useState('');
  const [toastMessage, setToastMessage] = useState(null);

  // Sync theme
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('gm_theme', theme);
  }, [theme]);

  // Sync language
  useEffect(() => {
    localStorage.setItem('gm_lang', language);
  }, [language]);

  // Sync sandbox
  useEffect(() => {
    localStorage.setItem('gm_sandbox', JSON.stringify(sandboxItems));
  }, [sandboxItems]);

  const showToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => {
      setToastMessage(null);
    }, 3000);
  };

  const handleAddToSandbox = (medicine) => {
    if (!medicine) return;
    if (sandboxItems.some((m) => m.id === medicine.id)) {
      showToast(`"${medicine.brand_name}" is already in your Price Sandbox!`);
      return;
    }
    setSandboxItems((prev) => [...prev, medicine]);
    showToast(`Added "${medicine.brand_name}" to Comparison Sandbox.`);
  };

  const handleRemoveFromSandbox = (id) => {
    setSandboxItems((prev) => prev.filter((m) => m.id !== id));
  };

  const handleClearSandbox = () => {
    setSandboxItems([]);
    showToast('Comparison Sandbox cleared.');
  };

  const handleSelectGroup = (groupName) => {
    setSearchInitialQuery(groupName);
    setActiveTab('search');
  };

  const handleLocateStores = () => {
    setActiveTab('kendras');
  };

  return (
    <div className="app-container">
      {/* Toast Notification */}
      {toastMessage && (
        <div style={{
          position: 'fixed',
          bottom: '24px',
          right: '24px',
          zIndex: 9999,
          background: 'var(--bg-surface)',
          color: 'var(--text-main)',
          border: '1px solid var(--terracotta-600)',
          borderRadius: '8px',
          padding: '0.65rem 1.15rem',
          boxShadow: 'var(--card-shadow-hover)',
          fontSize: '0.84rem',
          fontWeight: 600,
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          animation: 'fadeInScale 0.2s ease-out',
        }}>
          <Pill size={16} color="var(--terracotta-600)" />
          <span>{toastMessage}</span>
        </div>
      )}

      {/* Global Navbar */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        language={language}
        setLanguage={setLanguage}
        theme={theme}
        setTheme={setTheme}
        sandboxCount={sandboxItems.length}
      />

      {/* Main App Content Viewport */}
      <main style={{ flex: 1, padding: '2rem 0 3.5rem' }}>
        <div className="max-w-content">
          {activeTab === 'search' && (
            <MedicineSearch
              language={language}
              onAddToSandbox={handleAddToSandbox}
              onLocateStores={handleLocateStores}
              initialQuery={searchInitialQuery}
            />
          )}

          {activeTab === 'sandbox' && (
            <ComparisonSandbox
              sandboxItems={sandboxItems}
              onRemoveFromSandbox={handleRemoveFromSandbox}
              onClearSandbox={handleClearSandbox}
              onAddMedicine={handleAddToSandbox}
              language={language}
            />
          )}

          {activeTab === 'kendras' && (
            <KendraLocator language={language} />
          )}

          {activeTab === 'groups' && (
            <TherapeuticGroups
              onSelectGroup={handleSelectGroup}
              language={language}
            />
          )}

          {activeTab === 'guidelines' && (
            <ClinicalGuidelines language={language} />
          )}

          {activeTab === 'chat' && (
            <AIChatAssistant
              language={language}
              setLanguage={setLanguage}
            />
          )}

          {activeTab === 'sources' && (
            <DataSources language={language} />
          )}
        </div>
      </main>

      {/* Global Footer */}
      <Footer language={language} />
    </div>
  );
}
