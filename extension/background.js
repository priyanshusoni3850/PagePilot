chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.message === 'get_current_url') {
      chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        const currentTab = tabs[0];
        sendResponse({ url: currentTab.url });
      });
      return true;  // Will respond asynchronously.
    }
  });
  