# LiteLLM Proxy Service

A FastAPI-based proxy service that provides a unified interface for multiple Language Model providers (Bedrock, OpenAI, etc.). This service standardizes the API interface and handles request routing, authentication, and response processing.

## Features

- Unified API interface for multiple LLM providers
- Support for AWS Bedrock and OpenAI
- Request/Response handling and validation
- Streaming support
- Configurable logging
- Multiple deployment options (Docker, CDK, Terraform)

## Project Structure

```
backend/
├── proxy_litellm/          # Main service implementation
│   ├── api/               # API routes and handlers
│   ├── core/             # Core application logic
│   ├── models/           # Request/Response models
│   └── utils/            # Utility functions
├── deploy/               # Deployment configurations
│   ├── cdk/             # AWS CDK deployment
│   ├── docker/          # Docker deployment
│   └── terraform/       # Terraform deployment
└── logs/                # Application logs
```

## Requirements

- Python 3.8+
- FastAPI
- Uvicorn
- boto3 (for AWS Bedrock)
- Other dependencies listed in requirements.txt

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running Locally

Start the server:

```bash
python -m proxy_litellm
```

The server will start on `http://localhost:8000`

### Docker Deployment

Build and run using Docker:

```bash
cd deploy/docker
docker build -t litellm-proxy .
docker run -p 8000:8000 litellm-proxy
```

### AWS Deployment

The service can be deployed to AWS using either CDK or Terraform. See the respective directories in `deploy/` for detailed instructions.

## Configuration

The service can be configured using environment variables or configuration files:

- `log_conf.yaml`: Logging configuration
- `LITELLM_ENDPOINT`: URL of the LiteLLM service
- `LITELLM_MASTER_KEY`: Master key for the LiteLLM service

## API Documentation

### Health Check
```http
GET /health
```
Returns the health status of the service.

**Response**
```json
{
    "status": "ok"
}
```

### Chat Completion
```http
POST /model/{model_id}/converse
```
Send a chat completion request to a specific model. See https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_Converse.html for detailed API spec.

You need to add your API Key in the following format in header:

```
x-bedrock-api-key=<Your API Key>
```

### Streaming Chat Completion
```http
POST /model/{model_id}/converse-stream
```
Send a streaming chat completion request to a specific model. See https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_ConverseStream.html  for detailed API spec.

You need to add your API Key in the following format in header:

```
x-bedrock-api-key=<Your API Key>
```

### Register for API Key
```http
POST /register
```
Register and generate an API key using AWS credentials.

**Parameters**
Headers OR Body (one of the following):
- Headers:
  - `Authorization`: AWS credential string in the format `Credential=YOUR_AWS_ACCESS_KEY/...`
- Body:
  ```json
  {
      "accesskey": "YOUR_AWS_ACCESS_KEY"
  }
  ```

**Response**
Returns a generated API key from the LiteLLM service.

**Example Response**
```json
{
    "key": "generated-api-key",
    "expires": "expiration-timestamp"
}
```

**Error Responses**
- `400 Bad Request`: Invalid credential format
- `500 Internal Server Error`: LiteLLM configuration issues or key generation failures

## Logging

Logs are written to both console and file:
- Console: Debug level logging
- File: Configurable via log_conf.yaml
