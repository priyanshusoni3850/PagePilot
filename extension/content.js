function sendQueryToBackend(query, url) {
    console.log(url)
    
    console.log(query)
    fetch('http://localhost:5000/generate_response', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query, url }),
    })
      .then(response => response.json())
      .then(data => {
        const botResponse = data.response || 'No response';
        displayMessage('bot', botResponse);
        storeMessage('bot', botResponse);
      })
      .catch(error => {
        console.error('Error:', error);
        const errorMessage = 'Error occurred. Please try again.';
        displayMessage('bot', errorMessage);
        storeMessage('bot', errorMessage);
      });
}
  
  chrome.runtime.sendMessage({ message: 'get_current_url' }, (response) => {
    const currentUrl = response.url;
    
    document.getElementById('sendButton').addEventListener('click', () => {
      const userQuery = document.getElementById('userQuery').value;
      displayMessage('user', userQuery);
      storeMessage('user', userQuery);
      console.log(userQuery)
      console.log(currentUrl)
      sendQueryToBackend(userQuery, currentUrl);
    });
  
    document.getElementById('newSessionButton').addEventListener('click', () => {
      document.getElementById('chatWindow').innerHTML = '';
      displayMessage('bot', 'Welcome! How can I assist you today?');
      chrome.storage.local.remove('chatMessages');
      storeMessage('bot', 'Welcome! How can I assist you today?');
    });
  
    document.getElementById('closeButton').addEventListener('click', () => {
      window.close();
    });
  
    loadMessages();
  });
  
  function displayMessage(sender, message) {
    const chatWindow = document.getElementById('chatWindow');
    const messageDiv = document.createElement('div');
    messageDiv.className = `${sender}-message`;
    messageDiv.innerText = message;
    chatWindow.appendChild(messageDiv);
    chatWindow.scrollTop = chatWindow.scrollHeight; // Scroll to the bottom
  }
  
  function storeMessage(sender, message) {
    chrome.storage.local.get({ chatMessages: [] }, (result) => {
      const chatMessages = result.chatMessages;
      chatMessages.push({ sender, message });
      chrome.storage.local.set({ chatMessages });
    });
  }
  
  function loadMessages() {
    chrome.storage.local.get({ chatMessages: [] }, (result) => {
      const chatMessages = result.chatMessages;
      chatMessages.forEach(({ sender, message }) => {
        displayMessage(sender, message);
      });
    });
  }
  