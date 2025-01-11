import logging

from flask import Blueprint

from .handler import WebSocketHandler

ws_bp = Blueprint('ws', __name__)
ws_handler = WebSocketHandler()
logger = logging.getLogger(__name__) 