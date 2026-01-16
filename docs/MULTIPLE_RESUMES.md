# Multiple Resume Support

The LinkedIn Job Bot now supports **smart resume selection** - automatically choosing the best resume based on job requirements!

## Quick Setup

### 1. Place Your Resumes

Put your resumes in the `resumes/` folder with these exact names:

```
resumes/
├── Backend.pdf      ← For backend/API/web development jobs
└── embedded.pdf     ← For embedded/firmware/hardware jobs
```

### 2. Enable Smart Selection

In your `.env` file:

```env
USE_SMART_RESUME_SELECTION=true
```

### 3. Test It!

```powershell
# See which resumes are available
python main.py resumes

# Test which resume would be selected
python main.py resumes --test "Senior Backend Engineer"
python main.py resumes --test "Embedded Software Developer"
```

## How It Works

The bot analyzes the job title and description for keywords:

### Backend Resume (`Backend.pdf`)
**Keywords:** backend, python, django, flask, fastapi, api, rest, graphql, database, sql, postgresql, mysql, mongodb, redis, microservices, docker, kubernetes, aws, cloud, node.js, java, spring, .net, c#, ruby, php

### Embedded Resume (`embedded.pdf`)
**Keywords:** embedded, firmware, c, c++, microcontroller, mcu, arm, rtos, real-time, iot, hardware, fpga, vhdl, verilog, assembly, linux kernel, device driver, uart, spi, i2c, can, automotive, robotics, raspberry pi, arduino, stm32, esp32, sensor

### Selection Process

1. Bot reads the job title and description
2. Counts keyword matches for each resume
3. Selects the resume with the most matches
4. If no matches, uses the first resume (Backend.pdf)

## Examples

### Example 1: Backend Job

**Job Title:** "Senior Python Backend Developer"

**Keywords Found:** backend, python

**Selected:** `Backend.pdf`

### Example 2: Embedded Job

**Job Title:** "Firmware Engineer - IoT Devices"

**Keywords Found:** firmware, embedded, iot

**Selected:** `embedded.pdf`

### Example 3: Mixed Job

**Job Title:** "Full Stack Engineer with Embedded Experience"

If both resumes match, the one with more keyword matches wins.

## Testing Resume Selection

```powershell
# Test different job titles
python main.py resumes --test "Python Django Developer"
# Output: Selected resume: Backend.pdf (score: 3, keywords: python, django, backend...)

python main.py resumes --test "STM32 Firmware Engineer"
# Output: Selected resume: embedded.pdf (score: 4, keywords: firmware, embedded, stm32...)

python main.py resumes --test "DevOps Engineer"
# Output: Selected resume: Backend.pdf (score: 2, keywords: docker, kubernetes...)
```

## Advanced: Custom Resume Profiles

You can add more resumes programmatically in `src/resume_selector.py`:

```python
# In _load_resume_profiles method, add:
"fullstack": {
    "file": "Fullstack.pdf",
    "keywords": [
        "fullstack", "full-stack", "react", "vue", "angular",
        "frontend", "backend", "javascript", "typescript",
        "node.js", "python", "django", "flask"
    ],
    "weight": 1.0
},
"devops": {
    "file": "DevOps.pdf",
    "keywords": [
        "devops", "sre", "infrastructure", "terraform", "ansible",
        "jenkins", "gitlab", "ci/cd", "kubernetes", "docker",
        "monitoring", "prometheus", "grafana", "elk"
    ],
    "weight": 1.0
}
```

Then place the corresponding PDF files in `resumes/` folder.

## Configuration Options

### Option 1: Smart Selection (Recommended)

```env
USE_SMART_RESUME_SELECTION=true
```

The bot automatically selects the best resume for each job.

### Option 2: Single Resume (Legacy)

```env
USE_SMART_RESUME_SELECTION=false
RESUME_PATH=./resumes/my_resume.pdf
```

Always use the same resume for all jobs.

## Viewing Selection Results

The bot logs which resume it selected during application:

```
[cyan]Applying to: Backend Developer at TechCorp[/cyan]
[cyan]Selected resume:[/cyan] Backend.pdf (score: 5, keywords: backend, python, api, docker, aws...)
[cyan]Uploaded resume: Backend.pdf[/cyan]
```

You can also check the database:

```powershell
python main.py jobs --limit 10
```

The `resume_used` column shows which resume was uploaded for each application.

## Database Tracking

Each application records which resume was used:

```sql
SELECT title, company, resume_used, status 
FROM applications 
JOIN jobs ON applications.job_id = jobs.id;
```

This helps you track which resume performs better!

## Tips for Best Results

### 1. Name Your Files Correctly

The system expects:
- `Backend.pdf` (capital B)
- `embedded.pdf` (lowercase e)

Or update the names in `src/resume_selector.py`.

### 2. Add Relevant Keywords

Edit the keyword lists in `src/resume_selector.py` to match your experience.

### 3. Test Before Applying

Always test selection before enabling auto-apply:

```powershell
python main.py resumes --test "Your Target Job Title"
```

### 4. Monitor Results

Check which resume is selected:

```powershell
# Search for jobs (with logging)
python main.py search --pages 1

# Review the logs to see selections
```

### 5. Update Keywords

If jobs aren't matching correctly, add more keywords to your profiles.

## Fallback Behavior

If smart selection fails or no resumes are found:

1. Uses `RESUME_PATH` from `.env`
2. If that doesn't exist, skips resume upload
3. Logs a warning

## Example Workflow

```powershell
# 1. Set up your resumes
copy "C:\path\to\Backend_Resume.pdf" "resumes\Backend.pdf"
copy "C:\path\to\Embedded_Resume.pdf" "resumes\embedded.pdf"

# 2. Enable smart selection
echo "USE_SMART_RESUME_SELECTION=true" >> .env

# 3. Test it
python main.py resumes

# 4. Test specific jobs
python main.py resumes --test "Python Backend Engineer"
python main.py resumes --test "Embedded Linux Developer"

# 5. Search for jobs (watch the resume selection)
python main.py search --pages 1 --easy-apply

# 6. Apply (with smart resume selection)
python main.py apply --max 5
```

## Troubleshooting

### "No resume profiles configured"

**Problem:** Resume files not found.

**Solution:** 
- Check files exist: `dir resumes\`
- Verify exact names: `Backend.pdf` and `embedded.pdf`

### "Warning: Resume not found"

**Problem:** File name mismatch.

**Solution:**
```powershell
# List your files
dir resumes\

# Rename if needed
ren "resumes\backend_resume.pdf" "Backend.pdf"
ren "resumes\embedded_cv.pdf" "embedded.pdf"
```

### Wrong Resume Selected

**Problem:** Keywords don't match your jobs.

**Solution:**
- Edit `src/resume_selector.py`
- Add relevant keywords to your profile
- Test again: `python main.py resumes --test "Job Title"`

### Always Uses Default Resume

**Problem:** No keyword matches found.

**Solution:**
- The job description might not contain expected keywords
- Add more general keywords to your profiles
- Or use single resume mode for that job type

## Future Enhancements

Possible improvements:

1. **Machine Learning**: Use ML to learn which resume performs better
2. **Company-Specific**: Select resume based on company culture
3. **A/B Testing**: Automatically track success rates per resume
4. **Custom Rules**: Allow `.env` configuration of keywords
5. **More Profiles**: Support unlimited resume types

---

**Have both Backend and Embedded experience? Smart resume selection ensures you apply with the right resume every time!** 🎯
