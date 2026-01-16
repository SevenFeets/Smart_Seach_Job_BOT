# GitHub Actions - Quick Start

## 🚀 5-Minute Setup

### Step 1: Push to GitHub

```powershell
cd "E:\Projects\cv website\job seeker bot"

# If not already a git repo
git init
git add .
git commit -m "Initial commit"

# Add your GitHub repo (replace with your URL)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

### Step 2: Add Secrets

1. Go to: **Your Repo** → **Settings** → **Secrets and variables** → **Actions**
2. Click **"New repository secret"**
3. Add these **REQUIRED** secrets:

| Secret Name | Value | Example |
|------------|-------|---------|
| `LINKEDIN_EMAIL` | Your email | `your_email@example.com` |
| `LINKEDIN_PASSWORD` | Your password | `your_password` |

4. Add these **OPTIONAL** secrets (or use defaults):

| Secret Name | Value | Default |
|------------|-------|---------|
| `JOB_KEYWORDS` | Comma-separated | `Python Developer,Backend Engineer` |
| `AUTO_APPLY_ENABLED` | true/false | `false` |
| `MAX_APPLICATIONS_PER_RUN` | Number | `5` |
| `GROQ_API_KEY` | API key | (none) |

### Step 3: Test It!

1. Go to: **Your Repo** → **Actions** tab
2. Click **"LinkedIn Job Bot"**
3. Click **"Run workflow"** → **"Run workflow"**
4. Watch it run! ✅

### Step 4: Done!

The bot will now run **automatically every hour from 8 AM to 6 PM UTC**.

---

## 📋 Required Secrets Checklist

- [ ] `LINKEDIN_EMAIL`
- [ ] `LINKEDIN_PASSWORD`
- [ ] `JOB_KEYWORDS` (optional)
- [ ] `AUTO_APPLY_ENABLED` (optional)
- [ ] `GROQ_API_KEY` (optional, for AI cover letters)

---

## 🔍 View Results

1. Go to **Actions** tab
2. Click on any workflow run
3. Scroll to bottom → **"Print statistics"** step
4. See your results!

---

## ⚙️ Adjust Schedule

Edit `.github/workflows/job-bot.yml`:

```yaml
schedule:
  - cron: '0 9-17 * * 1-5'  # 9 AM to 5 PM, weekdays
```

---

## ❓ Troubleshooting

**Workflow not running?**
- Check **Actions** tab is enabled
- Verify secrets are added
- Check workflow file exists

**Login failed?**
- Verify email/password secrets are correct
- Check workflow logs for errors

**No jobs found?**
- Check `JOB_KEYWORDS` secret
- Try broader keywords

---

## 📚 Full Guide

See `docs/GITHUB_ACTIONS_SETUP.md` for complete documentation.

---

**That's it! Your bot is now automated! 🎉**
