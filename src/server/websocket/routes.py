import logging

from flask import Blueprint, jsonify, render_template_string, request

from .handler import WebSocketHandler

ws_bp = Blueprint('ws', __name__)
ws_handler = WebSocketHandler()
logger = logging.getLogger(__name__)

@ws_bp.route('/status')
async def ws_status():
    """Check WebSocket connection status"""
    status = ws_handler.get_connection_status()
    return jsonify({
        'status': 'active' if status else 'inactive',
        'connections': ws_handler.get_active_connections()
    })

@ws_bp.route('/test')
async def ws_test():
    """Serve WebSocket test page"""
    # Get the current host from request
    ws_protocol = 'wss' if request.is_secure else 'ws'
    ws_host = request.headers.get('Host', 'localhost:5000')
    ws_url = f'{ws_protocol}://{ws_host}/ws'

    return render_template_string('''
        <html>
            <head><title>WebSocket Test</title></head>
            <body>
                <h2>WebSocket Test</h2>
                <div id="status">Status: Disconnected</div>
                <div id="messages"></div>
                <input type="text" id="messageInput" placeholder="Type a message">
                <button onclick="sendMessage()">Send</button>
                
                <script>
                    const ws = new WebSocket('{{ ws_url }}');
                    const status = document.getElementById('status');
                    const messages = document.getElementById('messages');
                    
                    ws.onopen = () => {
                        status.textContent = 'Status: Connected';
                        console.log('Connected!');
                    };
                    
                    ws.onmessage = (event) => {
                        messages.innerHTML += `<p>Received: ${event.data}</p>`;
                        console.log('Received:', event.data);
                    };
                    
                    ws.onerror = (error) => {
                        status.textContent = 'Status: Error';
                        console.log('Error:', error);
                    };
                    
                    function sendMessage() {
                        const input = document.getElementById('messageInput');
                        ws.send(input.value);
                        messages.innerHTML += `<p>Sent: ${input.value}</p>`;
                        input.value = '';
                    }
                </script>
            </body>
        </html>
    ''', ws_url=ws_url)

@ws_bp.route('/ws')
async def ws(websocket):
    """Handle WebSocket connections"""
    try:
        await ws_handler.handle_websocket(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
