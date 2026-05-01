import React, { useState, useRef, useEffect } from "react";
import "./App.css";

const API_BASE = "";

function TypingDots() {
  return (
    <div className="typing-indicator">
      <span /><span /><span />
    </div>
  );
}

function Message({ msg }) {
  const isUser = msg.role === "user";

  return (
    <div className={`message-row ${isUser ? "user-row" : "ai-row"}`}>
      {!isUser && (
        <div className="avatar ai-avatar" title="Biostat AI">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="12" fill="url(#grad)" />
            <defs>
              <linearGradient id="grad" x1="0" y1="0" x2="24" y2="24" gradientUnits="userSpaceOnUse">
                <stop stopColor="#10b981" />
                <stop offset="1" stopColor="#059669" />
              </linearGradient>
            </defs>
            <path d="M8 12h8M12 8v8" stroke="#fff" strokeWidth="2" strokeLinecap="round" />
          </svg>
        </div>
      )}

      <div className={`bubble ${isUser ? "user-bubble" : "ai-bubble"}`}>
        {msg.loading ? (
          <TypingDots />
        ) : (
          <>
            <div className="bubble-text">{msg.content}</div>
            {msg.sources && msg.sources.length > 0 && (
              <div className="sources-block">
                <span className="sources-label">📚 Source</span>
                {msg.sources.map((s, i) => (
                  <div key={i} className="source-item">{s}</div>
                ))}
              </div>
            )}
          </>
        )}
      </div>

      {isUser && (
        <div className="avatar user-avatar" title="You">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="12" fill="#4f46e5" />
            <circle cx="12" cy="9" r="3.5" fill="#fff" />
            <path d="M5.5 19.5C5.5 16.46 8.46 14 12 14s6.5 2.46 6.5 5.5" stroke="#fff" strokeWidth="1.6" strokeLinecap="round" />
          </svg>
        </div>
      )}
    </div>
  );
}

function WelcomeScreen() {
  const examples = [
    "What is biostatistics?",
    "Explain p-value in simple terms",
    "What is a confidence interval?",
    "Describe hypothesis testing steps",
  ];
  return (
    <div className="welcome">
      <div className="welcome-icon">
        <svg width="56" height="56" viewBox="0 0 56 56" fill="none">
          <rect width="56" height="56" rx="16" fill="url(#wg)" />
          <defs>
            <linearGradient id="wg" x1="0" y1="0" x2="56" y2="56" gradientUnits="userSpaceOnUse">
              <stop stopColor="#10b981" />
              <stop offset="1" stopColor="#059669" />
            </linearGradient>
          </defs>
          <path d="M18 28h20M28 18v20" stroke="#fff" strokeWidth="3" strokeLinecap="round" />
        </svg>
      </div>
      <h1 className="welcome-title">Biostat AI</h1>
      <div className="example-grid">
        {examples.map((ex, i) => (
          <div key={i} className="example-card">
            <span>{ex}</span>
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M3 8h10M9 4l4 4-4 4" stroke="#10b981" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function App() {
  const [messages, setMessages] = useState([]);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);
  const textareaRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Auto-resize textarea
  const handleInputChange = (e) => {
    setInput(e.target.value);
    const ta = textareaRef.current;
    if (ta) {
      ta.style.height = "auto";
      ta.style.height = Math.min(ta.scrollHeight, 180) + "px";
    }
  };

  const sendMessage = async () => {
    const question = input.trim();
    if (!question || loading) return;

    setInput("");
    if (textareaRef.current) textareaRef.current.style.height = "auto";

    const userMsg = { id: Date.now(), role: "user", content: question };
    const placeholderId = Date.now() + 1;
    const placeholder = { id: placeholderId, role: "assistant", loading: true };

    setMessages((prev) => [...prev, userMsg, placeholder]);
    setLoading(true);

    try {
      const res = await fetch(`${API_BASE}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      const data = await res.json();

      setMessages((prev) =>
        prev.map((m) =>
          m.id === placeholderId
            ? { id: placeholderId, role: "assistant", content: data.answer, sources: data.sources }
            : m
        )
      );
    } catch (err) {
      setMessages((prev) =>
        prev.map((m) =>
          m.id === placeholderId
            ? { id: placeholderId, role: "assistant", content: "⚠️ Error connecting to the server. Make sure the backend is running on port 5000.", sources: [] }
            : m
        )
      );
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const clearChat = () => setMessages([]);

  return (
    <div className="app">
      {/* Sidebar */}
      <aside className={`sidebar${sidebarOpen ? "" : " sidebar-closed"}`}>
        <div className="sidebar-top">
          <button className="new-chat-btn" onClick={clearChat}>
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
              <path d="M9 3v12M3 9h12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
            </svg>
            New Chat
          </button>
        </div>
        <div className="sidebar-content">
          <div className="sidebar-section-label">Recent</div>
          {messages.filter((m) => m.role === "user").slice(-5).map((m) => (
            <div key={m.id} className="sidebar-history-item">
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                <path d="M2 7a5 5 0 1 0 10 0A5 5 0 0 0 2 7zm5-2v2l1.5 1.5" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" />
              </svg>
              <span>{m.content.slice(0, 28)}{m.content.length > 28 ? "…" : ""}</span>
            </div>
          ))}
        </div>
        <div className="sidebar-bottom">
          <div className="model-badge">
            <div className="model-dot" />
            llama3.2:latest
          </div>
        </div>
      </aside>

      {/* Main */}
      <main className="main">
        <header className="topbar">
          <div className="topbar-left">
            <button className="icon-btn" title="Toggle sidebar" onClick={() => setSidebarOpen((o) => !o)}>
              <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                <path d="M2 4.5h14M2 9h14M2 13.5h14" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
              </svg>
            </button>
            <span className="topbar-title">Biostat AI</span>
          </div>
          <div className="topbar-actions">
            <button className="icon-btn" title="Clear chat" onClick={clearChat}>
              <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                <path d="M3 4.5h12M7.5 4.5V3h3v1.5M6 4.5l.75 9h4.5L12 4.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </button>
          </div>
        </header>

        <div className="chat-area">
          {messages.length === 0 ? (
            <WelcomeScreen />
          ) : (
            <div className="messages">
              {messages.map((msg) => (
                <Message key={msg.id} msg={msg} />
              ))}
              <div ref={bottomRef} />
            </div>
          )}
        </div>

        {/* Input bar */}
        <div className="input-wrapper">
          <div className="input-box">
            <textarea
              ref={textareaRef}
              className="chat-input"
              placeholder="Ask a biostatistics question…"
              value={input}
              onChange={handleInputChange}
              onKeyDown={handleKeyDown}
              rows={1}
              disabled={loading}
            />
            <button
              className={`send-btn ${loading ? "loading" : ""}`}
              onClick={sendMessage}
              disabled={loading || !input.trim()}
              title="Send"
            >
              {loading ? (
                <svg className="spin" width="20" height="20" viewBox="0 0 20 20" fill="none">
                  <circle cx="10" cy="10" r="8" stroke="#fff" strokeWidth="2" strokeDasharray="40" strokeDashoffset="10" />
                </svg>
              ) : (
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                  <path d="M3 10l14-7-7 14V10H3z" fill="currentColor" />
                </svg>
              )}
            </button>
          </div>
          <p className="input-hint">Press <kbd>Enter</kbd> to send · <kbd>Shift+Enter</kbd> for new line</p>
        </div>
      </main>
    </div>
  );
}
