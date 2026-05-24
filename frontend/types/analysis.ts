export interface AnalysisJob {
  job_id: string;
  product_name: string;
  status: "queued" | "running" | "completed" | "failed";
  current_agent?: string;
  progress: number;
}

export interface SWOTItem {
  category: "strength" | "weakness" | "opportunity" | "threat";
  point: string;
  confidence: number;
  citations: string[];
}

export interface AnalysisResult {
  job_id: string;
  product_name: string;
  swot: SWOTItem[];
  summary: string;
  competitors: string[];
  report_markdown: string;
}

export interface SSEEvent {
  event: string;
  data: string;
}
