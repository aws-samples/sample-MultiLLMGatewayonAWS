from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Annotated
import os
import httpx
import re

from ..models.request_models import ConverseRequest
from .auth import get_api_key
from ..core.handler import handler

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check endpoint that returns 200 OK if the service is running."""
    return {"status": "ok"}

@router.post("/model/{model_id}/converse")
async def converse(
    model_id: str,
    request: ConverseRequest,
    api_key: Annotated[str, Depends(get_api_key)],
    raw_request: Request
):
    return await handler.handle_request(model_id, request.dict(), api_key, raw_request=raw_request)

@router.post("/model/{model_id}/converse-stream")
async def converse_stream(
    model_id: str,
    request: ConverseRequest,
    api_key: Annotated[str, Depends(get_api_key)],
    raw_request: Request
):
    return await handler.handle_request(model_id, request.dict(), api_key, stream=True, raw_request=raw_request)

@router.post("/register")
async def register(request: Request):
    """Register endpoint that generates a key based on AWS credentials."""
    # Get the Credential header
    credential = request.headers.get("Authorization")
    if credential:
        # Extract AWS access key from credential header
        try:
            # Split by 'Credential=' and get the second part
            credential_part = credential.split('Credential=')[1]
            # Split by '/' and get the first part (access key)
            aws_access_key = credential_part.split('/')[0]
        except (IndexError, AttributeError):
            raise HTTPException(status_code=400, detail="Invalid credential format")
    else:
        # Fetch accesskey from body
        try:
            body = await request.json()
            aws_access_key = body.get('accesskey')
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid credential format")

    # Get litellm configuration from environment
    litellm_endpoint = os.getenv("LITELLM_ENDPOINT")
    litellm_master_key = os.getenv("LITELLM_MASTER_KEY")

    if not litellm_endpoint or not litellm_master_key:
        raise HTTPException(
            status_code=500,
            detail="LiteLLM configuration is not properly set"
        )

    # Call litellm key generation endpoint
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{litellm_endpoint}/key/generate",
                headers={
                    "Authorization": f"Bearer {litellm_master_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "user_id": aws_access_key
                }
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate key: {str(e)}"
        )
