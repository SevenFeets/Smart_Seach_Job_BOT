# Quick Fix Guide - 90% Failure Rate

## 🚨 IMMEDIATE ACTION REQUIRED

Your bot is failing because LinkedIn has flagged your session. Here's how to fix it:

### Step 1: Create Fresh Session (5 minutes)

```bash
# 1. Run bot locally
python main.py search --pages 1

# 2. Complete any security challenges in the browser window that opens

# 3. Wait for it to complete successfully
```

### Step 2: Upload Session to GitHub (2 minutes)

```bash
# Run the upload script
python scripts/upload_session_to_github.py

# Copy the output (it will look like a long JSON string)
```

### Step 3: Update GitHub Secret (2 minutes)

1. Go to: `https://github.com/YOUR_USERNAME/YOUR_REPO/settings/secrets/actions`
2. Find `LINKEDIN_SESSION_JSON`
3. Click "Update"
4. Paste the JSON from Step 2
5. Click "Update secret"

### Step 4: Test It (1 minute)

1. Go to Actions tab in your repo
2. Click "Test LinkedIn Session" workflow
3. Click "Run workflow"
4. Wait for it to complete
5. Should show green checkmark ✓

### Step 5: Monitor (Ongoing)

Watch the next 3-5 scheduled runs:
- Should see green checkmarks ✓
- Should find 50-200+ jobs per run
- Should have "Already logged in" message

---

## 📊 What Was Fixed

| Issue | Solution |
|-------|----------|
| LinkedIn detecting bot | Added 8+ anti-detection techniques |
| Sessions expiring | Added validation & retry logic |
| No error feedback | Clear messages & troubleshooting |
| Too many runs | Reduced to 3x/day (8am, 2pm, 8pm) |
| Hard to diagnose | New test workflow + logging |

---

## 🎯 Expected Improvement

**Before:** 90% failure rate ❌  
**After:** 70-90% success rate ✅

---

## ⚡ Quick Commands

```bash
# Test locally
python main.py search --pages 1

# View statistics
python main.py stats

# Upload session
python scripts/upload_session_to_github.py

# Check database
sqlite3 data/jobs.db "SELECT COUNT(*) FROM jobs;"
```

---

## 🔍 How to Check if It's Working

### ✅ Good Signs:
- Green checkmarks in Actions tab
- "Already logged in" in logs
- Finding 50+ jobs per run
- Session artifact being created

### ❌ Bad Signs:
- Red X's in Actions tab
- "Login failed" in logs
- "Security challenge detected"
- Finding 0 jobs

---

## 📞 If Still Failing After Session Refresh

1. **Reduce frequency** - Edit `.github/workflows/job-bot.yml`:
   ```yaml
   schedule:
     - cron: '0 14 * * *'  # Once per day at 2 PM UTC
   ```

2. **Check LinkedIn account**:
   - Any security notifications?
   - Profile complete?
   - Account in good standing?

3. **Try different times**:
   - Avoid peak hours
   - Spread runs throughout the day

4. **Increase delays**:
   - Edit `src/linkedin/scraper.py`
   - Change `await asyncio.sleep(3)` to `await asyncio.sleep(10)`

---

## 📚 Full Documentation

- **TROUBLESHOOTING.md** - Comprehensive guide for all issues
- **FIXES_SUMMARY.md** - Detailed explanation of all fixes
- **README.md** - General setup and usage

---

## ⏱️ Timeline

- **Now**: Refresh session (Steps 1-3)
- **+5 min**: Test session (Step 4)
- **+1 day**: Check first few runs
- **+1 week**: Confirm stable success rate
- **+2-3 weeks**: Refresh session again (preventive)

---

## 💡 Pro Tips

1. **Refresh session every 2-3 weeks** (before it expires)
2. **Run test workflow** before important job searches
3. **Monitor GitHub Actions** weekly
4. **Keep LinkedIn profile active** (login manually sometimes)
5. **Don't run multiple bots** on same account

---

## 🎉 Success Criteria

You'll know it's fixed when:
- ✅ 3+ consecutive successful runs
- ✅ Finding jobs consistently
- ✅ Session lasting 2+ weeks
- ✅ No "Login failed" errors
- ✅ Applications being submitted (if enabled)

---

**Need help?** Check TROUBLESHOOTING.md for detailed solutions to specific issues.
