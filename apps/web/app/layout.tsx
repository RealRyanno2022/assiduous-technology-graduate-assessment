import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Senus PLC | Board Report",
  description: "AI-native board report for Senus PLC",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
