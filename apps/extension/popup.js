// Popup script for ZgrWise Clipper

document.addEventListener('DOMContentLoaded', function() {
    const savePageBtn = document.getElementById('savePage');
    const saveSelectionBtn = document.getElementById('saveSelection');
    const openSettingsBtn = document.getElementById('openSettings');
    const statusDiv = document.getElementById('status');

    // Check API settings on load
    checkSettings();

    savePageBtn.addEventListener('click', function() {
        saveCurrentPage();
    });

    saveSelectionBtn.addEventListener('click', function() {
        saveSelection();
    });

    openSettingsBtn.addEventListener('click', function() {
        chrome.runtime.openOptionsPage();
    });

    async function checkSettings() {
        try {
            const settings = await chrome.storage.sync.get(['apiBase', 'apiKey']);
            if (!settings.apiBase || !settings.apiKey) {
                showStatus('Please configure API settings', 'error');
                return false;
            }
            return true;
        } catch (error) {
            showStatus('Error checking settings', 'error');
            return false;
        }
    }

    async function saveCurrentPage() {
        if (!(await checkSettings())) return;

        try {
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            
            // Get page content
            const results = await chrome.scripting.executeScript({
                target: { tabId: tab.id },
                function: getPageContent
            });

            const pageData = results[0].result;
            
            // Save to ZgrWise
            const success = await saveToZgrWise({
                type: 'web',
                url: tab.url,
                title: pageData.title,
                content: pageData.content,
                origin: new URL(tab.url).hostname
            });

            if (success) {
                showStatus('Page saved successfully!', 'success');
            } else {
                showStatus('Failed to save page', 'error');
            }
        } catch (error) {
            console.error('Error saving page:', error);
            showStatus('Error saving page', 'error');
        }
    }

    async function saveSelection() {
        if (!(await checkSettings())) return;

        try {
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            
            // Get selection
            const results = await chrome.scripting.executeScript({
                target: { tabId: tab.id },
                function: getSelection
            });

            const selection = results[0].result;
            
            if (!selection.text) {
                showStatus('No text selected', 'error');
                return;
            }

            // Save to ZgrWise
            const success = await saveToZgrWise({
                type: 'web',
                url: tab.url,
                title: selection.title,
                content: selection.content,
                selection: selection.text,
                origin: new URL(tab.url).hostname
            });

            if (success) {
                showStatus('Selection saved successfully!', 'success');
            } else {
                showStatus('Failed to save selection', 'error');
            }
        } catch (error) {
            console.error('Error saving selection:', error);
            showStatus('Error saving selection', 'error');
        }
    }

    async function saveToZgrWise(data) {
        try {
            const settings = await chrome.storage.sync.get(['apiBase', 'apiKey']);
            
            // First, create or get source
            const sourceResponse = await fetch(`${settings.apiBase}/api/sources`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-API-Key': settings.apiKey
                },
                body: JSON.stringify({
                    type: 'web',
                    url: data.url,
                    origin: data.origin,
                    title: data.title,
                    raw: data.content
                })
            });

            if (!sourceResponse.ok) {
                throw new Error('Failed to create source');
            }

            const source = await sourceResponse.json();

            // If there's a selection, create highlight
            if (data.selection) {
                const highlightResponse = await fetch(`${settings.apiBase}/api/highlights`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-API-Key': settings.apiKey
                    },
                    body: JSON.stringify({
                        source_id: source.id,
                        text: data.selection,
                        note: '',
                        location: ''
                    })
                });

                if (!highlightResponse.ok) {
                    throw new Error('Failed to create highlight');
                }
            }

            return true;
        } catch (error) {
            console.error('Error saving to ZgrWise:', error);
            return false;
        }
    }

    function showStatus(message, type) {
        statusDiv.textContent = message;
        statusDiv.className = `status ${type}`;
        statusDiv.style.display = 'block';
        
        setTimeout(() => {
            statusDiv.style.display = 'none';
        }, 3000);
    }
});

// Functions to be executed in the page context
function getPageContent() {
    return {
        title: document.title,
        content: document.body.innerText || document.body.textContent || ''
    };
}

function getSelection() {
    const selection = window.getSelection();
    return {
        text: selection.toString(),
        title: document.title,
        content: document.body.innerText || document.body.textContent || ''
    };
}