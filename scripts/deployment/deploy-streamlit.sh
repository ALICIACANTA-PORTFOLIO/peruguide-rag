#!/bin/bash
# Deploy Streamlit app to Streamlit Cloud

set -e

echo "🚀 Deploying PeruGuide Streamlit to Streamlit Cloud..."

# Check if git repo is clean
if [[ -n $(git status -s) ]]; then
    echo "⚠️  You have uncommitted changes. Please commit them first."
    git status -s
    exit 1
fi

# Push to GitHub
echo "📤 Pushing to GitHub..."
git push origin main || git push origin master

echo "✅ Code pushed to GitHub!"
echo ""
echo "📋 Next steps:"
echo "1. Go to https://share.streamlit.io"
echo "2. Click 'New app'"
echo "3. Select your repository: $(git remote get-url origin)"
echo "4. Main file path: app/streamlit_app.py"
echo "5. Add secrets in Advanced settings:"
echo "   API_URL = \"https://your-api-url.com\""
echo ""
echo "🌐 Your app will be available at:"
echo "   https://your-app-name.streamlit.app"
