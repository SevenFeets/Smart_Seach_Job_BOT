# Troubleshooting Guide

## Common Issues and Solutions

### 1. High Failure Rate (90%+ failures in GitHub Actions)

**Symptoms:**
- Most GitHub Actions runs fail with "Exit code 1"
- Logs show "Login failed" or "Security challenge detected"
- Session keeps getting invalidated

**Root Cause:**
LinkedIn's anti-bot detection system is flagging the automated activity and invalidating sessions.

**Solutions:**

#### A. Refresh Your Session (Recommended)
1. Run the bot locally to create a fresh session:
   ```bash
   python main.py search --pages 1
   ```

2. Complete any security challenges that appear in the browser

3. Upload the new session to GitHub:
   ```bash
   python scripts/upload_session_to_github.py
   ```

4. Update the `LINKEDIN_SESSION_JSON` secret in your GitHub repository

5. Test the session:
   - Go to Actions → "Test LinkedIn Session" → Run workflow

#### B. Reduce Run Frequency
LinkedIn may flag your account if the bot runs too frequently:
- Reduce from hourly to 3 times per day (already configured)
- Consider running only once per day during peak hours
- Add more randomization to avoid patterns

#### C. Use More Realistic Browser Settings
The bot now includes:
- Realistic user agent strings
- Browser fingerprint masking
- Anti-detection scripts
- Random delays between actions

#### D. Verify Your LinkedIn Account
- Make sure your LinkedIn account is in good standing
- Complete your profile (photo, experience, etc.)
- Avoid running multiple bots on the same account
- Don't use a brand new LinkedIn account

### 2. "Artifact not found" Warnings

**Symptoms:**
```
Unable to download artifact(s): Artifact not found for name: linkedin-session
Unable to download artifact(s): Artifact not found for name: jobs-database
```

**This is NORMAL for:**
- First run of the workflow
- After artifacts expire (14 days for session, 90 days for database)
- After manually deleting artifacts

**Solution:**
- These warnings can be ignored if you have `LINKEDIN_SESSION_JSON` secret set
- The workflow will automatically load the session from the secret
- After the first successful run, artifacts will be created

### 3. Session Expires Quickly

**Symptoms:**
- Session works for a few runs, then fails
- Need to refresh session every few days

**Causes:**
- LinkedIn detected unusual activity
- IP address changes (GitHub Actions uses different IPs)
- Too many automated actions

**Solutions:**
1. **Use a more stable session:**
   - Run the bot from a consistent location
   - Complete LinkedIn's security verification
   - Enable 2FA on your LinkedIn account (ironically helps)

2. **Reduce automation frequency:**
   - Run less often (3x per day instead of hourly)
   - Use longer delays between actions

3. **Monitor session health:**
   - Run "Test LinkedIn Session" workflow weekly
   - Set up notifications for failed runs

### 4. No Jobs Found

**Symptoms:**
- Bot runs successfully but finds 0 or very few jobs
- "Warning: No jobs found for 'keyword'"

**Solutions:**
1. **Adjust search parameters:**
   ```bash
   # In .env file
   JOB_KEYWORDS=Python,Software Engineer,Backend Developer
   LOCATION=United States  # Try broader locations
   DATE_POSTED=PAST_MONTH  # Expand time range
   EXPERIENCE_LEVELS=ENTRY_LEVEL,ASSOCIATE,MID_SENIOR,DIRECTOR
   ```

2. **Increase search depth:**
   - The bot now searches 5 pages per keyword (125 jobs)
   - Includes non-Easy Apply jobs

3. **Verify keywords:**
   - Use common job titles
   - Check LinkedIn manually to see if jobs exist
   - Try different keyword combinations

### 5. Application Failures

**Symptoms:**
- Jobs are found but applications fail
- "Error applying to job"

**Solutions:**
1. **Check resume files:**
   ```bash
   ls -la resumes/
   # Make sure your resume files exist and are named correctly
   ```

