(function () {
  "use strict";

  const messages = [];
  let loading = false;

  const $ = (id) => document.getElementById(id);

  function escapeHtml(text) {
    const d = document.createElement("div");
    d.textContent = text === undefined || text === null ? "" : String(text);
    return d.innerHTML;
  }

  function scrollToBottom() {
    $("chat-bottom-anchor").scrollIntoView({ behavior: "smooth" });
  }

  function updateSendUi() {
    const ta = $("chat-input");
    const btn = $("btn-send");
    const hasText = !!(ta.value && ta.value.trim());
    btn.disabled = loading || !hasText;
    ta.disabled = loading;
    if (loading) {
      btn.classList.add("loading");
      btn.innerHTML =
        '<svg class="spin" width="20" height="20" viewBox="0 0 20 20" fill="none" aria-hidden="true">' +
        '<circle cx="10" cy="10" r="8" stroke="#fff" stroke-width="2" stroke-dasharray="40" stroke-dashoffset="10" />' +
        "</svg>";
    } else {
      btn.classList.remove("loading");
      btn.innerHTML =
        '<svg width="20" height="20" viewBox="0 0 20 20" fill="none" aria-hidden="true">' +
        '<path d="M3 10l14-7-7 14V10H3z" fill="currentColor" /></svg>';
    }
  }

  function autoResizeInput() {
    const ta = $("chat-input");
    ta.style.height = "auto";
    ta.style.height = Math.min(ta.scrollHeight, 180) + "px";
  }

  function renderSidebarRecent() {
    const container = $("sidebar-recent");
    const users = messages.filter(function (m) {
      return m.role === "user";
    }).slice(-5);

    container.textContent = "";
    const label = document.createElement("div");
    label.className = "sidebar-section-label";
    label.textContent = "Recent";
    container.appendChild(label);

    const clockSvg =
      '<svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true">' +
      '<path d="M2 7a5 5 0 1 0 10 0A5 5 0 0 0 2 7zm5-2v2l1.5 1.5" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" />' +
      "</svg>";

    users.forEach(function (m) {
      const div = document.createElement("div");
      div.className = "sidebar-history-item";
      const short = m.content.length > 28 ? m.content.slice(0, 28) + "…" : m.content;
      div.innerHTML = clockSvg + "<span></span>";
      div.querySelector("span").textContent = short;
      container.appendChild(div);
    });
  }

  function aiAvatarSvg() {
    /* Solid fill avoids duplicate gradient IDs when many messages render. */
    return (
      '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">' +
      '<circle cx="12" cy="12" r="12" fill="#10b981" />' +
      '<path d="M8 12h8M12 8v8" stroke="#fff" stroke-width="2" stroke-linecap="round" /></svg>'
    );
  }

  function userAvatarSvg() {
    return (
      '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">' +
      '<circle cx="12" cy="12" r="12" fill="#4f46e5" />' +
      '<circle cx="12" cy="9" r="3.5" fill="#fff" />' +
      '<path d="M5.5 19.5C5.5 16.46 8.46 14 12 14s6.5 2.46 6.5 5.5" stroke="#fff" stroke-width="1.6" stroke-linecap="round" />' +
      "</svg>"
    );
  }

  function bubbleHtml(msg) {
    if (msg.loading) {
      return '<div class="typing-indicator"><span></span><span></span><span></span></div>';
    }
    let inner = '<div class="bubble-text">' + escapeHtml(msg.content || "") + "</div>";
    if (msg.sources && msg.sources.length) {
      inner += '<div class="sources-block"><span class="sources-label">📚 Source</span>';
      msg.sources.forEach(function (s) {
        inner += '<div class="source-item">' + escapeHtml(s) + "</div>";
      });
      inner += "</div>";
    }
    return inner;
  }

  function messageRowHtml(msg) {
    const isUser = msg.role === "user";
    let row =
      '<div class="message-row ' +
      (isUser ? "user-row" : "ai-row") +
      '" data-msg-id="' +
      msg.id +
      '">';
    if (!isUser) {
      row += '<div class="avatar ai-avatar" title="Biostat AI">' + aiAvatarSvg() + "</div>";
    }
    row +=
      '<div class="bubble ' +
      (isUser ? "user-bubble" : "ai-bubble") +
      '">' +
      bubbleHtml(msg) +
      "</div>";
    if (isUser) {
      row += '<div class="avatar user-avatar" title="You">' + userAvatarSvg() + "</div>";
    }
    row += "</div>";
    return row;
  }

  function renderMessages() {
    const welcome = $("welcome-view");
    const view = $("messages-view");

    renderSidebarRecent();

    if (!messages.length) {
      welcome.hidden = false;
      view.hidden = true;
      view.innerHTML = "";
      return;
    }

    welcome.hidden = true;
    view.hidden = false;
    view.innerHTML = messages.map(messageRowHtml).join("");
    requestAnimationFrame(scrollToBottom);
  }

  function clearChat() {
    messages.length = 0;
    $("chat-input").value = "";
    $("chat-input").style.height = "auto";
    loading = false;
    updateSendUi();
    renderMessages();
  }

  async function sendMessage() {
    const ta = $("chat-input");
    const question = ta.value.trim();
    if (!question || loading) return;

    loading = true;
    ta.value = "";
    ta.style.height = "auto";

    const userId = Date.now();
    const asstId = userId + 1;
    messages.push({ id: userId, role: "user", content: question });
    messages.push({ id: asstId, role: "assistant", loading: true });

    updateSendUi();
    renderMessages();

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: question }),
      });
      const data = await res.json();

      let idx = messages.findIndex(function (m) {
        return m.id === asstId;
      });
      if (idx >= 0) {
        if (data.error) {
          messages[idx] = {
            id: asstId,
            role: "assistant",
            content:
              "Sorry, something went wrong: " + (data.error || "unknown error"),
            sources: [],
          };
        } else {
          messages[idx] = {
            id: asstId,
            role: "assistant",
            content: data.answer || "",
            sources: data.sources || [],
          };
        }
      }
    } catch (err) {
      let idx = messages.findIndex(function (m) {
        return m.id === asstId;
      });
      if (idx >= 0) {
        messages[idx] = {
          id: asstId,
          role: "assistant",
          content:
            "⚠️ Error connecting to the server. Run `python app.py` and reload this page (http://localhost:5000).",
          sources: [],
        };
      }
    } finally {
      loading = false;
      updateSendUi();
      renderMessages();
      autoResizeInput();
    }
  }

  $("btn-toggle-sidebar").addEventListener("click", function () {
    $("sidebar").classList.toggle("sidebar-closed");
  });

  $("btn-clear-chat").addEventListener("click", clearChat);
  $("btn-new-chat").addEventListener("click", clearChat);

  $("chat-input").addEventListener("input", function () {
    autoResizeInput();
    updateSendUi();
  });

  $("chat-input").addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  $("btn-send").addEventListener("click", sendMessage);

  document.querySelectorAll(".example-card").forEach(function (card) {
    card.addEventListener("click", function () {
      const span = card.querySelector("span");
      if (!span) return;
      $("chat-input").value = span.textContent.trim();
      autoResizeInput();
      updateSendUi();
      $("chat-input").focus();
    });
  });

  updateSendUi();
  renderMessages();
})();
