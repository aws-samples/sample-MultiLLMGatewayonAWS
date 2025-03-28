from typing import Dict, Any, Optional, AsyncGenerator, Union, Tuple
import json
import os
import time
import logging
from fastapi.responses import StreamingResponse
from fastapi import Request, HTTPException
from .utils import BaseHandler
from proxy_litellm.utils.eventstream import EventStreamMessageEncoder

OPENAI_API_URL = os.environ.get("OPENAI_API_URL", "http://127.0.0.1:4000/v1/chat/completions")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class OpenAIHandler(BaseHandler):
    def _create_event_message(self, headers: Dict[str, str], payload: Dict[str, Any], request_id: str) -> bytes:
        """Create an event message with proper checksums using AWS event stream wire format.

        Args:
            headers: Event headers
            payload: Event payload
            request_id: Request ID for logging

        Returns:
            Bytes containing the complete event message
        """
        logger.debug(f"[{request_id}] Creating event message with headers: {headers}, payload: {payload}")
        return EventStreamMessageEncoder.encode(headers, payload)

    def _convert_bedrock_to_openai(self, bedrock_request: Dict[str, Any], model_id: str) -> Dict[str, Any]:
        """Convert Bedrock request format to OpenAI format

        Args:
            bedrock_request: The original Bedrock-formatted request
            model_id: The model identifier to use

        Returns:
            Dict containing the OpenAI-formatted request
        """
        # Clean up messages by removing None values
        messages = bedrock_request.get("messages", [{
            "role": "user",
            "content": bedrock_request.get("prompt", "")
        }])

        # Clean up message content
        for msg in messages:
            if isinstance(msg.get("content"), list):
                # If content is a list of content items, extract just the text
                msg["content"] = next((
                    item.get("text") for item in msg["content"]
                    if isinstance(item, dict) and item.get("text")
                ), "")

        # Build request without None values
        request = {
            "model": model_id,
            "messages": messages
        }

        # Add optional parameters only if they exist
        if "temperature" in bedrock_request:
            request["temperature"] = bedrock_request["temperature"]
        if "max_tokens" in bedrock_request:
            request["max_tokens"] = bedrock_request["max_tokens"]
        if "stream" in bedrock_request:
            request["stream"] = bedrock_request["stream"]
            
        # Extract parameters from inferenceConfig if present
        inference_config = bedrock_request.get("inferenceConfig", {})
        if inference_config:
            logger.debug(f"Found inferenceConfig: {inference_config}")
            if "temperature" in inference_config:
                request["temperature"] = inference_config["temperature"]
            if "maxTokens" in inference_config:
                request["max_tokens"] = inference_config["maxTokens"]
            if "topP" in inference_config:
                request["top_p"] = inference_config["topP"]
            if "stopSequences" in inference_config:
                request["stop"] = inference_config["stopSequences"]

        return request

    def _convert_to_bedrock_response(self, openai_response: Dict[str, Any], start_time: float) -> Dict[str, Any]:
        """Convert OpenAI response format to Bedrock format

        Args:
            openai_response: The response from OpenAI API
            start_time: The timestamp when request started

        Returns:
            Dict containing the Bedrock-formatted response
        """
        # Extract message from first choice
        choice = openai_response["choices"][0] if openai_response["choices"] else {}
        message = choice.get("message", {})

        # Build output with message structure
        output = {
            "message": {
                "role": message.get("role", "assistant"),
                "content": [{"text": message.get("content", "")}]
            }
        }

        # Calculate elapsed time in milliseconds
        elapsed_ms = int((time.time() - start_time) * 1000)

        # Basic Bedrock response structure
        bedrock_response = {
            "output": output,
            "stopReason": openai_response["choices"][0]["finish_reason"] if openai_response["choices"] else "stop",
            "metrics": {
                "latencyMs": elapsed_ms
            },
            "usage": {
                "inputTokens": openai_response["usage"]["prompt_tokens"],
                "outputTokens": openai_response["usage"]["completion_tokens"],
                "totalTokens": openai_response["usage"]["total_tokens"]
            },
            "performanceConfig": {
                "latency": "low"  # Default value
            },
            "trace": {
                "promptRouter": {
                    "invokedModelId": openai_response["model"]
                }
            },
            # Preserve original OpenAI fields that might be useful
            "additionalModelResponseFields": {
                "id": openai_response.get("id"),
                "created": openai_response.get("created"),
                "model": openai_response.get("model"),
                "system_fingerprint": openai_response.get("system_fingerprint"),
                "object": openai_response.get("object"),
                # Preserve function/tool calls if present
                "function_call": openai_response["choices"][0]["message"].get("function_call") if openai_response["choices"] else None,
                "tool_calls": openai_response["choices"][0]["message"].get("tool_calls") if openai_response["choices"] else None
            }
        }
        return bedrock_response

    def _generate_random_string(self, length: int = 32) -> str:
        """Generate a random string for the 'p' field

        Args:
            length: Length of the random string to generate

        Returns:
            A random string of specified length
        """
        import random
        import string
        return ''.join(random.choices(string.ascii_letters, k=length))

    def _convert_to_bedrock_stream_chunk(self, chunk: Dict[str, Any], start_time: float) -> Union[Dict[str, Any], list[Dict[str, Any]], None]:
        """Convert OpenAI stream chunk to Bedrock format

        Args:
            chunk: The chunk from OpenAI streaming response
            start_time: The timestamp when request started

        Returns:
            A single chunk or list of chunks in Bedrock format, or None if chunk should be skipped
        """
        if not chunk.get("choices"):
            return None

        delta = chunk["choices"][0].get("delta", {})
        content = delta.get("content", "")
        finish_reason = chunk["choices"][0].get("finish_reason")
        index = chunk["choices"][0].get("index", 0)

        # If this is the first chunk with role, send messageStart
        if delta.get("role"):
            return {
                "p": self._generate_random_string(),
                "role": delta["role"]
            }

        # For content, send contentBlockDelta
        if content:
            return {
                "contentBlockIndex": index,
                "delta": {
                    "text": content
                },
                "p": self._generate_random_string()
            }

        # If we have a finish reason, return multiple chunks
        if finish_reason:
            elapsed_ms = int((time.time() - start_time) * 1000)
            return [
                # ContentBlockStop
                {
                    "contentBlockIndex": index,
                    "p": self._generate_random_string()
                },
                # MessageStop
                {
                    "p": self._generate_random_string(),
                    "stopReason": finish_reason
                },
                # Metadata
                {
                    "p": self._generate_random_string(),
                    "metrics": {
                        "latencyMs": elapsed_ms
                    },
                    "usage": {
                        "inputTokens": chunk.get("usage", {}).get("prompt_tokens", 0),
                        "outputTokens": chunk.get("usage", {}).get("completion_tokens", 0),
                        "totalTokens": chunk.get("usage", {}).get("total_tokens", 0)
                    }
                }
            ]

        return None

    def _extract_aws_access_key(self, request: Dict[str, Any]) -> Optional[str]:
        """Extract AWS access key from request credentials

        Args:
            request: The request dictionary that may contain credentials

        Returns:
            The AWS access key if found, None otherwise
        """
        # Check both Authorization and Credential fields
        credential = request.get("Authorization") or request.get("Credential")
        if not credential:
            return None

        try:
            # Handle both formats: "Credential=KEY/..." and "KEY/..."
            if "Credential=" in credential:
                credential = credential.split("Credential=")[1]
            return credential.split("/")[0]
        except (IndexError, AttributeError):
            logger.warning("Failed to extract AWS access key from credential")
            return None

    def _handle_error(self, error: Exception, request_id: str) -> None:
        """Log error and raise appropriate HTTP exception

        Args:
            error: The exception that occurred
            request_id: The ID of the request for logging

        Raises:
            HTTPException with appropriate status code and details
        """
        error_msg = str(error)
        logger.error(f"Request {request_id} failed: {error_msg}")

        if "401" in error_msg:
            raise HTTPException(status_code=401, detail="Unauthorized")
        elif "403" in error_msg:
            raise HTTPException(status_code=403, detail="Forbidden")
        elif "404" in error_msg:
            raise HTTPException(status_code=404, detail="Not Found")
        else:
            raise HTTPException(status_code=500, detail=f"OpenAI API Error: {error_msg}")

    def _log_request(self, request_id: str, request: Dict[str, Any]) -> None:
        """Log request details

        Args:
            request_id: The ID of the request
            request: The request being made
        """
        logger.info(f"Request {request_id}: Making request to OpenAI API",
                   extra={"model": request.get("model"), "stream": request.get("stream", False)})

    def _log_success(self, request_id: str, start_time: float) -> None:
        """Log successful request completion

        Args:
            request_id: The ID of the request
            start_time: When the request started
        """
        elapsed = time.time() - start_time
        logger.info(f"Request {request_id}: Completed successfully in {elapsed:.2f}s")

    def _prepare_headers(self, api_key: str, request: Dict[str, Any]) -> Dict[str, str]:
        """Prepare headers for the request

        Args:
            api_key: The API key to use
            request: The request that may contain AWS credentials

        Returns:
            Dict containing the prepared headers
        """
        if api_key.startswith("Bearer "):
            api_key = api_key[7:]
        headers = {"Authorization": "Bearer " + api_key}
        aws_access_key = self._extract_aws_access_key(request)
        if aws_access_key:
            headers["x-aws-accesskey"] = aws_access_key
        return headers

    async def handle_converse(self, model_id: str, request: Dict[str, Any],
                            api_key: str, request_id: str, start_time: float, raw_request: Request):
        """Handle non-streaming conversation requests"""
        openai_request = self._convert_bedrock_to_openai(request, model_id)
        self._log_request(request_id, openai_request)

        headers = self._prepare_headers(api_key, request)

        try:
            session = await self.session
            async with session.post(
                OPENAI_API_URL,
                headers=headers,
                json=openai_request
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise ValueError(error_text)

                data = await response.json()
                self._log_success(request_id, start_time)
                return self._convert_to_bedrock_response(data, start_time)

        except Exception as e:
            self._handle_error(e, request_id)

    async def handle_stream(self, model_id: str, request: Dict[str, Any],
                          api_key: str, request_id: str, start_time: float, raw_request: Request):
        """Handle streaming conversation requests"""
        openai_request = self._convert_bedrock_to_openai(request, model_id)
        openai_request["stream"] = True
        self._log_request(request_id, openai_request)

        headers = self._prepare_headers(api_key, request)

        async def generate():
            try:
                session = await self.session
                async with session.post(
                    OPENAI_API_URL,
                    headers=headers,
                    json=openai_request
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        self._handle_error(ValueError(error_text), request_id)

                    async for line in response.content:
                        if line.startswith(b"data: "):
                            chunk = line[6:].strip()
                            if chunk == b"[DONE]":
                                self._log_success(request_id, start_time)
                                break

                            try:
                                data = json.loads(chunk)
                                bedrock_chunks = self._convert_to_bedrock_stream_chunk(data, start_time)

                                # Handle multiple chunks or single chunk
                                chunks_to_process = (
                                    bedrock_chunks if isinstance(bedrock_chunks, list)
                                    else [bedrock_chunks] if bedrock_chunks
                                    else []
                                )

                                for chunk in chunks_to_process:
                                    # Create event headers
                                    event_headers = {
                                        ":event-type": (
                                            "messageStart" if "role" in chunk
                                            else "contentBlockStop" if "contentBlockIndex" in chunk and "delta" not in chunk
                                            else "messageStop" if "stopReason" in chunk
                                            else "metadata" if "metrics" in chunk
                                            else "contentBlockDelta"
                                        ),
                                        ":content-type": "application/json",
                                        ":message-type": "event"
                                    }

                                    # Create event message with checksums
                                    event_message = self._create_event_message(event_headers, chunk, request_id)
                                    yield event_message

                            except json.JSONDecodeError as e:
                                logger.warning(f"Failed to decode JSON chunk in stream: {e}")
                                continue

            except Exception as e:
                self._handle_error(e, request_id)

        return StreamingResponse(
            generate(),
            media_type="application/vnd.amazon.eventstream",
            headers={
                "Transfer-Encoding": "chunked",
                "Connection": "keep-alive",
                "x-amzn-RequestId": request_id,
                "Content-Type": "application/vnd.amazon.eventstream"  # Ensure proper content type
            }
        )
