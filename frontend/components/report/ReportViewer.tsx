"use client";

import ReactMarkdown from "react-markdown";

interface ReportViewerProps {
  markdown: string;
}

export default function ReportViewer({ markdown }: ReportViewerProps) {
  return (
    <div className="prose prose-invert prose-zinc max-w-none">
      <ReactMarkdown>{markdown}</ReactMarkdown>
    </div>
  );
}
