import yaml

CONFIG_PATH = "config.yaml"

def load_config():
    """
    Load the YAML configuration file and return the parsed config.
    """
    with open(CONFIG_PATH, "r") as file:
        config = yaml.safe_load(file)
    return config

def get_environment_config():
    """
    Load the configuration for the current environment.
    """
    config = load_config()
    environment = config["app"]["environment"]
    return config, config["websocket"][environment]["url"]

# Example usage
if __name__ == "__main__":
    # Load full configuration
    config = load_config()
    print("App Name:", config["app"]["name"])
    print("Redirect URI:", config["zoom"]["redirect_uri"])

    # Load current environment and WebSocket URL
    _, websocket_url = get_environment_config()
    print("Current WebSocket URL:", websocket_url)
