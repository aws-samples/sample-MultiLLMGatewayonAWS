# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
"""
Shows how to use the <noloc>Converse</noloc> API to stream a response from Anthropic Claude 3 Sonnet (on demand).
"""

import logging
import boto3

from botocore.config import Config
from botocore.exceptions import ClientError

config = Config(
   retries = {
      'max_attempts': 1,
      'mode': 'adaptive'
   }
)
boto3.set_stream_logger('')

LITELLM_API_KEY="sk-7654"

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def add_auth_header(model, params, request_signer, **kwargs):
    params['headers']['x-bedrock-api-key'] = LITELLM_API_KEY

def get_bedrock_client():
    bedrock_client = boto3.client(service_name='bedrock-runtime',
                                  endpoint_url='http://127.0.0.1:8000',
                                  config=config)
    event_system = bedrock_client.meta.events
    event_system.register('before-call.*', add_auth_header)
    return bedrock_client

def stream_conversation(bedrock_client,
                    model_id,
                    messages,
                    system_prompts,
                    inference_config,
                    additional_model_fields):
    """
    Sends messages to a model and streams the response.
    Args:
        bedrock_client: The Boto3 Bedrock runtime client.
        model_id (str): The model ID to use.
        messages (JSON) : The messages to send.
        system_prompts (JSON) : The system prompts to send.
        inference_config (JSON) : The inference configuration to use.
        additional_model_fields (JSON) : Additional model fields to use.

    Returns:
        Nothing.

    """

    logger.info("Streaming messages with model %s", model_id)

    response = bedrock_client.converse_stream(
        modelId=model_id,
        messages=messages,
        system=system_prompts,
        inferenceConfig=inference_config,
        additionalModelRequestFields=additional_model_fields
    )

    stream = response.get('stream')
    if stream:
        for event in stream:

            if 'messageStart' in event:
                print(f"\nRole: {event['messageStart']['role']}")

            if 'contentBlockDelta' in event:
                print(event['contentBlockDelta']['delta']['text'], end="")

            if 'messageStop' in event:
                print(f"\nStop reason: {event['messageStop']['stopReason']}")

            if 'metadata' in event:
                metadata = event['metadata']
                if 'usage' in metadata:
                    print("\nToken usage")
                    print(f"Input tokens: {metadata['usage']['inputTokens']}")
                    print(
                        f":Output tokens: {metadata['usage']['outputTokens']}")
                    print(f":Total tokens: {metadata['usage']['totalTokens']}")
                if 'metrics' in event['metadata']:
                    print(
                        f"Latency: {metadata['metrics']['latencyMs']} milliseconds")


def main():
    """
    Entrypoint for streaming message API response example.
    """

    logging.basicConfig(level=logging.INFO,
                        format="%(levelname)s: %(message)s")

    # model_id = "anthropic.claude-3-5-sonnet-20241022-v2:0"
    model_id = "litellm-anthropic.claude-3-5-haiku-20241022-v1:0"
    system_prompt = """You are an app that creates playlists for a radio station
      that plays rock and pop music. Only return song names and the artist."""

    # Message to send to the model.
    input_text = "Create a list of 3 pop songs."

    message = {
        "role": "user",
        "content": [{"text": input_text}]
    }
    messages = [message]

    # System prompts.
    system_prompts = [{"text" : system_prompt}]

    # inference parameters to use.
    temperature = 0.5
    top_k = 200
    # Base inference parameters.
    inference_config = {
        "temperature": temperature
    }
    # Additional model inference parameters.
    additional_model_fields = {"top_k": top_k}

    try:
        bedrock_client = get_bedrock_client()

        stream_conversation(bedrock_client, model_id, messages,
                        system_prompts, inference_config, additional_model_fields)

    except ClientError as err:
        message = err.response['Error']['Message']
        logger.error("A client error occurred: %s", message)
        print("A client error occured: " +
              format(message))

    else:
        print(
            f"Finished streaming messages with model {model_id}.")


if __name__ == "__main__":
    main()
