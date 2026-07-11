// frontend/src/components/Nav.tsx
"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  { href: "/", label: "Dashboard" },
  { href: "/ai-call-center", label: "AI Call Center" },
];

export function Nav({ caregiverName }: { caregiverName?: string }) {
  const pathname = usePathname();

  return (
    <header className="border-b border-line bg-surface">
      <div className="mx-auto max-w-5xl px-4 sm:px-8 h-14 flex items-center justify-between">
        <div className="flex items-center gap-6">
          <span className="text-sm font-semibold text-ink tracking-tight">HealthBuddy AI</span>
          <nav className="flex items-center gap-1">
            {links.map((link) => {
              const active = pathname === link.href;
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  className={`text-2xs font-mono uppercase tracking-wide px-3 py-1.5 rounded-md transition-colors ${
                    active ? "bg-accent-soft text-accent" : "text-muted hover:text-ink"
                  }`}
                >
                  {link.label}
                </Link>
              );
            })}
          </nav>
        </div>
        {caregiverName && (
          <div className="flex items-center gap-2">
            <span className="h-6 w-6 rounded-full bg-accent text-white text-2xs font-medium flex items-center justify-center">
              {caregiverName.charAt(0)}
            </span>
            <span className="text-2xs font-mono text-muted">{caregiverName}</span>
          </div>
        )}
      </div>
    </header>
  );
}