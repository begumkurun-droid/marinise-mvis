"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

// Section 15 - "SOL MENÜ YAPISI", in order. Items without a built FAZ-1 page
// yet link to a simple "yakında" (coming soon) placeholder route rather
// than a dead/missing link, per Section 21: "Çalışmayan butonlar bırakma."
const MENU = [
  { label: "Executive Dashboard", href: "/" },
  { label: "Live Vessel Map", href: "/map" },
  { label: "Vessel Database", href: "/vessels" },
  { label: "Engine Intelligence", href: "/soon?from=Engine+Intelligence" },
  { label: "Superyacht Intelligence", href: "/soon?from=Superyacht+Intelligence" },
  { label: "Commercial Vessels", href: "/soon?from=Commercial+Vessels" },
  { label: "Ownership & Management", href: "/ownership" },
  { label: "Company Directory", href: "/companies" },
  { label: "Geofencing", href: "/soon?from=Geofencing" },
  { label: "Vessel Watchlist", href: "/soon?from=Vessel+Watchlist" },
  { label: "AI Research Center", href: "/soon?from=AI+Research+Center" },
  { label: "Potential Customers", href: "/soon?from=Potential+Customers" },
  { label: "Notifications", href: "/soon?from=Notifications" },
  { label: "Reports & Analytics", href: "/soon?from=Reports+%26+Analytics" },
  { label: "CRM Integration", href: "/soon?from=CRM+Integration" },
  { label: "API Management", href: "/soon?from=API+Management" },
  { label: "User Management", href: "/soon?from=User+Management" },
  { label: "System Settings", href: "/soon?from=System+Settings" },
  { label: "Audit Logs", href: "/soon?from=Audit+Logs" },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex h-full w-64 flex-col bg-marinise-navy text-white">
      <div className="flex items-center gap-2 border-b border-white/10 px-5 py-5">
        <span className="text-lg font-bold tracking-wide">MARINISE®</span>
        <span className="rounded bg-marinise-orange px-1.5 py-0.5 text-[10px] font-semibold">MVIS</span>
      </div>
      <nav className="flex-1 overflow-y-auto py-2">
        {MENU.map((item, idx) => {
          const active = pathname === item.href;
          return (
            <Link
              key={item.href + idx}
              href={item.href}
              className={`flex items-center gap-3 px-5 py-2.5 text-sm transition-colors ${
                active ? "bg-marinise-orange/90 font-medium text-white" : "text-white/80 hover:bg-white/10"
              }`}
            >
              <span className="w-5 text-right text-xs text-white/40">{idx + 1}</span>
              {item.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
