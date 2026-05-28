"use client";

import { useEffect, useRef, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import DAGVisualizer from "@/components/dag/DAGVisualizer";

const STATUS_MESSAGES: Record<string, string> = {
  planner: "规划师正在制定搜索策略...",
  research: "研究员正在全网搜索竞品信息...",
  analysis: "分析师正在提炼 SWOT 洞察...",
  writer: "撰稿人正在撰写分析报告...",
  reviewer: "审查员正在审核报告质量...",
};

export default function TaskDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [agentStates, setAgentStates] = useState<Record<string, { status: string }>>({});
  const [statusMessage, setStatusMessage] = useState("任务已提交，等待启动...");
  const [error, setError] = useState("");
  const esRef = useRef<EventSource | null>(null);

  useEffect(() => {
    const base = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    const es = new EventSource(`${base}/api/analyze/${id}/stream`);
    esRef.current = es;

    es.addEventListener("agent_start", (e: MessageEvent) => {
      const data = JSON.parse(e.data);
      setAgentStates((prev) => ({ ...prev, [data.agent]: { status: "running" } }));
      setStatusMessage(STATUS_MESSAGES[data.agent] || `${data.agent} 正在执行...`);
    });

    es.addEventListener("agent_complete", (e: MessageEvent) => {
      const data = JSON.parse(e.data);
      setAgentStates((prev) => ({ ...prev, [data.agent]: { status: "completed" } }));
    });

    es.addEventListener("task_complete", (e: MessageEvent) => {
      es.close();
      const data = JSON.parse(e.data);
      // Navigate to report page using report_id from the event
      const reportId = data.report_id || id;
      setTimeout(() => router.push(`/reports/${reportId}`), 500);
    });

    es.addEventListener("task_start", () => {
      setStatusMessage("Agent 工作流已启动...");
    });

    es.addEventListener("task_failed", (e: MessageEvent) => {
      const data = JSON.parse(e.data);
      setError(data.error || "任务执行失败");
      es.close();
    });

    es.onerror = () => {
      // EventSource will auto-reconnect
    };

    return () => {
      es.close();
    };
  }, [id, router]);

  return (
    <div className="mx-auto max-w-xl">
      <h2 className="text-2xl font-bold text-white mb-8">任务执行中</h2>

      <DAGVisualizer agentStates={agentStates} />

      <div className="mt-8 text-center">
        {error ? (
          <p className="text-red-400">{error}</p>
        ) : (
          <p className="text-zinc-400">{statusMessage}</p>
        )}
      </div>
    </div>
  );
}
