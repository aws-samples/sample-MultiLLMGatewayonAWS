import time
import logging
from typing import Dict, Any
from fastapi import Request

from ..api.handlers.bedrock_handler import BedrockHandler
from ..api.handlers.openai_handler import OpenAIHandler
from ..utils.bedrock import get_bedrock_models
from ..api.model_utils import validate_model

logger = logging.getLogger(__name__)

class Handler:
    def __init__(self):
        self.handlers = {
            "bedrock": BedrockHandler(),
            "openai": OpenAIHandler()
        }

    async def close(self):
        """Close all handler resources"""
        for handler in self.handlers.values():
            if hasattr(handler, 'aclose'):
                await handler.aclose()

    async def handle_request(self, model_id: str, request: Dict[str, Any],
                           api_key: str, stream: bool = False, raw_request: Request = None):
        """Handle both streaming and non-streaming requests"""
        start_time = time.time()
        request_id = f"req_{int(start_time * 1000)}"
        logger.info(f"[{request_id}] Starting {'streaming ' if stream else ''}request for model: {model_id}")

        validate_model(model_id)

        # Determine handler type based on model
        handler_type = "bedrock" if model_id in get_bedrock_models() else "openai"
        handler = self.handlers[handler_type]

        # Call appropriate handler method
        handler_method = handler.handle_stream if stream else handler.handle_converse
        return await handler_method(model_id, request, api_key, request_id, start_time, raw_request)

# Create single handler instance
handler = Handler()

# Convenience functions
async def handle_converse(*args, **kwargs):
    return await handler.handle_request(*args, **kwargs)

async def handle_converse_stream(*args, **kwargs):
    return await handler.handle_request(*args, stream=True, **kwargs)
