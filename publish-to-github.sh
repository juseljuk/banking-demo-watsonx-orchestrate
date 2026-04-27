#!/bin/bash

# Banking Demo - Publish to GitHub Script
# This script helps you publish the banking demo to a new GitHub repository

set -e

echo "=========================================="
echo "Banking Demo - GitHub Publication Helper"
echo "=========================================="
echo ""

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "❌ Error: Git repository not initialized"
    echo "Run: git init"
    exit 1
fi

# Get repository details
echo "📝 Repository Setup"
echo "-------------------"
echo ""
read -p "Enter your GitHub username: " GITHUB_USERNAME
read -p "Enter repository name (default: banking-demo-watsonx-orchestrate): " REPO_NAME
REPO_NAME=${REPO_NAME:-banking-demo-watsonx-orchestrate}

echo ""
echo "Repository will be created at:"
echo "https://github.com/$GITHUB_USERNAME/$REPO_NAME"
echo ""
read -p "Is this correct? (y/n): " CONFIRM

if [ "$CONFIRM" != "y" ]; then
    echo "Aborted."
    exit 0
fi

echo ""
echo "🔍 Checking for sensitive data..."
echo "-----------------------------------"

# Check for .env files
if [ -f ".env" ]; then
    echo "⚠️  WARNING: .env file found!"
    echo "This file should NOT be committed."
    read -p "Remove .env from git? (y/n): " REMOVE_ENV
    if [ "$REMOVE_ENV" = "y" ]; then
        git rm --cached .env 2>/dev/null || true
        echo "✓ .env removed from git"
    fi
fi

# Check for session files with real data
if [ -f "data/sessions.json" ]; then
    echo "ℹ️  Session file found (should be empty for demo)"
fi

echo "✓ Security check complete"
echo ""

echo "📦 Preparing repository..."
echo "-----------------------------------"

# Add all files
git add .

# Show what will be committed
echo ""
echo "Files to be committed:"
git status --short

echo ""
read -p "Proceed with commit? (y/n): " PROCEED

if [ "$PROCEED" != "y" ]; then
    echo "Aborted."
    exit 0
fi

# Create commit
git commit -m "Initial commit: Banking demo with multi-agent orchestration, guardrails, and workflows

Features:
- 5 specialized agents (orchestrator, customer service, fraud, loans, compliance)
- 4 production guardrails (PII protection, transaction limits, lending compliance, fraud detection)
- 3 MCP servers with 25 tools
- Agentic workflow for loan approval
- UK banking compliance (FCA, GDPR, Consumer Credit Act)
- Comprehensive test suite
- Complete documentation"

echo "✓ Commit created"
echo ""

echo "🔗 Connecting to GitHub..."
echo "-----------------------------------"

# Check if remote already exists
if git remote | grep -q "origin"; then
    echo "ℹ️  Remote 'origin' already exists"
    CURRENT_REMOTE=$(git remote get-url origin)
    echo "Current remote: $CURRENT_REMOTE"
    read -p "Update remote URL? (y/n): " UPDATE_REMOTE
    if [ "$UPDATE_REMOTE" = "y" ]; then
        git remote set-url origin "https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
        echo "✓ Remote URL updated"
    fi
else
    git remote add origin "https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
    echo "✓ Remote added"
fi

echo ""
echo "📤 Ready to push to GitHub"
echo "-----------------------------------"
echo ""
echo "⚠️  IMPORTANT: Before pushing, you must:"
echo "1. Create the repository on GitHub:"
echo "   https://github.com/new"
echo "2. Repository name: $REPO_NAME"
echo "3. DO NOT initialize with README, .gitignore, or license"
echo ""
echo "OR use GitHub CLI:"
echo "   gh repo create $REPO_NAME --public"
echo ""
read -p "Have you created the repository on GitHub? (y/n): " REPO_CREATED

if [ "$REPO_CREATED" != "y" ]; then
    echo ""
    echo "Please create the repository first, then run:"
    echo "  git push -u origin main"
    echo ""
    exit 0
fi

echo ""
echo "Pushing to GitHub..."

# Rename branch to main if needed
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    git branch -M main
    echo "✓ Branch renamed to main"
fi

# Push to GitHub
if git push -u origin main; then
    echo ""
    echo "=========================================="
    echo "✅ Successfully published to GitHub!"
    echo "=========================================="
    echo ""
    echo "Repository URL:"
    echo "https://github.com/$GITHUB_USERNAME/$REPO_NAME"
    echo ""
    echo "Next steps:"
    echo "1. Add repository topics (watsonx-orchestrate, ai-agents, banking, etc.)"
    echo "2. Add a license file (MIT, Apache 2.0, etc.)"
    echo "3. Create a release: git tag -a v1.0.0 -m 'Initial release'"
    echo "4. Share with your team!"
    echo ""
else
    echo ""
    echo "❌ Push failed"
    echo ""
    echo "Common issues:"
    echo "1. Repository doesn't exist on GitHub"
    echo "2. Authentication failed (set up SSH keys or use personal access token)"
    echo "3. Branch protection rules"
    echo ""
    echo "Try manually:"
    echo "  git push -u origin main"
    echo ""
    exit 1
fi

# Made with Bob
