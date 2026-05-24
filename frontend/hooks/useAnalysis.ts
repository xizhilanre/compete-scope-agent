"use client";

import { useState, useCallback, useRef } from "react";
import { apiFetch } from "@/lib/utils";
import type { AnalysisJob } from "@/types/analysis";

export function useAnalysis() {
  const [job, setJob] = useState<AnalysisJob | null>(null);
  const [loading, setLoading] = useState(false);
  const [events, setEvents] = useState<string[]>([]);
  const eventSourceRef = useRef<EventSource | null>(null);

  const start = useCallback(async (productName: string) => {
    setLoading(true);
    setEvents([]);
    const data = await apiFetch<AnalysisJob>("/api/analyze/start", {
      method: "POST",
      body: JSON.stringify({ product_name: productName }),
    });
    setJob(data);

    const base = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    const es = new EventSource(`${base}/api/analyze/${data.job_id}/stream`);
    eventSourceRef.current = es;

    es.onmessage = (e) => {
      setEvents((prev) => [...prev, e.data]);
    };
    es.addEventListener("complete", () => {
      setLoading(false);
      es.close();
    });
    es.onerror = () => {
      setLoading(false);
      es.close();
    };
  }, []);

  return { job, loading, events, start };
}
