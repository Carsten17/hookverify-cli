"""Configuration management for HookVerify CLI."""
import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".hookverify"
CONFIG_FILE = CONFIG_DIR / "credentials.json"


def ensure_config_dir():
    """Create config directory if it doesn't exist."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def save_credentials(api_key: str, api_url: str = "https://hookverify.com"):
    """Save API credentials to config file."""
    ensure_config_dir()
    config = {
        "api_key": api_key,
        "api_url": api_url
    }
    CONFIG_FILE.write_text(json.dumps(config, indent=2))


def load_credentials() -> dict | None:
    """Load API credentials from config file."""
    if not CONFIG_FILE.exists():
        return None
    try:
        return json.loads(CONFIG_FILE.read_text())
    except (json.JSONDecodeError, IOError):
        return None


def clear_credentials():
    """Remove stored credentials."""
    if CONFIG_FILE.exists():
        CONFIG_FILE.unlink()


def get_api_key() -> str | None:
    """Get stored API key."""
    creds = load_credentials()
    return creds.get("api_key") if creds else None


def get_api_url() -> str:
    """Get stored API URL."""
    creds = load_credentials()
    return creds.get("api_url", "https://hookverify.com") if creds else "https://hookverify.com"
    