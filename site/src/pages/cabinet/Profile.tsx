import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { LogOut, MapPin, CheckCircle, Clock, Upload, Loader2 } from "lucide-react";
import { ThemeToggle } from "@/components/ThemeToggle";
import { useCurrentUser } from "@/hooks/use-current-user";
import { useNavigate } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { toast } from "sonner";

const ROLE_LABELS: Record<string, string> = {
  ADMIN: "Администратор",
  SUPERVISOR: "Супервайзер",
  ENGINEER: "Инженер",
};

export default function Profile() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { data: currentUser, isLoading, isError, error } = useCurrentUser();

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (isError || !currentUser) {
    return (
      <div className="space-y-4 p-4 text-center text-muted-foreground">
        <p>Не удалось загрузить профиль.</p>
        <p>{error instanceof Error ? error.message : "Попробуйте позже."}</p>
      </div>
    );
  }

  const initials = currentUser.full_name
    ? currentUser.full_name
        .split(" ")
        .filter(Boolean)
        .slice(0, 2)
        .map((part) => part[0]?.toUpperCase() ?? "")
        .join("")
    : "?";

  const handleLogout = () => {
    api.logout();
    queryClient.clear();
    toast.success("Вы вышли из системы");
    navigate("/auth/login", { replace: true });
  };

  return (
    <div className="space-y-4 p-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Профиль</h1>
        <ThemeToggle />
      </div>

      <Card>
        <CardContent className="pt-6">
          <div className="flex items-start gap-4">
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary text-2xl font-bold text-primary-foreground">
              {initials}
            </div>
            <div className="flex-1 space-y-1">
              <h2 className="text-lg font-semibold">{currentUser.full_name}</h2>
              <Badge variant="outline">{ROLE_LABELS[currentUser.role] ?? currentUser.role}</Badge>
              <div className="flex items-center gap-1 text-sm text-muted-foreground">
                <MapPin className="h-3 w-3" />
                {currentUser.city?.name || "Город не указан"}
                {currentUser.district?.name ? ` • ${currentUser.district.name}` : ""}
              </div>
              {currentUser.email && (
                <p className="text-sm text-muted-foreground">{currentUser.email}</p>
              )}
              {currentUser.phone && (
                <p className="text-sm text-muted-foreground">{currentUser.phone}</p>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Состояние синхронизации</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">Статус:</span>
            <Badge variant="outline" className="bg-success text-success-foreground">
              Онлайн
            </Badge>
          </div>
          <div className="grid grid-cols-3 gap-2 text-center">
            <div className="rounded-lg bg-muted p-3">
              <div className="flex items-center justify-center gap-1 text-sm text-muted-foreground">
                <Clock className="h-3 w-3" />
              </div>
              <div className="mt-1 text-lg font-bold">—</div>
              <div className="text-xs text-muted-foreground">На устройстве</div>
            </div>
            <div className="rounded-lg bg-muted p-3">
              <div className="flex items-center justify-center gap-1 text-sm text-muted-foreground">
                <Upload className="h-3 w-3" />
              </div>
              <div className="mt-1 text-lg font-bold">—</div>
              <div className="text-xs text-muted-foreground">В очереди</div>
            </div>
            <div className="rounded-lg bg-muted p-3">
              <div className="flex items-center justify-center gap-1 text-sm text-muted-foreground">
                <CheckCircle className="h-3 w-3" />
              </div>
              <div className="mt-1 text-lg font-bold">—</div>
              <div className="text-xs text-muted-foreground">Отправлено</div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Настройки</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <Label htmlFor="start-view" className="text-sm">
              Стартовый вид
            </Label>
            <Badge variant="secondary">Список</Badge>
          </div>
          <div className="flex items-center justify-between">
            <Label htmlFor="gps" className="text-sm">
              GPS
            </Label>
            <Switch id="gps" defaultChecked />
          </div>
          <div className="flex items-center justify-between">
            <Label htmlFor="camera" className="text-sm">
              Камера
            </Label>
            <Switch id="camera" defaultChecked />
          </div>
          <div className="flex items-center justify-between">
            <Label htmlFor="notifications" className="text-sm">
              Уведомления
            </Label>
            <Switch id="notifications" defaultChecked />
          </div>
        </CardContent>
      </Card>

      <Button variant="outline" className="w-full" onClick={handleLogout}>
        <LogOut className="mr-2 h-4 w-4" />
        Выйти
      </Button>

      <p className="text-center text-xs text-muted-foreground">Версия 1.0.0</p>
    </div>
  );
}
