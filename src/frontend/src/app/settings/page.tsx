"use client";
import * as React from "react";
import Form from "@cloudscape-design/components/form";
import SpaceBetween from "@cloudscape-design/components/space-between";
import Button from "@cloudscape-design/components/button";
import Container from "@cloudscape-design/components/container";
import Header from "@cloudscape-design/components/header";
import FormField from "@cloudscape-design/components/form-field";
import Input from "@cloudscape-design/components/input";
import {
  BreadcrumbGroup,
  Popover,
  StatusIndicator,
} from "@cloudscape-design/components";
import {
  LOCAL_STORAGE_AK_NAME,
  LOCAL_STORAGE_BEDROCK_API_KEY_NAME,
  LOCAL_STORAGE_ENDPOINT_NAME,
  LOCAL_STORAGE_SK_NAME,
} from "../consts";

export default function Settings() {
  const [ak, setAk] = React.useState("");
  const [sk, setSk] = React.useState("");
  const [endpoint, setEndpoint] = React.useState("");
  const [apiKey, setApiKey] = React.useState("");

  React.useEffect(() => {
    setAk(localStorage.getItem(LOCAL_STORAGE_AK_NAME) ?? "");
    setSk(localStorage.getItem(LOCAL_STORAGE_SK_NAME) ?? "");
    setEndpoint(localStorage.getItem(LOCAL_STORAGE_ENDPOINT_NAME) ?? "");
    setApiKey(localStorage.getItem(LOCAL_STORAGE_BEDROCK_API_KEY_NAME) ?? "");
  }, []);

  return (
    <div>
      <BreadcrumbGroup
        items={[
          { text: "Bedrock CN", href: "/" },
          { text: "Settings", href: "/settings" },
        ]}
      />
      <form onSubmit={(e) => e.preventDefault()}>
        <Form
          actions={
            <SpaceBetween direction="horizontal" size="xs">
              <Popover
                dismissButton={false}
                position="top"
                size="small"
                triggerType="custom"
                content={
                  <StatusIndicator type="success">Saved</StatusIndicator>
                }
              >
                <Button
                  onClick={() => {
                    window.localStorage.setItem(LOCAL_STORAGE_AK_NAME, ak);
                    window.localStorage.setItem(LOCAL_STORAGE_SK_NAME, sk);
                    window.localStorage.setItem(
                      LOCAL_STORAGE_ENDPOINT_NAME,
                      endpoint
                    );
                    window.localStorage.setItem(
                      LOCAL_STORAGE_BEDROCK_API_KEY_NAME,
                      apiKey
                    );
                  }}
                >
                  Save
                </Button>
              </Popover>
            </SpaceBetween>
          }
          header={<Header variant="h1">Settings</Header>}
        >
          <Container>
            <SpaceBetween direction="vertical" size="l">
              <FormField label="Access key">
                <Input
                  value={ak}
                  onChange={(e) => setAk(e.detail.value)}
                  type="password"
                />
              </FormField>
              <FormField label="Secret key">
                <Input
                  value={sk}
                  onChange={(e) => setSk(e.detail.value)}
                  type="password"
                />
              </FormField>
              <FormField label="Endpoint override (Optional)">
                <Input
                  value={endpoint}
                  onChange={(e) => setEndpoint(e.detail.value)}
                />
              </FormField>
              <FormField label="Bedrock API Key (Optional)">
                <Input
                  value={apiKey}
                  onChange={(e) => setApiKey(e.detail.value)}
                  type="password"
                />
              </FormField>
            </SpaceBetween>
          </Container>
        </Form>
      </form>
    </div>
  );
}
