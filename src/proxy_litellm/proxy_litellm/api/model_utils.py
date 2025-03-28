import logging
from typing import Dict, Any
from ..models.request_models import ConverseRequest
from ..utils.bedrock import get_bedrock_models

logger = logging.getLogger(__name__)

def validate_model(model_id: str) -> None:
    """Simple check if model is supported, but ignore it since we have a catch-all plan"""
    pass

# Model-specific parameter mappings
MODEL_PARAM_MAPPINGS = {
    "anthropic": {
        "prompt": "prompt",
        "max_tokens": "max_tokens_to_sample",
        "temperature": "temperature",
        "top_p": "top_p",
        "stop_sequences": "stop_sequences"
    }
}

def transform_model_parameters(model_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Transform model parameters to the required format"""
    model_type = next((mtype for mtype in MODEL_PARAM_MAPPINGS if model_id.startswith(mtype)), None)
    if not model_type:
        return params

    mapping = MODEL_PARAM_MAPPINGS[model_type]
    defaults = {
        "prompt": "",
        "max_tokens": 512,
        "temperature": 0.7,
        "top_p": 0.9,
        "stop_sequences": []
    }
    return {mapping[k]: params.get(k, default) for k, default in defaults.items()}

def prepare_inference_config(request: ConverseRequest) -> Dict[str, Any]:
    """Extract inference configuration from request"""
    if not request.inferenceConfig:
        return {}

    config = {
        "temperature": request.inferenceConfig.temperature,
        "max_tokens": request.inferenceConfig.maxTokens,
        "top_p": request.inferenceConfig.topP,
        "stop_sequences": request.inferenceConfig.stopSequences
    }
    return {k: v for k, v in config.items() if v is not None}
