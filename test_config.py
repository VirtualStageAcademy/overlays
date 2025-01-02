import yaml

CONFIG_PATH = "config.yaml"  # Adjust path if needed

# Load the YAML configuration
with open(CONFIG_PATH, 'r') as config_file:
    config = yaml.safe_load(config_file)

# Print configurations to verify
print("App Name:", config['app']['name'])
print("Zoom Client ID:", config['zoom']['client_id'])
print("Redirect URI:", config['zoom']['redirect_uri'])
print("Webhook Endpoint:", config['webhook']['endpoint'])
