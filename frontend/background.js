// background.js
let initialized = false;
const BASE_URL = "https://5f19-34-16-186-250.ngrok-free.app";  // Replace with the latest Ngrok URL

chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
  if (request.type === "init" && !initialized) {
    initialized = true;

    fetch(`${BASE_URL}/process`, {
      method: "POST",
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url: request.url })
    })
    .then(response => response.json())
    .then(data => {
      sendResponse({ message: data.success ? "Initialization successful." : (data.error || "Initialization failed.") });
    })
    .catch(error => sendResponse({ message: "Error occurred during initialization." }));
  } else if (request.type === "query") {
    fetch(`${BASE_URL}/ask`, {
      method: "POST",
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ question: request.query })
    })
    .then(response => response.json())
    .then(data => sendResponse({ message: data.response }))
    .catch(error => sendResponse({ message: "Error occurred." }));
  } else if (request.type === "search") {
    // Perform Google Search and scrape data for further processing
    fetch(`${BASE_URL}/search`, {
      method: "POST",
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query: request.query })
    })
    .then(response => response.json())
    .then(data => {
      sendResponse({ message: data.success ? data.response : (data.error || "Failed to gather additional information.") });
    })
    .catch(error => sendResponse({ message: "Error occurred during Google search." }));
  }

  return true; // Keep the message channel open for async response
});
