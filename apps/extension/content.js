// Content script for ZgrWise Clipper

// Listen for messages from background script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "getSelection") {
        const selection = getSelection();
        sendResponse(selection);
    } else if (request.action === "showNotification") {
        showNotification(request.message, request.type);
    }
});

function getSelection() {
    const selection = window.getSelection();
    const selectedText = selection.toString().trim();
    
    if (!selectedText) {
        return {
            text: '',
            title: document.title,
            content: document.body.innerText || document.body.textContent || '',
            url: window.location.href
        };
    }

    // Get the selected text and surrounding context
    const range = selection.getRangeAt(0);
    const container = range.commonAncestorContainer;
    
    // Try to get the parent element for context
    let context = '';
    if (container.nodeType === Node.TEXT_NODE) {
        context = container.parentElement ? container.parentElement.textContent : '';
    } else {
        context = container.textContent || '';
    }

    return {
        text: selectedText,
        title: document.title,
        content: document.body.innerText || document.body.textContent || '',
        url: window.location.href,
        context: context.substring(0, 500) // Limit context length
    };
}

// Add visual feedback when text is selected
document.addEventListener('mouseup', function() {
    const selection = window.getSelection();
    if (selection.toString().trim()) {
        // Add a subtle highlight to selected text
        const range = selection.getRangeAt(0);
        const span = document.createElement('span');
        span.style.backgroundColor = 'rgba(37, 99, 235, 0.2)';
        span.style.borderRadius = '2px';
        span.style.padding = '1px 2px';
        
        try {
            range.surroundContents(span);
            // Remove highlight after a short delay
            setTimeout(() => {
                if (span.parentNode) {
                    span.parentNode.replaceChild(document.createTextNode(span.textContent), span);
                }
            }, 1000);
        } catch (e) {
            // If we can't surround the selection, just continue
        }
    }
});

// Add keyboard shortcut support (Ctrl+Shift+S)
document.addEventListener('keydown', function(e) {
    if (e.ctrlKey && e.shiftKey && e.key === 'S') {
        e.preventDefault();
        const selection = getSelection();
        if (selection.text) {
            // Send message to background script to save selection
            chrome.runtime.sendMessage({
                action: "saveHighlight",
                data: selection
            }, (response) => {
                if (response && response.success) {
                    showNotification('Selection saved to ZgrWise!');
                } else {
                    showNotification('Failed to save selection', 'error');
                }
            });
        } else {
            showNotification('No text selected');
        }
    }
});

function showNotification(message, type = 'success') {
    // Create notification element
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 12px 16px;
        border-radius: 6px;
        color: white;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-size: 14px;
        font-weight: 500;
        z-index: 10000;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        transition: all 0.3s ease;
        ${type === 'success' ? 'background: #10b981;' : 'background: #ef4444;'}
    `;
    
    notification.textContent = message;
    document.body.appendChild(notification);
    
    // Remove notification after 3 seconds
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}