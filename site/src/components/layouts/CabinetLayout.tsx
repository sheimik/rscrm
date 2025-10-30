import { NavLink, Outlet, useLocation } from "react-router-dom";
import { MapPin, Building2, PlusCircle, Users, User } from "lucide-react";
import { cn } from "@/lib/utils";

const navigation = [
  { name: "Маршрут", href: "/cabinet/route", icon: MapPin },
  { name: "Объекты", href: "/cabinet/objects", icon: Building2 },
  { name: "Добавить", href: "/cabinet/add", icon: PlusCircle },
  { name: "Клиенты", href: "/cabinet/customers", icon: Users },
  { name: "Профиль", href: "/cabinet/profile", icon: User },
];

export function CabinetLayout() {
  const location = useLocation();

  return (
    <div className="flex h-screen w-full flex-col overflow-hidden bg-background">
      {/* Main content */}
      <main className="flex-1 overflow-auto pb-20">
        <Outlet />
      </main>

      {/* Bottom Tab Bar */}
      <nav className="fixed bottom-0 left-0 right-0 z-50 flex h-16 items-center justify-around border-t border-border bg-card px-2 pb-safe">
        {navigation.map((item) => {
          const isActive = location.pathname === item.href;
          const isAddButton = item.href === "/cabinet/add";
          
          if (isAddButton) {
            return (
              <NavLink
                key={item.name}
                to={item.href}
                className="flex flex-col items-center justify-center"
              >
                <div className="flex h-14 w-14 -translate-y-4 items-center justify-center rounded-full bg-primary shadow-lg">
                  <item.icon className="h-7 w-7 text-primary-foreground" />
                </div>
              </NavLink>
            );
          }

          return (
            <NavLink
              key={item.name}
              to={item.href}
              className="flex flex-1 flex-col items-center justify-center gap-1 py-2"
            >
              <item.icon
                className={cn(
                  "h-6 w-6 transition-colors",
                  isActive ? "text-primary" : "text-muted-foreground"
                )}
              />
              <span
                className={cn(
                  "text-xs font-medium transition-colors",
                  isActive ? "text-primary" : "text-muted-foreground"
                )}
              >
                {item.name}
              </span>
            </NavLink>
          );
        })}
      </nav>
    </div>
  );
}
