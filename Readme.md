PagePilot
<p align="center">
  <img src="frontend\icon-128.png" alt="PagePilot Logo" width="200"/>
</p>
<p align="center">
  <b>Chat with web pages and news articles directly from your Chrome browser.</b>
</p>
📖 Overview
PagePilot is a Chrome extension that allows you to have interactive conversations with webpage content and news articles. Using advanced natural language processing, PagePilot can understand context, summarize content, answer questions, and provide insights based on the webpage you're viewing.
✨ Features

Contextual Chat: Engage in meaningful conversations about the content you're browsing
Article Summarization: Get quick summaries of lengthy news articles or blog posts
Question Answering: Ask specific questions about the content and receive relevant answers
Easy Activation: Simple one-click activation from any webpage
Persistent Context: PagePilot remembers the conversation context throughout your browsing session

🛠️ Installation
From Chrome Web Store
Coming soon
Manual Installation

Clone this repository:
Copygit clone https://github.com/priyanshusoni3850/PagePilot.git

Open Chrome and navigate to chrome://extensions/
Enable "Developer mode" in the top right corner
Click "Load unpacked" and select the frontend directory from the cloned repository

🚀 Getting Started
Setting up the Backend

Open the .ipynb file in Google Colab
Add your Hugging Face authentication token in the designated cell
Run all cells to start the backend server
Copy the ngrok tunnel URL that is generated

Connecting Frontend to Backend

Open config.js in the frontend directory
Replace the placeholder API URL with your ngrok tunnel URL:
javascriptCopyconst API_URL = "your-ngrok-url-here";

Save the file and reload the extension in Chrome

🧩 How It Works

Content Extraction: When activated, PagePilot extracts the relevant content from the current webpage
Processing: The extracted content is sent to the backend through the ngrok tunnel
AI Analysis: The backend processes the content using Hugging Face models
User Interaction: You can then chat with PagePilot about the webpage content

🧰 Tech Stack

Frontend: JavaScript, HTML, CSS, Chrome Extension API
Backend: Python, Colab notebook
AI: Hugging Face Transformers
Connectivity: ngrok for exposing local endpoints

⚙️ Configuration
Required Environment Variables
In your Colab notebook, you'll need to set:

NGROK_AUTH_TOKEN: Your ngrok authentication token
HUGGINGFACE_TOKEN: Your Hugging Face API token

🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

Fork the repository
Create your feature branch (git checkout -b feature/amazing-feature)
Commit your changes (git commit -m 'Add some amazing feature')
Push to the branch (git push origin feature/amazing-feature)
Open a Pull Request


📞 Contact
Priyanshu Soni - GitHub
Project Link: https://github.com/priyanshusoni3850/PagePilot