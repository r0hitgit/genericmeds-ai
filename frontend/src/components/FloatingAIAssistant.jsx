import React, { useState, useRef, useEffect } from 'react';
import {
  Bot,
  X,
  Send,
  RotateCcw,
  Maximize2,
  AlertCircle,
  Sparkles,
  MessageSquare
} from 'lucide-react';
import { api } from '../services/api';

export default function FloatingAIAssistant({ language, onOpenFullChat }) {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      sender: 'ai',
      text:
        language === 'hi'
          ? 'नमस्ते! मैं **GenericMeds AI** सहायक हूँ। ब्रांडेड दवाओं के सस्ते जेनेरिक विकल्प (PMBJP जन औषधि) और बचत जानने के लिए यहाँ पूछें।'
          : 'Namaste! I am **GenericMeds AI Assistant**. Ask me about verified generic alternatives, PMBJP Jan Aushadhi prices, or salt compositions.',
      followUps: [
        'Generic alternative to Augmentin 625 Duo?',
        'Dolo 650 का जन औषधि विकल्प?',
        'How much can I save on Pan 40?',
        'Are generic medicines equally effective?',
      ],
    },
  ]);

  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
      setTimeout(() => {
        inputRef.current?.focus();
      }, 150);
    }
  }, [isOpen, messages, loading]);

  const handleSend = async (messageText = input) => {
    const text = messageText.trim();
    if (!text || loading) return;

    const userMsg = {
      id: 'user-' + Date.now(),
      sender: 'user',
      text,
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    const history = messages
      .filter((m) => m.id !== 'welcome')
      .map((m) => ({
        role: m.sender === 'user' ? 'user' : 'assistant',
        content: m.text,
      }));

    try {
      const res = await api.sendChatMessage({
        message: text,
        language: language || 'en',
        conversationHistory: history,
      });

      const aiMsg = {
        id: 'ai-' + Date.now(),
        sender: 'ai',
        text: res.answer,
        followUps: res.follow_up_questions || [],
        safetyNotice: res.safety_notice,
      };

      setMessages((prev) => [...prev, aiMsg]);
    } catch (err) {
      const errorMsg = {
        id: 'error-' + Date.now(),
        sender: 'ai',
        text: `Error connecting to AI Assistant: ${err.message}. Please try again.`,
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const clearChat = () => {
    setMessages([
      {
        id: 'welcome-' + Date.now(),
        sender: 'ai',
        text:
          language === 'hi'
            ? 'चैट रीसेट हो गई है। आप अपनी दवा के बारे में कोई नया सवाल पूछ सकते हैं।'
            : 'Chat reset. Ask any question about medicine formulations, price comparisons, or Jan Aushadhi alternatives.',
        followUps: [
          'What is the generic alternative to Augmentin 625 Duo?',
          'Dolo 650 vs Paracetamol PMBJP',
        ],
      },
    ]);
  };

  const renderFormattedText = (raw) => {
    if (!raw) return '';
    const lines = raw.split('\n');

    return lines.map((line, idx) => {
      const trimmed = line.trim();
      if (!trimmed) return <div key={idx} style={{ height: '0.3rem' }} />;

      if (
        trimmed.toLowerCase().includes('medical notice:') ||
        trimmed.toLowerCase().includes('this tool provides medicine information') ||
        trimmed.toLowerCase().includes('चिकित्सकीय परामर्श:')
      ) {
        return (
          <div
            key={idx}
            style={{
              margin: '0.4rem 0',
              padding: '0.5rem 0.7rem',
              background: 'var(--disclaimer-bg)',
              border: '1px solid var(--disclaimer-border)',
              borderRadius: '6px',
              color: 'var(--disclaimer-text)',
              fontSize: '0.74rem',
              display: 'flex',
              gap: '0.35rem',
              alignItems: 'flex-start',
            }}
          >
            <AlertCircle size={13} style={{ flexShrink: 0, marginTop: '2px' }} />
            <div>
              <strong>Notice:</strong> {trimmed.replace(/^(\*|•|-|\s|Medical Notice:)+/i, '')}
            </div>
          </div>
        );
      }

      const parts = line.split(/(\*\*.*?\*\*)/g);
      const isBullet = trimmed.startsWith('•') || trimmed.startsWith('-');

      return (
        <p
          key={idx}
          style={{
            margin: '0.2rem 0',
            fontSize: '0.82rem',
            lineHeight: 1.5,
            paddingLeft: isBullet ? '0.65rem' : '0',
          }}
        >
          {parts.map((p, pIdx) => {
            if (p.startsWith('**') && p.endsWith('**')) {
              return (
                <strong key={pIdx} style={{ color: 'var(--text-main)', fontWeight: 700 }}>
                  {p.slice(2, -2)}
                </strong>
              );
            }
            return p;
          })}
        </p>
      );
    });
  };

  return (
    <>
      {/* Floating Chat Window */}
      {isOpen && (
        <div
          style={{
            position: 'fixed',
            bottom: '88px',
            right: '24px',
            zIndex: 1051,
            width: 'min(400px, calc(100vw - 32px))',
            height: 'min(540px, calc(100vh - 120px))',
            background: 'var(--bg-surface)',
            border: '1px solid var(--border-subtle)',
            borderRadius: '16px',
            boxShadow: '0 20px 50px -10px rgba(0, 0, 0, 0.28), 0 0 0 1px rgba(0, 0, 0, 0.06)',
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden',
            animation: 'fadeInScale 0.22s cubic-bezier(0.16, 1, 0.3, 1)',
          }}
        >
          {/* Header matching Screenshot 1 */}
          <div
            style={{
              padding: '0.85rem 1rem',
              background: 'var(--bg-surface-elevated)',
              borderBottom: '1px solid var(--border-subtle)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              gap: '0.5rem',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
              {/* Exact Terracotta Squircle Icon from Screenshot */}
              <div
                style={{
                  width: '34px',
                  height: '34px',
                  borderRadius: '8px',
                  background: 'var(--terracotta-600)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#fff',
                  flexShrink: 0,
                  boxShadow: '0 2px 6px rgba(184, 66, 24, 0.3)',
                }}
              >
                <Bot size={19} color="#fff" strokeWidth={2} />
              </div>
              <div style={{ lineHeight: 1.2 }}>
                <div style={{ fontSize: '0.92rem', fontWeight: 800, color: 'var(--text-main)', letterSpacing: '-0.01em' }}>
                  GenericMeds AI
                </div>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                  RAG Grounded in PMBI & NPPA
                </div>
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
              <button
                type="button"
                onClick={clearChat}
                title="Reset conversation"
                style={{
                  width: '28px',
                  height: '28px',
                  borderRadius: '6px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'var(--text-muted)',
                  background: 'transparent',
                  border: '1px solid var(--border-subtle)',
                }}
              >
                <RotateCcw size={13} />
              </button>

              {onOpenFullChat && (
                <button
                  type="button"
                  onClick={() => {
                    setIsOpen(false);
                    onOpenFullChat();
                  }}
                  title="Expand to full Assistant page"
                  style={{
                    width: '28px',
                    height: '28px',
                    borderRadius: '6px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'var(--text-muted)',
                    background: 'transparent',
                    border: '1px solid var(--border-subtle)',
                  }}
                >
                  <Maximize2 size={13} />
                </button>
              )}

              <button
                type="button"
                onClick={() => setIsOpen(false)}
                title="Close"
                style={{
                  width: '28px',
                  height: '28px',
                  borderRadius: '6px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'var(--text-muted)',
                  background: 'transparent',
                  border: '1px solid var(--border-subtle)',
                }}
              >
                <X size={15} />
              </button>
            </div>
          </div>

          {/* Messages Scroll Area */}
          <div
            style={{
              padding: '1rem',
              display: 'flex',
              flexDirection: 'column',
              gap: '0.85rem',
              flex: 1,
              overflowY: 'auto',
              background: 'var(--bg-surface-subtle)',
              overscrollBehavior: 'contain',
            }}
          >
            {messages.map((m) => {
              const isUser = m.sender === 'user';
              return (
                <div
                  key={m.id}
                  style={{
                    display: 'flex',
                    justifyContent: isUser ? 'flex-end' : 'flex-start',
                    alignItems: 'flex-start',
                    gap: '0.45rem',
                  }}
                >
                  {!isUser && (
                    <div
                      style={{
                        width: '26px',
                        height: '26px',
                        borderRadius: '6px',
                        background: 'var(--terracotta-600)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: '#fff',
                        flexShrink: 0,
                        marginTop: '2px',
                      }}
                    >
                      <Bot size={14} color="#fff" strokeWidth={2} />
                    </div>
                  )}

                  <div
                    style={{
                      maxWidth: '82%',
                      padding: isUser ? '0.6rem 0.85rem' : '0.75rem 0.95rem',
                      borderRadius: isUser ? '14px 14px 2px 14px' : '14px 14px 14px 2px',
                      background: isUser ? 'var(--terracotta-600)' : 'var(--bg-surface)',
                      color: isUser ? '#fff' : 'var(--text-main)',
                      border: isUser ? 'none' : '1px solid var(--border-subtle)',
                      boxShadow: 'var(--card-shadow)',
                      fontSize: '0.82rem',
                    }}
                  >
                    <div>{renderFormattedText(m.text)}</div>

                    {/* Follow-up suggestions */}
                    {!isUser && m.followUps && m.followUps.length > 0 && (
                      <div style={{ marginTop: '0.65rem', display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
                        <span style={{ fontSize: '0.68rem', fontWeight: 600, color: 'var(--text-dim)' }}>
                          Suggested:
                        </span>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem' }}>
                          {m.followUps.map((q, idx) => (
                            <button
                              key={idx}
                              type="button"
                              onClick={() => handleSend(q)}
                              style={{
                                background: 'var(--bg-surface-elevated)',
                                border: '1px solid var(--border-subtle)',
                                borderRadius: '12px',
                                padding: '3px 8px',
                                fontSize: '0.72rem',
                                color: 'var(--terracotta-600)',
                                fontWeight: 500,
                                textAlign: 'left',
                                cursor: 'pointer',
                              }}
                            >
                              {q}
                            </button>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}

            {loading && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem', fontSize: '0.76rem', color: 'var(--text-muted)' }}>
                <div
                  style={{
                    width: '24px',
                    height: '24px',
                    borderRadius: '6px',
                    background: 'var(--terracotta-600)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: '#fff',
                  }}
                >
                  <Bot size={13} color="#fff" />
                </div>
                <span>Retrieving verified PMBI records...</span>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input Bar */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            style={{
              padding: '0.65rem 0.85rem',
              background: 'var(--bg-surface)',
              borderTop: '1px solid var(--border-subtle)',
              display: 'flex',
              gap: '0.45rem',
              alignItems: 'center',
            }}
          >
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about a medicine, salts, savings..."
              style={{
                flex: 1,
                padding: '0.55rem 0.8rem',
                borderRadius: '8px',
                border: '1px solid var(--border-subtle)',
                background: 'var(--bg-surface-elevated)',
                color: 'var(--text-main)',
                fontSize: '0.82rem',
                outline: 'none',
              }}
            />

            <button
              type="submit"
              disabled={!input.trim() || loading}
              className="btn-primary"
              style={{
                padding: '0.55rem 0.85rem',
                borderRadius: '8px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Send size={14} />
            </button>
          </form>

          {/* Quick Disclaimer strip */}
          <div
            style={{
              padding: '0.3rem 0.85rem',
              background: 'var(--bg-surface-elevated)',
              borderTop: '1px solid var(--border-subtle)',
              fontSize: '0.66rem',
              color: 'var(--text-dim)',
              textAlign: 'center',
            }}
          >
            PMBJP drug data verification. Not medical advice.
          </div>
        </div>
      )}

      {/* Floating Launcher Button in Bottom-Right */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        aria-label="GenericMeds AI Assistant"
        style={{
          position: 'fixed',
          bottom: '24px',
          right: '24px',
          zIndex: 1050,
          background: 'var(--bg-surface)',
          border: '1px solid var(--border-subtle)',
          borderRadius: '9999px',
          padding: '6px 14px 6px 6px',
          boxShadow: '0 8px 28px rgba(0, 0, 0, 0.15), 0 2px 8px rgba(184, 66, 24, 0.2)',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          transition: 'all 0.2s cubic-bezier(0.16, 1, 0.3, 1)',
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.transform = 'translateY(-2px)';
          e.currentTarget.style.boxShadow = '0 12px 32px rgba(184, 66, 24, 0.28)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.transform = 'translateY(0)';
          e.currentTarget.style.boxShadow = '0 8px 28px rgba(0, 0, 0, 0.15), 0 2px 8px rgba(184, 66, 24, 0.2)';
        }}
      >
        {/* Exact Terracotta Squircle Icon from Screenshot */}
        <div
          style={{
            width: '38px',
            height: '38px',
            borderRadius: '10px',
            background: 'var(--terracotta-600)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#fff',
            flexShrink: 0,
            boxShadow: '0 2px 6px rgba(184, 66, 24, 0.35)',
          }}
        >
          <Bot size={22} color="#fff" strokeWidth={2} />
        </div>

        {/* Text Label */}
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', lineHeight: 1.2 }}>
          <span style={{ fontSize: '0.84rem', fontWeight: 800, color: 'var(--text-main)', letterSpacing: '-0.01em' }}>
            {isOpen ? 'Close Chat' : 'AI Assistant'}
          </span>
          <span style={{ fontSize: '0.68rem', color: 'var(--terracotta-600)', fontWeight: 600 }}>
            {isOpen ? 'Minimize' : 'Ask PMBJP AI ●'}
          </span>
        </div>
      </button>
    </>
  );
}
