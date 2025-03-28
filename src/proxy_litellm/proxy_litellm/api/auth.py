from typing import Annotated
from fastapi import Header, HTTPException

async def get_api_key(x_bedrock_api_key: Annotated[str, Header()] = None) -> str:
    """Validate and return the API key from request header"""
    if not x_bedrock_api_key:
        raise HTTPException(
            status_code=401,
            detail="x-bedrock-api-key header is required"
        )
    return x_bedrock_api_key
