# Streamlit Cloud Deployment Checklist

## Before Deploying

- [ ] All dependencies are in `requirements.txt`
- [ ] `packages.txt` exists with `build-essential`
- [ ] API keys are NOT in `.env` file (only local)
- [ ] `.gitignore` includes `.streamlit/secrets.toml`
- [ ] Test locally with `streamlit run main.py`

## GitHub Setup

- [ ] Code pushed to GitHub repository
- [ ] No API keys or secrets in commits
- [ ] `.env` file is in `.gitignore`
- [ ] Latest changes committed and pushed

## Streamlit Cloud Configuration

- [ ] App created on Streamlit Cloud
- [ ] Repository connected
- [ ] Main file set to `main.py`
- [ ] Python version is 3.9+ (automatic)

## Secrets Configuration

- [ ] Go to Settings → Secrets in Streamlit Cloud
- [ ] Add `GROQ_API_KEY` with your actual key
- [ ] Add `GEMINI_API_KEY` if using Gemini models
- [ ] Secrets saved successfully

## Post-Deployment

- [ ] App loads without errors
- [ ] API key validation passes (no warning message)
- [ ] Can upload documents
- [ ] Can ask questions and get responses
- [ ] Check logs for any warnings

## Troubleshooting

### ModuleNotFoundError
- Ensure all packages are in `requirements.txt`
- Check that `packages.txt` contains `build-essential`
- Redeploy after adding missing packages

### API Key Errors
- Verify secrets are added in Streamlit Cloud dashboard
- Check secret names match exactly (case-sensitive)
- Restart the app from the dashboard

### Build Failures
- Check build logs in Streamlit Cloud
- Ensure `packages.txt` is in root directory
- Try clearing cache and redeploying

## Useful Commands

```bash
# Test locally
streamlit run main.py

# Check installed packages
pip list

# Generate requirements.txt
pip freeze > requirements.txt

# Check git status
git status

# Push to GitHub
git add .
git commit -m "Update deployment files"
git push
```

## Files Required for Deployment

✅ `main.py` - Main application file
✅ `rag_setup.py` - Vector store builder
✅ `rag_tool.py` - RAG search tool
✅ `requirements.txt` - Python dependencies
✅ `packages.txt` - System dependencies
✅ `.gitignore` - Ignore sensitive files
✅ `.streamlit/secrets.toml.template` - Template for secrets
