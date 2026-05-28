"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/tasks/new", label: "新建任务" },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex h-screen w-60 flex-col border-r border-zinc-800 bg-[#0f1117]">
      <div className="px-6 py-5">
        <h1 className="text-lg font-bold tracking-tight text-white">
          Compete<span className="text-indigo-400">Scope</span>
        </h1>
      </div>

      <nav className="flex-1 px-3 py-2 space-y-1">
        {NAV_ITEMS.map((item) => {
          const active = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`block rounded-lg px-3 py-2 text-sm transition ${
                active
                  ? "bg-[#1a1d2e] text-indigo-400"
                  : "text-zinc-400 hover:bg-[#1a1d2e] hover:text-zinc-200"
              }`}
            >
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className="px-6 py-4 text-xs text-zinc-600">v0.1.0 MVP</div>
    </aside>
  );
}
Claude opus4.7
