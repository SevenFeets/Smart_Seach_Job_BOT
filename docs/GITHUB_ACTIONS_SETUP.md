# GitHub Actions Setup Guide

Complete guide to enable automated job searching with GitHub Actions.

## Step 1: Create GitHub Repository

### Option A: Create New Repository on GitHub

1. Go to [GitHub.com](https://github.com) and sign in
2. Click the **"+"** icon → **"New repository"**
3. Fill in:
   - **Repository name**: `linkedin-job-bot` (or your choice)
   - **Description**: "Automated LinkedIn job search and application bot"
   - **Visibility**: 
     - ✅ **Private** (recommended - keeps your credentials safe)
     - ⚠️ Public (if you want to share, but be careful with secrets)
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
4. Click **"Create repository"**

### Option B: Use Existing Repository

If you already have a repository, skip to Step 2.

---

## Step 2: Push Your Code to GitHub

### Initialize Git (if not already done)

```powershell
# Navigate to your project
cd "E:\Projects\cv website\job seeker bot"

# Initialize Git (if not already done)
git init

# Add all files
git add .

# Make initial commit
git commit -m "Initial commit - LinkedIn Job Bot"

# Add remote (replace YOUR_USERNAME and YOUR_REPO with your actual values)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**Example:**
```powershell
git remote add origin https://github.com/johndoe/linkedin-job-bot.git
git push -u origin main
```

---

## Step 3: Add GitHub Secrets

**⚠️ CRITICAL:** Never put real credentials in workflow files! Use GitHub Secrets.

### How to Add Secrets

1. Go to your repository on GitHub
2. Click **Settings** (top menu)
3. In the left sidebar, click **Secrets and variables** → **Actions**
4. Click **"New repository secret"**

### Required Secrets

Add these secrets one by one:

#### 1. LinkedIn Credentials (REQUIRED)

**Name:** `LINKEDIN_EMAIL`
**Value:** Your LinkedIn email address
```
your_email@example.com
```

**Name:** `LINKEDIN_PASSWORD`
**Value:** Your LinkedIn password
```
your_actual_password
```

#### 2. Job Search Configuration (Optional - has defaults)

**Name:** `JOB_KEYWORDS`
**Value:** Comma-separated keywords
```
Python Developer,Backend Engineer,Software Engineer
```

**Name:** `EXPERIENCE_LEVELS`
**Value:** Experience levels
```
ENTRY_LEVEL,ASSOCIATE,MID_SENIOR
```

**Name:** `LOCATION`
**Value:** Job location
```
Remote
```

**Name:** `DATE_POSTED`
**Value:** Date filter
```
PAST_WEEK
```

#### 3. Auto-Apply Settings (Optional)

**Name:** `AUTO_APPLY_ENABLED`
**Value:** Enable/disable auto-apply
```
true
```
or
```
false
```

**Name:** `MAX_APPLICATIONS_PER_RUN`
**Value:** Maximum applications per run
```
5
```

#### 4. AI Cover Letter (Optional)

**Name:** `GROQ_API_KEY`
**Value:** Your Groq API key (if using Groq)
```
gsk_your_actual_key_here
```

**Name:** `LLM_PROVIDER`
**Value:** LLM provider choice
```
groq
```
or
```
ollama
```

**Note:** For Ollama, you'd need a self-hosted runner or use Groq instead (recommended for GitHub Actions).

---

## Step 4: Enable GitHub Actions

### Automatic Enable

GitHub Actions are **automatically enabled** when you push a workflow file (`.github/workflows/job-bot.yml`).

### Manual Enable (if needed)

1. Go to your repository
2. Click **Settings** → **Actions** → **General**
3. Under **"Workflow permissions"**, select:
   - ✅ **Read and write permissions**
   - ✅ **Allow GitHub Actions to create and approve pull requests**
4. Click **Save**

---

## Step 5: Test the Workflow

### Test 1: Manual Trigger

1. Go to your repository on GitHub
2. Click **Actions** tab (top menu)
3. You should see **"LinkedIn Job Bot"** workflow
4. Click on it
5. Click **"Run workflow"** button (right side)
6. Select mode:
   - **search** - Just search for jobs
   - **apply** - Apply to saved jobs
   - **full** - Search + apply
7. Click **"Run workflow"**

### Test 2: Check Workflow Run

1. Click on the workflow run
2. Click on **"job-bot"** job
3. Watch the logs in real-time
4. Check for any errors

### Expected Output

You should see:
- ✅ Checkout repository
- ✅ Set up Python
- ✅ Install dependencies
- ✅ Install Playwright browsers
- ✅ Run Job Bot
- ✅ Upload artifacts
- ✅ Print statistics

---

## Step 6: Verify Scheduled Runs

The workflow is configured to run **every hour from 8 AM to 6 PM UTC**.

### Check Schedule

1. Go to **Actions** tab
2. You'll see scheduled runs appear automatically
3. They run at: 08:00, 09:00, 10:00, 11:00, 12:00, 13:00, 14:00, 15:00, 16:00, 17:00, 18:00 UTC

### Adjust Schedule

Edit `.github/workflows/job-bot.yml`:

```yaml
schedule:
  - cron: '0 8-18 * * 1-5'  # 8 AM to 6 PM, weekdays only
```

Or for different hours:
```yaml
schedule:
  - cron: '0 9 * * *'   # 9 AM UTC daily
  - cron: '0 17 * * *'  # 5 PM UTC daily
```

**Cron format:** `minute hour day month weekday`
- `0 8 * * *` = Every day at 8:00 AM UTC
- `0 8-18 * * *` = Every hour from 8 AM to 6 PM UTC
- `0 9 * * 1-5` = 9 AM UTC, weekdays only

---

## Step 7: Monitor and Debug

### View Workflow Runs

1. Go to **Actions** tab
2. Click on any run to see details
3. Click on **"job-bot"** to see logs

### Common Issues

#### Issue: "Secrets not found"

**Solution:**
- Verify secrets are added in Settings → Secrets → Actions
- Check secret names match exactly (case-sensitive)

#### Issue: "Login failed"

**Solution:**
- Verify `LINKEDIN_EMAIL` and `LINKEDIN_PASSWORD` are correct
- LinkedIn may require manual verification on first run
- Check workflow logs for specific error

#### Issue: "No jobs found"

**Solution:**
- Check `JOB_KEYWORDS` secret
- Verify `LOCATION` is correct
- Try broader keywords

#### Issue: "Playwright browser not found"

**Solution:**
- The workflow installs browsers automatically
- If it fails, check the "Install Playwright browsers" step

---

## Step 8: View Results

### Statistics

After each run, check the **"Print statistics"** step to see:
- Total jobs scraped
- Total applications
- Success/failure rates

### Artifacts

1. Go to workflow run
2. Scroll to bottom
3. Download artifacts:
   - **linkedin-session** - Saved login session (7 days retention)
   - **jobs-database** - Job database (30 days retention)

### Database

The database is saved as an artifact. Download it to see:
- All scraped jobs
- Application history
- Resume used for each application

---

## Security Best Practices

### ✅ DO:

- Use GitHub Secrets for all credentials
- Keep repository **Private** if possible
- Regularly rotate passwords
- Monitor workflow runs for suspicious activity
- Review logs regularly

### ❌ DON'T:

- Never commit `.env` file
- Never put credentials in workflow files
- Never share your repository publicly with secrets
- Never hardcode passwords in code

---

## Advanced: Custom Schedule

### Different Timezones

UTC times in cron:
- **EST (UTC-5)**: Add 5 hours
  - 8 AM EST = 1 PM UTC → `cron: '0 13 * * *'`
- **PST (UTC-8)**: Add 8 hours
  - 8 AM PST = 4 PM UTC → `cron: '0 16 * * *'`

### Weekdays Only

```yaml
schedule:
  - cron: '0 8-18 * * 1-5'  # Monday-Friday, 8 AM to 6 PM
```

### Specific Days

```yaml
schedule:
  - cron: '0 9 * * 1,3,5'  # Monday, Wednesday, Friday at 9 AM
```

---

## Troubleshooting

### Workflow Not Running

1. Check **Actions** tab is enabled
2. Verify workflow file is in `.github/workflows/`
3. Check workflow syntax is valid
4. Look for errors in workflow file

### Secrets Not Working

1. Verify secret names match exactly
2. Check for extra spaces in secret values
3. Ensure secrets are added to correct repository
4. Try re-adding the secret

### Browser Automation Fails

1. Check Playwright installation step
2. Verify headless mode is enabled (`HEADLESS: 'true'`)
3. Check for LinkedIn security challenges
4. Review browser logs in workflow output

---

## Quick Reference

### Essential Secrets

```yaml
LINKEDIN_EMAIL          # Required
LINKEDIN_PASSWORD       # Required
JOB_KEYWORDS            # Optional (has default)
AUTO_APPLY_ENABLED      # Optional (default: false)
```

### Workflow Locations

- Workflow file: `.github/workflows/job-bot.yml`
- Secrets: Repository → Settings → Secrets → Actions
- Runs: Repository → Actions tab

### Manual Trigger

1. Go to **Actions** tab
2. Select **"LinkedIn Job Bot"**
3. Click **"Run workflow"**
4. Choose mode and run

---

## Next Steps

1. ✅ Push code to GitHub
2. ✅ Add all required secrets
3. ✅ Test with manual trigger
4. ✅ Verify scheduled runs work
5. ✅ Monitor results

**Your bot will now run automatically every hour from 8 AM to 6 PM UTC!** 🚀

---

## Support

If you encounter issues:

1. Check workflow logs in **Actions** tab
2. Verify all secrets are set correctly
3. Test with manual trigger first
4. Review error messages in logs

Good luck with your automated job search! 🎯
