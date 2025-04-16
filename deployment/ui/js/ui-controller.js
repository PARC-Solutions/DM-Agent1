/**
 * UI Controller for Medical Billing Denial Assistant
 * Central controller that coordinates all UI components and interactions
 */

class UIController {
    /**
     * Initialize the UI controller
     * @param {Object} config - Configuration options
     */
    constructor(config = {}) {
        // Initialize API client
        this.apiClient = new ApiClient({
            onError: this.handleError.bind(this)
        });
        
        // Initialize document handler
        this.documentHandler = new DocumentHandler({
            apiClient: this.apiClient,
            onError: this.handleError.bind(this),
            onSuccess: this.showToast.bind(this),
            onProcessing: this.toggleLoading.bind(this)
        });
        
        // Initialize conversation handler
        this.conversationHandler = new ConversationHandler({
            apiClient: this.apiClient,
            documentHandler: this.documentHandler,
            onError: this.handleError.bind(this),
            onProcessing: this.toggleLoading.bind(this)
        });
        
        // UI elements
        this.settingsBtn = document.getElementById('settings-btn');
        this.helpBtn = document.getElementById('help-btn');
        this.settingsModal = document.getElementById('settings-modal');
        this.helpModal = document.getElementById('help-modal');
        this.closeButtons = document.querySelectorAll('.close-btn');
        this.cancelButtons = document.querySelectorAll('.cancel-btn');
        this.saveSettingsBtn = document.getElementById('save-settings-btn');
        this.newSessionBtn = document.getElementById('new-session-btn');
        this.themeSelector = document.getElementById('theme-selector');
        this.fontSizeSelector = document.getElementById('font-size');
        this.apiEndpointInput = document.getElementById('api-endpoint');
        this.apiKeyInput = document.getElementById('api-key');
        this.showKeyBtn = document.getElementById('show-key-btn');
        this.sessionIdElement = document.getElementById('session-id').querySelector('span');
        this.sessionStartedElement = document.getElementById('session-started').querySelector('span');
        this.loadingOverlay = document.getElementById('loading-overlay');
        this.loadingMessage = document.querySelector('.loading-message');
        this.toastContainer = document.getElementById('toast-container');
        
        // Initialize UI
        this._initEventListeners();
        this._loadSettings();
        this._applyTheme();
        this._applyFontSize();
        
        // Flag to track initialization status
        this.initialized = false;
    }

    /**
     * Initialize the application
     */
    async initialize() {
        try {
            this.toggleLoading(true, 'Initializing application...');
            
            // Load API configuration from settings
            const endpoint = localStorage.getItem('mbda_api_endpoint');
            const apiKey = localStorage.getItem('mbda_api_key');
            
            if (endpoint) {
                this.apiClient.updateConfig({ endpoint, apiKey });
                this.apiEndpointInput.value = endpoint;
                this.apiKeyInput.value = apiKey ? '••••••••••••••••' : '';
            }
            
            // Try to get session information
            try {
                const sessionInfo = await this.apiClient.getSessionInfo();
                this._updateSessionInfo(sessionInfo);
            } catch (error) {
                console.warn('No active session found:', error);
                // Use mock data if real API fails and mock mode is enabled
                if (this._isMockModeEnabled()) {
                    this._setupMockSession();
                }
            }
            
            // Load documents
            await this.documentHandler.loadDocuments();
            
            // Load conversation history
            await this.conversationHandler.loadConversationHistory();
            
            this.initialized = true;
            this.toggleLoading(false);
        } catch (error) {
            this.handleError(`Failed to initialize application: ${error.message}`);
            this.toggleLoading(false);
            
            // If initialization fails and mock mode is enabled, set up mock environment
            if (this._isMockModeEnabled()) {
                this._setupMockEnvironment();
            }
        }
    }

