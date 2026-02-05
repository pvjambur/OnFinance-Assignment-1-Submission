import sys
import os
from dotenv import load_dotenv

# Load env before imports if possible, though settings handles it
load_dotenv()

from config.logging_config import configure_logging
from core.orchestrator import orchestrator

def main():
    configure_logging()
    
    try:
        orchestrator.start()
    except KeyboardInterrupt:
        print("\nSee you next time!")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
