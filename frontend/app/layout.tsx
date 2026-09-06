import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Tử Vi GraphRAG",
  description: "Lập lá số Tử Vi và luận giải với GraphRAG.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="vi">
      <body>{children}</body>
    </html>
  );
}
