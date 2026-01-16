#!/usr/bin/env python3
"""Security verification script - checks for potential credential leaks."""
import os
import re
from pathlib import Path
from typing import List, Tuple

# Simple markers (no special chars for Windows compatibility)
GREEN = '[OK]'
RED = '[!!]'
YELLOW = '[WARN]'
RESET = ''
BOLD = ''


def check_file_exists(filepath: str) -> Tuple[bool, str]:
    """Check if a sensitive file exists."""
    if Path(filepath).exists():
        return True, f"{RED} {filepath} exists (should not be committed)"
    return False, f"{GREEN} {filepath} not found (good)"


def check_gitignore() -> List[str]:
    """Check if .gitignore has required entries."""
    issues = []
    required_entries = ['.env', 'resumes/', '*.pdf', 'data/', 'browser_data/', '*.db']
    
    gitignore_path = Path('.gitignore')
    if not gitignore_path.exists():
        return [f"{RED} .gitignore file not found!"]
    
    content = gitignore_path.read_text()
    
    for entry in required_entries:
        if entry not in content:
            issues.append(f"{YELLOW} .gitignore missing: {entry}")
    
    if not issues:
        issues.append(f"{GREEN} .gitignore properly configured")
    
    return issues


def check_for_secrets(filepath: str) -> List[str]:
    """Check a file for potential secrets."""
    issues = []
    
    if not Path(filepath).exists():
        return []
    
    # Patterns that might indicate secrets
    secret_patterns = [
        (r'gsk_[a-zA-Z0-9]{32,}', 'Groq API key'),
        (r'sk-[a-zA-Z0-9]{32,}', 'OpenAI API key'),
        (r'AIza[a-zA-Z0-9_-]{35}', 'Google API key'),
        (r'password\s*=\s*["\'][^"\']{8,}["\']', 'Hardcoded password'),
    ]
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        for pattern, description in secret_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                # Exclude example values
                if 'example' not in content.lower() and 'your_' not in content.lower():
                    issues.append(
                        f"{RED} Potential {description} found in {filepath}"
                    )
    except Exception as e:
        pass
    
    return issues


def main():
    """Run security checks."""
    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}LinkedIn Job Bot - Security Verification{RESET}")
    print(f"{BOLD}{'='*60}{RESET}\n")
    
    all_issues = []
    
    # Check 1: .env should exist locally but not be in example files
    print(f"{BOLD}1. Checking sensitive files...{RESET}")
    env_exists = Path('.env').exists()
    if env_exists:
        print(f"  {GREEN} .env exists locally (good for local dev)")
    else:
        print(f"  {YELLOW} .env not found (create from config.example.env)")
    
    # Check 2: .gitignore configuration
    print(f"\n{BOLD}2. Checking .gitignore...{RESET}")
    gitignore_issues = check_gitignore()
    for issue in gitignore_issues:
        print(f"  {issue}")
        if '[!!' in issue or '[WARN' in issue:
            all_issues.append(issue)
    
    # Check 3: Check example files for secrets
    print(f"\n{BOLD}3. Checking for leaked secrets...{RESET}")
    files_to_check = [
        'config.example.env',
        'README.md',
        '.github/workflows/job-bot.yml',
        'main.py'
    ]
    
    secret_found = False
    for filepath in files_to_check:
        issues = check_for_secrets(filepath)
        if issues:
            for issue in issues:
                print(f"  {issue}")
                all_issues.append(issue)
                secret_found = True
    
    if not secret_found:
        print(f"  {GREEN} No secrets found in public files")
    
    # Check 4: Resumes
    print(f"\n{BOLD}4. Checking resume files...{RESET}")
    resumes_dir = Path('resumes')
    if resumes_dir.exists():
        pdf_files = list(resumes_dir.glob('*.pdf'))
        if pdf_files:
            print(f"  {GREEN} Found {len(pdf_files)} resume(s)")
            for pdf in pdf_files:
                print(f"    - {pdf.name}")
        else:
            print(f"  {YELLOW} No resumes found in resumes/")
    else:
        print(f"  {YELLOW} resumes/ directory not found")
    
    # Check 5: Database
    print(f"\n{BOLD}5. Checking database...{RESET}")
    db_path = Path('data/jobs.db')
    if db_path.exists():
        size = db_path.stat().st_size / 1024  # KB
        print(f"  {GREEN} Database exists ({size:.1f} KB)")
    else:
        print(f"  {YELLOW} No database yet (will be created on first run)")
    
    # Summary
    print(f"\n{BOLD}{'='*60}{RESET}")
    if all_issues:
        print(f"{RED} SECURITY ISSUES FOUND:")
        for issue in all_issues:
            print(f"  {issue}")
        print(f"\n{YELLOW}Please review and fix the issues above.")
        return 1
    else:
        print(f"{GREEN} All security checks passed!")
        print(f"\n{GREEN}Your configuration is secure.")
        return 0


if __name__ == "__main__":
    exit(main())
