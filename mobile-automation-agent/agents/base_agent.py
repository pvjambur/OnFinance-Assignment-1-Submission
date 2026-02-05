from abc import ABC, abstractmethod
from typing import Dict, Any
import logging
import yaml
from pathlib import Path
from config.settings import settings

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    def __init__(self, config_name: str):
        self.config_name = config_name
        self.config = self._load_config()
        self.system_prompt = self.config.get('system_prompt', '')

    def _load_config(self) -> Dict[str, Any]:
        """Load YAML config for this agent"""
        config_path = settings.AGENT_CONFIG_DIR / f"{self.config_name}.yaml"
        if not config_path.exists():
            logger.warning(f"Config not found: {config_path}")
            return {}
            
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    @abstractmethod
    def run(self, input_data: Any) -> Dict[str, Any]:
        """Execute agent logic"""
        pass