2. **Test cover letter generation:**
   ```bash
   # Make sure your LLM provider is configured
   python main.py apply --max 1
   ```

3. **Review application logs:**
   - Check `data/jobs.db` for application status
   - Run `python main.py stats` to see details

### 6. Rate Limiting

**Symptoms:**
- Bot slows down or stops mid-run
- "Too many requests" errors
- Temporary blocks

**Solutions:**
1. **Increase delays:**
   - Edit `src/linkedin/scraper.py`
   - Increase `await asyncio.sleep()` values

2. **Reduce scope:**
   - Fewer keywords
   - Fewer pages per keyword
   - Fewer applications per run

3. **Spread out runs:**
   - Run less frequently
   - Use different times of day

### 7. GitHub Actions Quota Exceeded

**Symptoms:**
- "You have exceeded your GitHub Actions minutes"
- Workflows queued but not running

**Solutions:**
1. **Reduce run frequency:**
   - Edit `.github/workflows/job-bot.yml`
   - Remove some cron schedules

2. **Use self-hosted runner:**
   - Set up a local machine as a GitHub runner
   - Use `.github/workflows/job-bot-self-hosted.yml`

3. **Optimize workflow:**
   - Each run uses ~3-5 minutes
   - Free tier: 2000 minutes/month
   - 3 runs/day = ~300 minutes/month (well within limits)

## Monitoring and Debugging

### Check Bot Status
```bash
# View statistics
python main.py stats

# Test search locally
python main.py search --pages 1

# Test application locally
python main.py apply --max 1
```

### View Logs in GitHub Actions
1. Go to your repository → Actions
2. Click on a workflow run
3. Expand "Run Job Bot" step
4. Look for error messages in red

### Validate Session
```bash
# Check if session file exists
ls -la browser_data/linkedin_session.json

# Validate JSON format
python -c "import json; print(json.load(open('browser_data/linkedin_session.json')))"
```

### Database Inspection
```bash
# Install SQLite browser or use command line
sqlite3 data/jobs.db

# View jobs
SELECT COUNT(*) FROM jobs;
SELECT * FROM jobs LIMIT 10;

# View applications
SELECT COUNT(*) FROM applications;
SELECT * FROM applications ORDER BY created_at DESC LIMIT 10;
```

## Best Practices

1. **Start Small:**
   - Test locally first
   - Run with 1-2 keywords initially
   - Gradually increase scope

2. **Monitor Regularly:**
   - Check GitHub Actions weekly
   - Review statistics
   - Update session when needed

3. **Be Respectful:**
   - Don't spam applications
   - Use realistic delays
   - Follow LinkedIn's terms of service

4. **Maintain Your Session:**
   - Refresh every 2-3 weeks
   - Complete security challenges promptly
   - Keep credentials secure

5. **Backup Your Data:**
   - Download `jobs.db` periodically
   - Export job lists
   - Keep track of applications

## Getting Help

If you're still experiencing issues:

1. **Check the logs:**
   - GitHub Actions logs
   - Local terminal output
   - Error messages

2. **Review configuration:**
   - `.env` file settings
   - GitHub Secrets
   - Workflow files

3. **Test components individually:**
   - Session validation
   - Search only
   - Application only

4. **Common error patterns:**
   - "Failed to log in" → Session issue
   - "No jobs found" → Search parameters
   - "Error applying" → Resume/LLM issue
   - "Exit code 1" → Check specific error in logs

## Emergency Reset

If nothing works, start fresh:

```bash
# 1. Delete old data
rm -rf browser_data/ data/

# 2. Create fresh session
python main.py search --pages 1

# 3. Upload new session
python scripts/upload_session_to_github.py

# 4. Update GitHub Secret
# Go to Settings → Secrets → Update LINKEDIN_SESSION_JSON

# 5. Test
# Run "Test LinkedIn Session" workflow

# 6. Monitor
# Watch the next scheduled run
```
