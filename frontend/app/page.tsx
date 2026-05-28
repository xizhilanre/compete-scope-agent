"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { apiFetch } from "@/lib/utils";

export default function Home() {
  const [product, setProduct] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!product.trim()) return;
    setLoading(true);
    setError("");

    try {
      const res = await apiFetch<{ data: { id: string } }>("/api/tasks", {
        method: "POST",
        body: JSON.stringify({
          target_product: product.trim(),
          analysis_dimensions: ["SWOT分析", "功能分析", "定价策略", "市场定位"],
        }),
      });
      router.push(`/tasks/${res.data.id}`);
    } catch {
      setError("无法连接后端服务，请确保后端已启动 (localhost:8000)");
      setLoading(false);
    }
  };

  return (
    <main className="mx-auto flex max-w-3xl flex-col items-center gap-8 px-6 py-24">
      <h1 className="text-4xl font-bold tracking-tight">
        Compete<span className="text-indigo-400">Scope</span>
      </h1>
      <p className="text-zinc-400 text-center max-w-md">
        输入产品名，5 个 AI Agent 协同工作，自动生成企业级竞品分析报告
      </p>

      <form
        onSubmit={handleSubmit}
        className="flex w-full max-w-md gap-3"
      >
        <input
          value={product}
          onChange={(e) => setProduct(e.target.value)}
          placeholder="例如：Notion, Figma, Linear..."
          className="flex-1 rounded-lg border border-zinc-700 bg-zinc-800 px-4 py-3 text-sm outline-none focus:border-indigo-400"
          autoFocus
        />
        <button
          type="submit"
          disabled={loading || !product.trim()}
          className="rounded-lg bg-indigo-600 px-6 py-3 text-sm font-medium text-white transition hover:bg-indigo-500 disabled:opacity-50"
        >
          {loading ? "正在创建..." : "开始分析"}
        </button>
      </form>

      {error && <p className="text-sm text-red-400">{error}</p>}

      <div className="mt-4 flex gap-4 text-sm text-zinc-500">
        <a href="/dashboard" className="hover:text-zinc-300 transition">
          查看 Dashboard →
        </a>
        <a href="http://localhost:8000/api/docs" className="hover:text-zinc-300 transition">
          API 文档 →
        </a>
      </div>
    </main>
  );
}
