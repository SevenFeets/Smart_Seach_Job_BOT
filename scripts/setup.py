#!/usr/bin/env python3
"""Setup script for LinkedIn Job Bot."""
import os
import sys
import subprocess
from pathlib import Path


def run_command(command, description):
    """Run a shell command."""
    print(f"\n{'='*50}")
    print(f"📦 {description}")
    print(f"{'='*50}")
    result = subprocess.run(command, shell=True)
    return result.returncode == 0


def main():
    """Set up the LinkedIn Job Bot."""
    print("""
    ╔═══════════════════════════════════════════════════════╗
    ║       🤖 LinkedIn Job Bot Setup                       ║
    ╚═══════════════════════════════════════════════════════╝
    """)
    
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # Create virtual environment
    if not Path("venv").exists():
        run_command("python -m venv venv", "Creating virtual environment...")
    
    # Determine activate script
    if sys.platform == "win32":
        activate = "venv\\Scripts\\activate"
        pip = "venv\\Scripts\\pip"
        python = "venv\\Scripts\\python"
    else:
        activate = "source venv/bin/activate"
        pip = "venv/bin/pip"
        python = "venv/bin/python"
    
    # Install dependencies
    run_command(f"{pip} install --upgrade pip", "Upgrading pip...")
    run_command(f"{pip} install -r requirements.txt", "Installing dependencies...")
    
    # Install Playwright browsers
    run_command(f"{python} -m playwright install chromium", "Installing Playwright Chromium...")
    
    # Create directories
    for directory in ["data", "browser_data", "resumes", "logs"]:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Created {directory}/ directory")
    
    # Create .env from example if not exists
    if not Path(".env").exists() and Path("config.example.env").exists():
        import shutil
        shutil.copy("config.example.env", ".env")
        print("✓ Created .env from config.example.env")
    
    print("""
    ╔═══════════════════════════════════════════════════════╗
    ║       ✓ Setup Complete!                               ║
    ╚═══════════════════════════════════════════════════════╝
    
    Next steps:
    1. Edit .env with your LinkedIn credentials
    2. Add your resume to resumes/my_resume.pdf
    3. Run: python main.py search
    
    For full options, run: python main.py --help
    """)


if __name__ == "__main__":
    main()
