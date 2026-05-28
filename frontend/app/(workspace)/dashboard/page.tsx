"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { apiFetch } from "@/lib/utils";
import TaskCard from "@/components/workspace/TaskCard";

interface TaskItem {
  id: string;
  target_product: string;
  status: string;
  created_at: string;
}

export default function DashboardPage() {
  const [tasks, setTasks] = useState<TaskItem[]>([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    apiFetch<{ data: { items: TaskItem[] } }>("/api/tasks?skip=0&limit=20")
      .then((res) => setTasks(res.data.items || []))
      .catch(() => setTasks([]))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <h2 className="text-2xl font-bold text-white">任务列表</h2>
        <button
          onClick={() => router.push("/tasks/new")}
          className="rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-indigo-500 transition"
        >
          新建任务
        </button>
      </div>

      {loading ? (
        <p className="text-zinc-500">加载中...</p>
      ) : tasks.length === 0 ? (
        <p className="text-zinc-500">暂无任务，点击右上角创建第一个分析任务</p>
      ) : (
        <div className="grid gap-4 grid-cols-1 md:grid-cols-2">
          {tasks.map((t) => (
            <TaskCard key={t.id} {...t} />
          ))}
        </div>
      )}
    </div>
  );
}
