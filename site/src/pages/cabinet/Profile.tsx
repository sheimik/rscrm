import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { LogOut, User, MapPin, CheckCircle, Clock, Upload } from "lucide-react";
import { ThemeToggle } from "@/components/ThemeToggle";
import { toast } from "sonner";

export default function Profile() {
  const handleLogout = () => {
    toast.info("Демо-режим: выход не реализован");
  };

  return (
    <div className="space-y-4 p-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Профиль</h1>
        <ThemeToggle />
      </div>

      {/* User Info */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-start gap-4">
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary text-2xl font-bold text-primary-foreground">
              ИИ
            </div>
            <div className="flex-1 space-y-1">
              <h2 className="text-lg font-semibold">Иванов Иван Иванович</h2>
              <Badge variant="outline">Инженер</Badge>
              <div className="flex items-center gap-1 text-sm text-muted-foreground">
                <MapPin className="h-3 w-3" />
                Москва • Центральный район
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Sync Status */}
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
              <div className="mt-1 text-lg font-bold">3</div>
              <div className="text-xs text-muted-foreground">На устройстве</div>
            </div>
            <div className="rounded-lg bg-muted p-3">
              <div className="flex items-center justify-center gap-1 text-sm text-muted-foreground">
                <Upload className="h-3 w-3" />
              </div>
              <div className="mt-1 text-lg font-bold">1</div>
              <div className="text-xs text-muted-foreground">В очереди</div>
            </div>
            <div className="rounded-lg bg-muted p-3">
              <div className="flex items-center justify-center gap-1 text-sm text-muted-foreground">
                <CheckCircle className="h-3 w-3" />
              </div>
              <div className="mt-1 text-lg font-bold">45</div>
              <div className="text-xs text-muted-foreground">Отправлено</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Settings */}
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

      {/* Logout */}
      <Button
        variant="outline"
        className="w-full"
        onClick={handleLogout}
      >
        <LogOut className="mr-2 h-4 w-4" />
        Выйти
      </Button>

      {/* Version */}
      <p className="text-center text-xs text-muted-foreground">
        Версия 1.0.0 (демо)
      </p>
    </div>
  );
}
