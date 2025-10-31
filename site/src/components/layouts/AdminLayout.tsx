import { NavLink, Outlet, useLocation } from "react-router-dom";
import {
  LayoutDashboard,
  Building2,
  ClipboardList,
  Users,
  BarChart3,
  FileText,
  // Settings,
  History,
  Bell,
  UserCog,
} from "lucide-react";
import { ThemeToggle } from "@/components/ThemeToggle";
import { cn } from "@/lib/utils";
import { useCurrentUser } from "@/hooks/use-current-user";

const ROLE_LABELS: Record<string, string> = {
  ADMIN: "Администратор",
  SUPERVISOR: "Супервайзер",
  ENGINEER: "Инженер",
};

const navigation = [
  { name: "Dashboard", href: "/_admin/dashboard", icon: LayoutDashboard },
  { name: "Объекты", href: "/_admin/objects", icon: Building2 },
  { name: "Визиты", href: "/_admin/visits", icon: ClipboardList },
  { name: "Клиенты", href: "/_admin/customers", icon: Users },
  { name: "Отчёты", href: "/_admin/reports", icon: FileText },
  { name: "Аналитика", href: "/_admin/analytics", icon: BarChart3 },
  { name: "Сотрудники", href: "/_admin/users", icon: UserCog },
  { name: "Аудит", href: "/_admin/audit", icon: History },
  { name: "Уведомления", href: "/_admin/notifications", icon: Bell },
  // { name: "Настройки", href: "/_admin/settings", icon: Settings },
];

export function AdminLayout() {
  const location = useLocation();
  const { data: currentUser } = useCurrentUser();
  const initials = currentUser?.full_name
    ? currentUser.full_name
        .split(" ")
        .filter(Boolean)
        .slice(0, 2)
        .map((part) => part[0]?.toUpperCase() ?? "")
        .join("")
    : "CRM";

  return (
    <div className="flex h-screen w-full overflow-hidden bg-background">
      {/* Sidebar */}
      <aside className="hidden w-64 border-r border-border bg-card lg:flex lg:flex-col">
        <div className="flex h-16 items-center border-b border-border px-6">
          <h1 className="text-xl font-bold text-foreground">CRM Admin</h1>
        </div>
        <nav className="flex-1 space-y-1 overflow-y-auto p-4">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href || 
                           (item.href !== "/_admin/dashboard" && location.pathname.startsWith(item.href));
            return (
              <NavLink
                key={item.name}
                to={item.href}
                className={cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                  isActive
                    ? "bg-primary text-primary-foreground"
                    : "text-muted-foreground hover:bg-muted hover:text-foreground"
                )}
              >
                <item.icon className="h-5 w-5" />
                {item.name}
              </NavLink>
            );
          })}
        </nav>
        <div className="border-t border-border p-4">
          <div className="flex items-center gap-3 rounded-lg bg-muted p-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary text-primary-foreground">
              {initials || "?"}
            </div>
            <div className="flex-1 text-sm">
              <p className="font-medium text-foreground">{currentUser?.full_name || "—"}</p>
              <p className="text-muted-foreground">
                {ROLE_LABELS[currentUser?.role ?? ""] || ""}
              </p>
            </div>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Header */}
        <header className="flex h-16 items-center justify-between border-b border-border bg-card px-6">
          <div className="flex items-center gap-4">
            <h2 className="text-lg font-semibold text-foreground">
              {navigation.find((item) => location.pathname.startsWith(item.href))?.name || "CRM"}
            </h2>
          </div>
          <div className="flex items-center gap-2">
            <ThemeToggle />
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-auto bg-background p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
