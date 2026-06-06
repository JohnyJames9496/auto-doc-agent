sed -i 's/Paste your JWT token here.../Paste your API key here.../g' ~/auto-doc-agent/backend/app/templates/dashboard.html---
sidebar_position: 1
---

# Setup Guide

## 1. Install the Extension
Install from the [VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=JohnyJames.auto-doc-agent)

## 2. Register
Go to [auto-doc-agent.onrender.com](https://auto-doc-agent.onrender.com) and register.

## 3. Configure VS Code
Press `Ctrl+Shift+P` → Open User Settings JSON and add:

```json
{
  "autoDocAgent.apiUrl": "https://auto-doc-agent.onrender.com",
  "autoDocAgent.apiKey": "autodoc_your_key_here"
}
```

## 4. Start Coding!
Open any Python, TypeScript or JavaScript file and hover over any function!
