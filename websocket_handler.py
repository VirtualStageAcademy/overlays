import json
import time
import websocket
import yaml
from token_manager import load_tokens, refresh_access_token, save_tokens
from config_loader import get_environment_config  # Dynamically get environment settings

# ======================
# WebSocketHandler Class
# ======================
class WebSocketHandler:
    def __init__(self):
        """
        Initialize the WebSocketHandler with dynamic configuration.
        """
        # Load environment settings
        _, websocket_url = get_environment_config()  # Dynamically fetch the WebSocket URL
        self.websocket_url = websocket_url
        self.token_issue_time = time.time()
        self.token_expiry_time = 3600  # Default token validity (1 hour)
        self.ws = None

    def refresh_token_if_needed(self):
        """
        Refresh the access token if it's about to expire.
        """
        if time.time() - self.token_issue_time >= self.token_expiry_time - 300:  # Refresh 5 minutes before expiry
            print("[INFO] Access token is about to expire. Refreshing...")
            _, refresh_token = load_tokens()
            if refresh_token:
                new_access_token, new_refresh_token = refresh_access_token(refresh_token)
                if new_access_token and new_refresh_token:
                    save_tokens(new_access_token, new_refresh_token)
                    self.token_issue_time = time.time()
                    print("[INFO] Token refreshed successfully.")
                    # Update the WebSocket URL with the new token
                    self.websocket_url = self.websocket_url.split("&access_token=")[0] + f"&access_token={new_access_token}"
                else:
                    raise Exception("[ERROR] Failed to refresh access token.")
            else:
                raise Exception("[ERROR] Missing refresh token. Cannot refresh access token.")

    def connect(self):
        """
        Establish a WebSocket connection.
        """
        self.refresh_token_if_needed()  # Ensure the token is valid before connecting
        print(f"[INFO] Connecting to WebSocket: {self.websocket_url}")
        self.ws = websocket.WebSocketApp(
            self.websocket_url,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        self.ws.on_open = self.on_open
        self.run_forever()
        
    def run_forever(self):
        """
        Run the WebSocket connection and handle reconnections.
        """
        while True:
            try:
                self.ws.run_forever()
            except Exception as e:
                print(f"[WARNING] WebSocket connection closed: {e}. Reconnecting...")
                time.sleep(5)  # Wait before reconnecting
                self.refresh_token_if_needed()
                    
    def on_open(self, ws):
        """
        Called when the WebSocket connection is established.
        """
        print("[INFO] WebSocket connection established.")
    
    def on_message(self, ws, message):
        """
        Called when a message is received from the WebSocket.
        """
        print(f"[INFO] Received message: {message}")
        try:
            data = json.loads(message)
            event = data.get("module", "unknown_event")
            if event == "meeting.chat_message_sent":
                payload = data.get("content", {})
                print(f"[INFO] Chat message: {payload}")
            elif event == "reaction_added":
                payload = data.get("content", {})
                print(f"[INFO] Reaction added: {payload}")
            else:
                print(f"[INFO] Unhandled event type: {event}")
        except json.JSONDecodeError:
            print("[ERROR] Failed to parse message as JSON.")

    def on_error(self, ws, error):
        """
        Called when an error occurs in the WebSocket connection.
        """
        print(f"[ERROR] WebSocket error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        """
        Called when the WebSocket connection is closed.
        """
        print(f"[INFO] WebSocket closed with code: {close_status_code}, message: {close_msg}")
