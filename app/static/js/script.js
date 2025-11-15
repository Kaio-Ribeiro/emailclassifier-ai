// Estado da aplicação
let currentFile = null;
let isProcessing = false;

// Elementos DOM
const elements = {
    // Tabs
    tabButtons: document.querySelectorAll('.tab-btn'),
    tabContents: document.querySelectorAll('.tab-content'),
    
    // File upload
    fileDropArea: document.getElementById('file-drop-area'),
    fileInput: document.getElementById('file-input'),
    selectedFile: document.getElementById('selected-file'),
    removeFileBtn: document.getElementById('remove-file'),
    fileSubmitBtn: document.getElementById('file-submit-btn'),
    fileUploadForm: document.getElementById('file-upload-form'),
    
    // Text input
    emailText: document.getElementById('email-text'),
    charCount: document.getElementById('char-count'),
    textSubmitBtn: document.getElementById('text-submit-btn'),
    textUploadForm: document.getElementById('text-upload-form'),
    
    // Sections
    loadingSection: document.getElementById('loading-section'),
    resultsSection: document.getElementById('results-section'),
    
    // Results
    classificationBadge: document.getElementById('classification-badge'),
    classificationText: document.getElementById('classification-text'),
    confidenceScore: document.getElementById('confidence-score'),
    suggestedResponse: document.getElementById('suggested-response'),
    copyResponseBtn: document.getElementById('copy-response'),
    analyzeAnotherBtn: document.getElementById('analyze-another'),
    downloadResultBtn: document.getElementById('download-result')
};

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    initializeTabs();
    initializeFileUpload();
    initializeTextInput();
    initializeResultActions();
});

// Gerenciamento de Tabs
function initializeTabs() {
    elements.tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabName = button.dataset.tab;
            switchTab(tabName);
        });
    });
}

function switchTab(tabName) {
    // Remove active class from all tabs
    elements.tabButtons.forEach(btn => btn.classList.remove('active'));
    elements.tabContents.forEach(content => content.classList.remove('active'));
    
    // Add active class to selected tab
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    document.getElementById(`${tabName}-tab`).classList.add('active');
    
    // Reset forms when switching tabs
    resetForms();
}

// File Upload Functionality
function initializeFileUpload() {
    // Click to select file
    elements.fileDropArea.addEventListener('click', () => {
        elements.fileInput.click();
    });
    
    // File input change
    elements.fileInput.addEventListener('change', handleFileSelect);
    
    // Drag and drop
    elements.fileDropArea.addEventListener('dragover', handleDragOver);
    elements.fileDropArea.addEventListener('dragleave', handleDragLeave);
    elements.fileDropArea.addEventListener('drop', handleFileDrop);
    
    // Remove file
    elements.removeFileBtn.addEventListener('click', removeSelectedFile);
    
    // Form submission
    elements.fileUploadForm.addEventListener('submit', handleFileSubmit);
}

function handleDragOver(e) {
    e.preventDefault();
    elements.fileDropArea.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    elements.fileDropArea.classList.remove('dragover');
}

function handleFileDrop(e) {
    e.preventDefault();
    elements.fileDropArea.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileSelect({ target: { files } });
    }
}

function handleFileSelect(e) {
    const file = e.target.files[0];
    
    if (!file) return;
    
    // Validate file type
    const allowedTypes = ['.txt', '.pdf'];
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
    
    if (!allowedTypes.includes(fileExtension)) {
        showNotification('Formato de arquivo não suportado. Use apenas .txt ou .pdf', 'error');
        return;
    }
    
    // Validate file size (16MB max)
    const maxSize = 16 * 1024 * 1024; // 16MB
    if (file.size > maxSize) {
        showNotification('Arquivo muito grande. Tamanho máximo: 16MB', 'error');
        return;
    }
    
    currentFile = file;
    showSelectedFile(file);
    elements.fileSubmitBtn.disabled = false;
}

function showSelectedFile(file) {
    const fileName = elements.selectedFile.querySelector('.file-name');
    fileName.textContent = file.name;
    elements.selectedFile.style.display = 'flex';
    elements.fileDropArea.style.display = 'none';
}

function removeSelectedFile() {
    currentFile = null;
    elements.selectedFile.style.display = 'none';
    elements.fileDropArea.style.display = 'block';
    elements.fileInput.value = '';
    elements.fileSubmitBtn.disabled = true;
}

function handleFileSubmit(e) {
    e.preventDefault();
    
    if (!currentFile || isProcessing) return;
    
    processEmail('file', currentFile);
}

// Text Input Functionality
function initializeTextInput() {
    elements.emailText.addEventListener('input', handleTextInput);
    elements.textUploadForm.addEventListener('submit', handleTextSubmit);
}

function handleTextInput(e) {
    const text = e.target.value;
    const charCount = text.length;
    
    elements.charCount.textContent = charCount.toLocaleString();
    elements.textSubmitBtn.disabled = charCount === 0;
    
    // Color code based on length
    if (charCount > 5000) {
        elements.charCount.style.color = 'var(--danger-color)';
    } else if (charCount > 3000) {
        elements.charCount.style.color = 'var(--warning-color)';
    } else {
        elements.charCount.style.color = 'var(--text-muted)';
    }
}

function handleTextSubmit(e) {
    e.preventDefault();
    
    const text = elements.emailText.value.trim();
    
    if (!text || isProcessing) return;
    
    if (text.length < 10) {
        showNotification('Por favor, insira pelo menos 10 caracteres', 'warning');
        return;
    }
    
    processEmail('text', text);
}

