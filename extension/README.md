# Auto-Doc Agent

AI-powered automatic documentation generator for VSCode — generates hover tooltips as you write code.

## Features

- 🤖 **AI-Generated Docs** — Automatically documents your functions using Gemini AI
- ⚡ **Instant Hover Tooltips** — See documentation by hovering over any function
- 🐍 **Multi-language** — Supports Python, TypeScript, and JavaScript
- 🔒 **Private Dashboard** — View all your project docs at [auto-doc-agent.onrender.com/dashboard](https://auto-doc-agent.onrender.com/dashboard)
- 🔄 **Always Up-to-date** — Docs update automatically as you write code

## Setup

### Step 1 — Install the Extension
Install **Auto-Doc Agent** from the VS Code Marketplace.

### Step 2 — Get Your API Key
1. Go to 👉 [auto-doc-agent.onrender.com](https://auto-doc-agent.onrender.com)
2. Register or Login with your email
3. Copy your API key (starts with `autodoc_...`)

### Step 3 — Add to VS Code Settings
1. Press `Ctrl+Shift+P` → type **"Open User Settings (JSON)"**
2. Add the following:

```json
{
  "autoDocAgent.apiUrl": "https://auto-doc-agent.onrender.com",
  "autoDocAgent.apiKey": "autodoc_your_key_here"
}
```

### Step 4 — Reload VS Code
Press `Ctrl+Shift+P` → **"Reload Window"**

You should see **"Auto-Doc Agent is active."** at the bottom.

### Step 5 — Start Writing Code!
Open any `.py`, `.ts`, or `.js` file and write a function. After a few seconds, hover over the function name to see AI-generated documentation.

## Viewing Your Documentation

Visit your private dashboard to browse all documented functions:

👉 [auto-doc-agent.onrender.com/dashboard](https://auto-doc-agent.onrender.com/dashboard)

- Projects are organized by your workspace folder name
- Each file and function is listed in the sidebar
- Documentation updates automatically as you code

## Settings

| Setting | Default | Description |
|---|---|---|
| `autoDocAgent.apiUrl` | `https://auto-doc-agent.onrender.com` | Backend API URL |
| `autoDocAgent.apiKey` | `""` | Your API key from the website |
| `autoDocAgent.enabled` | `true` | Enable/disable auto documentation |
| `autoDocAgent.debounceMs` | `3000` | Milliseconds to wait after typing stops |


## Support

- 🐛 Issues: [GitHub Issues](https://github.com/JohnyJames9496/auto-doc-agent/issues)
- 📖 Docs: [auto-doc-agent.onrender.com](https://auto-doc-agent.onrender.com)