/**
 * Document Handler for Medical Billing Denial Assistant
 * Manages document uploads and manipulation in the UI
 */

class DocumentHandler {
    /**
     * Initialize the document handler
     * @param {Object} config - Configuration options
     * @param {ApiClient} config.apiClient - API client instance
     * @param {Function} config.onError - Error callback function
     * @param {Function} config.onSuccess - Success callback function
     * @param {Function} config.onProcessing - Processing status callback
     */
    constructor(config = {}) {
        this.apiClient = config.apiClient;
        this.onError = config.onError || (error => console.error('Document Error:', error));
        this.onSuccess = config.onSuccess || (message => console.log('Document Success:', message));
        this.onProcessing = config.onProcessing || (isProcessing => {});
        
        this.documentList = document.getElementById('document-list');
        this.documentUploadInput = document.getElementById('document-upload-input');
        this.documentTypeSelector = document.getElementById('document-type');
        
        this._initEventListeners();
        this.documents = [];
    }

    /**
     * Initialize event listeners
     * @private
     */
    _initEventListeners() {
        // Listen for file uploads
        this.documentUploadInput.addEventListener('change', this._handleFileSelect.bind(this));
        
        // Handle drag and drop
        const dropArea = document.querySelector('.document-section');
        
        dropArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropArea.classList.add('drag-over');
        });
        
        dropArea.addEventListener('dragleave', (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropArea.classList.remove('drag-over');
        });
        
        dropArea.addEventListener('drop', (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropArea.classList.remove('drag-over');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this._processFiles(files);
            }
        });
    }

    /**
     * Handle file selection from input
     * @param {Event} event - Change event
     * @private
     */
    _handleFileSelect(event) {
        const files = event.target.files;
        if (files.length > 0) {
            this._processFiles(files);
        }
    }

    /**
     * Process selected files
     * @param {FileList} files - Files to process
     * @private
     */
    async _processFiles(files) {
        const documentType = this.documentTypeSelector.value;
        
        this.onProcessing(true);
        
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            
            try {
                // Upload the document
                const response = await this.apiClient.uploadDocument(file, documentType);
                
                // Add to documents array
                this.documents.push({
                    id: response.document_id,
                    name: file.name,
                    type: documentType,
                    timestamp: new Date().toISOString(),
                    metadata: response.metadata || {}
                });
                
                // Show success message
                this.onSuccess(`Document '${file.name}' uploaded successfully`);
                
                // Refresh the document list
                this._renderDocumentList();
            } catch (error) {
                this.onError(`Failed to upload document '${file.name}': ${error.message}`);
            }
        }
        
        // Reset file input
        this.documentUploadInput.value = '';
        
        this.onProcessing(false);
    }

    /**
     * Load documents from the API
     */
    async loadDocuments() {
        try {
            this.onProcessing(true);
            const documents = await this.apiClient.getDocuments();
            this.documents = documents;
            this._renderDocumentList();
            this.onProcessing(false);
        } catch (error) {
            this.onProcessing(false);
            this.onError(`Failed to load documents: ${error.message}`);
        }
    }

    /**
     * Delete a document
     * @param {string} documentId - Document ID to delete
     */
    async deleteDocument(documentId) {
        try {
            this.onProcessing(true);
            await this.apiClient.deleteDocument(documentId);
            
            // Remove from documents array
            this.documents = this.documents.filter(doc => doc.id !== documentId);
            
            // Refresh the document list
            this._renderDocumentList();
            
            this.onSuccess('Document deleted successfully');
            this.onProcessing(false);
        } catch (error) {
            this.onProcessing(false);
            this.onError(`Failed to delete document: ${error.message}`);
        }
    }

    /**
     * Preview a document (placeholder - would open document viewer in real implementation)
     * @param {string} documentId - Document ID to preview
     */
    previewDocument(documentId) {
        const document = this.documents.find(doc => doc.id === documentId);
        if (!document) {
            this.onError('Document not found');
            return;
        }
        
        // For now, just show an alert with document info
        // In a real implementation, this would open a document viewer
        alert(`Document Preview\n\nName: ${document.name}\nType: ${document.type}\nID: ${document.id}`);
    }

    /**
     * Render the document list in the UI
     * @private
     */
    _renderDocumentList() {
        // Clear the list
        this.documentList.innerHTML = '';
        
        if (this.documents.length === 0) {
            const emptyMessage = document.createElement('li');
            emptyMessage.className = 'document-empty';
            emptyMessage.textContent = 'No documents uploaded';
            this.documentList.appendChild(emptyMessage);
            return;
        }
        
        // Add each document to the list
        this.documents.forEach(document => {
            const listItem = document.createElement('li');
            
            // Document name
            const nameSpan = document.createElement('span');
            nameSpan.className = 'document-name';
            nameSpan.textContent = document.name;
            nameSpan.setAttribute('title', document.name);
            listItem.appendChild(nameSpan);
            
            // Document actions
            const actions = document.createElement('div');
            actions.className = 'document-actions';
            
            // Preview button
            const previewButton = document.createElement('button');
            previewButton.innerHTML = '<i class="fas fa-eye"></i>';
            previewButton.setAttribute('title', 'Preview Document');
            previewButton.setAttribute('aria-label', 'Preview Document');
            previewButton.addEventListener('click', () => this.previewDocument(document.id));
            actions.appendChild(previewButton);
            
            // Delete button
            const deleteButton = document.createElement('button');
            deleteButton.innerHTML = '<i class="fas fa-trash-alt"></i>';
            deleteButton.setAttribute('title', 'Delete Document');
            deleteButton.setAttribute('aria-label', 'Delete Document');
            deleteButton.addEventListener('click', () => {
                if (confirm('Are you sure you want to delete this document?')) {
                    this.deleteDocument(document.id);
                }
            });
            actions.appendChild(deleteButton);
            
            listItem.appendChild(actions);
            
            // Add document type indicator
            let typeIcon = 'fa-file';
            let typeName = 'Document';
            
            if (document.type === 'cms1500') {
                typeIcon = 'fa-file-medical';
                typeName = 'CMS-1500 Form';
            } else if (document.type === 'eob') {
                typeIcon = 'fa-file-invoice-dollar';
                typeName = 'EOB';
            }
            
            listItem.setAttribute('data-type', document.type);
            listItem.setAttribute('data-document-id', document.id);
            listItem.setAttribute('title', `${document.name} (${typeName})`);
            listItem.classList.add(`document-type-${document.type}`);
            
            this.documentList.appendChild(listItem);
        });
    }

    /**
     * Get the list of document IDs
     * @returns {Array<string>} - List of document IDs
     */
    getDocumentIds() {
        return this.documents.map(doc => doc.id);
    }

    /**
     * Get document information by ID
     * @param {string} documentId - Document ID
     * @returns {Object|null} - Document information or null if not found
     */
    getDocumentById(documentId) {
        return this.documents.find(doc => doc.id === documentId) || null;
    }
}

// Export the document handler
window.DocumentHandler = DocumentHandler;
