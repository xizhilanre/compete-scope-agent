"use client";

import Link from "next/link";

interface TaskCardProps {
  id: string;
  target_product: string;
  status: string;
  created_at: string;
}

const STATUS_COLORS: Record<string, string> = {
  PENDING: "bg-zinc-600 text-zinc-300",
  RUNNING: "bg-blue-600 text-blue-100",
  COMPLETED: "bg-green-600 text-green-100",
  FAILED: "bg-red-600 text-red-100",
};

const STATUS_LABELS: Record<string, string> = {
  PENDING: "等待中",
  RUNNING: "执行中",
  COMPLETED: "已完成",
  FAILED: "失败",
};

function timeAgo(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "刚刚";
  if (mins < 60) return `${mins} 分钟前`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours} 小时前`;
  return `${Math.floor(hours / 24)} 天前`;
}

export default function TaskCard({ id, target_product, status, created_at }: TaskCardProps) {
  const color = STATUS_COLORS[status] || "bg-zinc-600 text-zinc-300";
  const label = STATUS_LABELS[status] || status;

  return (
    <Link
      href={`/tasks/${id}`}
      className="block rounded-xl border border-zinc-800 bg-[#1a1d2e] p-5 transition hover:border-zinc-600"
    >
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-white">{target_product}</h3>
        <span className={`rounded-full px-3 py-1 text-xs font-medium ${color}`}>{label}</span>
      </div>
      <p className="mt-2 text-sm text-zinc-500">{timeAgo(created_at)}</p>
    </Link>
  );
}
