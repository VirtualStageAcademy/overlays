import datetime
import os

from flask import Flask, jsonify, redirect, request, send_from_directory

from .websocket.routes import ws_bp

app = Flask(__name__)
app.register_blueprint(ws_bp, url_prefix='/ws')

# Configuration
config = {
    'zoom': {
        'client_id': os.getenv('DEV_CLIENT_ID'),
        'client_secret': os.getenv('DEV_CLIENT_SECRET'),
        'redirect_uri': os.getenv('DEV_REDIRECT_URI')
    },
    'environment': 'development'
}

@app.route('/')
def root():
    """Root endpoint returning API information"""
    return jsonify({
        'service': 'Virtual Stage Academy OAuth Server',
        'status': 'online',
        'version': '1.0.0',
        'endpoints': {
            'health': '/health',
            'oauth': '/oauth',
            'websocket': '/ws'
        }
    })

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'environment': config['environment'],
        'timestamp': datetime.datetime.now().isoformat()
    })

@app.route('/oauth/start')
def oauth_start():
    """Start the OAuth flow by redirecting to Zoom"""
    zoom_auth_url = f"https://zoom.us/oauth/authorize?response_type=code&client_id={config['zoom']['client_id']}&redirect_uri={config['zoom']['redirect_uri']}"
    return redirect(zoom_auth_url)

@app.route('/oauth/callback')
def oauth_callback():
    """Handle the OAuth callback from Zoom"""
    code = request.args.get('code')
    if not code:
        return 'No code provided', 400
    
    # For now, just return success
    return jsonify({
        'status': 'success',
        'message': 'Authorization successful'
    })

@app.route('/overlays/<overlay_type>')
def serve_overlay(overlay_type):
    """Serve overlay HTML files from their respective directories"""
    valid_overlays = {
        'chat': 'chat.html',
        'reactions': 'reactions.html',
        'word_cloud': 'word_cloud.html',
        'world_map': 'world_map.html',
        'countdown': 'countdown.html'
    }
    
    if overlay_type in valid_overlays:
        return send_from_directory(
            f'src/frontend/overlays/{overlay_type}', 
            valid_overlays[overlay_type]
        )
    
    return 'Overlay not found', 404

# Add route for shared resources
@app.route('/overlays/shared/<path:filename>')
def serve_shared(filename):
    """Serve shared overlay resources"""
    return send_from_directory('src/frontend/overlays/shared', filename)

if __name__ == '__main__':
    app.run(debug=True)

