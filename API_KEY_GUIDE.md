# API Key Configuration Guide

## Overview
The Smart Book Q&A Crew app now includes a user-friendly API key input section in the sidebar, making it easy to configure your GROQ API key directly in the web interface.

## How to Use the API Key Input

### Step 1: Get Your GROQ API Key
1. Visit [https://console.groq.com/keys](https://console.groq.com/keys)
2. Sign up or log in to your account
3. Click "Create API Key"
4. Copy your API key (it starts with `gsk_`)

### Step 2: Enter API Key in the App
1. Open the Streamlit app
2. Look at the **sidebar on the left**
3. Find the **"🔑 API Key Configuration"** section
4. Paste your GROQ API key in the text input field
5. Click **"💾 Save & Use"** button

### Step 3: Start Using the App
- The app will automatically refresh with your API key configured
- You can now upload documents and ask questions!

## Features

### 🔒 Security
- Your API key is stored only in the browser session
- It's NOT saved to any file or database
- The key is cleared when you close the browser tab
- The input field is masked (shows dots instead of actual characters)

### 💾 Save & Use Button
- Validates that you've entered a key
- Sets the key in the environment
- Automatically refreshes the app
- Shows a success message

### 🗑️ Clear Button
- Removes the API key from the session
- Clears it from the environment
- Allows you to enter a different key

### ✅ Status Indicator
- Shows "✅ API key configured from environment/secrets" if detected automatically
- Shows instructions if no key is configured
- Prevents app usage until a key is provided

## Different Deployment Scenarios

### Local Development
You have three options:

**Option 1: Use the Sidebar Input (Easiest)**
- Just paste your key in the sidebar
- No need to create any files

**Option 2: Use .env File**
```bash
# Create a .env file in the project root
GROQ_API_KEY=gsk_your_api_key_here
```
The app will detect this automatically.

**Option 3: Set Environment Variable**
```bash
# Windows PowerShell
$env:GROQ_API_KEY="gsk_your_api_key_here"

# Linux/Mac
export GROQ_API_KEY="gsk_your_api_key_here"
```

### Streamlit Cloud Deployment
For production deployment on Streamlit Cloud:

1. **Don't use the sidebar input** (it won't persist across sessions)
2. Go to your app dashboard on Streamlit Cloud
3. Click **Settings → Secrets**
4. Add your API key:
```toml
GROQ_API_KEY = "gsk_your_actual_key_here"
```
5. The app will automatically detect it

## Troubleshooting

### "Please configure your API key" Warning
**Problem**: The app shows a warning and won't let you proceed.

**Solution**:
1. Check the sidebar for the API key configuration section
2. Enter your GROQ API key
3. Click "Save & Use"

### API Key Not Working
**Problem**: You entered a key but still get errors.

**Solutions**:
1. Verify the key is correct (starts with `gsk_`)
2. Check that your GROQ account is active
3. Try clearing and re-entering the key
4. Check the browser console for error messages

### Key Lost After Refresh
**Problem**: You have to re-enter the key every time.

**Explanation**: This is by design for security. The key is only stored in the session.

**Solutions**:
- For local use: Create a `.env` file (see above)
- For Streamlit Cloud: Use the Secrets settings

### Can't See the Sidebar
**Problem**: The sidebar is collapsed.

**Solution**: Click the hamburger menu (☰) in the top-left corner to expand it.

## Best Practices

### For Development
- Use the sidebar input for quick testing
- Create a `.env` file for regular use
- Never commit `.env` to version control

### For Production
- Always use Streamlit Cloud Secrets
- Never hardcode API keys in the code
- Rotate your API keys periodically

### Security Tips
- Never share your API key publicly
- Don't commit API keys to GitHub
- Use different keys for development and production
- Monitor your API usage at console.groq.com

## Getting Help

If you encounter issues:
1. Check the [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) for deployment steps
2. Review the [DEPLOYMENT_FIX_SUMMARY.md](DEPLOYMENT_FIX_SUMMARY.md) for technical details
3. Visit [GROQ Documentation](https://console.groq.com/docs) for API key help
4. Check the app logs for error messages

## Example Workflow

```
1. Open app → http://localhost:8501
2. See warning: "Please configure your API key"
3. Expand sidebar (if needed)
4. Go to https://console.groq.com/keys
5. Copy your API key
6. Paste into sidebar input
7. Click "Save & Use"
8. App refreshes automatically
9. Upload documents in "Knowledge Base" tab
10. Ask questions in "Chat" tab
```

That's it! You're ready to use the Smart Book Q&A Crew with your own API key.
