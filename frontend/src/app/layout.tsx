import type { Metadata } from "next";
import "./globals.css";
import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";

export const metadata: Metadata = {
  title: "Socievo — Group-Buying Home Services for Residential Societies",
  description:
    "Unlock massive volume discounts on AC servicing, deep cleaning, RO repair, and residential services by booking together with your apartment neighbors.",
  keywords: [
    "society group buying",
    "apartment services",
    "AC servicing Bangalore",
    "society RWA discounts",
    "deep cleaning group deal",
    "Socievo marketplace",
  ],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen flex flex-col bg-surface-100 text-charcoal-900 antialiased selection:bg-forest-100 selection:text-forest-900">
        <Navbar />
        <main className="flex-1">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
