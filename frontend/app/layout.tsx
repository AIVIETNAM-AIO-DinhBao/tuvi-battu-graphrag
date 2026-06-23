import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "TuVi GraphRAG",
  description: "Hệ thống hỏi đáp Tử Vi với Hybrid GraphRAG",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="vi">
      <body>{children}</body>
    </html>
  );
}
