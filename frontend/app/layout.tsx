import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "CompeteScope — 竞品分析 Agent",
  description: "输入产品名，5 个 Agent 协同 10 分钟自动生成企业级竞品分析报告",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <body className="min-h-screen bg-zinc-950 text-zinc-100 antialiased">
        {children}
      </body>
    </html>
  );
}
