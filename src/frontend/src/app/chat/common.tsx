// modified from https://github.com/cloudscape-design/demos/blob/4e047ce9e1af02e4305750621dc0ed74a58855f4/src/pages/chat/common-components.tsx

import { forwardRef } from "react";
import { AuthorAvatarProps } from "./config";
import Avatar from "@cloudscape-design/chat-components/avatar";

export function ChatBubbleAvatar({
  type,
  name,
  initials,
  loading,
}: AuthorAvatarProps) {
  if (type === "gen-ai") {
    return (
      <Avatar
        color="gen-ai"
        iconName="gen-ai"
        tooltipText={name}
        ariaLabel={name}
        loading={loading}
      />
    );
  }

  return <Avatar initials={initials} tooltipText={name} ariaLabel={name} />;
}

export const ScrollableContainer = forwardRef(function ScrollableContainer(
  { children }: { children: React.ReactNode },
  ref: React.Ref<HTMLDivElement>
) {
  return (
    <div style={{ position: "relative", blockSize: "100%" }}>
      <div
        style={{ position: "absolute", inset: 0, overflowY: "auto" }}
        ref={ref}
      >
        {children}
      </div>
    </div>
  );
});
