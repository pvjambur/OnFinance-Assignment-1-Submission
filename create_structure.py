import os
from pathlib import Path

# Root directory
ROOT_DIR = Path('mobile-automation-agent')

# Directory Structure
DIRECTORIES = [
    "docker",
    "config",
    "agents",
    "supabase/migrations",
    "supabase/functions",
    "models",
    "core",
    "strategies",
    "clients",
    "services",
    "utils",
    "security",
    "api/routes",
    "api/schemas",
    "websocket",
    "tests",
    "fixtures/sample_screens",
    "fixtures/mock_responses",
    "scripts",
    "examples",
    "docs",
    "diagrams"
]

# File Map: path -> content (empty for now, or basic template)
FILES = {
    # Docker & Deployment
    "Dockerfile": "# Dockerfile\nFROM python:3.11-slim\n",
    "docker-compose.yml": "# docker-compose.yml\nversion: '3.8'\n",
    ".dockerignore": "__pycache__\n*.pyc\n.env\n",
    "docker/redis.conf": "",
    "docker/nginx.conf": "",

    # Configuration
    ".env.example": "APP_ENV=development\n",
    "config/__init__.py": "",
    "config/settings.py": "",
    "config/logging_config.py": "",
    "config/constants.py": "",
    
    # Agents (Config + Logic merged into 'agents' folder as discussed)
    # YAMLs
    "agents/intent_agent.yaml": "",
    "agents/vision_agent.yaml": "",
    "agents/action_agent.yaml": "",
    "agents/auth_agent.yaml": "",
    # Python
    "agents/__init__.py": "",
    "agents/base_agent.py": "",
    "agents/intent_agent.py": "",
    "agents/vision_agent.py": "",
    "agents/action_agent.py": "",
    "agents/auth_agent.py": "",

    # Database
    "supabase/migrations/001_initial_schema.sql": "",
    "supabase/migrations/002_credentials_table.sql": "",
    "supabase/migrations/003_task_history.sql": "",
    "supabase/functions/encrypt_credential.sql": "",
    "supabase/schema.sql": "",
    
    # Models
    "models/__init__.py": "",
    "models/user.py": "",
    "models/credential.py": "",
    "models/task.py": "",
    "models/session.py": "",

    # Core System
    "core/__init__.py": "",
    "core/voice_interface.py": "",
    "core/task_analyzer.py": "",
    "core/screen_analyzer.py": "",
    "core/action_executor.py": "",
    "core/credential_manager.py": "",
    "core/orchestrator.py": "",
    
    # Strategies
    "strategies/__init__.py": "",
    "strategies/detection.py": "",
    "strategies/navigation.py": "",
    "strategies/authentication.py": "",
    "strategies/validation.py": "",

    # Integration Layer
    "clients/__init__.py": "",
    "clients/browserstack.py": "",
    "clients/supabase_client.py": "",
    "clients/gemini_client.py": "",
    "clients/openai_client.py": "",
    "clients/redis_client.py": "",
    
    "services/__init__.py": "",
    "services/device_service.py": "",
    "services/storage_service.py": "",
    "services/queue_service.py": "",

    # Security & Utils
    "utils/__init__.py": "",
    "utils/logger.py": "",
    "utils/encryption.py": "",
    "utils/validators.py": "",
    "utils/helpers.py": "",
    
    "security/__init__.py": "",
    "security/pin_manager.py": "",
    "security/secret_masking.py": "",

    # API
    "api/__init__.py": "",
    "api/main.py": "",
    "api/routes/__init__.py": "",
    "api/routes/tasks.py": "",
    "api/routes/auth.py": "",
    "api/routes/health.py": "",
    "api/schemas/__init__.py": "",
    "api/schemas/task.py": "",
    "api/schemas/response.py": "",
    "websocket/handler.py": "",

    # Testing
    "tests/__init__.py": "",
    "tests/test_voice.py": "",
    "tests/test_analyzer.py": "",
    "tests/test_executor.py": "",
    "tests/test_integration.py": "",

    # Scripts
    "scripts/setup.py": "",
    "scripts/credential_setup.py": "",
    "scripts/test_connection.py": "",
    "scripts/migrate_db.py": "",
    
    "examples/demo_chatgpt.py": "",
    "examples/demo_whatsapp.py": "",
    "examples/demo_browser.py": "",

    # Docs
    "docs/README.md": "",
    "docs/SETUP.md": "",
    "docs/ARCHITECTURE.md": "",
    "docs/API.md": "",
    "docs/SECURITY.md": "",
    "diagrams/architecture.png": "", # Will be empty files
    "diagrams/flow.png": "",

    # Dependencies
    "requirements.txt": "",
    "requirements-dev.txt": "",
    "pyproject.toml": "",

    # Entry Points (Root)
    "main.py": "",
    "run_api.py": "",
    "run_demo.py": "",

    # Project Files (Root)
    ".gitignore": "",
    "README.md": "",
    "LICENSE": "",
    "CHANGELOG.md": ""
}

def create_project():
    print(f"Creating project in {ROOT_DIR}...")
    
    if not ROOT_DIR.exists():
        ROOT_DIR.mkdir()

    # Create Directories
    for folder in DIRECTORIES:
        path = ROOT_DIR / folder
        path.mkdir(parents=True, exist_ok=True)
        print(f"📁 Created: {path}")

    # Create Files
    for file_path, content in FILES.items():
        path = ROOT_DIR / file_path
        # Ensure parent exists (for root files mostly)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        if not path.exists():
            path.write_text(content, encoding='utf-8')
            print(f"📄 Created: {path}")
        else:
            print(f"⏩ Skipped (exists): {path}")

    print("\n✅ Project structure created successfully!")

if __name__ == "__main__":
    create_project()
