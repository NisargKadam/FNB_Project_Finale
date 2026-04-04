# Quick Git Push - Copy & Paste Commands

**Run these commands in PowerShell in your project directory**

```powershell
# Navigate to project directory
cd "C:\Users\nisar\Documents\AI Builder 3\Projects\Final_Project"

# Check if git is already initialized
git status

# If git is NOT initialized, run this:
git init

# Add the remote repository
git remote add origin https://github.com/NisargKadam/FNB_Project_Finale.git

# Verify remote is added
git remote -v

# Configure git (one-time setup - use your info)
git config --global user.name "Nisar Kadam"
git config --global user.email "nisar.kadam@example.com"

# Stage all files
git add .

# See what will be committed
git status

# Create commit
git commit -m "Initial commit: Food & Beverage AI System

- 11-stage workflow pipeline
- 20 pre-configured agents
- OpenAI GPT-4 Mini integration
- Student assignment framework
- Complete documentation"

# Push to GitHub (you'll be prompted for credentials)
git push -u origin main

# Verify push was successful
git log --oneline
```

---

## If You Get an Error About "Main" Branch Name

GitHub uses `main` but you might have `master`. Try:

```powershell
# Check current branch name
git branch

# If it shows 'master', rename it to 'main'
git branch -M main

# Then push
git push -u origin main
```

---

## GitHub Authentication

When prompted for credentials:
- **Username:** Your GitHub username
- **Password:** Your Personal Access Token (NOT your password!)

**To get a Personal Access Token:**
1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Check box: `repo` and `workflow`
4. Click "Generate token"
5. Copy the token and paste when prompted in PowerShell

---

## After Push - Verify It Worked

Visit: https://github.com/NisargKadam/FNB_Project_Finale

You should see all your code files there!

---

## Making Repository Public for Students

1. Go to: https://github.com/NisargKadam/FNB_Project_Finale
2. Click **Settings**
3. Scroll down to **Danger Zone**
4. If private, click **Make public**
5. Confirm

Now students can see and clone your repository!

---

## For Future Pushes

```powershell
git add .
git commit -m "Description of changes"
git push origin main
```

That's it! 🚀
