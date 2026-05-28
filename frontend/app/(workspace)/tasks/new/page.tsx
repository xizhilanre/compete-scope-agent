"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { apiFetch } from "@/lib/utils";

const DIMENSIONS = ["功能分析", "定价策略", "SWOT分析", "市场定位", "用户口碑"];

export default function NewTaskPage() {
  const [product, setProduct] = useState("");
  const [selected, setSelected] = useState<string[]>(["SWOT分析"]);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const router = useRouter();

  const toggle = (dim: string) => {
    setSelected((prev) =>
      prev.includes(dim) ? prev.filter((d) => d !== dim) : [...prev, dim]
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!product.trim() || selected.length === 0) return;
    setSubmitting(true);
    setError("");

    try {
      const res = await apiFetch<{ data: { id: string } }>("/api/tasks", {
        method: "POST",
        body: JSON.stringify({ target_product: product.trim(), analysis_dimensions: selected }),
      });
      router.push(`/tasks/${res.data.id}`);
    } catch {
      setError("创建任务失败，请检查后端服务是否运行");
      setSubmitting(false);
    }
  };

  return (
    <div className="mx-auto max-w-xl">
      <h2 className="text-2xl font-bold text-white mb-8">新建分析任务</h2>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-zinc-300 mb-2">目标产品</label>
          <input
            value={product}
            onChange={(e) => setProduct(e.target.value)}
            placeholder="例如：Notion、Figma、Linear..."
            className="w-full rounded-lg border border-zinc-700 bg-zinc-800 px-4 py-3 text-sm text-white outline-none focus:border-indigo-400"
            autoFocus
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-zinc-300 mb-2">分析维度（至少选一项）</label>
          <div className="flex flex-wrap gap-2">
            {DIMENSIONS.map((dim) => (
              <button
                key={dim}
                type="button"
                onClick={() => toggle(dim)}
                className={`rounded-full px-4 py-1.5 text-sm transition ${
                  selected.includes(dim)
                    ? "bg-indigo-600 text-white"
                    : "bg-zinc-800 text-zinc-400 hover:bg-zinc-700"
                }`}
              >
                {dim}
              </button>
            ))}
          </div>
        </div>

        {error && <p className="text-sm text-red-400">{error}</p>}

        <button
          type="submit"
          disabled={submitting || !product.trim() || selected.length === 0}
          className="w-full rounded-lg bg-indigo-600 py-3 text-sm font-medium text-white hover:bg-indigo-500 transition disabled:opacity-50"
        >
          {submitting ? "正在创建任务..." : "开始分析"}
        </button>
      </form>
    </div>
  );
}
