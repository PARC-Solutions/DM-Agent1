/**
 * Main Application Script for Medical Billing Denial Assistant
 * Initializes all components and sets up the application
 */

// Mock API implementation for testing without a backend
class MockApi {
    /**
     * Initialize the mock API
     */
    constructor() {
        // Check if mock data exists in localStorage
        let mockData = localStorage.getItem('mbda_mock_data');
        
        if (!mockData) {
            // Initialize with empty data
            mockData = {
                sessionId: 'mock-' + Math.random().toString(36).substring(2, 10),
                createdAt: new Date().toISOString(),
                messages: [],
                documents: []
            };
            
            localStorage.setItem('mbda_mock_data', JSON.stringify(mockData));
        } else {
            mockData = JSON.parse(mockData);
        }
        
        this.mockData = mockData;
    }

    /**
     * Install mock API endpoints
     * @param {ApiClient} apiClient - API client instance
     */
    install(apiClient) {
        // Store original methods
        this.originalMethods = {
            _makeRequest: apiClient._makeRequest,
            _makeFormRequest: apiClient._makeFormRequest
        };

        // Override API methods
        apiClient._makeRequest = this._mockRequest.bind(this, apiClient);
        apiClient._makeFormRequest = this._mockFormRequest.bind(this, apiClient);
        
        console.log('Mock API installed');
        return apiClient;
    }

    /**
     * Remove mock API endpoints
     * @param {ApiClient} apiClient - API client instance
     */
    uninstall(apiClient) {
        // Restore original methods
        if (this.originalMethods) {
            apiClient._makeRequest = this.originalMethods._makeRequest;
            apiClient._makeFormRequest = this.originalMethods._makeFormRequest;
            console.log('Mock API uninstalled');
        }
        
        return apiClient;
    }

    /**
     * Mock API request handler
     * @param {ApiClient} apiClient - API client instance
     * @param {string} path - API path
     * @param {string} method - HTTP method
     * @param {Object} data - Request data
     * @returns {Promise<Object>} - Response data
     * @private
     */
    async _mockRequest(apiClient, path, method, data = null) {
        console.log(`Mock API Request: ${method} ${path}`, data);
        
        // Simulate network delay
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // Handle different API endpoints
        if (path.startsWith('/sessions') && method === 'POST') {
            return this._handleCreateSession();
        } else if (path.match(/^\/sessions\/[^/]+$/) && method === 'GET') {
            return this._handleGetSessionInfo();
        } else if (path.match(/^\/sessions\/[^/]+\/messages$/) && method === 'GET') {
            return this._handleGetMessages();
        } else if (path.match(/^\/sessions\/[^/]+\/messages$/) && method === 'POST') {
            return this._handleSendMessage(data);
        } else if (path.match(/^\/sessions\/[^/]+\/documents$/) && method === 'GET') {
            return this._handleGetDocuments();
        } else if (path.match(/^\/sessions\/[^/]+\/documents\/[^/]+$/) && method === 'DELETE') {
            const documentId = path.split('/').pop();
            return this._handleDeleteDocument(documentId);
        }
        
        // Default: return error for unhandled endpoints
        throw new Error(`Mock API endpoint not implemented: ${method} ${path}`);
    }

    /**
     * Mock form data request handler
     * @param {ApiClient} apiClient - API client instance
     * @param {string} path - API path
     * @param {string} method - HTTP method
     * @param {FormData} formData - Form data
     * @returns {Promise<Object>} - Response data
     * @private
     */
    async _mockFormRequest(apiClient, path, method, formData) {
        console.log(`Mock API Form Request: ${method} ${path}`);
        
        // Simulate network delay
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Handle file uploads
        if (path.match(/^\/sessions\/[^/]+\/documents$/) && method === 'POST') {
            const file = formData.get('file');
            const documentType = formData.get('document_type');
            return this._handleUploadDocument(file, documentType);
        }
        
        // Default: return error for unhandled endpoints
        throw new Error(`Mock API form endpoint not implemented: ${method} ${path}`);
    }

    /**
     * Handle create session request
     * @returns {Promise<Object>} - Session data
     * @private
     */
    async _handleCreateSession() {
        // Create new session
        const sessionId = 'mock-' + Math.random().toString(36).substring(2, 10);
        const createdAt = new Date().toISOString();
        
        // Update mock data
        this.mockData.sessionId = sessionId;
        this.mockData.createdAt = createdAt;
        this.mockData.messages = [];
        this.mockData.documents = [];
        
        // Save to localStorage
        localStorage.setItem('mbda_mock_data', JSON.stringify(this.mockData));
        
        return {
            session_id: sessionId,
            created_at: createdAt
        };
    }

    /**
     * Handle get session info request
     * @returns {Promise<Object>} - Session info
     * @private
     */
    async _handleGetSessionInfo() {
        if (!this.mockData.sessionId) {
            throw new Error('No active session');
        }
        
        return {
            session_id: this.mockData.sessionId,
            created_at: this.mockData.createdAt,
            message_count: this.mockData.messages.length,
            document_count: this.mockData.documents.length
        };
    }

    /**
     * Handle get messages request
     * @returns {Promise<Object>} - Messages data
     * @private
     */
    async _handleGetMessages() {
        return {
            messages: this.mockData.messages
        };
    }

