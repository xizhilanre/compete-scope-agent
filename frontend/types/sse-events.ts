/**
 * SSE event type definitions — exact mirror of backend/schemas/events.py.
 *
 * Field names, types, and optionality must stay in sync with the Pydantic models.
 */

export type SSEEventType =
  | "task_start"
  | "agent_start"
  | "agent_complete"
  | "tool_call"
  | "tool_result"
  | "task_complete"
  | "task_failed"
  | "heartbeat";

export type AgentName =
  | "planner"
  | "research"
  | "analysis"
  | "writer"
  | "reviewer";

export const ALL_AGENTS: readonly AgentName[] = [
  "planner",
  "research",
  "analysis",
  "writer",
  "reviewer",
] as const;

// ---------------------------------------------------------------------------
// Individual event interfaces
// ---------------------------------------------------------------------------

export interface TaskStartEvent {
  event: "task_start";
  task_id: string;
  target_product: string;
  timestamp: string;
}

export interface AgentStartEvent {
  event: "agent_start";
  task_id: string;
  agent: AgentName;
  timestamp: string;
}

export interface AgentCompleteEvent {
  event: "agent_complete";
  task_id: string;
  agent: AgentName;
  timestamp: string;
  duration_ms: number;
  output_summary: string;
}

export interface ToolCallEvent {
  event: "tool_call";
  task_id: string;
  agent: AgentName;
  tool_name: string;
  tool_input: Record<string, unknown>;
  timestamp: string;
}

export interface ToolResultEvent {
  event: "tool_result";
  task_id: string;
  agent: AgentName;
  tool_name: string;
  success: boolean;
  duration_ms: number;
  timestamp: string;
}

export interface TaskCompleteEvent {
  event: "task_complete";
  task_id: string;
  timestamp: string;
  total_duration_ms: number;
  report_id: string;
}

export interface TaskFailedEvent {
  event: "task_failed";
  task_id: string;
  error: string;
  timestamp: string;
}

export interface HeartbeatEvent {
  event: "heartbeat";
  task_id: string;
  timestamp: string;
}

// ---------------------------------------------------------------------------
// Discriminated union
// ---------------------------------------------------------------------------

export type SSEEvent =
  | TaskStartEvent
  | AgentStartEvent
  | AgentCompleteEvent
  | ToolCallEvent
  | ToolResultEvent
  | TaskCompleteEvent
  | TaskFailedEvent
  | HeartbeatEvent;

// ---------------------------------------------------------------------------
// Agent state tracking (UI-level, not from backend)
// ---------------------------------------------------------------------------

export type AgentState = "waiting" | "running" | "completed";

export type AgentStateMap = Record<AgentName, AgentState>;
