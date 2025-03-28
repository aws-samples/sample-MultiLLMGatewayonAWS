"use client";
import {
  ContentLayout,
  Container,
  Header,
  BreadcrumbGroup,
} from "@cloudscape-design/components";

export default function Home() {
  return (
    <div>
      <BreadcrumbGroup
        items={[
          { text: "Bedrock CN", href: "/" },
          { text: "Overview", href: "/" },
        ]}
      />
      <ContentLayout header={<Header>Overview</Header>}>
        <Container></Container>
      </ContentLayout>
    </div>
  );
}
