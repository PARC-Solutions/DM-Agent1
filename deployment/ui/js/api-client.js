/**
 * API Client for Medical Billing Denial Assistant
 * Handles communication with the deployed Vertex AI agent
 */

class ApiClient {
    /**
     * Initialize the API client
     * @param {Object} config - Configuration options
     * @param {string} config.endpoint - API endpoint URL
     * @param {string} config.apiKey - API key for authentication
     * @param {Function} config.onError - Error callback function
     */
    constructor(config = {}) {
        this.endpoint = config.endpoint || '';
        this.apiKey = config.apiKey || '';
        this.onError = config.onError || (error => console.error('API Error:', error));
        
        // Check if settings exist in local storage
        const savedEndpoint = localStorage.getItem('mbda_api_endpoint');
        const savedApiKey = localStorage.getItem('mbda_api_key');
        
        if (savedEndpoint) this.endpoint = savedEndpoint;
        if (savedApiKey) this.apiKey = savedApiKey;
        
        this.sessionId = null;
    }

    /**
     * Update API configuration
     * @param {Object} config - New configuration options
     */
    updateConfig(config = {}) {
        if (config.endpoint) {
            this.endpoint = config.endpoint;
            localStorage.setItem('mbda_api_endpoint', config.endpoint);
        }
        
        if (config.apiKey) {
            this.apiKey = config.apiKey;
            localStorage.setItem('mbda_api_key', config.apiKey);
        }
    }

    /**
     * Create or get a session for conversation
     * @returns {Promise<string>} - Session ID
     */
    async getSession() {
        if (this.sessionId) {
            return this.sessionId;
        }

        try {
            const response = await this._makeRequest('/sessions', 'POST');
            this.sessionId = response.session_id;
            return this.sessionId;
        } catch (error) {
            this.onError(error);
            throw error;
        }
    }

    /**
     * Create a new session
     * @returns {Promise<string>} - New session ID
     */
    async createNewSession() {
        try {
            const response = await this._makeRequest('/sessions', 'POST');
            this.sessionId = response.session_id;
            return this.sessionId;
        } catch (error) {
            this.onError(error);
            throw error;
        }
    }

    /**
     * Get session information
     * @returns {Promise<Object>} - Session information
     */
    async getSessionInfo() {
        if (!this.sessionId) {
            await this.getSession();
        }

        try {
            const response = await this._makeRequest(`/sessions/${this.sessionId}`, 'GET');
            return response;
        } catch (error) {
            this.onError(error);
            throw error;
        }
    }

    /**
     * Send a message to the agent
     * @param {string} message - User message
     * @returns {Promise<Object>} - Agent response
     */
    async sendMessage(message) {
        if (!this.sessionId) {
            await this.getSession();
        }

        try {
            const response = await this._makeRequest(`/sessions/${this.sessionId}/messages`, 'POST', {
                message: message
            });
            return response;
        } catch (error) {
            this.onError(error);
            throw error;
        }
    }

    /**
     * Upload a document
     * @param {File} file - File to upload
     * @param {string} documentType - Type of document (cms1500, eob, other)
     * @returns {Promise<Object>} - Document information
     */
    async uploadDocument(file, documentType) {
        if (!this.sessionId) {
            await this.getSession();
        }

        try {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('document_type', documentType);

            const response = await this._makeFormRequest(`/sessions/${this.sessionId}/documents`, 'POST', formData);
            return response;
        } catch (error) {
            this.onError(error);
            throw error;
        }
    }

    /**
     * Get a list of documents in the session
     * @returns {Promise<Array>} - List of documents
     */
    async getDocuments() {
        if (!this.sessionId) {
            await this.getSession();
        }

        try {
            const response = await this._makeRequest(`/sessions/${this.sessionId}/documents`, 'GET');
            return response.documents || [];
        } catch (error) {
            this.onError(error);
            throw error;
        }
    }

    /**
     * Delete a document
     * @param {string} documentId - Document ID
     * @returns {Promise<Object>} - Response
     */
    async deleteDocument(documentId) {
        if (!this.sessionId) {
            throw new Error('No active session');
        }

        try {
            const response = await this._makeRequest(`/sessions/${this.sessionId}/documents/${documentId}`, 'DELETE');
            return response;
        } catch (error) {
            this.onError(error);
            throw error;
        }
    }

    /**
     * Get conversation history
     * @returns {Promise<Array>} - List of messages
     */
    async getConversationHistory() {
        if (!this.sessionId) {
            await this.getSession();
        }

        try {
            const response = await this._makeRequest(`/sessions/${this.sessionId}/messages`, 'GET');
            return response.messages || [];
        } catch (error) {
            this.onError(error);
            throw error;
        }
    }

    /**
     * Make a request to the API
     * @param {string} path - API path
     * @param {string} method - HTTP method
     * @param {Object} data - Request data
     * @returns {Promise<Object>} - Response data
     * @private
     */
    async _makeRequest(path, method, data = null) {
        if (!this.endpoint) {
            throw new Error('API endpoint not configured');
        }

        const url = `${this.endpoint}${path}`;
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        };

        if (this.apiKey) {
            options.headers['Authorization'] = `Bearer ${this.apiKey}`;
        }

        if (data) {
            options.body = JSON.stringify(data);
        }

        try {
            const response = await fetch(url, options);
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.message || `API request failed with status ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            throw error;
        }
    }

    /**
     * Make a form data request to the API
     * @param {string} path - API path
     * @param {string} method - HTTP method
     * @param {FormData} formData - Form data
     * @returns {Promise<Object>} - Response data
     * @private
     */
    async _makeFormRequest(path, method, formData) {
        if (!this.endpoint) {
            throw new Error('API endpoint not configured');
        }

        const url = `${this.endpoint}${path}`;
        const options = {
            method,
            headers: {}
        };

        if (this.apiKey) {
            options.headers['Authorization'] = `Bearer ${this.apiKey}`;
        }

        options.body = formData;

        try {
            const response = await fetch(url, options);
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.message || `API request failed with status ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            throw error;
        }
    }
}

// Export the API client
window.ApiClient = ApiClient;
