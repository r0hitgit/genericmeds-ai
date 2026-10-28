import React, { useState, useRef, useEffect } from 'react';
import {
  Bot,
  User,
  Send,
  RotateCcw,
  AlertCircle,
  Sparkles
} from 'lucide-react';
import { api } from '../services/api';

export default function AIChatAssistant({ language, setLanguage }) {
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      sender: 'ai',
      text:
        language === 'hi'
          ? 'नमस्ते! मैं **GenericMeds AI** सहायक हूँ। मैं आपको ब्रांडेड दवाओं के सस्ते जेनेरिक विकल्प (PMBJP जन औषधि), संरचना मिलान और मूल्य बचत समझने में मदद कर सकता हूँ।'
          : 'Namaste! I am **GenericMeds AI Assistant**. I can help you discover affordable generic medicine alternatives, compare verified MRPs with Pradhan Mantri Jan Aushadhi prices, and explain active formulations.',
      followUps: [
        'What is the generic alternative to Augmentin 625 Duo?',
        'Dolo 650 का जन औषधि में क्या विकल्प है?',
        'What is the difference between branded and generic medicines?',
        'How much can I save on Glycomet 500 SR?',
      ],
    },
  ]);

  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

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
        text: `Error communicating with AI Assistant: ${err.message}. Please try again.`,
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
          'What is the generic alternative to Pan 40?',
          'Atorva 10 vs Atorvastatin savings',
        ],
      },
    ]);
  };

  const renderFormattedText = (raw) => {
    if (!raw) return '';
    const lines = raw.split('\n');

    return lines.map((line, idx) => {
      const trimmed = line.trim();
      if (!trimmed) return <div key={idx} style={{ height: '0.4rem' }} />;

      if (
        trimmed.toLowerCase().includes('medical notice:') ||
        trimmed.toLowerCase().includes('this tool provides medicine information') ||
        trimmed.toLowerCase().includes('चिकित्सकीय परामर्श:')
      ) {
        return (
          <div
            key={idx}
            style={{
              margin: '0.5rem 0',
              padding: '0.65rem 0.85rem',
              background: 'var(--disclaimer-bg)',
              border: '1px solid var(--disclaimer-border)',
              borderRadius: '6px',
              color: 'var(--disclaimer-text)',
              fontSize: '0.78rem',
              display: 'flex',
              gap: '0.4rem',
              alignItems: 'flex-start',
            }}
          >
            <AlertCircle size={14} style={{ flexShrink: 0, marginTop: '2px' }} />
            <div>
              <strong>Medical Advisory:</strong> {trimmed.replace(/^(\*|•|-|\s|Medical Notice:)+/i, '')}
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
            margin: '0.25rem 0',
            fontSize: '0.86rem',
            lineHeight: 1.55,
            paddingLeft: isBullet ? '0.75rem' : '0',
          }}
        >
          {parts.map((p, pIdx) => {
            if (p.startsWith('**') && p.endsWith('**')) {
              return <strong key={pIdx} style={{ color: 'var(--text-main)', fontWeight: 700 }}>{p.slice(2, -2)}</strong>;
            }
            return p;
          })}
        </p>
      );
    });
  };

  return (
    <section className="animate-fade-in" style={{
      display: 'flex',
      flexDirection: 'column',
      background: 'var(--bg-surface)',
      borderRadius: '12px',
      border: '1px solid var(--border-subtle)',
      boxShadow: 'var(--card-shadow)',
      overflow: 'hidden',
      maxWidth: '860px',
      margin: '0 auto',
      width: '100%',
    }}>
      {/* Header */}
      <div style={{
        padding: '1rem 1.25rem',
        background: 'var(--bg-surface-elevated)',
        borderBottom: '1px solid var(--border-subtle)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
          <div style={{
            width: '32px',
            height: '32px',
            borderRadius: '6px',
            background: 'var(--terracotta-600)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#fff',
          }}>
            <Bot size={17} />
          </div>
          <div>
            <h3 style={{ fontSize: '0.98rem', fontWeight: 700, color: 'var(--text-main)', margin: 0 }}>
              GenericMeds AI Assistant
            </h3>
            <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
              RAG Grounded in PMBI Jan Aushadhi & NPPA Databases
            </span>
          </div>
        </div>

        <button
          onClick={clearChat}
          className="btn-secondary"
          style={{ padding: '0.35rem 0.65rem', fontSize: '0.74rem' }}
        >
          <RotateCcw size={12} />
          <span>Clear Chat</span>
        </button>
      </div>

      {/* Messages */}
      <div style={{
        padding: '1.25rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '0.85rem',
        minHeight: '380px',
        maxHeight: '500px',
        overflowY: 'auto',
        background: 'var(--bg-surface-subtle)',
      }}>
        {messages.map((m) => {
          const isUser = m.sender === 'user';
          return (
            <div
              key={m.id}
              style={{
                display: 'flex',
                justifyContent: isUser ? 'flex-end' : 'flex-start',
                alignItems: 'flex-start',
                gap: '0.5rem',
              }}
            >
              {!isUser && (
                <div style={{
                  width: '28px',
                  height: '28px',
                  borderRadius: '6px',
                  background: 'var(--terracotta-600)',
                  color: '#fff',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0,
                  marginTop: '0.2rem',
                }}>
                  <Bot size={14} />
                </div>
              )}

              <div style={{
                maxWidth: '82%',
                background: isUser ? 'var(--terracotta-600)' : 'var(--bg-surface)',
                color: isUser ? '#ffffff' : 'var(--text-main)',
                border: isUser ? 'none' : '1px solid var(--border-subtle)',
                padding: '0.75rem 1rem',
                borderRadius: '8px',
                fontSize: '0.86rem',
              }}>
                <div>{renderFormattedText(m.text)}</div>

                {m.followUps && m.followUps.length > 0 && (
                  <div style={{
                    marginTop: '0.65rem',
                    paddingTop: '0.55rem',
                    borderTop: '1px solid var(--border-subtle)',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '0.35rem',
                  }}>
                    <span style={{ fontSize: '0.7rem', fontWeight: 600, color: 'var(--text-dim)' }}>
                      Suggested questions:
                    </span>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem' }}>
                      {m.followUps.map((q, idx) => (
                        <button
                          key={idx}
                          onClick={() => handleSend(q)}
                          style={{
                            background: 'var(--bg-surface-elevated)',
                            border: '1px solid var(--border-subtle)',
                            color: 'var(--terracotta-600)',
                            padding: '0.2rem 0.55rem',
                            borderRadius: '4px',
                            fontSize: '0.72rem',
                            fontWeight: 500,
                            textAlign: 'left',
                          }}
                        >
                          {q}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {isUser && (
                <div style={{
                  width: '28px',
                  height: '28px',
                  borderRadius: '6px',
                  background: 'var(--bg-surface-elevated)',
                  border: '1px solid var(--border-subtle)',
                  color: 'var(--text-main)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0,
                  marginTop: '0.2rem',
                }}>
                  <User size={14} />
                </div>
              )}
            </div>
          );
        })}

        {loading && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            <Bot size={15} color="var(--terracotta-600)" />
            <span>Retrieving verified PMBI records...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
        style={{
          padding: '0.75rem 1rem',
          background: 'var(--bg-surface)',
          borderTop: '1px solid var(--border-subtle)',
          display: 'flex',
          gap: '0.5rem',
          alignItems: 'center',
        }}
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about a medicine, active ingredients, or price comparison..."
          className="form-input"
          style={{ flex: 1, padding: '0.65rem 0.95rem' }}
        />

        <button
          type="submit"
          disabled={!input.trim() || loading}
          className="btn-primary"
          style={{ padding: '0.65rem 1.15rem' }}
        >
          <span>Send</span>
          <Send size={14} />
        </button>
      </form>
    </section>
  );
}
