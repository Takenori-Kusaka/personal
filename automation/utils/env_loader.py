"""
Environment Variable Loader
Loads environment variables from .env file for configuration

Author: Claude Code Assistant
Date: 2025-10-04
"""

import os
from pathlib import Path
from typing import Optional

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

def load_environment(env_file: Optional[str] = None) -> bool:
    """
    Load environment variables from .env file

    Args:
        env_file: Path to .env file (default: searches for .env in project root)

    Returns:
        True if .env file was loaded, False otherwise
    """
    if not DOTENV_AVAILABLE:
        print("Warning: python-dotenv not installed. Install with: pip install python-dotenv")
        return False

    # If no env_file specified, search for .env in project root
    if env_file is None:
        # Try to find project root
        current_dir = Path(__file__).resolve()
        project_root = None

        # Search up the directory tree for .env file
        for parent in [current_dir] + list(current_dir.parents):
            env_path = parent / ".env"
            if env_path.exists():
                project_root = parent
                env_file = str(env_path)
                break

        # If not found, try default location relative to automation directory
        if project_root is None:
            automation_dir = Path(__file__).parent.parent
            env_path = automation_dir.parent / ".env"
            if env_path.exists():
                env_file = str(env_path)

    # Load environment variables
    if env_file and Path(env_file).exists():
        load_dotenv(env_file, override=True)
        print(f"[OK] Loaded environment variables from: {env_file}")
        return True
    else:
        print("[INFO] No .env file found. Using system environment variables only.")
        return False

def get_required_env(key: str, default: Optional[str] = None) -> str:
    """
    Get required environment variable with fallback

    Args:
        key: Environment variable name
        default: Default value if not found

    Returns:
        Environment variable value

    Raises:
        ValueError: If required variable not found and no default provided
    """
    value = os.getenv(key, default)
    if value is None:
        raise ValueError(
            f"Required environment variable '{key}' not set. "
            f"Please set it in your .env file or system environment."
        )
    return value

def get_bool_env(key: str, default: bool = False) -> bool:
    """
    Get boolean environment variable

    Args:
        key: Environment variable name
        default: Default value if not found

    Returns:
        Boolean value
    """
    value = os.getenv(key, str(default)).lower()
    return value in ("true", "1", "yes", "on")

def get_int_env(key: str, default: int) -> int:
    """
    Get integer environment variable

    Args:
        key: Environment variable name
        default: Default value if not found

    Returns:
        Integer value
    """
    try:
        return int(os.getenv(key, str(default)))
    except ValueError:
        return default

def validate_api_keys() -> dict[str, bool]:
    """
    Validate that required API keys are set

    Returns:
        Dictionary with validation status for each API key
    """
    return {
        "anthropic": bool(os.getenv("ANTHROPIC_API_KEY") or os.getenv("CLAUDE_API_KEY")),
        "perplexity": bool(os.getenv("PERPLEXITY_API_KEY"))
    }

def print_environment_status():
    """Print current environment configuration status"""
    print("\n" + "="*50)
    print("Environment Configuration Status")
    print("="*50)

    # API Keys
    api_keys = validate_api_keys()
    print("\nAPI Keys:")
    print(f"  - Anthropic/Claude: {'[OK] Set' if api_keys['anthropic'] else '[X] Not set'}")
    print(f"  - Perplexity:       {'[OK] Set' if api_keys['perplexity'] else '[X] Not set'}")

    # Configuration
    print("\nConfiguration:")
    print(f"  - Whisper Model: {os.getenv('WHISPER_MODEL', 'default')}")
    print(f"  - Whisper Device: {os.getenv('WHISPER_DEVICE', 'auto')}")
    print(f"  - Test Mode: {get_bool_env('TEST_MODE', False)}")
    print(f"  - Debug Mode: {get_bool_env('DEBUG', False)}")

    # Paths
    print("\nPaths:")
    print(f"  - Digital Garden: {os.getenv('DIGITAL_GARDEN_PATH', 'digital-garden')}")
    print(f"  - Input Path: {os.getenv('INPUT_PATH', 'input')}")
    print(f"  - Log Path: {os.getenv('LOG_FILE_PATH', 'logs/automation.log')}")

    print("\n" + "="*50 + "\n")

# Auto-load .env on import if in test mode or if explicitly enabled
if os.getenv("AUTO_LOAD_ENV", "true").lower() == "true":
    load_environment()