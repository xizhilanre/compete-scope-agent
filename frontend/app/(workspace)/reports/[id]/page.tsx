"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { apiFetch } from "@/lib/utils";
import ReportViewer from "@/components/report/ReportViewer";

interface ReportData {
  id: string;
  markdown_content: string;
  quality_score: number;
}

export default function ReportPage() {
  const { id } = useParams<{ id: string }>();
  const [report, setReport] = useState<ReportData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    apiFetch<{ data: ReportData }>(`/api/reports/${id}`)
      .then((res) => setReport(res.data))
      .catch(() => setError("报告未找到"))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <p className="text-zinc-500">加载中...</p>;
  if (error) return <p className="text-red-400">{error}</p>;
  if (!report) return null;

  return (
    <div className="mx-auto max-w-3xl">
      <div className="mb-8 flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white">分析报告</h2>
        <span className="rounded-full bg-green-600/20 px-4 py-1 text-sm text-green-400">
          质量评分 {(report.quality_score * 100).toFixed(0)}%
        </span>
      </div>

      <ReportViewer markdown={report.markdown_content} />
    </div>
  );
}
