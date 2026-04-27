# Publishing Banking Demo to GitHub - Step-by-Step Guide

## 📋 Prerequisites

- GitHub account
- Git installed locally
- GitHub CLI (`gh`) installed (optional but recommended)

## 🚀 Step-by-Step Instructions

### Step 1: Create GitHub Repository

**Option A: Using GitHub Web Interface**

1. Go to https://github.com/new
2. Repository name: `banking-demo-watsonx-orchestrate` (or your preferred name)
3. Description: "Banking AI Demo showcasing IBM watsonx Orchestrate capabilities"
4. Choose: **Public** or **Private**
5. **DO NOT** initialize with README, .gitignore, or license (we already have these)
6. Click "Create repository"

**Option B: Using GitHub CLI**

```bash
# Create public repository
gh repo create banking-demo-watsonx-orchestrate --public --description "Banking AI Demo showcasing IBM watsonx Orchestrate capabilities"

# OR create private repository
gh repo create banking-demo-watsonx-orchestrate --private --description "Banking AI Demo showcasing IBM watsonx Orchestrate capabilities"
```

### Step 2: Prepare Local Repository

The repository has already been initialized. Now add all files:

```bash
cd banking-demo

# Check status
git status

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Banking demo with multi-agent orchestration, guardrails, and workflows"
```

### Step 3: Connect to GitHub

Replace `YOUR_USERNAME` with your GitHub username:

```bash
# Add remote repository
git remote add origin https://github.com/YOUR_USERNAME/banking-demo-watsonx-orchestrate.git

# Verify remote
git remote -v
```

### Step 4: Push to GitHub

```bash
# Push to main branch
git push -u origin main

# If you get an error about 'master' vs 'main', rename the branch:
git branch -M main
git push -u origin main
```

### Step 5: Verify on GitHub

1. Go to your repository: `https://github.com/YOUR_USERNAME/banking-demo-watsonx-orchestrate`
2. Verify all files are present
3. Check that README.md displays correctly

## 📁 What Gets Published

### Core Files (✅ Included)
- ✅ All agent configurations (`agents/*.yaml`)
- ✅ All MCP servers (`toolkits/*.py`)
- ✅ All guardrail plugins (`plugins/*.py`)
- ✅ All test files (`tests/*.py`)
- ✅ All data files (`data/*.json`)
- ✅ All documentation (`*.md`)
- ✅ Deployment scripts (`import-all.sh`, `import-no-guardrails.sh`)
- ✅ Requirements file (`requirements.txt`)

### Excluded Files (❌ Not Included)
- ❌ Python cache (`__pycache__/`)
- ❌ Virtual environments (`.venv/`)
- ❌ IDE settings (`.vscode/`, `.idea/`)
- ❌ Environment variables (`.env`)
- ❌ Session data with sensitive info (`data/sessions.json`)

## 🔒 Security Considerations

### ✅ Safe to Publish
- Demo customer data (fictional)
- Demo PINs (1234, 5678, 9012)
- Sample transactions
- Agent configurations
- Guardrail logic
- Documentation

### ⚠️ DO NOT Publish
- Real API keys
- Real customer data
- Production credentials
- Actual session tokens
- `.env` files with secrets

## 📝 Repository Structure

```
banking-demo/
├── README.md                    # Main documentation
├── .gitignore                   # Git exclusions
├── requirements.txt             # Python dependencies
├── import-all.sh               # Deployment script
├── agents/                     # 5 agent configurations
├── toolkits/                   # 3 MCP servers
├── plugins/                    # 4 guardrail plugins
├── tools/                      # Agentic workflow
├── data/                       # Demo data (JSON)
├── tests/                      # Test suite
└── docs/                       # Planning documents
```

## 🎯 Post-Publication Steps

### 1. Add Repository Topics (GitHub Web)

Go to your repository → Settings → Topics, add:
- `watsonx-orchestrate`
- `ai-agents`
- `banking`
- `fintech`
- `guardrails`
- `mcp-servers`
- `python`
- `ibm-watsonx`

### 2. Create Release (Optional)

```bash
# Tag the initial release
git tag -a v1.0.0 -m "Initial release: Banking demo with guardrails"
git push origin v1.0.0

# Or use GitHub CLI
gh release create v1.0.0 --title "v1.0.0 - Initial Release" --notes "Complete banking demo with multi-agent orchestration, security guardrails, and agentic workflows"
```

### 3. Add License (Recommended)

Create a `LICENSE` file. For open source, consider:
- MIT License (permissive)
- Apache 2.0 (permissive with patent grant)
- GPL v3 (copyleft)

Example MIT License:
```bash
cat > LICENSE << 'EOF'
MIT License

Copyright (c) 2026 [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF

git add LICENSE
git commit -m "Add MIT License"
git push
```

### 4. Update README with Repository URL

After publishing, update any documentation that references the repository:

```bash
# Update README.md with actual clone URL
# Replace placeholder URLs with your actual repository URL
```

## 🔄 Future Updates

To push updates to GitHub:

```bash
# Make your changes
git add .
git commit -m "Description of changes"
git push
```

## 🆘 Troubleshooting

### Issue: "Permission denied (publickey)"

**Solution**: Set up SSH keys or use HTTPS with personal access token

```bash
# Use HTTPS instead
git remote set-url origin https://github.com/YOUR_USERNAME/banking-demo-watsonx-orchestrate.git
```

### Issue: "Repository not found"

**Solution**: Verify repository name and your access

```bash
# Check remote URL
git remote -v

# Update if needed
git remote set-url origin https://github.com/YOUR_USERNAME/CORRECT-REPO-NAME.git
```

### Issue: "Failed to push some refs"

**Solution**: Pull first, then push

```bash
git pull origin main --rebase
git push origin main
```

## 📞 Support

For issues with:
- **Git/GitHub**: Check GitHub documentation
- **watsonx Orchestrate**: See project documentation
- **Demo Setup**: Review IMPLEMENTATION.md and TESTING_GUIDE.md

## ✅ Verification Checklist

After publishing, verify:

- [ ] Repository is accessible at GitHub URL
- [ ] README.md displays correctly
- [ ] All folders are present (agents, toolkits, plugins, etc.)
- [ ] .gitignore is working (no __pycache__, .venv, etc.)
- [ ] Documentation is readable
- [ ] No sensitive data is exposed
- [ ] Repository topics are added
- [ ] License is included (if open source)

---

**Ready to publish!** Follow the steps above to create your GitHub repository.