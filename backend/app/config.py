import logging
import os
import sys
from pathlib import Path

from dynaconf import Dynaconf


ROOT = Path(__file__).resolve().parent.parent

# Environment setup
environment = os.environ.get("ENV", "dev")

settings_files = [ROOT / "settings.toml"]
if (ROOT / ".secrets.toml").exists():
    settings_files.append(ROOT / ".secrets.toml")

settings = Dynaconf(
    settings_files=settings_files,  # Property files, order matters.
    environments=True,  # Enable multiple environments (default is False)
    env=environment,  # Set the environment; defaults to 'dev'
    envvar_prefix=False,
)


# Simple logging setup - captures all modules
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
)

logger = logging.getLogger(__name__)
logger.info("Application environment: %s", environment)
logger.info("Settings files loaded: %s", [str(f) for f in settings_files])