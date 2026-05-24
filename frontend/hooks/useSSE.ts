"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import type { AgentName, AgentStateMap, SSEEvent } from "@/types/sse-events";
import { ALL_AGENTS } from "@/types/sse-events";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export type TaskStatus = "idle" | "running" | "completed" | "failed";

interface UseSSEReturn {
  connect: (taskId: string) => void;
  disconnect: () => void;
  isConnected: boolean;
  taskStatus: TaskStatus;
  agentStates: AgentStateMap;
  events: SSEEvent[];
  targetProduct: string;
  error: string | null;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function initialAgentStates(): AgentStateMap {
  const map = {} as AgentStateMap;
  for (const name of ALL_AGENTS) {
    map[name] = "waiting";
  }
  return map;
}

// ---------------------------------------------------------------------------
// Hook
// ---------------------------------------------------------------------------

export function useSSE(): UseSSEReturn {
  const [isConnected, setIsConnected] = useState(false);
  const [taskStatus, setTaskStatus] = useState<TaskStatus>("idle");
  const [agentStates, setAgentStates] = useState<AgentStateMap>(initialAgentStates);
  const [events, setEvents] = useState<SSEEvent[]>([]);
  const [targetProduct, setTargetProduct] = useState("");
  const [error, setError] = useState<string | null>(null);

  // Refs to avoid stale closures inside EventSource callbacks
  const taskStatusRef = useRef<TaskStatus>("idle");
  const esRef = useRef<EventSource | null>(null);
  const taskIdRef = useRef<string | null>(null);
  const reconnectAttempts = useRef(0);
  const reconnectTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const MAX_RECONNECT_MS = 30_000;

  // Keep the ref in sync with state
  const setTaskStatusBoth = useCallback((s: TaskStatus) => {
    taskStatusRef.current = s;
    setTaskStatus(s);
  }, []);

  // ----- Core event handler (stable via refs) -----
  const handleMessage = useCallback((e: MessageEvent) => {
    let parsed: SSEEvent;
    try {
      parsed = JSON.parse(e.data);
    } catch {
      return;
    }

    setEvents((prev) => [...prev, parsed]);

    switch (parsed.event) {
      case "task_start":
        setTaskStatusBoth("running");
        setTargetProduct(parsed.target_product);
        break;
      case "agent_start":
        setAgentStates((prev) => {
          if (prev[parsed.agent as AgentName] === "running") return prev;
          return { ...prev, [parsed.agent]: "running" };
        });
        break;
      case "agent_complete":
        setAgentStates((prev) => ({ ...prev, [parsed.agent]: "completed" }));
        break;
      case "task_complete":
        setTaskStatusBoth("completed");
        break;
      case "task_failed":
        setTaskStatusBoth("failed");
        setError(parsed.error);
        break;
    }
  }, [setTaskStatusBoth]);

  // Keep a stable ref to the handler so onerror can reference it without
  // re-registering EventSource listeners.
  const handleMessageRef = useRef(handleMessage);
  handleMessageRef.current = handleMessage;

  // ----- Disconnect -----
  const disconnect = useCallback(() => {
    if (reconnectTimer.current) {
      clearTimeout(reconnectTimer.current);
      reconnectTimer.current = null;
    }
    if (esRef.current) {
      esRef.current.close();
      esRef.current = null;
    }
    setIsConnected(false);
    taskIdRef.current = null;
  }, []);

  // ----- Connect -----
  const connect = useCallback(
    (taskId: string) => {
      disconnect();

      taskIdRef.current = taskId;
      setEvents([]);
      setAgentStates(initialAgentStates());
      setTaskStatusBoth("idle");
      setTargetProduct("");
      setError(null);
      reconnectAttempts.current = 0;

      const base = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const url = `${base}/api/analyze/${taskId}/stream`;

      const es = new EventSource(url);
      esRef.current = es;

      es.onopen = () => {
        setIsConnected(true);
        reconnectAttempts.current = 0;
      };

      es.onmessage = (e: MessageEvent) => {
        handleMessageRef.current(e);
      };

      es.onerror = () => {
        setIsConnected(false);
        es.close();
        esRef.current = null;

        // Only reconnect if the task is still in progress
        if (taskStatusRef.current === "running" || taskStatusRef.current === "idle") {
          const delay = Math.min(1000 * 2 ** reconnectAttempts.current, MAX_RECONNECT_MS);
          reconnectAttempts.current += 1;
          reconnectTimer.current = setTimeout(() => {
            if (taskIdRef.current) {
              // Reconnect only if a taskId is still set (user hasn't called disconnect)
              connect(taskIdRef.current);
            }
          }, delay);
        }
      };
    },
    [disconnect, setTaskStatusBoth],
  );

  // ----- Cleanup on unmount -----
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return {
    connect,
    disconnect,
    isConnected,
    taskStatus,
    agentStates,
    events,
    targetProduct,
    error,
  };
}
