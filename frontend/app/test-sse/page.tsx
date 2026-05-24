"use client";

import { useEffect, useRef, useState } from "react";
import { ALL_AGENTS } from "@/types/sse-events";
import { useSSE } from "@/hooks/useSSE";

const AGENT_LABELS: Record<string, string> = {
  planner: "Planner",
  research: "Research",
  analysis: "Analysis",
  writer: "Writer",
  reviewer: "Reviewer",
};

const STATUS_COLORS: Record<string, string> = {
  waiting: "text-zinc-500",
  running: "text-yellow-400",
  completed: "text-green-400",
};

export default function TestSSEPage() {
  const { connect, disconnect, isConnected, taskStatus, agentStates, events, error } =
    useSSE();
  const [taskId, setTaskId] = useState("test-1");
  const [loading, setLoading] = useState(false);
  const logEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [events]);

  async function handleStart() {
    setLoading(true);
    try {
      const base = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      await fetch(`${base}/api/analyze/${taskId}/_simulate`, { method: "POST" });
      // Brief pause so the first events land in the queue before we connect
      await new Promise((r) => setTimeout(r, 400));
      connect(taskId);
    } catch {
      // Fallback: try to connect even if simulate failed
      connect(taskId);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto max-w-2xl px-6 py-12">
      <h1 className="mb-2 text-2xl font-bold">SSE Smoke Test</h1>
      <p className="mb-8 text-sm text-zinc-500">
        One click: fires simulation, then connects.
      </p>

      {/* Controls */}
      <div className="mb-6 flex flex-wrap items-center gap-3">
        <input
          value={taskId}
          onChange={(e) => setTaskId(e.target.value)}
          placeholder="Task ID"
          className="w-40 rounded border border-zinc-700 bg-zinc-900 px-3 py-2 text-sm outline-none focus:border-brand"
        />

        {!isConnected ? (
          <button
            onClick={handleStart}
            disabled={loading}
            className="rounded bg-brand px-4 py-2 text-sm font-medium text-white hover:bg-brand-light disabled:opacity-50"
          >
            {loading ? "Starting..." : "Simulate & Connect"}
          </button>
        ) : (
          <button
            onClick={disconnect}
            className="rounded border border-zinc-600 px-4 py-2 text-sm text-zinc-300 hover:bg-zinc-800"
          >
            Disconnect
          </button>
        )}

        <span
          className={`ml-auto text-xs ${isConnected ? "text-green-400" : "text-zinc-600"}`}
        >
          {isConnected ? "● LIVE" : "○ IDLE"}
        </span>
      </div>

      {/* Task status */}
      <div className="mb-6 text-sm">
        <span className="text-zinc-500">Task: </span>
        <span
          className={
            taskStatus === "running"
              ? "text-yellow-400"
              : taskStatus === "completed"
                ? "text-green-400"
                : taskStatus === "failed"
                  ? "text-red-400"
                  : "text-zinc-500"
          }
        >
          {taskStatus.toUpperCase()}
        </span>
        {error && <span className="ml-3 text-red-400">Error: {error}</span>}
      </div>

      {/* Agent states */}
      <div className="mb-6 rounded-lg border border-zinc-800 bg-zinc-900 p-5">
        <h2 className="mb-3 text-xs font-semibold uppercase tracking-wider text-zinc-500">
          Agent States
        </h2>
        <div className="space-y-2">
          {ALL_AGENTS.map((agent) => (
            <div key={agent} className="flex items-center justify-between">
              <span className="text-sm">{AGENT_LABELS[agent] ?? agent}</span>
              <span className={`text-sm font-medium ${STATUS_COLORS[agentStates[agent]] ?? "text-zinc-600"}`}>
                {agentStates[agent].toUpperCase()}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Raw SSE log */}
      <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-5">
        <h2 className="mb-3 text-xs font-semibold uppercase tracking-wider text-zinc-500">
          Raw SSE Events ({events.length})
        </h2>
        <div className="max-h-96 overflow-y-auto rounded bg-zinc-950 p-3 font-mono text-xs leading-relaxed text-zinc-400">
          {events.length === 0 && (
            <span className="text-zinc-600">Waiting for events...</span>
          )}
          {events.map((ev, i) => (
            <div key={i} className="border-b border-zinc-900 py-1">
              <span className="text-brand">{ev.event}</span>{" "}
              <span>{JSON.stringify(ev)}</span>
            </div>
          ))}
          <div ref={logEndRef} />
        </div>
      </div>
    </main>
  );
}