    /**
     * Initialize event listeners
     * @private
     */
    _initEventListeners() {
        // Modal toggle buttons
        this.settingsBtn.addEventListener('click', () => this._toggleModal(this.settingsModal, true));
        this.helpBtn.addEventListener('click', () => this._toggleModal(this.helpModal, true));
        
        // Close modals
        this.closeButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const modal = e.target.closest('.modal');
                this._toggleModal(modal, false);
            });
        });
        
        // Cancel buttons
        this.cancelButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const modal = e.target.closest('.modal');
                this._toggleModal(modal, false);
            });
        });
        
        // Close modal on outside click
        window.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                this._toggleModal(e.target, false);
            }
        });
        
        // Save settings
        this.saveSettingsBtn.addEventListener('click', this._saveSettings.bind(this));
        
        // New session
        this.newSessionBtn.addEventListener('click', this._createNewSession.bind(this));
        
        // Theme selector
        this.themeSelector.addEventListener('change', this._applyTheme.bind(this));
        
        // Font size selector
        this.fontSizeSelector.addEventListener('change', this._applyFontSize.bind(this));
        
        // Toggle API key visibility
        this.showKeyBtn.addEventListener('click', this._toggleApiKeyVisibility.bind(this));
        
        // System theme change detection
        if (window.matchMedia) {
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
                if (this.themeSelector.value === 'system') {
                    this._applyTheme();
                }
            });
        }
    }

    /**
     * Load settings from local storage
     * @private
     */
    _loadSettings() {
        // Load theme preference
        const savedTheme = localStorage.getItem('mbda_theme');
        if (savedTheme) {
            this.themeSelector.value = savedTheme;
        }
        
        // Load font size preference
        const savedFontSize = localStorage.getItem('mbda_font_size');
        if (savedFontSize) {
            this.fontSizeSelector.value = savedFontSize;
        }
        
        // Load API settings
        const savedEndpoint = localStorage.getItem('mbda_api_endpoint');
        const savedApiKey = localStorage.getItem('mbda_api_key');
        
        if (savedEndpoint) {
            this.apiEndpointInput.value = savedEndpoint;
        }
        
        if (savedApiKey) {
            this.apiKeyInput.value = '••••••••••••••••';
        }
    }

    /**
     * Save settings to local storage
     * @private
     */
    _saveSettings() {
        // Save theme preference
        localStorage.setItem('mbda_theme', this.themeSelector.value);
        
        // Save font size preference
        localStorage.setItem('mbda_font_size', this.fontSizeSelector.value);
        
        // Save API settings
        const endpoint = this.apiEndpointInput.value.trim();
        localStorage.setItem('mbda_api_endpoint', endpoint);
        
        // Only save API key if it has changed (not masked)
        const apiKey = this.apiKeyInput.value;
        if (apiKey && apiKey !== '••••••••••••••••') {
            localStorage.setItem('mbda_api_key', apiKey);
        }
        
        // Update API client
        this.apiClient.updateConfig({
            endpoint,
            apiKey: apiKey !== '••••••••••••••••' ? apiKey : localStorage.getItem('mbda_api_key')
        });
        
        // Apply theme and font size
        this._applyTheme();
        this._applyFontSize();
        
        // Close the modal
        this._toggleModal(this.settingsModal, false);
        
        // Show success toast
        this.showToast('Settings saved successfully');
    }

    /**
     * Apply the selected theme
     * @private
     */
    _applyTheme() {
        const theme = this.themeSelector.value;
        
        if (theme === 'system') {
            // Use system preference
            const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
            document.body.classList.toggle('dark-theme', prefersDark);
            document.body.classList.toggle('light-theme', !prefersDark);
        } else if (theme === 'dark') {
            // Force dark theme
            document.body.classList.add('dark-theme');
            document.body.classList.remove('light-theme');
        } else {
            // Force light theme
            document.body.classList.add('light-theme');
            document.body.classList.remove('dark-theme');
        }
    }

    /**
     * Apply the selected font size
     * @private
     */
    _applyFontSize() {
        const fontSize = this.fontSizeSelector.value;
        document.body.classList.remove('font-small', 'font-medium', 'font-large');
        document.body.classList.add(`font-${fontSize}`);
    }

    /**
     * Toggle modal visibility
     * @param {Element} modal - Modal element
     * @param {boolean} show - Whether to show or hide
     * @private
     */
    _toggleModal(modal, show) {
        if (show) {
            modal.style.display = 'flex';
            setTimeout(() => {
                modal.classList.add('show');
            }, 10);
        } else {
            modal.classList.remove('show');
            setTimeout(() => {
                modal.style.display = 'none';
            }, 300);
        }
    }

    /**
     * Toggle API key visibility
     * @private
     */
    _toggleApiKeyVisibility() {
        const input = this.apiKeyInput;
        const icon = this.showKeyBtn.querySelector('i');
        
        if (input.type === 'password') {
            input.type = 'text';
            icon.classList.remove('fa-eye');
            icon.classList.add('fa-eye-slash');
        } else {
            input.type = 'password';
            icon.classList.remove('fa-eye-slash');
            icon.classList.add('fa-eye');
        }
    }

    /**
     * Create a new session
     * @private
     */
    async _createNewSession() {
        try {
            this.toggleLoading(true, 'Creating new session...');
            
            // Create new session
            const sessionId = await this.apiClient.createNewSession();
            
            // Get session info
            const sessionInfo = await this.apiClient.getSessionInfo();
            this._updateSessionInfo(sessionInfo);
            
            // Clear conversation
            await this.conversationHandler.loadConversationHistory();
            
            // Clear documents
            await this.documentHandler.loadDocuments();
            
            this.toggleLoading(false);
            this.showToast('New session created successfully');
            
            // Close the modal
            this._toggleModal(this.settingsModal, false);
        } catch (error) {
            this.toggleLoading(false);
            this.handleError(`Failed to create new session: ${error.message}`);
            
            // If real API fails and mock mode is enabled, create mock session
            if (this._isMockModeEnabled()) {
                this._setupMockSession();
                this._toggleModal(this.settingsModal, false);
            }
        }
    }

    /**
     * Update session information in the UI
     * @param {Object} sessionInfo - Session information
     * @private
     */
    _updateSessionInfo(sessionInfo) {
        if (sessionInfo && sessionInfo.session_id) {
            this.sessionIdElement.textContent = sessionInfo.session_id;
            
            // Format timestamp
            const timestamp = new Date(sessionInfo.created_at || new Date()).toLocaleString();
            this.sessionStartedElement.textContent = timestamp;
        }
    }

    /**
     * Show a toast notification
     * @param {string} message - Toast message
     * @param {string} type - Toast type ('success', 'error', 'info')
     * @param {number} duration - Duration in milliseconds
     */
    showToast(message, type = 'success', duration = 3000) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        
        this.toastContainer.appendChild(toast);
        
        // Trigger animation
        setTimeout(() => {
            toast.classList.add('show');
        }, 10);
        
        // Remove after duration
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => {
                this.toastContainer.removeChild(toast);
            }, 300);
        }, duration);
    }

    /**
     * Handle errors
     * @param {string|Error} error - Error message or object
     */
    handleError(error) {
        const errorMessage = error instanceof Error ? error.message : error;
        console.error('Application Error:', errorMessage);
        this.showToast(errorMessage, 'error', 5000);
    }

    /**
     * Toggle loading overlay
     * @param {boolean} isLoading - Whether to show or hide
     * @param {string} message - Loading message
     */
    toggleLoading(isLoading, message = 'Processing...') {
        if (isLoading) {
            this.loadingMessage.textContent = message;
            this.loadingOverlay.style.display = 'flex';
            setTimeout(() => {
                this.loadingOverlay.classList.add('show');
            }, 10);
        } else {
            this.loadingOverlay.classList.remove('show');
            setTimeout(() => {
                this.loadingOverlay.style.display = 'none';
            }, 300);
        }
    }

    /**
     * Check if mock mode is enabled
     * @returns {boolean} - Whether mock mode is enabled
     * @private
     */
    _isMockModeEnabled() {
        // Check URL parameter or localStorage
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.has('mock') || localStorage.getItem('mbda_mock_mode') === 'true';
    }

    /**
     * Set up mock environment when API is unavailable
     * @private
     */
    _setupMockEnvironment() {
        this._setupMockSession();
        this.showToast('Using mock data for demonstration', 'info', 5000);
    }

    /**
     * Set up a mock session
     * @private
     */
    _setupMockSession() {
        // Create mock session data
        const mockSessionId = 'mock-' + Math.random().toString(36).substring(2, 10);
        const mockCreatedAt = new Date().toISOString();
        
        // Update session info in UI
        this.sessionIdElement.textContent = mockSessionId;
        this.sessionStartedElement.textContent = new Date(mockCreatedAt).toLocaleString();
        
        // Store mock session ID
        this.apiClient.sessionId = mockSessionId;
        
        this.showToast('Mock session created for demonstration', 'info', 3000);
    }
}

// Export the UI controller
window.UIController = UIController;
