// Options page script for ZgrWise Clipper

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('settingsForm');
    const testBtn = document.getElementById('testConnection');
    const statusDiv = document.getElementById('status');
    const apiBaseInput = document.getElementById('apiBase');
    const apiKeyInput = document.getElementById('apiKey');

    // Load saved settings
    loadSettings();

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        saveSettings();
    });

    testBtn.addEventListener('click', function() {
        testConnection();
    });

    async function loadSettings() {
        try {
            const settings = await chrome.storage.sync.get(['apiBase', 'apiKey']);
            if (settings.apiBase) {
                apiBaseInput.value = settings.apiBase;
            }
            if (settings.apiKey) {
                apiKeyInput.value = settings.apiKey;
            }
        } catch (error) {
            console.error('Error loading settings:', error);
        }
    }

    async function saveSettings() {
        try {
            const settings = {
                apiBase: apiBaseInput.value.trim(),
                apiKey: apiKeyInput.value.trim()
            };

            await chrome.storage.sync.set(settings);
            showStatus('Settings saved successfully!', 'success');
        } catch (error) {
            console.error('Error saving settings:', error);
            showStatus('Error saving settings', 'error');
        }
    }

    async function testConnection() {
        const apiBase = apiBaseInput.value.trim();
        const apiKey = apiKeyInput.value.trim();

        if (!apiBase || !apiKey) {
            showStatus('Please fill in both API Base URL and API Key', 'error');
            return;
        }

        try {
            showStatus('Testing connection...', 'success');
            
            const response = await fetch(`${apiBase}/health`, {
                method: 'GET',
                headers: {
                    'X-API-Key': apiKey
                }
            });

            if (response.ok) {
                showStatus('Connection successful! API is responding.', 'success');
            } else {
                showStatus(`Connection failed: ${response.status} ${response.statusText}`, 'error');
            }
        } catch (error) {
            console.error('Connection test error:', error);
            showStatus(`Connection failed: ${error.message}`, 'error');
        }
    }

    function showStatus(message, type) {
        statusDiv.textContent = message;
        statusDiv.className = `status ${type}`;
        statusDiv.style.display = 'block';
        
        setTimeout(() => {
            statusDiv.style.display = 'none';
        }, 5000);
    }
});