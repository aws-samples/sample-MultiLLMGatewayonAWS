from fastapi.responses import StreamingResponse
from typing import Dict, Any
import os
import asyncio
import urllib.parse
from fastapi import Request
import logging

from .utils import BaseHandler

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class BedrockHandler(BaseHandler):
    def __init__(self):
        super().__init__()
        self.litellm_endpoint = os.environ.get("LITELLM_ENDPOINT")
        if not self.litellm_endpoint:
            raise ValueError("LITELLM_ENDPOINT environment variable is required")

        # Parse endpoint URL (assuming HTTP)
        url = urllib.parse.urlparse(self.litellm_endpoint)
        self.proxy_host = url.hostname
        self.proxy_port = url.port or 80

    async def _forward_raw(self, request: Request, path: str):
        """Forward raw request through socket"""
        reader, writer = await asyncio.open_connection(self.proxy_host, self.proxy_port)

        try:
            body = await request.body()
            body_len = len(body) if body else 0

            # Forward request line with encoded path
            request_line = f"{request.method} {path} HTTP/1.1\r\n"
            logger.debug(f"Request line: {request_line.strip()}")

            # Get and modify headers
            headers = dict(request.headers)

            # Remove specified headers
            headers.pop('Authorization', None)  # Remove if exists
            headers.pop('X-Amz-Security-Token', None)
            headers.pop('X-Amz-Date', None)

            # Move x-bedrock-api-key to Authorization
            if 'x-bedrock-api-key' in headers:
                headers['Authorization'] = "Bearer " + headers.pop('x-bedrock-api-key')

            # Set host header
            headers["host"] = f"{self.proxy_host}:{self.proxy_port}"

            # Log headers
            logger.debug("Request headers:")
            for k, v in headers.items():
                logger.debug(f"{k}: {v}")

            # Forward request line
            writer.write(request_line.encode())

            # Forward headers
            for k, v in headers.items():
                writer.write(f"{k}: {v}\r\n".encode())
            writer.write(b"\r\n")

            # Forward body
            if body:
                logger.debug(f"Request body ({body_len} bytes): {body.decode()}")
                writer.write(body)
            await writer.drain()

            return reader, writer
        except Exception as e:
            logger.error(f"Error forwarding request: {str(e)}")
            writer.close()
            await writer.wait_closed()
            raise e

    def _encode_path(self, base_path: str, model_id: str) -> str:
        """Encode path components properly"""
        # URL encode model ID
        encoded_model = urllib.parse.quote(model_id, safe='')
        # Construct and encode full path
        path = f"{base_path}/{encoded_model}/converse"
        return path

    async def handle_converse(self, model_id: str, request: Dict[str, Any], api_key: str, request_id: str, start_time: float, raw_request: Request):
        """Forward non-streaming request through proxy"""
        path = self._encode_path("/bedrock/model", model_id)
        logger.debug(f"[{request_id}] Forwarding request to: {path}")

        reader, writer = await self._forward_raw(raw_request, path)

        try:
            # Read response status line
            status_line = await reader.readline()
            status_text = status_line.decode().strip()
            logger.debug(f"[{request_id}] Response status line: {status_text}")
            status = int(status_line.split()[1])

            # Read response headers
            headers = {}
            logger.debug(f"[{request_id}] Response headers:")
            while True:
                line = await reader.readline()
                if line == b"\r\n":
                    break
                if line:
                    header_line = line.decode().strip()
                    logger.debug(f"Header: {header_line}")
                    name, value = header_line.split(": ", 1)
                    headers[name] = value

            # Read response body
            body = await reader.read()
            body_text = body.decode()
            logger.debug(f"[{request_id}] Response body: {body_text}")

            return StreamingResponse(
                [body],
                status_code=status,
                headers=headers
            )
        except Exception as e:
            logger.error(f"[{request_id}] Error handling response: {str(e)}")
            raise
        finally:
            writer.close()
            await writer.wait_closed()

    async def handle_stream(self, model_id: str, request: Dict[str, Any], api_key: str, request_id: str, start_time: float, raw_request: Request):
        """Forward streaming request through proxy"""
        path = self._encode_path("/bedrock/model", model_id)
        path = path.replace("/converse", "/converse-stream")
        logger.debug(f"[{request_id}] Forwarding streaming request to: {path}")

        reader, writer = await self._forward_raw(raw_request, path)

        try:
            # Read response status line
            status_line = await reader.readline()
            status_text = status_line.decode().strip()
            logger.debug(f"[{request_id}] Response status line: {status_text}")
            status = int(status_line.split()[1])

            # Read response headers
            response_headers = {}
            logger.debug(f"[{request_id}] Response headers:")
            while True:
                line = await reader.readline()
                if line == b"\r\n":
                    break
                if line:
                    header_line = line.decode().strip()
                    logger.debug(f"Header: {header_line}")
                    name, value = header_line.split(": ", 1)
                    response_headers[name] = value

            if status >= 400:
                error_body = await reader.read()
                error_text = error_body.decode()
                logger.error(f"[{request_id}] Error response: {error_text}")
                writer.close()
                await writer.wait_closed()
                raise ValueError(f"Proxy returned error status: {status}")

            async def generate():
                try:
                    # Read the response in binary mode without decoding
                    # This preserves the AWS event stream format and checksums
                    buffer = bytearray()
                    chunk_count = 0
                    while True:
                        # Read a smaller chunk to avoid buffering too much
                        chunk = await reader.read(4096)
                        if not chunk:
                            break

                        buffer.extend(chunk)
                        chunk_count += 1

                        # Forward complete event stream messages
                        # This ensures we don't split messages in the middle
                        while len(buffer) >= 12:  # Minimum size for prelude
                            # Parse prelude to get message size
                            total_length = int.from_bytes(buffer[0:4], byteorder='big')

                            # Wait for complete message
                            if len(buffer) < total_length:
                                break

                            # Extract and forward complete message
                            message = buffer[:total_length]
                            buffer = buffer[total_length:]

                            logger.debug(f"[{request_id}] Forwarding message {chunk_count}, size: {len(message)}")
                            yield bytes(message)

                finally:
                    logger.debug(f"[{request_id}] Stream complete after {chunk_count} chunks")
                    writer.close()
                    await writer.wait_closed()

            return StreamingResponse(
                generate(),
                headers=response_headers
            )
        except Exception as e:
            logger.error(f"[{request_id}] Error handling streaming response: {str(e)}")
            raise
