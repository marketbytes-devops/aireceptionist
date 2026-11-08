import "./globals.css";
import type { Metadata, Viewport } from "next";
import AppLayout from "@/components/AppLayout";

export const metadata: Metadata = {
  title: "AyurVoice SaaS - Clinic Admin Portal",
  description: "Multi-tenant autonomous AI voice receptionist for Ayurvedic clinics",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-50 antialiased overflow-x-hidden">
        <AppLayout>{children}</AppLayout>
      </body>
    </html>
  );
}
