# 🤖 LinkedIn Job Bot

Automated LinkedIn job search and application bot built with Python and Playwright.

## ✨ Features

- **🔍 Job Search**: Search LinkedIn jobs by keywords, experience level, location, and date posted
- **💾 Database Storage**: SQLite database to track jobs and prevent duplicate applications
- **📝 Auto-Apply**: Automatically apply to Easy Apply jobs
- **✉️ AI Cover Letters**: Generate personalized cover letters using free LLMs (Ollama, Groq, etc.)
- **⏰ Scheduling**: Run hourly within specified hours (8 AM - 6 PM)
- **🔄 GitHub Actions**: Cloud-based scheduling with GitHub Actions

## 📁 Project Structure

```
linkedin-job-bot/
├── .github/
│   └── workflows/
│       ├── job-bot.yml              # GitHub Actions workflow
│       └── job-bot-self-hosted.yml  # For self-hosted runners
├── src/
│   ├── ai/
│   │   ├── __init__.py
│   │   └── cover_letter.py          # AI cover letter generation
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models.py                # SQLAlchemy models
│   │   └── repository.py            # Database operations
│   ├── linkedin/
│   │   ├── __init__.py
│   │   ├── authenticator.py         # LinkedIn login
│   │   ├── scraper.py               # Job scraping
│   │   └── job_applier.py           # Auto-apply logic
│   ├── __init__.py
│   ├── config.py                    # Configuration management
│   └── scheduler.py                 # Local scheduling
├── data/                            # Database storage (gitignored)
├── browser_data/                    # Session storage (gitignored)
├── resumes/                         # Your resume files (gitignored)
├── main.py                          # CLI entry point
├── requirements.txt
├── config.example.env               # Example configuration
└── README.md
```

## 🚀 Quick Start

### 1. Clone and Install

```bash
git clone <your-repo-url>
cd linkedin-job-bot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### 2. Configure

```bash
# Copy example config
cp config.example.env .env

# Edit .env with your settings
```

**Required settings in `.env`:**
```env
LINKEDIN_EMAIL=your_email@example.com
LINKEDIN_PASSWORD=your_password
JOB_KEYWORDS=Python Developer,Software Engineer,Backend Developer
EXPERIENCE_LEVELS=ENTRY_LEVEL,ASSOCIATE,MID_SENIOR
LOCATION=Remote
```

### 3. Add Your Resume(s)

**Option A: Single Resume**
```bash
mkdir resumes
# Copy your resume to resumes/my_resume.pdf
```

**Option B: Multiple Resumes (Smart Selection)**
```bash
mkdir resumes
# For backend jobs
copy Backend_Resume.pdf resumes/Backend.pdf
# For embedded/firmware jobs  
copy Embedded_Resume.pdf resumes/embedded.pdf

# Enable in .env
USE_SMART_RESUME_SELECTION=true
```

The bot will automatically select the best resume based on job keywords! See `docs/MULTIPLE_RESUMES.md` for details.

### 4. Run

```bash
# Search for jobs
python main.py search

# Apply to jobs (if AUTO_APPLY_ENABLED=true)
python main.py apply

# Full pipeline (search + apply)
python main.py run

# View statistics
python main.py stats

# List saved jobs
python main.py jobs
```

## ⚙️ Configuration Options

| Variable | Description | Default |
|----------|-------------|---------|
| `LINKEDIN_EMAIL` | Your LinkedIn email | Required |
| `LINKEDIN_PASSWORD` | Your LinkedIn password | Required |
| `JOB_KEYWORDS` | Comma-separated keywords | Python Developer |
| `EXPERIENCE_LEVELS` | ENTRY_LEVEL, ASSOCIATE, MID_SENIOR, DIRECTOR, EXECUTIVE | ENTRY_LEVEL,ASSOCIATE |
| `LOCATION` | Job location filter | Remote |
| `DATE_POSTED` | ANY_TIME, PAST_MONTH, PAST_WEEK, PAST_24_HOURS | PAST_WEEK |
| `AUTO_APPLY_ENABLED` | Enable auto-apply | false |
| `MAX_APPLICATIONS_PER_RUN` | Max applications per run | 10 |
| `LLM_PROVIDER` | ollama, groq, openai, google | ollama |
| `HEADLESS` | Run browser headlessly | true |

## 🤖 AI Cover Letter Generation

### Option 1: Ollama (Free, Local or Remote)

**Local Installation:**
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model
ollama pull llama2

# Start Ollama server
ollama serve
```

