#!/bin/bash

echo "🚀 Uploading Automated Agent Paper Bot to GitHub"
echo "================================================"

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed"
    echo "Please install Git first:"
    echo "  macOS: brew install git"
    echo "  Or download from https://git-scm.com/"
    exit 1
fi

echo "✅ Git is available"

# Initialize git repository if not already initialized
if [ ! -d ".git" ]; then
    echo "📁 Initializing Git repository..."
    git init
else
    echo "✅ Git repository already exists"
fi

# Add all files
echo "📦 Adding files to Git..."
git add .

# Create initial commit
echo "💾 Creating initial commit..."
git commit -m "Initial commit: Automated Agent Paper Bot

- Complete paper crawling and analysis system
- AI-powered filtering using Groq LLM
- Cross-platform automation (Windows/macOS)
- Twitter integration for automatic posting
- PostgreSQL database for paper storage
- Comprehensive deployment scripts"

echo "✅ Initial commit created"

echo ""
echo "🔗 Next steps:"
echo "1. Create a new repository on GitHub"
echo "2. Copy the repository URL (e.g., https://github.com/username/automated-agent-paper-bot.git)"
echo "3. Run the following commands:"
echo ""
echo "   git branch -M main"
echo "   git remote add origin YOUR_REPOSITORY_URL"
echo "   git push -u origin main"
echo ""
echo "Replace YOUR_REPOSITORY_URL with your actual GitHub repository URL"