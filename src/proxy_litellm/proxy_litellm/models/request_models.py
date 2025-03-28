from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel

class ContentBlock(BaseModel):
    text: Optional[str] = None
    image: Optional[Dict] = None
    document: Optional[Dict] = None
    video: Optional[Dict] = None
    toolUse: Optional[Dict] = None
    toolResult: Optional[Dict] = None
    guardContent: Optional[Dict] = None

class Message(BaseModel):
    role: str
    content: Union[str, List[ContentBlock], List[Dict[str, Any]]]

class SystemBlock(BaseModel):
    text: str
    guardContent: Optional[Dict] = None

class InferenceConfig(BaseModel):
    maxTokens: Optional[int] = None
    temperature: Optional[float] = None
    topP: Optional[float] = None
    stopSequences: Optional[List[str]] = None

class ToolConfig(BaseModel):
    tools: Optional[List[Dict]] = None
    toolChoice: Optional[Dict] = None

class GuardrailConfig(BaseModel):
    guardrailIdentifier: Optional[str] = None
    guardrailVersion: Optional[str] = None
    trace: Optional[str] = None

class PerformanceConfig(BaseModel):
    latency: Optional[str] = None

class ConverseRequest(BaseModel):
    messages: List[Message]
    system: Optional[List[SystemBlock]] = None
    inferenceConfig: Optional[InferenceConfig] = None
    toolConfig: Optional[ToolConfig] = None
    guardrailConfig: Optional[GuardrailConfig] = None
    additionalModelRequestFields: Optional[Dict[str, Any]] = None
    promptVariables: Optional[Dict[str, Dict[str, str]]] = None
    additionalModelResponseFieldPaths: Optional[List[str]] = None
    requestMetadata: Optional[Dict[str, str]] = None
    performanceConfig: Optional[PerformanceConfig] = None
