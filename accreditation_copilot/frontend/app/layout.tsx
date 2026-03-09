import type { Metadata } from "next";
import { Inter, Plus_Jakarta_Sans } from "next/font/google";
import "./globals.css";
import HelpChatbot from "@/components/HelpChatbot";

const inter = Inter({ subsets: ["latin"] });
const jakarta = Plus_Jakarta_Sans({ 
  subsets: ["latin"],
  weight: ['300', '400', '500', '600', '700', '800'],
  variable: '--font-jakarta'
});

export const metadata: Metadata = {
  title: "Omni Accreditation Copilot",
  description: "AI-powered accreditation audit system",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${jakarta.className} antialiased`}>
        {children}
        <HelpChatbot />
      </body>
    </html>
  );
}
