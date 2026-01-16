#!/usr/bin/env python3
"""Upload LinkedIn session to GitHub Actions as a secret (one-time setup)."""
import json
import base64
import os
from pathlib import Path

def main():
    """Upload session file content."""
    session_path = Path("browser_data/linkedin_session.json")
    
    if not session_path.exists():
        print("[ERROR] Session file not found!")
        print(f"Expected: {session_path.absolute()}")
        return
    
    # Read session file
    with open(session_path, 'r', encoding='utf-8') as f:
        session_content = f.read()
    
    # Validate it's valid JSON
    try:
        json.loads(session_content)
        print("[OK] Session file is valid JSON")
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON: {e}")
        return
    
    # Encode to base64 for easier handling
    encoded = base64.b64encode(session_content.encode('utf-8')).decode('utf-8')
    
    print("\n" + "="*60)
    print("INSTRUCTIONS TO UPLOAD SESSION TO GITHUB:")
    print("="*60)
    print("\nOption 1: Use GitHub CLI (Recommended)")
    print("-" * 60)
    print("1. Install GitHub CLI: https://cli.github.com/")
    print("2. Run this command:")
    print(f"   gh secret set LINKEDIN_SESSION --body '{encoded}'")
    print("\nOption 2: Manual Upload via GitHub UI")
    print("-" * 60)
    print("1. Go to your repo → Settings → Secrets → Actions")
    print("2. Click 'New repository secret'")
    print("3. Name: LINKEDIN_SESSION")
    print("4. Value: (paste the base64 string below)")
    print("\n" + "-" * 60)
    print("BASE64 ENCODED SESSION:")
    print("-" * 60)
    print(encoded)
    print("\n" + "="*60)
    print("\n[NOTE] This is a temporary solution.")
    print("After first successful run, the session will be saved as artifact.")
    print("You can then delete this secret.")

if __name__ == "__main__":
    main()
