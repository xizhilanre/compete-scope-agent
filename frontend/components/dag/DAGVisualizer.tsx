"use client";

interface DAGVisualizerProps {
  agentStates: Record<string, { status: string }>;
}

const AGENT_NAMES: Record<string, string> = {
  planner: "规划师",
  research: "研究员",
  analysis: "分析师",
  writer: "撰稿人",
  reviewer: "审查员",
};

const AGENT_COLORS: Record<string, string> = {
  planner: "#3b82f6",
  research: "#f59e0b",
  analysis: "#8b5cf6",
  writer: "#22c55e",
  reviewer: "#64748b",
};

export default function DAGVisualizer({ agentStates }: DAGVisualizerProps) {
  const agents = Object.keys(agentStates);
  if (agents.length === 0) return null;

  const NODE_H = 48;
  const NODE_W = 140;
  const GAP = 24;
  const PADDING = 20;
  const totalH = agents.length * NODE_H + (agents.length - 1) * GAP + PADDING * 2;
  const centerX = NODE_W / 2 + PADDING;
  const viewBoxW = NODE_W + PADDING * 2;
  const viewBoxH = totalH;

  return (
    <div className="flex justify-center">
      <svg viewBox={`0 0 ${viewBoxW} ${viewBoxH}`} className="w-48 h-auto">
        {agents.map((agent, i) => {
          const y = PADDING + i * (NODE_H + GAP);
          const label = AGENT_NAMES[agent] || agent;
          const state = agentStates[agent]?.status || "waiting";

          let borderColor = "#374151";
          let textColor = "#6b7280";
          let pulse = false;
          let icon = "";

          if (state === "running") {
            borderColor = AGENT_COLORS[agent] || "#6366f1";
            textColor = borderColor;
            pulse = true;
          } else if (state === "completed") {
            borderColor = "#22c55e";
            textColor = "#4ade80";
            icon = "✓";
          } else if (state === "failed") {
            borderColor = "#ef4444";
            textColor = "#f87171";
            icon = "✗";
          }

          return (
            <g key={agent}>
              <rect
                x={PADDING}
                y={y}
                width={NODE_W}
                height={NODE_H}
                rx={8}
                ry={8}
                fill="#1a1d2e"
                stroke={borderColor}
                strokeWidth={2}
                className={pulse ? "animate-pulse" : ""}
              />
              <text
                x={centerX}
                y={y + NODE_H / 2 + 1}
                textAnchor="middle"
                dominantBaseline="middle"
                fill={textColor}
                fontSize={14}
                fontWeight={500}
              >
                {label} {icon}
              </text>
              {i < agents.length - 1 && (
                <line
                  x1={centerX}
                  y1={y + NODE_H}
                  x2={centerX}
                  y2={y + NODE_H + GAP}
                  stroke="#374151"
                  strokeWidth={2}
                />
              )}
            </g>
          );
        })}
      </svg>
    </div>
  );
}
