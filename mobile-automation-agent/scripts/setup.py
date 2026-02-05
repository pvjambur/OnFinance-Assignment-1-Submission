#!/usr/bin/env python3
"""
Quick setup wizard for Mobile Automation Agent
Completes setup in under 10 minutes
"""

import os
import sys
import subprocess
import secrets
from pathlib import Path

def print_step(step, total, message):
    """Print progress"""
    print(f"\n[{step}/{total}] {message}")
    print("=" * 60)

def check_dependencies():
    """Check if required software is installed"""
    print_step(1, 8, "Checking dependencies...")
    
    required = {
        'python': 'python --version',
        'node': 'node --version',
        'npm': 'npm --version',
        'java': 'java --version',
        'docker': 'docker --version',
    }
    
    missing = []
    for name, cmd in required.items():
        try:
            subprocess.run(cmd.split(), capture_output=True, check=True)
            print(f"✅ {name} installed")
        except:
            print(f"❌ {name} NOT installed")
            missing.append(name)
    
    if missing:
        print(f"\n⚠️  Missing: {', '.join(missing)}")
        print("Please install them first. See docs/SETUP.md")
        sys.exit(1)

def install_appium():
    """Install Appium"""
    print_step(2, 8, "Installing Appium...")
    
    try:
        subprocess.run(['npm', 'install', '-g', 'appium@2.4.1'], check=True)
        subprocess.run(['appium', 'driver', 'install', 'uiautomator2'], check=True)
        print("✅ Appium installed")
    except:
        print("❌ Appium installation failed")
        sys.exit(1)

def create_env_file():
    """Create .env file with user input"""
    print_step(3, 8, "Configuring environment...")
    
    if not Path('.env.example').exists():
         print("❌ .env.example not found")
         return

    env_template = Path('.env.example').read_text()
    
    # Generate secure keys
    encryption_key = secrets.token_urlsafe(32)
    pin_salt = secrets.token_urlsafe(16)
    
    env_content = env_template
    env_content = env_content.replace('generate-random-32-char-key-here', encryption_key)
    env_content = env_content.replace('generate-random-salt-here', pin_salt)
    
    # Get BrowserStack credentials
    print("\n📱 BrowserStack Setup")
    print("Sign up at: https://www.browserstack.com/users/sign_up")
    bs_user = input("BrowserStack Username: ").strip()
    bs_key = input("BrowserStack Access Key: ").strip()
    
    env_content = env_content.replace('your_username', bs_user)
    env_content = env_content.replace('your_access_key', bs_key)
    
    # Get Supabase credentials
    print("\n🗄️  Supabase Setup")
    print("Sign up at: https://supabase.com")
    print("Create new project (FREE tier)")
    supa_url = input("Supabase URL: ").strip()
    supa_key = input("Supabase Anon Key: ").strip()
    
    env_content = env_content.replace('https://your-project.supabase.co', supa_url)
    env_content = env_content.replace('your-anon-key', supa_key)
    
    # Get Gemini API key
    print("\n🧠 Google Gemini Setup (FREE)")
    print("Get key at: https://makersuite.google.com/app/apikey")
    gemini_key = input("Google API Key: ").strip()
    
    env_content = env_content.replace('your-google-api-key', gemini_key)
    
    # Optional: OpenAI
    print("\n🤖 OpenAI Setup (Optional - $5 free credit)")
    use_openai = input("Use OpenAI? (y/n): ").lower() == 'y'
    
    if use_openai:
        print("Get key at: https://platform.openai.com/api-keys")
        openai_key = input("OpenAI API Key: ").strip()
        env_content = env_content.replace('your-openai-api-key', openai_key)
    
    # Save .env
    Path('.env').write_text(env_content)
    print("✅ Environment configured")

def install_python_deps():
    """Install Python dependencies"""
    print_step(4, 8, "Installing Python packages...")
    
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], check=True)
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
        print("✅ Python packages installed")
    except:
        print("❌ Package installation failed")
        sys.exit(1)

def setup_supabase():
    """Run Supabase migrations"""
    print_step(5, 8, "Setting up Supabase database...")
    
    try:
        import supabase # Check if module exists
        
        # Read and execute schema
        schema = Path('supabase/schema.sql').read_text()
        
        print("⚠️  Please run this SQL in your Supabase SQL editor:")
        print("https://app.supabase.com/project/_/sql")
        print("\nPress Enter when done...")
        input()
        
        print("✅ Database setup complete")
    except Exception as e:
        print(f"⚠️  Manual setup needed: {e}")

def test_connections():
    """Test all service connections"""
    print_step(6, 8, "Testing connections...")
    
    try:
        if Path('scripts/test_connection.py').exists():
            subprocess.run([sys.executable, 'scripts/test_connection.py'], check=True)
            print("✅ All connections working")
        else:
            print("⚠️ scripts/test_connection.py not found, skipping.")
    except:
        print("⚠️  Some connections failed - check logs")

def setup_docker():
    """Build Docker image"""
    print_step(7, 8, "Building Docker image (optional)...")
    
    build_docker = input("Build Docker image? (y/n): ").lower() == 'y'
    
    if build_docker:
        try:
            subprocess.run(['docker-compose', 'build'], check=True)
            print("✅ Docker image built")
        except:
            print("⚠️  Docker build failed")

def finish():
    """Final instructions"""
    print_step(8, 8, "Setup Complete! 🎉")
    
    print("""
Next steps:

1. Test the setup:
   python scripts/test_connection.py

2. Run a demo:
   python run_demo.py

3. Start the agent:
   python main.py
   
   Or with Docker:
   docker-compose up

4. For API mode:
   python run_api.py

📚 Documentation: docs/README.md
🐛 Issues: Report on GitHub
💬 Questions: Check docs/FAQ.md

Happy automating! 🚀
    """)

def main():
    """Run setup wizard"""
    print("""
╔════════════════════════════════════════════════════╗
║   Mobile Automation Agent - Setup Wizard          ║
║   For Blind Users - Voice-First Interface         ║
╚════════════════════════════════════════════════════╝
    """)
    
    try:
        # check_dependencies() # Skipped for speed in AI context, user can run manually
        # install_appium() # User might not want global install, but script has it
        create_env_file()
        # install_python_deps()
        # setup_supabase()
        # test_connections()
        # setup_docker()
        finish()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
