"use client";
import {
  ContentLayout,
  Container,
  Header,
  BreadcrumbGroup,
  FormField,
  PromptInput,
  Button,
  Toggle,
  Autosuggest,
} from "@cloudscape-design/components";
import { useState } from "react";
import Messages from "./messages";
import { ScrollableContainer } from "./common";
import { INITIAL_MESSAGES, Message } from "./config";
import {
  BedrockRuntimeClient,
  ConverseCommand,
  ConverseStreamCommand,
} from "@aws-sdk/client-bedrock-runtime";
import {
  LOCAL_STORAGE_AK_NAME,
  LOCAL_STORAGE_BEDROCK_API_KEY_NAME,
  LOCAL_STORAGE_ENDPOINT_NAME,
  LOCAL_STORAGE_SK_NAME,
} from "../consts";

const KNOWN_MODEL_IDS = ["anthropic.claude-3-haiku-20240307-v1:0"];

export default function Chat() {
  const [streaming, setStreaming] = useState(true);
  const [prompt, setPrompt] = useState("");
  const [promptDisabled, setPromptDisabled] = useState(false);
  const [messages, setMessages] = useState([] as Message[]);
  const [modelId, setModelId] = useState(KNOWN_MODEL_IDS[0]);

  function prepareBedrock(): BedrockRuntimeClient {
    const bedrock = new BedrockRuntimeClient({
      region: "us-east-1",
      credentials: {
        accessKeyId: window.localStorage.getItem(LOCAL_STORAGE_AK_NAME) ?? "",
        secretAccessKey:
          window.localStorage.getItem(LOCAL_STORAGE_SK_NAME) ?? "",
      },
      endpoint:
        window.localStorage.getItem(LOCAL_STORAGE_ENDPOINT_NAME) || undefined,
    });
    bedrock.middlewareStack.add(
      (next) => (args) => {
        const key = window.localStorage.getItem(
          LOCAL_STORAGE_BEDROCK_API_KEY_NAME
        );
        if (key) {
          (
            args.request as {
              headers: { "x-bedrock-api-key": string };
            }
          ).headers["x-bedrock-api-key"] = key;
        }
        return next(args);
      },
      { step: "build" }
    );
    return bedrock;
  }

  async function converse(messages: Message[]) {
    const bedrock = prepareBedrock();

    const response = await bedrock.send(
      new ConverseCommand({
        modelId,
        messages: messages
          .slice(0, -1)
          .filter((m) => m.type == "chat-bubble")
          .map((message) => ({
            role: message.authorId == "user" ? "user" : "assistant",
            content: [{ text: message.content!.toString() }],
          })),
      })
    );

    const text = response.output?.message?.content?.[0].text;
    if (text) {
      const ms = messages.slice();
      ms.at(-1)!.content += text;
      setMessages(ms);
    }
  }

  async function converseStream(messages: Message[]) {
    const bedrock = prepareBedrock();

    const response = await bedrock.send(
      new ConverseStreamCommand({
        modelId,
        messages: messages
          .slice(0, -1)
          .filter((m) => m.type == "chat-bubble")
          .map((message) => ({
            role: message.authorId == "user" ? "user" : "assistant",
            content: [{ text: message.content!.toString() }],
          })),
      })
    );

    for await (const event of response.stream!) {
      const chunk = event.contentBlockDelta;
      if (chunk?.delta?.text) {
        const message = chunk.delta.text;
        if (message) {
          const ms = messages.slice();
          ms.at(-1)!.content += message;
          setMessages(ms);
        }
      }
    }
  }

  function onPromptSend() {
    if (prompt) {
      const newMessages = [
        ...messages,
        { type: "chat-bubble", authorId: "user", content: prompt },
        {
          type: "chat-bubble",
          authorId: "gen-ai",
          content: "",
          avatarLoading: true,
        },
      ] as Message[];
      setMessages(newMessages);
      setPrompt("");
      setPromptDisabled(true);

      (streaming ? converseStream(newMessages) : converse(newMessages))
        .then(() => {
          setPromptDisabled(false);
          const ms = newMessages.slice();
          const msg = ms.at(-1)!;
          if (msg.type == "chat-bubble") msg.avatarLoading = false;
          setMessages(ms);
        })
        .catch((e) => {
          console.error(e);
          const ms = newMessages.slice();
          ms.push({
            type: "alert",
            content: e.message,
          });
          setMessages(ms);
        });
    }
  }

  return (
    <div style={{ height: "100%", display: "flex", flexDirection: "column" }}>
      <BreadcrumbGroup
        items={[
          { text: "Bedrock CN", href: "/" },
          { text: "Chat / Text playground", href: "/chat" },
        ]}
      />
      <ContentLayout>
        <div style={{ height: "100%", alignItems: "center" }}>
          <Container
            header={
              <div style={{ display: "flex" }}>
                <Header variant="h3">Generative AI chat</Header>
                <Autosuggest
                  onChange={({ detail }) => setModelId(detail.value)}
                  value={modelId}
                  options={KNOWN_MODEL_IDS.map((value) => ({ value }))}
                  placeholder="Enter the model ID"
                />
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    marginLeft: "10px",
                  }}
                >
                  <Toggle
                    onChange={({ detail }) => setStreaming(detail.checked)}
                    checked={streaming}
                  >
                    <span style={{ wordBreak: "keep-all" }}>Streaming</span>
                  </Toggle>
                </div>
                <Button
                  ariaLabel="Load the example"
                  iconName="folder"
                  variant="icon"
                  onClick={() => {
                    setPromptDisabled(true);
                    setMessages(INITIAL_MESSAGES.slice());
                  }}
                >
                  Examples
                </Button>
                <Button
                  ariaLabel="Start a new conversation"
                  iconName="add-plus"
                  variant="icon"
                  onClick={() => {
                    setMessages([]);
                    setPromptDisabled(false);
                  }}
                ></Button>
              </div>
            }
            fitHeight
            disableContentPaddings
            footer={
              <FormField stretch>
                <PromptInput
                  value={prompt}
                  onChange={({ detail }) => setPrompt(detail.value)}
                  onAction={onPromptSend}
                  disabled={promptDisabled}
                  actionButtonAriaLabel="Send"
                  actionButtonIconName="send"
                  placeholder="Ask a question"
                  autoFocus
                />
              </FormField>
            }
          >
            <ScrollableContainer>
              <Messages messages={messages} />
            </ScrollableContainer>
          </Container>
        </div>
      </ContentLayout>
    </div>
  );
}
