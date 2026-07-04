import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "HealthBuddy AI — Call Console",
  description: "Scheduled AI medication reminder calls and on-demand caregiver calls, via Telnyx Call Control.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="font-sans">{children}</body>
    </html>
  );
}
