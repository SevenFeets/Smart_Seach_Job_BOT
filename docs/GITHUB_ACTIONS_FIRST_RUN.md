# GitHub Actions - First Run Setup

## Problem: Security Challenge in Headless Mode

LinkedIn requires a security challenge on first login, which **cannot be completed** in headless GitHub Actions (no browser visible).

## Solution: Use Your Local Session

Since you already logged in successfully locally, you can upload your session file to GitHub Actions.

### Step 1: Get Your Local Session File

Your session is saved at:
```
browser_data/linkedin_session.json
```

### Step 2: Upload to GitHub Actions (Option A - Manual)

1. Go to your GitHub repository
2. Go to **Actions** → **LinkedIn Job Bot**
3. Click **"Run workflow"** → **"Run workflow"**
4. After it fails (expected on first run), go to the run
5. Scroll to **"Upload session artifact"** step
6. Click to download/upload manually (if possible)

**Better Option:** Use the workflow artifact upload after a successful local run.

### Step 3: Upload Session via Workflow (Option B - Recommended)

1. **Run locally one more time** to ensure session is fresh:
   ```powershell
   python main.py search --pages 1 --easy-apply
   ```

2. **Copy the session file** to a location you can access

3. **Create a GitHub Actions workflow** that uploads it, OR

4. **Use the artifact from a successful local test**

### Step 4: Alternative - Accept First Run Failure

The workflow is now configured to:
- Continue even if artifacts don't exist (first run)
- Continue even if session upload fails
- The second run will work once session is saved

**You can simply:**
1. Let the first run fail (expected)
2. Manually trigger a second run
3. It should work if the first run got past the login

## Quick Fix: Increase Security Challenge Wait Time

If you want to try letting it wait longer, we can increase the timeout in the code.

## Best Solution: Pre-authenticate Locally

1. Run locally: `python main.py search --pages 1`
2. Complete any security challenges
3. Session is saved to `browser_data/linkedin_session.json`
4. This file will be uploaded as artifact on first successful GitHub Actions run
5. Future runs will download and use this session

## Current Workflow Behavior

The workflow now:
- ✅ Handles missing artifacts gracefully (first run)
- ✅ Continues even if upload fails
- ⚠️ First run may fail if security challenge appears
- ✅ Second run should work (uses saved session)

## Troubleshooting

### If first run fails:
1. Check the "Run Job Bot" step logs
2. Look for "Security challenge detected"
3. This is expected - LinkedIn requires manual verification
4. Run again manually - it should work on second attempt

### If session not saving:
1. Check that `browser_data/` directory exists
2. Verify file permissions
3. Check workflow logs for errors

---

**Recommendation:** Let the first run complete (even if it fails), then manually trigger a second run. The session should be saved and future runs will work automatically.