Set in `.env`:
```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
```

**Remote Ollama (hosted on another server):**
```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=https://your-ollama-server.com
OLLAMA_MODEL=llama2
OLLAMA_API_KEY=your_api_key_if_required
```

Popular remote Ollama providers:
- [Replicate](https://replicate.com) - Pay per use
- Self-hosted on cloud (AWS, DigitalOcean, etc.)
- [Ollama Cloud](https://ollama.ai) (when available)

### Option 2: Groq (Free Tier)

1. Get API key from [console.groq.com](https://console.groq.com)
2. Set in `.env`:
```env
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_...
```

### Option 3: Google AI (Free Tier)

1. Get API key from [makersuite.google.com](https://makersuite.google.com)
2. Set in `.env`:
```env
LLM_PROVIDER=google
GOOGLE_AI_API_KEY=...
```

## 📅 GitHub Actions Setup

### 1. Add Repository Secrets

Go to your repo → Settings → Secrets and variables → Actions → New repository secret

**Required secrets:**
- `LINKEDIN_EMAIL`
- `LINKEDIN_PASSWORD`

**Optional secrets:**
- `JOB_KEYWORDS`
- `EXPERIENCE_LEVELS`
- `LOCATION`
- `AUTO_APPLY_ENABLED`
- `GROQ_API_KEY` (for AI cover letters)

### 2. Enable Actions

The workflow will automatically run every hour from 8 AM to 6 PM UTC.

You can also trigger manually: Actions → LinkedIn Job Bot → Run workflow

### 3. Adjust Schedule

Edit `.github/workflows/job-bot.yml` to change the cron schedule:

```yaml
schedule:
  - cron: '0 8-18 * * 1-5'  # 8 AM to 6 PM, weekdays only
```

## 📋 CLI Commands

```bash
# Search for jobs
python main.py search [OPTIONS]
  --keywords, -k    Comma-separated keywords
  --pages, -p       Pages to scrape (default: 3)
  --easy-apply, -e  Only Easy Apply jobs
  --details, -d     Fetch job descriptions

# Apply to jobs
python main.py apply [OPTIONS]
  --max, -m         Max applications (default: 10)
  --ai/--no-ai      Use AI cover letters (default: --ai)

# Full pipeline
python main.py run [OPTIONS]
  --keywords, -k    Comma-separated keywords
  --max, -m         Max applications (default: 10)
  --easy-apply      Only Easy Apply jobs

# Local scheduler
python main.py schedule [OPTIONS]
  --start, -s       Start hour (default: 8)
  --end, -e         End hour (default: 18)

# Statistics
python main.py stats

# List jobs
python main.py jobs [OPTIONS]
  --limit, -l       Number to show (default: 20)
  --search, -s      Search keyword

# Manage resumes
python main.py resumes [OPTIONS]
  --test, -t        Test which resume would be selected
```

## ⚠️ Important Notes

1. **LinkedIn ToS**: Automated tools may violate LinkedIn's Terms of Service. Use responsibly.

2. **Rate Limiting**: The bot includes delays to avoid rate limiting. Don't remove them.

3. **Security Challenges**: LinkedIn may require additional verification. The bot will wait for manual completion.

4. **Session Persistence**: Login sessions are saved to avoid repeated logins.

5. **Resume Verification**: Always verify your resume is properly uploaded before enabling auto-apply.

## 🛠️ Troubleshooting

### Login Issues
- Verify credentials in `.env`
- Check for security challenges (run with `HEADLESS=false`)
- Delete `browser_data/linkedin_session.json` to force re-login

### No Jobs Found
- Check your search keywords and filters
- Verify location spelling
- Try relaxing experience level filters

### Application Failures
- Some jobs have complex application forms
- External applications are skipped
- Check error messages in output

## 📄 License

MIT License - Use at your own risk.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

---

**⚠️ Disclaimer**: This tool is for educational purposes. Automated job applications may violate LinkedIn's Terms of Service. Use responsibly and at your own risk.
