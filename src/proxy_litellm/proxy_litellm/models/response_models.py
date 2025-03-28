from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from .request_models import ContentBlock, PerformanceConfig

class ResponseMessage(BaseModel):
    role: str
    content: List[ContentBlock]

class ConverseOutput(BaseModel):
    message: ResponseMessage

class TokenUsage(BaseModel):
    inputTokens: int
    outputTokens: int
    totalTokens: int

class Metrics(BaseModel):
    latencyMs: int

class ConverseResponse(BaseModel):
    output: ConverseOutput
    stopReason: str = "end_turn"
    usage: TokenUsage
    metrics: Metrics
    additionalModelResponseFields: Optional[Dict[str, Any]] = None
    trace: Optional[Dict[str, Any]] = None
    performanceConfig: Optional[PerformanceConfig] = None
