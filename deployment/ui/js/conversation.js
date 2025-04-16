/**
 * Conversation Handler for Medical Billing Denial Assistant
 * Manages conversation display and interaction with the agent
 */

class ConversationHandler {
    /**
     * Initialize the conversation handler
     * @param {Object} config - Configuration options
     * @param {ApiClient} config.apiClient - API client instance
     * @param {DocumentHandler} config.documentHandler - Document handler instance
     * @param {Function} config.onError - Error callback function
     * @param {Function} config.onProcessing - Processing status callback
     */
    constructor(config = {}) {
        this.apiClient = config.apiClient;
        this.documentHandler = config.documentHandler;
        this.onError = config.onError || (error => console.error('Conversation Error:', error));
        this.onProcessing = config.onProcessing || (isProcessing => {});
        
        this.conversationContainer = document.getElementById('conversation-container');
        this.userInput = document.getElementById('user-input');
        this.sendButton = document.getElementById('send-btn');
        this.clearButton = document.getElementById('clear-btn');
        this.exportButton = document.getElementById('export-btn');
        
        this._initEventListeners();
        this.messages = [];
    }

    /**
     * Initialize event listeners
     * @private
     */
    _initEventListeners() {
        // Send message on button click
        this.sendButton.addEventListener('click', this._sendMessage.bind(this));
        
        // Send message on Enter key (without Shift)
        this.userInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this._sendMessage();
            }
        });
        
        // Auto-resize textarea as user types
        this.userInput.addEventListener('input', this._autoResizeTextarea.bind(this));
        
        // Clear conversation
        this.clearButton.addEventListener('click', this._confirmClearConversation.bind(this));
        
        // Export conversation
        this.exportButton.addEventListener('click', this._exportConversation.bind(this));
    }

    /**
     * Auto-resize textarea based on content
     * @private
     */
    _autoResizeTextarea() {
        this.userInput.style.height = 'auto';
        this.userInput.style.height = (this.userInput.scrollHeight) + 'px';
    }

    /**
     * Send a message to the agent
     * @private
     */
    async _sendMessage() {
        const message = this.userInput.value.trim();
        
        if (!message) {
            return;
        }
        
        // Display user message
        this._addMessageToUI({
            role: 'user',
            content: message,
            timestamp: new Date().toISOString()
        });
        
        // Clear input
        this.userInput.value = '';
        this.userInput.style.height = 'auto';
        
        // Focus input
        this.userInput.focus();
        
        // Send to agent
        this.onProcessing(true);
        
        try {
            const response = await this.apiClient.sendMessage(message);
            
            // Display agent response
            this._addMessageToUI({
                role: 'assistant',
                content: response.message || 'I understand your request. Let me help with that.',
                timestamp: new Date().toISOString()
            });
            
            // Store in messages array
            this.messages.push({
                role: 'user',
                content: message,
                timestamp: new Date().toISOString()
            });
            
            this.messages.push({
                role: 'assistant',
                content: response.message || '',
                timestamp: new Date().toISOString()
            });
            
            // Scroll to bottom
            this._scrollToBottom();
        } catch (error) {
            this.onError(`Failed to send message: ${error.message}`);
            
            // Display error as system message
            this._addMessageToUI({
                role: 'system',
                content: `An error occurred: ${error.message}. Please try again.`,
                timestamp: new Date().toISOString()
            });
        } finally {
            this.onProcessing(false);
        }
    }

    /**
     * Add a message to the UI
     * @param {Object} message - Message object
     * @param {string} message.role - Message role (user, assistant, system)
     * @param {string} message.content - Message content
     * @param {string} message.timestamp - Message timestamp
     * @private
     */
    _addMessageToUI(message) {
        const messageElement = document.createElement('div');
        messageElement.className = `message ${message.role}-message`;
        
        // Message content
        const contentElement = document.createElement('div');
        contentElement.className = 'message-content';
        
        // Use Markdown parsing for assistant and system messages
        if (message.role === 'assistant' || message.role === 'system') {
            contentElement.innerHTML = this._markdownToHTML(message.content);
        } else {
            // For user messages, just use text with line break support
            contentElement.innerHTML = message.content.replace(/\n/g, '<br>');
        }
        
        messageElement.appendChild(contentElement);
        
        // Message timestamp
        const timestamp = new Date(message.timestamp);
        const timeElement = document.createElement('div');
        timeElement.className = 'message-time';
        timeElement.textContent = timestamp.toLocaleTimeString();
        messageElement.appendChild(timeElement);
        
        // Add to conversation container
        this.conversationContainer.appendChild(messageElement);
        
        // Scroll to bottom
        this._scrollToBottom();
    }

    /**
     * Load conversation history from the API
     */
    async loadConversationHistory() {
        try {
            this.onProcessing(true);
            
            // Clear existing messages
            this.conversationContainer.innerHTML = '';
            
            // Add welcome message
            const welcomeMessage = document.createElement('div');
            welcomeMessage.className = 'message system-message';
            
            const welcomeContent = document.createElement('div');
            welcomeContent.className = 'message-content';
            welcomeContent.innerHTML = '<p>Welcome to the Medical Billing Denial Assistant. I can help you analyze claim denials and provide remediation steps. You can upload relevant documents like CMS-1500 forms or EOBs to assist in the analysis.</p>';
            
            welcomeMessage.appendChild(welcomeContent);
            this.conversationContainer.appendChild(welcomeMessage);
            
            // Get conversation history
            const history = await this.apiClient.getConversationHistory();
            this.messages = history;
            
            // Add messages to UI
            history.forEach(message => {
                this._addMessageToUI(message);
            });
            
            this.onProcessing(false);
        } catch (error) {
            this.onProcessing(false);
            this.onError(`Failed to load conversation history: ${error.message}`);
            
            // Reset with welcome message
            this._resetConversation();
        }
    }

    /**
     * Reset the conversation
     * @private
     */
    _resetConversation() {
        // Clear messages array
        this.messages = [];
        
        // Clear UI
        this.conversationContainer.innerHTML = '';
        
        // Add welcome message
        const welcomeMessage = document.createElement('div');
        welcomeMessage.className = 'message system-message';
        
        const welcomeContent = document.createElement('div');
        welcomeContent.className = 'message-content';
        welcomeContent.innerHTML = '<p>Welcome to the Medical Billing Denial Assistant. I can help you analyze claim denials and provide remediation steps. You can upload relevant documents like CMS-1500 forms or EOBs to assist in the analysis.</p>';
        
        welcomeMessage.appendChild(welcomeContent);
        this.conversationContainer.appendChild(welcomeMessage);
    }

    /**
     * Confirm and clear the conversation
     * @private
     */
    _confirmClearConversation() {
        if (confirm('Are you sure you want to clear the conversation? This cannot be undone.')) {
            this._resetConversation();
        }
    }

    /**
     * Export the conversation as a text file
     * @private
     */
    _exportConversation() {
        if (this.messages.length === 0) {
            alert('No messages to export.');
            return;
        }
        
        let exportText = 'Medical Billing Denial Assistant - Conversation Export\n';
        exportText += '==================================================\n\n';
        exportText += `Date: ${new Date().toLocaleString()}\n\n`;
        
        this.messages.forEach(message => {
            const timestamp = new Date(message.timestamp).toLocaleString();
            const role = message.role === 'user' ? 'You' : 'Assistant';
            
            exportText += `${role} (${timestamp}):\n`;
            exportText += `${message.content}\n\n`;
        });
        
        // Create download link
        const blob = new Blob([exportText], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `medical-billing-denial-conversation-${new Date().toISOString().split('T')[0]}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    /**
     * Scroll the conversation container to the bottom
     * @private
     */
    _scrollToBottom() {
        this.conversationContainer.scrollTop = this.conversationContainer.scrollHeight;
    }

    /**
     * Convert Markdown to HTML
     * @param {string} markdown - Markdown text
     * @returns {string} - HTML string
     * @private
     */
    _markdownToHTML(markdown) {
        if (!markdown) return '';
        
        // This is a simple Markdown parser. In a production application,
        // you would use a dedicated library like Marked.js
        
        // Escape HTML tags
        let html = markdown
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');
        
        // Headers
        html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');
        html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>');
        html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>');
        
        // Bold
        html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
        
        // Italic
        html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');
        
        // Lists
        html = html.replace(/^\* (.+)$/gm, '<li>$1</li>');
        html = html.replace(/^(\d+)\. (.+)$/gm, '<li>$2</li>');
        
        // Wrap lists
        html = html.replace(/(<li>.+<\/li>)\n<li>/g, '$1\n<li>');
        html = html.replace(/(<li>.+<\/li>)\n([^<])/g, '$1</ul>\n$2');
        html = html.replace(/([^>])\n<li>/g, '$1\n<ul><li>');
        html = html.replace(/(<li>.+<\/li>)$/g, '$1</ul>');
        
        // Code blocks
        html = html.replace(/```(.+?)```/gs, '<pre><code>$1</code></pre>');
        
        // Inline code
        html = html.replace(/`(.+?)`/g, '<code>$1</code>');
        
        // Paragraphs
        html = html.replace(/\n\n/g, '</p><p>');
        html = html.replace(/^(.+?)(?=<\/p>|$)/s, '<p>$1');
        
        // Line breaks
        html = html.replace(/\n/g, '<br>');
        
        return html;
    }
}

// Export the conversation handler
window.ConversationHandler = ConversationHandler;
