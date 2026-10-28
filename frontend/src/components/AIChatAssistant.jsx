import React, { useState, useRef, useEffect } from 'react';
import { api } from '../services/api';

export default function AIChatAssistant({ language, setLanguage }) {
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      sender: 'ai',
      text:
        language === 'hi'
          ? 'नमस्ते! मैं **GenericMeds AI** सहायक हूँ। मैं आपको ब्रांडेड दवाओं के सस्ते जेनेरिक विकल्प (PMBJP जन औषधि), संरचना मिलान और मूल्य बचत समझने में मदद कर सकता हूँ। आप नीचे प्रश्न पूछ सकते हैं।'
          : 'Namaste! I am **GenericMeds AI**. I can help you discover affordable generic medicine alternatives, compare verified MRPs with Pradhan Mantri Jan Aushadhi ceiling rates, and explain active formulations in simple terms.',
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

    // Build conversation history for API
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
        text: `⚠️ **Error communicating with AI Assistant:** ${err.message}. Please check your connection or try again.`,
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

  // Helper to format text with medical disclaimers and bolding
  const renderFormattedText = (raw) => {
    if (!raw) return '';
    const lines = raw.split('\n');

    return lines.map((line, idx) => {
      const trimmed = line.trim();
      if (!trimmed) return <div key={idx} style={{ height: '0.4rem' }} />;

      // Notice line detection
      if (
        trimmed.toLowerCase().includes('medical notice:') ||
        trimmed.toLowerCase().includes('this tool provides medicine information') ||
        trimmed.toLowerCase().includes('चिकित्सकीय परामर्श:')
      ) {
        return (
          <div
            key={idx}
            style={{
              margin: '0.65rem 0',
              padding: '0.65rem 0.85rem',
              background: 'var(--disclaimer-bg)',
              border: '1px solid var(--disclaimer-border)',
              borderRadius: '0.5rem',
              color: 'var(--disclaimer-text)',
              fontSize: '0.78rem',
              fontWeight: 500,
            }}
          >
            <strong>⚠️ Medical Advisory:</strong> {trimmed.replace(/^(\*|•|-|\s|Medical Notice:)+/i, '')}
          </div>
        );
      }

      // Replace markdown bold **text**
      const parts = line.split(/(\*\*.*?\*\*)/g);
      const isBullet = trimmed.startsWith('•') || trimmed.startsWith('-');

      return (
        <p
          key={idx}
          style={{
            margin: '0.3rem 0',
            fontSize: '0.86rem',
            lineHeight: 1.6,
            paddingLeft: isBullet ? '1rem' : '0',
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
      borderRadius: '1.25rem',
      border: '1px solid var(--border-subtle)',
      boxShadow: 'var(--card-shadow)',
      overflow: 'hidden',
      maxWidth: '920px',
      margin: '0 auto',
      width: '100%',
    }}>
      {/* Chat Header */}
      <div style={{
        padding: '1rem 1.25rem',
        background: 'var(--bg-surface-elevated)',
        borderBottom: '1px solid var(--border-subtle)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '0.75rem',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
          <div style={{
            width: '36px',
            height: '36px',
            borderRadius: '10px',
            background: 'linear-gradient(135deg, var(--teal-600) 0%, var(--teal-800) 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '1.2rem',
            color: '#fff',
          }}>
            🤖
          </div>
          <div>
            <h3 style={{ fontSize: '1rem', fontWeight: 800, color: 'var(--text-main)', margin: 0 }}>
              GenericMeds AI Assistant
            </h3>
            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
              RAG Grounded in PMBI Jan Aushadhi & NPPA Databases
            </span>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <button
            onClick={clearChat}
            style={{
              padding: '0.35rem 0.65rem',
              borderRadius: '0.45rem',
              background: 'var(--bg-surface)',
              border: '1px solid var(--border-medium)',
              fontSize: '0.74rem',
              color: 'var(--text-muted)',
              fontWeight: 600,
            }}
          >
            Clear Chat
          </button>
        </div>
      </div>

      {/* Messages Scroll Feed */}
      <div style={{
        padding: '1.25rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '1rem',
        minHeight: '380px',
        maxHeight: '520px',
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
                gap: '0.6rem',
              }}
            >
              {!isUser && (
                <div style={{
                  width: '30px',
                  height: '30px',
                  borderRadius: '50%',
                  background: 'var(--teal-600)',
                  color: '#fff',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '0.75rem',
                  fontWeight: 800,
                  flexShrink: 0,
                  marginTop: '0.2rem',
                }}>
                  AI
                </div>
              )}

              <div style={{
                maxWidth: '82%',
                background: isUser ? 'var(--teal-600)' : 'var(--bg-surface)',
                color: isUser ? '#ffffff' : 'var(--text-main)',
                border: isUser ? 'none' : '1px solid var(--border-subtle)',
                padding: '0.85rem 1.1rem',
                borderRadius: isUser ? '1rem 1rem 0.2rem 1rem' : '1rem 1rem 1rem 0.2rem',
                boxShadow: 'var(--card-shadow)',
                fontSize: '0.88rem',
              }}>
                <div>{renderFormattedText(m.text)}</div>

                {/* Follow up suggestions */}
                {m.followUps && m.followUps.length > 0 && (
                  <div style={{
                    marginTop: '0.75rem',
                    paddingTop: '0.65rem',
                    borderTop: '1px solid var(--border-subtle)',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '0.35rem',
                  }}>
                    <span style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-dim)' }}>
                      Suggested Inquiries:
                    </span>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem' }}>
                      {m.followUps.map((q, idx) => (
                        <button
                          key={idx}
                          onClick={() => handleSend(q)}
                          style={{
                            background: 'var(--bg-surface-elevated)',
                            border: '1px solid var(--border-medium)',
                            color: 'var(--teal-600)',
                            padding: '0.25rem 0.65rem',
                            borderRadius: '0.45rem',
                            fontSize: '0.74rem',
                            fontWeight: 600,
                            textAlign: 'left',
                            transition: 'all var(--transition-fast)',
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
                  width: '30px',
                  height: '30px',
                  borderRadius: '50%',
                  background: 'var(--bg-surface-elevated)',
                  border: '1px solid var(--border-medium)',
                  color: 'var(--text-main)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '0.72rem',
                  fontWeight: 700,
                  flexShrink: 0,
                  marginTop: '0.2rem',
                }}>
                  You
                </div>
              )}
            </div>
          );
        })}

        {loading && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <div style={{
              width: '30px',
              height: '30px',
              borderRadius: '50%',
              background: 'var(--teal-600)',
              color: '#fff',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '0.75rem',
              fontWeight: 800,
            }}>
              AI
            </div>
            <div style={{
              background: 'var(--bg-surface)',
              border: '1px solid var(--border-subtle)',
              padding: '0.65rem 1rem',
              borderRadius: '0.85rem',
              fontSize: '0.82rem',
              color: 'var(--text-muted)',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
            }}>
              <span style={{ animation: 'spinSlow 1.5s linear infinite' }}>🔄</span>
              <span>Retrieving verified PMBI & NPPA records...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Form Bar */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
        style={{
          padding: '0.85rem 1.25rem',
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
          placeholder={
            language === 'hi'
              ? 'दवा, सॉल्ट या जेनेरिक विकल्प के बारे में पूछें...'
              : 'Ask about any medicine, active ingredients, or PMBJP generic alternatives...'
          }
          className="form-input"
          style={{ flex: 1, padding: '0.75rem 1rem', fontSize: '0.9rem' }}
        />

        <button
          type="submit"
          disabled={!input.trim() || loading}
          className="btn-primary"
          style={{ padding: '0.75rem 1.25rem', fontSize: '0.88rem' }}
        >
          <span>Send</span>
          <span>➤</span>
        </button>
      </form>
    </section>
  );
}
