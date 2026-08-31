import "./globals.css";
import type { Metadata } from "next";
import Nav from "@/components/Nav";
import GridFX from "@/components/GridFX";

export const metadata: Metadata = { title: "WARDEN", description: "A software supply-chain firewall for AI agents." };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <GridFX />
        <div className="shell">
          <Nav />
          <main className="content">{children}</main>
        </div>
      </body>
    </html>
  );
}
