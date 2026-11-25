import type { Metadata } from "next";
import Sidebar from "@/components/Sidebar";
import "../styles/globals.css";

export const metadata: Metadata = {
  title: "MARINISE Vessel Intelligence System",
  description: "MARINISE® MVIS - denizcilik istihbarat ve potansiyel müşteri platformu",
  robots: { index: false, follow: false }, // Section 18
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="tr">
      <body>
        <div className="flex h-screen w-screen overflow-hidden">
          <Sidebar />
          <main className="flex-1 overflow-y-auto">{children}</main>
        </div>
      </body>
    </html>
  );
}
