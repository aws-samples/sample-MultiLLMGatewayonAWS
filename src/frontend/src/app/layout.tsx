import type { Metadata } from "next";
import "@cloudscape-design/global-styles/index.css";
import ClientLayout from "./layout.client";

export const metadata: Metadata = {
  title: "Bedrock CN",
  description: "Bedrock CN",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html>
      <body>
        <ClientLayout>{children}</ClientLayout>
      </body>
    </html>
  );
}
