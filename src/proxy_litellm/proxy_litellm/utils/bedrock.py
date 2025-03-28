import os
import logging
import boto3
from functools import lru_cache

logger = logging.getLogger(__name__)

@lru_cache()
def get_bedrock_models():
    """Get list of available Bedrock models"""
    bedrock_client = boto3.client(
        'bedrock',
        region_name=os.environ.get("AWS_REGION_NAME", "us-west-2")
    )
    response = bedrock_client.list_foundation_models()
    return {model['modelId']: model for model in response['modelSummaries']}
