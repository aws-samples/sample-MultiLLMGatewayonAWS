import json
import time
import logging
import asyncio
from typing import Dict, Any
import aiohttp
from fastapi import HTTPException

class BaseHandler:
    """Base handler class providing common functionality for all API handlers"""

    def __init__(self):
        self._session = None
        self.logger = logging.getLogger(__name__)
        self.timeout = 60.0  # Default timeout of 60 seconds

    @property
    async def session(self):
        """Lazy initialization of aiohttp session"""
        if self._session is None:
            self._session = aiohttp.ClientSession()
        return self._session

    async def aclose(self):
        """Close the aiohttp session if it exists"""
        if self._session is not None:
            await self._session.close()
            self._session = None

    def _handle_error(self, error: Exception, request_id: str):
        """Handle and log errors consistently"""
        error_message = str(error)
        self.logger.error(f"[{request_id}] Error: {error_message}")
        raise HTTPException(status_code=500, detail=f"API error: {error_message}")

    def _log_request(self, request_id: str, request_data: Dict[str, Any]):
        """Log request details"""
        self.logger.debug(f"[{request_id}] Request data: {json.dumps(request_data)}")

    def _log_success(self, request_id: str, start_time: float):
        """Log successful request completion"""
        self.logger.info(f"[{request_id}] Successfully completed request in {time.time() - start_time:.2f}s")

    async def _execute_with_timeout(self, coro, request_id: str):
        """Execute coroutine with timeout"""
        try:
            async with asyncio.timeout(self.timeout):
                return await coro
        except asyncio.TimeoutError:
            self.logger.error(f"[{request_id}] Request timed out after {self.timeout} seconds")
            raise HTTPException(
                status_code=408,
                detail=f"Request timed out after {self.timeout} seconds"
            )
