// =========================================================================
// JARVIS Assistant — Chat & Message Rendering Module (v4.0 Mobile-Ready)
// =========================================================================

export class ChatEngine {
    constructor(options = {}) {
        this.messagesContainer = options.messagesContainer || document.getElementById('messages-list');
        this.welcomeScreen = options.welcomeScreen || document.getElementById('welcome-screen');
    }

    appendUserMessage(text, attachment = null) {
        if (this.welcomeScreen) {
            this.welcomeScreen.style.display = 'none';
        }

        const msgItem = document.createElement('div');
        msgItem.className = 'message-item user';

        let attachmentHtml = '';
        if (attachment) {
            if (attachment.file_type === 'image' && attachment.data_url) {
                attachmentHtml = `<img src="${attachment.data_url}" alt="Adjunto" class="chat-attached-image">`;
            } else {
                attachmentHtml = `
                    <div class="chat-attached-doc">
                        <span class="chat-doc-icon">📄</span>
                        <div class="chat-doc-info">
                            <span class="chat-doc-name">${attachment.filename}</span>
                            <span class="chat-doc-meta">${attachment.file_type.toUpperCase()} • ${Math.round(attachment.size_bytes / 1024)} KB</span>
                        </div>
                    </div>
                `;
            }
        }

        msgItem.innerHTML = `
            ${attachmentHtml}
            <div class="bubble">${this._escapeHtml(text)}</div>
        `;

        this.messagesContainer.appendChild(msgItem);
        this.scrollToBottom();
        return msgItem;
    }

    createAssistantBubble() {
        if (this.welcomeScreen) {
            this.welcomeScreen.style.display = 'none';
        }

        const msgItem = document.createElement('div');
        msgItem.className = 'message-item jarvis';

        const bubble = document.createElement('div');
        bubble.className = 'bubble';
        bubble.dataset.rawText = '';

        msgItem.appendChild(bubble);
        this.messagesContainer.appendChild(msgItem);
        this.scrollToBottom();

        return bubble;
    }

    formatMarkdown(text) {
        if (!text) return '';
        // Conversión ligera de markdown seguro (bold, italic, list, code)
        let formatted = this._escapeHtml(text);
        formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');
        formatted = formatted.replace(/`([^`]+)`/g, '<code>$1</code>');
        formatted = formatted.replace(/\n/g, '<br>');
        return formatted;
    }

    scrollToBottom() {
        if (this.messagesContainer) {
            this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        }
    }

    _escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }
}

if (typeof window !== 'undefined') {
    window.ChatEngine = ChatEngine;
}
