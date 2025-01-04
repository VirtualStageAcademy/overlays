import yaml
import os

CONFIG_PATH = "config.yaml"

# Custom YAML constructor for !ENV tag
def env_constructor(loader, node):
    value = loader.construct_scalar(node)
    return os.getenv(value)  # Return the value of the environment variable

# Register the custom constructor for !ENV tag
yaml.add_constructor('!ENV', env_constructor)

def load_config():
    """
    Load the YAML configuration file and return the parsed config.
    """
    try:
        with open(CONFIG_PATH, "r") as file:
            config = yaml.safe_load(file)
        validate_config(config)  # Validate configuration structure
        return config
    except FileNotFoundError:
        print("[ERROR] config.yaml not found.")
        raise
    except yaml.YAMLError as e:
        print(f"[ERROR] Failed to parse config.yaml: {e}")
        raise

def validate_config(config):
    """
    Validate the structure of the configuration.
    """
    if "app" not in config or "environment" not in config["app"]:
        raise ValueError("Missing 'environment' under 'app' in config.yaml")
    if "websocket" not in config:
        raise ValueError("Missing 'websocket' settings in config.yaml")

def get_environment_config():
    """
    Load the configuration for the current environment.
    """
    config = load_config()
    active_env = config["app"]["environment"]

    # Validate environment
    if active_env not in config["websocket"]:
        raise ValueError(f"Invalid environment '{active_env}' in config.yaml")

    return config, config["websocket"][active_env]["url"]

# ==========================
# Example Usage
# ==========================
if __name__ == "__main__":
    # Load full configuration
    try:
        config = load_config()
        print("[INFO] App Name:", config["app"]["name"])
        print("[INFO] Redirect URI:", config["zoom"]["redirect_uri"])
    except Exception as e:
        print(f"[ERROR] {e}")

    # Load current environment and WebSocket URL
    try:
        _, websocket_url = get_environment_config()
        print("[INFO] Current WebSocket URL:", websocket_url)
    except Exception as e:
        print(f"[ERROR] {e}")
