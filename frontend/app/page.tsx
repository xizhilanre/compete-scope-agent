"use client";

import { useAnalysis } from "@/hooks/useAnalysis";
import { useState } from "react";

export default function Home() {
  const [product, setProduct] = useState("");
  const { job, loading, events, start } = useAnalysis();

  return (
    <main className="mx-auto flex max-w-3xl flex-col items-center gap-8 px-6 py-24">
      <h1 className="text-4xl font-bold tracking-tight">
        Compete<span className="text-brand">Scope</span>
      </h1>
      <p className="text-zinc-400">
        Input a product name. 5 agents. 10 minutes. Full competitive analysis report.
      </p>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          if (product.trim()) start(product.trim());
        }}
        className="flex w-full max-w-md gap-3"
      >
        <input
          value={product}
          onChange={(e) => setProduct(e.target.value)}
          placeholder="e.g. Notion, Figma, Linear..."
          className="flex-1 rounded-lg border border-zinc-700 bg-zinc-800 px-4 py-3 text-sm outline-none focus:border-brand"
        />
        <button
          type="submit"
          disabled={loading || !product.trim()}
          className="rounded-lg bg-brand px-6 py-3 text-sm font-medium text-white transition hover:bg-brand-light disabled:opacity-50"
        >
          {loading ? "Analyzing..." : "Analyze"}
        </button>
      </form>

      {job && (
        <div className="w-full max-w-md rounded-lg border border-zinc-800 bg-zinc-900 p-4 text-sm">
          <p>Status: <span className="text-brand">{job.status}</span></p>
          <p>Agent: {job.current_agent || "—"}</p>
          {events.length > 0 && (
            <pre className="mt-3 max-h-48 overflow-y-auto rounded bg-zinc-950 p-3 text-xs text-zinc-400">
              {events.map((e, i) => (
                <div key={i}>{e}</div>
              ))}
            </pre>
          )}
        </div>
      )}
    </main>
  );
}
