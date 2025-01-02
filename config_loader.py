import yaml

CONFIG_PATH = "config.yaml"

def load_config():
    with open(CONFIG_PATH, "r") as file:
        config = yaml.safe_load(file)
    return config

# Load the config (example usage)
if __name__ == "__main__":
    config = load_config()
    print("App Name:", config["app"]["name"])
    print("Redirect URI:", config["zoom"]["redirect_uri"])
