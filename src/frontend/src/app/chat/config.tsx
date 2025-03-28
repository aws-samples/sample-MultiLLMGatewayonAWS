// modified from https://github.com/cloudscape-design/demos/blob/4e047ce9e1af02e4305750621dc0ed74a58855f4/src/pages/chat/config.tsx

import { CodeView } from "@cloudscape-design/code-view";
import {
  Box,
  ButtonGroup,
  ExpandableSection,
  Link,
  Popover,
  StatusIndicator,
} from "@cloudscape-design/components";

export type Message = ChatBubbleMessage | AlertMessage;

type ChatBubbleMessage = {
  type: "chat-bubble";
  authorId: string;
  content: React.ReactNode;
  actions?: React.ReactNode;
  hideAvatar?: boolean;
  avatarLoading?: boolean;
};

type AlertMessage = {
  type: "alert";
  content: React.ReactNode;
  header?: string;
};

export type AuthorAvatarProps = {
  type: "user" | "gen-ai";
  name: string;
  initials?: string;
  loading?: boolean;
};
type AuthorsType = {
  [key: string]: AuthorAvatarProps;
};
export const AUTHORS: AuthorsType = {
  user: { type: "user", name: "User", initials: "U" },
  "gen-ai": { type: "gen-ai", name: "Generative AI assistant" },
};

const CitationPopover = ({ count, href }: { count: number; href: string }) => (
  <Box color="text-status-info" display="inline">
    <Popover
      header="Source"
      content={
        <Link href={href} external variant="primary">
          {href}
        </Link>
      }
      position="right"
    >
      [{count}]
    </Popover>
  </Box>
);

export function CodeViewActions() {
  return (
    <ButtonGroup
      variant="icon"
      onItemClick={() => void 0}
      items={[
        {
          type: "group",
          text: "Feedback",
          items: [
            {
              type: "icon-button",
              id: "run-command",
              iconName: "play",
              text: "Run command",
            },
            {
              type: "icon-button",
              id: "send-cloudshell",
              iconName: "script",
              text: "Send to IDE",
            },
          ],
        },
        {
          type: "icon-button",
          id: "copy",
          iconName: "copy",
          text: "Copy",
          popoverFeedback: (
            <StatusIndicator type="success">Message copied</StatusIndicator>
          ),
        },
      ]}
    />
  );
}

export const INITIAL_MESSAGES: Array<Message> = [
  {
    type: "chat-bubble",
    authorId: "user",
    content: "What can I do with Amazon S3?",
  },
  {
    type: "chat-bubble",
    authorId: "gen-ai",
    content:
      "Amazon S3 provides a simple web service interface that you can use to store and retrieve any amount of data, at any time, from anywhere. Using this service, you can easily build applications that make use of cloud native storage. Since Amazon S3 is highly scalable and you only pay for what you use, you can start small and grow your application as you wish, with no compromise on performance or reliability.",
  },
  {
    type: "chat-bubble",
    authorId: "user",
    content: "How can I create an S3 bucket configuration?",
  },
  {
    type: "chat-bubble",
    authorId: "gen-ai",
    content: (
      <>
        Creating a configuration for Amazon S3 involves setting up a bucket and
        configuring its properties{" "}
        <CitationPopover
          count={1}
          href="https://docs.aws.amazon.com/AmazonS3/latest/userguide/GetStartedWithS3.html"
        />
        . Here&apos;s a step-by-step guide to help you create an S3
        configuration:
        <div>1. Sign in to AWS Management Console</div>
        <div>2. Access Amazon S3 console</div>
        <div>3. Create a new S3 bucket</div>
        <div>
          4. Configure bucket settings{" "}
          <CitationPopover
            count={2}
            href="https://docs.aws.amazon.com/appconfig/latest/userguide/appconfig-creating-configuration-and-profile-S3-source.html"
          />
        </div>
        <div>5. Review and create</div>
        <Box padding={{ top: "xs" }}>
          <ExpandableSection headerText="Sources">
            <div>
              <Link
                href="https://docs.aws.amazon.com/AmazonS3/latest/userguide/GetStartedWithS3.html"
                external
                variant="primary"
              >
                [1] Getting started with Amazon S3 - Amazon Simple Storage
                Service
              </Link>
            </div>
            <div>
              <Link
                href="https://docs.aws.amazon.com/appconfig/latest/userguide/appconfig-creating-configuration-and-profile-S3-source.html"
                external
                variant="primary"
              >
                [2] Understanding configurations stored in Amazon S3 - AWS
                AppConfig
              </Link>
            </div>
            <div>
              <Link
                href="https://docs.aws.amazon.com/AmazonS3/latest/userguide/HostingWebsiteOnS3Setup.html"
                external
                variant="primary"
              >
                [3] Tutorial: Configuring a static website on Amazon S3 - Amazon
                Simple Storage Service
              </Link>
            </div>
          </ExpandableSection>
        </Box>
      </>
    ),
  },
  {
    type: "chat-bubble",
    authorId: "user",
    content: "Give me an example of a Typescript code block.",
  },
  {
    type: "chat-bubble",
    authorId: "gen-ai",
    content:
      "Here's a simple TypeScript code example that implements the 'Hello, World!' functionality:",
  },
  {
    type: "chat-bubble",
    authorId: "gen-ai",
    content: (
      <CodeView
        content={`// This is the main function that will be executed when the script runs
function main(): void {
  // Use console.log to print "Hello, World!" to the console
  console.log("Hello, World!");
}
// Call the main function to execute the program
main();`}
        // highlight={typescriptHighlight}
      />
    ),
    actions: <CodeViewActions />,
    hideAvatar: true,
  },
];