// Email Processing
async function processEmail(type, data) {
    if (isProcessing) return;
    
    isProcessing = true;
    showLoadingSection();
    
    try {
        let result;
        
        if (type === 'text') {
            result = await classifyText(data);
        } else if (type === 'file') {
            result = await classifyFile(data);
        }
        
        showResults(result);
        
    } catch (error) {
        console.error('Error processing email:', error);
        showNotification('Erro ao processar email. Tente novamente.', 'error');
        hideLoadingSection();
    } finally {
        isProcessing = false;
    }
}

async function classifyText(text) {
    const response = await fetch('/api/classify/text', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: text })
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Erro na classificação');
    }
    
    return await response.json();
}

async function classifyFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch('/api/classify/file', {
        method: 'POST',
        body: formData
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Erro na classificação');
    }
    
    return await response.json();
}



function showResults(result) {
    hideLoadingSection();
    
    // Update UI with API results
    const classification = result.classification;
    const confidence = Math.round(result.confidence * 100);
    
    elements.classificationText.textContent = classification.charAt(0).toUpperCase() + classification.slice(1);
    elements.classificationBadge.className = `classification-badge ${classification}`;
    elements.confidenceScore.textContent = `${confidence}%`;
    elements.suggestedResponse.textContent = result.suggested_response;
    
    // Show results
    elements.resultsSection.style.display = 'block';
    elements.resultsSection.scrollIntoView({ behavior: 'smooth' });
}



// UI State Management
function showLoadingSection() {
    elements.loadingSection.style.display = 'block';
    elements.resultsSection.style.display = 'none';
    elements.loadingSection.scrollIntoView({ behavior: 'smooth' });
}

function hideLoadingSection() {
    elements.loadingSection.style.display = 'none';
}

// Result Actions
function initializeResultActions() {
    elements.copyResponseBtn.addEventListener('click', copyResponse);
    elements.analyzeAnotherBtn.addEventListener('click', analyzeAnother);
    elements.downloadResultBtn.addEventListener('click', downloadResult);
}

async function copyResponse() {
    try {
        await navigator.clipboard.writeText(elements.suggestedResponse.textContent);
        showNotification('Resposta copiada para a área de transferência!', 'success');
        
        // Visual feedback
        const originalText = elements.copyResponseBtn.innerHTML;
        elements.copyResponseBtn.innerHTML = '<i class="fas fa-check"></i> Copiado!';
        setTimeout(() => {
            elements.copyResponseBtn.innerHTML = originalText;
        }, 2000);
        
    } catch (error) {
        showNotification('Erro ao copiar. Tente selecionar o texto manualmente.', 'error');
    }
}

function analyzeAnother() {
    resetForms();
    elements.resultsSection.style.display = 'none';
    document.querySelector('.upload-section').scrollIntoView({ behavior: 'smooth' });
}

function downloadResult() {
    const classification = elements.classificationText.textContent;
    const confidence = elements.confidenceScore.textContent;
    const response = elements.suggestedResponse.textContent;
    
    const result = `RESULTADO DA ANÁLISE - EMAIL CLASSIFIER AI
=====================================

Data: ${new Date().toLocaleString('pt-BR')}

CLASSIFICAÇÃO: ${classification}
CONFIANÇA: ${confidence}

RESPOSTA SUGERIDA:
${response}

=====================================
Gerado por Email Classifier AI
`;
    
    const blob = new Blob([result], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `resultado-analise-${new Date().toISOString().slice(0, 10)}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    showNotification('Resultado baixado com sucesso!', 'success');
}

// Utility Functions
function resetForms() {
    // Reset file upload
    removeSelectedFile();
    
    // Reset text input
    elements.emailText.value = '';
    elements.charCount.textContent = '0';
    elements.textSubmitBtn.disabled = true;
    
    // Reset UI state
    isProcessing = false;
    elements.resultsSection.style.display = 'none';
    elements.loadingSection.style.display = 'none';
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${getNotificationIcon(type)}"></i>
            <span>${message}</span>
        </div>
    `;
    
    // Add styles
    Object.assign(notification.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        zIndex: '1000',
        padding: '1rem 1.5rem',
        borderRadius: 'var(--border-radius)',
        color: 'white',
        fontWeight: '500',
        boxShadow: 'var(--shadow-lg)',
        transform: 'translateX(100%)',
        transition: 'transform 0.3s ease',
        maxWidth: '400px'
    });
    
    // Set background color based on type
    const colors = {
        success: 'var(--success-color)',
        error: 'var(--danger-color)',
        warning: 'var(--warning-color)',
        info: 'var(--primary-color)'
    };
    notification.style.background = colors[type] || colors.info;
    
    // Add to DOM
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 5000);
}

function getNotificationIcon(type) {
    const icons = {
        success: 'check-circle',
        error: 'exclamation-circle',
        warning: 'exclamation-triangle',
        info: 'info-circle'
    };
    return icons[type] || icons.info;
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + Enter to submit
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        const activeTab = document.querySelector('.tab-content.active');
        if (activeTab.id === 'text-tab' && !elements.textSubmitBtn.disabled) {
            handleTextSubmit(e);
        } else if (activeTab.id === 'file-tab' && !elements.fileSubmitBtn.disabled) {
            handleFileSubmit(e);
        }
    }
    
    // Escape to reset
    if (e.key === 'Escape' && elements.resultsSection.style.display === 'block') {
        analyzeAnother();
    }
});

// Prevent form submission on Enter (except in textarea)
document.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && e.target.tagName !== 'TEXTAREA') {
        e.preventDefault();
    }
});