// Background service worker for ZgrWise Clipper

// Create context menu on installation
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "saveSelection",
    title: "Save Selection to ZgrWise",
    contexts: ["selection"]
  });
});

// Handle context menu clicks
chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === "saveSelection") {
    // Send message to content script to get selection
    chrome.tabs.sendMessage(tab.id, {
      action: "getSelection"
    }, (response) => {
      if (response && response.text) {
        saveHighlight(response, (result) => {
          if (result.success) {
            // Show notification
            chrome.tabs.sendMessage(tab.id, {
              action: "showNotification",
              message: "Selection saved to ZgrWise!",
              type: "success"
            });
          } else {
            chrome.tabs.sendMessage(tab.id, {
              action: "showNotification",
              message: "Failed to save selection",
              type: "error"
            });
          }
        });
      }
    });
  }
});

// Listen for messages from content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "saveHighlight") {
    saveHighlight(request.data, sendResponse);
    return true; // Keep message channel open for async response
  }
});

async function saveHighlight(data, sendResponse) {
  try {
    // Get API settings from storage
    const settings = await chrome.storage.sync.get(['apiBase', 'apiKey']);
    
    if (!settings.apiBase || !settings.apiKey) {
      sendResponse({ success: false, error: "API settings not configured" });
      return;
    }

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

    // Then create highlight
    const highlightResponse = await fetch(`${settings.apiBase}/api/highlights`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': settings.apiKey
      },
      body: JSON.stringify({
        source_id: source.id,
        text: data.selection,
        note: data.note || '',
        location: data.location || ''
      })
    });

    if (!highlightResponse.ok) {
      throw new Error('Failed to create highlight');
    }

    sendResponse({ success: true, message: "Highlight saved successfully!" });
  } catch (error) {
    console.error('Error saving highlight:', error);
    sendResponse({ success: false, error: error.message });
  }
} 