    /**
     * Handle send message request
     * @param {Object} data - Message data
     * @returns {Promise<Object>} - Response data
     * @private
     */
    async _handleSendMessage(data) {
        const userMessage = data.message;
        
        // Add user message to history
        this.mockData.messages.push({
            role: 'user',
            content: userMessage,
            timestamp: new Date().toISOString()
        });
        
        // Generate mock response based on user message
        let responseContent = 'I understand your request about medical billing denials. ';
        
        if (userMessage.toLowerCase().includes('denial')) {
            responseContent += 'Based on the information provided, this appears to be a denial due to missing information. I recommend reviewing the claim for completeness and resubmitting with all required fields properly filled out.';
        } else if (userMessage.toLowerCase().includes('code')) {
            responseContent += 'The code in question may be related to incorrect procedure coding. Ensure that the CPT or HCPCS codes match the documented services and check for any required modifiers.';
        } else if (userMessage.toLowerCase().includes('document')) {
            responseContent += 'Please upload any additional documentation such as the CMS-1500 form or Explanation of Benefits to help with further analysis.';
        } else {
            responseContent += 'To provide more specific guidance, I would need additional details about the denial reason or access to relevant documentation such as the claim form or EOB. Could you provide more information?';
        }
        
        // Add assistant response to history
        this.mockData.messages.push({
            role: 'assistant',
            content: responseContent,
            timestamp: new Date().toISOString()
        });
        
        // Save to localStorage
        localStorage.setItem('mbda_mock_data', JSON.stringify(this.mockData));
        
        return {
            message: responseContent
        };
    }

    /**
     * Handle get documents request
     * @returns {Promise<Object>} - Documents data
     * @private
     */
    async _handleGetDocuments() {
        return {
            documents: this.mockData.documents
        };
    }

    /**
     * Handle upload document request
     * @param {File} file - Uploaded file
     * @param {string} documentType - Document type
     * @returns {Promise<Object>} - Document data
     * @private
     */
    async _handleUploadDocument(file, documentType) {
        const documentId = 'doc-' + Math.random().toString(36).substring(2, 10);
        
        // Create mock document
        const document = {
            id: documentId,
            name: file.name,
            type: documentType,
            size: file.size,
            timestamp: new Date().toISOString(),
            metadata: {
                contentType: file.type,
                mockData: true
            }
        };
        
        // Add to documents array
        this.mockData.documents.push(document);
        
        // Save to localStorage
        localStorage.setItem('mbda_mock_data', JSON.stringify(this.mockData));
        
        return {
            document_id: documentId,
            name: file.name,
            type: documentType,
            metadata: document.metadata
        };
    }

    /**
     * Handle delete document request
     * @param {string} documentId - Document ID
     * @returns {Promise<Object>} - Response data
     * @private
     */
    async _handleDeleteDocument(documentId) {
        // Find document index
        const index = this.mockData.documents.findIndex(doc => doc.id === documentId);
        
        if (index === -1) {
            throw new Error('Document not found');
        }
        
        // Remove document
        this.mockData.documents.splice(index, 1);
        
        // Save to localStorage
        localStorage.setItem('mbda_mock_data', JSON.stringify(this.mockData));
        
        return {
            success: true,
            message: 'Document deleted successfully'
        };
    }

    /**
     * Reset all mock data
     */
    reset() {
        // Reset mock data
        this.mockData = {
            sessionId: 'mock-' + Math.random().toString(36).substring(2, 10),
            createdAt: new Date().toISOString(),
            messages: [],
            documents: []
        };
        
        // Save to localStorage
        localStorage.setItem('mbda_mock_data', JSON.stringify(this.mockData));
        
        console.log('Mock data reset');
    }
}

// Application initialization
document.addEventListener('DOMContentLoaded', () => {
    console.log('Initializing Medical Billing Denial Assistant...');
    
    // Create UI controller
    const uiController = new UIController();
    
    // Check for mock mode
    const urlParams = new URLSearchParams(window.location.search);
    const mockMode = urlParams.has('mock') || localStorage.getItem('mbda_mock_mode') === 'true';
    
    if (mockMode) {
        console.log('Mock mode enabled');
        localStorage.setItem('mbda_mock_mode', 'true');
        
        // Create and install mock API
        const mockApi = new MockApi();
        mockApi.install(uiController.apiClient);
        
        // Store mock API instance for debugging
        window.mockApi = mockApi;
    }
    
    // Initialize UI
    uiController.initialize().catch(error => {
        console.error('Initialization error:', error);
        uiController.handleError('Failed to initialize application. Please check your connection and try again.');
    });
    
    // Store UI controller instance for debugging
    window.uiController = uiController;
    
    console.log('Initialization complete');
});

// Expose mock mode toggle function for debugging
window.toggleMockMode = (enable) => {
    const uiController = window.uiController;
    
    if (!uiController) {
        console.error('UI controller not initialized');
        return;
    }
    
    if (enable) {
        localStorage.setItem('mbda_mock_mode', 'true');
        
        // Create and install mock API if not already installed
        if (!window.mockApi) {
            window.mockApi = new MockApi();
            window.mockApi.install(uiController.apiClient);
        }
        
        console.log('Mock mode enabled');
    } else {
        localStorage.removeItem('mbda_mock_mode');
        
        // Uninstall mock API if installed
        if (window.mockApi) {
            window.mockApi.uninstall(uiController.apiClient);
            window.mockApi = null;
        }
        
        console.log('Mock mode disabled');
    }
    
    // Reload the page to apply changes
    window.location.reload();
};
