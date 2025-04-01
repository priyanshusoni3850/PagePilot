// popup.js
document.addEventListener('DOMContentLoaded', async function () {
  const messagesDiv = document.getElementById('messages');
  const queryInput = document.getElementById('query');
  const sendButton = document.getElementById('send');

  async function sendUrlToBackend() {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      chrome.runtime.sendMessage({ type: "init", url: tab.url }, function (response) {
          messagesDiv.innerHTML += `<div class='message bot'>${response.message}</div>`;
      });
  }

  // Send initial URL to backend
  sendUrlToBackend();

  sendButton.addEventListener('click', sendQuery);

  function sendQuery() {
      const query = queryInput.value.trim();
      if (!query) return;

      messagesDiv.innerHTML += `<div class='message user'>You: ${query}</div>`;
      updateStorage(messagesDiv.innerHTML);

      queryInput.value = '';

      chrome.runtime.sendMessage({ type: "query", query }, function (response) {
          messagesDiv.innerHTML += `<div class='message bot'>Bot: ${response.message}</div>`;
          updateStorage(messagesDiv.innerHTML);
          askUserSatisfaction(query); // Ask for satisfaction after bot response
      });
  }

  document.getElementById('new-session').addEventListener('click', async function () {
      chrome.storage.local.set({ 'chatHistory': '' }, function () {
          messagesDiv.innerHTML = '';
          greetUser(messagesDiv);
      });
      sendUrlToBackend();
  });

  chrome.storage.local.get(['chatHistory'], function (result) {
      if (result.chatHistory) {
          messagesDiv.innerHTML = result.chatHistory;
      } else {
          greetUser(messagesDiv);
      }
  });

  // Ask if the user is satisfied with the response
  function askUserSatisfaction(query) {
      removeExistingPrompt('satisfaction'); // Clear any existing satisfaction prompt

      const satisfactionDiv = document.createElement('div');
      satisfactionDiv.className = 'satisfaction';

      satisfactionDiv.innerHTML = `
          <div>Are you satisfied with the response?</div>
          <button id="satisfaction-yes">Yes</button>
          <button id="satisfaction-no">No</button>
      `;

      messagesDiv.appendChild(satisfactionDiv);

      document.getElementById('satisfaction-yes').addEventListener('click', function () {
          messagesDiv.innerHTML += `<div class='message bot'>Okay, feel free to ask more questions!</div>`;
          updateStorage(messagesDiv.innerHTML);
          satisfactionDiv.remove(); // Remove the prompt after response
      });

      document.getElementById('satisfaction-no').addEventListener('click', function () {
          askInternetSearch(query); // Ask if the user wants to search the internet
          satisfactionDiv.remove(); // Remove the prompt after response
      });
  }

  // Ask if the user wants an internet search
  function askInternetSearch(query) {
      removeExistingPrompt('internet-search'); // Clear any existing internet search prompt

      const internetSearchDiv = document.createElement('div');
      internetSearchDiv.className = 'internet-search';

      internetSearchDiv.innerHTML = `
          <div>Would you like me to search the internet for more information on this topic?</div>
          <button id="internet-search-yes">Yes</button>
          <button id="internet-search-no">No</button>
      `;

      messagesDiv.appendChild(internetSearchDiv);

      document.getElementById('internet-search-yes').addEventListener('click', function () {
          chrome.runtime.sendMessage({ type: "search", query }, function (response) {
              messagesDiv.innerHTML += `<div class='message bot'>${response.message}</div>`;
              updateStorage(messagesDiv.innerHTML);
              askUserSatisfaction(query); // Ask satisfaction again after internet search
          });
          internetSearchDiv.remove(); // Remove the prompt after response
      });

      document.getElementById('internet-search-no').addEventListener('click', function () {
          messagesDiv.innerHTML += `<div class='message bot'>You can try our PDF option for more detailed information.</div>`;
          updateStorage(messagesDiv.innerHTML);
          internetSearchDiv.remove(); // Remove the prompt after response
      });
  }

  // Helper function to remove any existing prompt of a given type
  function removeExistingPrompt(className) {
      const existingPrompt = document.querySelector(`.${className}`);
      if (existingPrompt) {
          existingPrompt.remove(); // Remove any existing prompt
      }
  }

  // Helper functions
  function updateStorage(html) {
      chrome.storage.local.set({ 'chatHistory': html });
  }

  function greetUser(messagesDiv) {
      const greeting = "Hi, I'm PagePilot! How can I assist you today?";
      messagesDiv.innerHTML += `<div class='message bot'>${greeting}</div>`;
      updateStorage(messagesDiv.innerHTML);
  }
});
