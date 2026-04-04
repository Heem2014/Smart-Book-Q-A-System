# Streamlit Cloud Deployment Troubleshooting

## Common Issues and Solutions

### Issue 1: ModuleNotFoundError for python-dotenv or other packages

**Error**: `ModuleNotFoundError: This app has encountered an error... from dotenv import load_dotenv`

**Solutions**:

1. **Check requirements.txt format**
   - ✅ Use simple format (one package per line)
   - ❌ Avoid inline comments after package names
   - Example of correct format:
     ```
     streamlit
     python-dotenv
     crewai
     ```

2. **Verify packages.txt exists**
   - Must contain: `build-essential`
   - Required for compiling CrewAI dependencies

3. **Clear cache and redeploy**
   - Go to Streamlit Cloud dashboard
   - Click "Manage app" → "Advanced settings"
   - Click "Clear cache and redeploy"

4. **Check build logs**
   - Click "Manage app" in lower right
   - Review the build logs for installation errors
   - Look for any packages that failed to install

### Issue 2: API Key Not Found

**Error**: CrewAI/LiteLLM fallback error or API key missing

**Solutions**:

1. **Verify secrets are set**
   - Go to Settings → Secrets
   - Ensure `GROQ_API_KEY` is set exactly (case-sensitive)
   - Format: `GROQ_API_KEY = "your_key_here"`

2. **Check secret name spelling**
   - Must be exactly `GROQ_API_KEY` (all caps, underscore)
   - No extra spaces before or after the equals sign

3. **Restart the app**
   - After adding secrets, restart from the dashboard
   - Sometimes the app needs a fresh start to pick up secrets

### Issue 3: Build Fails or Times Out

**Solutions**:

1. **Check packages.txt**
   - Ensure it's in the root directory
   - Contains only: `build-essential`

2. **Simplify requirements**
   - Remove unnecessary packages
   - Use specific versions if needed: `package==1.2.3`

3. **Build time optimization**
   - First build takes 5-10 minutes (normal)
   - Subsequent builds are faster
   - Be patient during initial deployment

### Issue 4: App Runs but Can't Find Vector Store

**Solutions**:

1. **Upload documents first**
   - Use the Knowledge Base tab
   - Upload PDF or TXT files
   - Click "Build Vector Store"

2. **Check chroma_db folder**
   - Should be created automatically
   - Don't add to .gitignore if you want to persist it
   - Note: Streamlit Cloud resets on each deploy

### Issue 5: Import Errors for Custom Modules

**Error**: `ModuleNotFoundError: No module named 'rag_tool'`

**Solutions**:

1. **Verify file structure**
   ```
   ├── main.py
   ├── rag_setup.py
   ├── rag_tool.py
   ├── requirements.txt
   └── packages.txt
   ```

2. **Check file names**
   - Must match exactly (case-sensitive on Linux)
   - `rag_tool.py` not `Rag_Tool.py`

3. **Ensure all files are committed**
   ```bash
   git status
   git add .
   git commit -m "Add all files"
   git push
   ```

## Debugging Checklist

Before deploying to Streamlit Cloud:

- [ ] All Python files are committed to GitHub
- [ ] requirements.txt has clean format (no inline comments)
- [ ] packages.txt exists with `build-essential`
- [ ] .gitignore doesn't exclude necessary files
- [ ] Test locally first: `streamlit run main.py`
- [ ] API keys work locally with .env file

After deploying:

- [ ] Check build logs for errors
- [ ] Verify all packages installed successfully
- [ ] Add GROQ_API_KEY to Secrets
- [ ] Restart the app after adding secrets
- [ ] Test basic functionality

## Getting Build Logs

1. Go to your app on Streamlit Cloud
2. Click "Manage app" (lower right corner)
3. Click "Logs" tab
4. Review both "Build logs" and "App logs"
5. Look for red error messages

## Clearing Cache

If changes aren't showing up:

1. Go to "Manage app"
2. Click "Advanced settings"
3. Click "Clear cache and redeploy"
4. Wait for rebuild (5-10 minutes)

## Contact Support

If issues persist:
- Streamlit Community: https://discuss.streamlit.io/
- Include your build logs when asking for help
- Share your repository URL
- Describe what you've tried already

## Quick Fix Commands

```bash
# Update requirements.txt format
# (Remove inline comments, one package per line)

# Commit and push
git add .
git commit -m "Fix deployment issues"
git push origin main

# On Streamlit Cloud
# 1. Clear cache and redeploy
# 2. Check build logs
# 3. Verify secrets are set
```

## Example Working Configuration

**requirements.txt**:
```
streamlit
python-dotenv
crewai
langchain
langchain-chroma
langchain-huggingface
langchain-community
chromadb
pypdf
```

**packages.txt**:
```
build-essential
```

**.gitignore**:
```
.env
.streamlit/secrets.toml
chroma_db/
__pycache__/
*.pyc
```

This configuration has been tested and works on Streamlit Cloud.
