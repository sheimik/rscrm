import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { RefreshCw, Bell, Play } from "lucide-react";
import { mockBuildings } from "@/lib/mockData";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";

export default function Route() {
  const navigate = useNavigate();
  
  // Задачи на сегодня - первые 3 объекта в работе
  const todayTasks = mockBuildings.filter(b => b.status === "В работе").slice(0, 3);

  const handleSync = () => {
    toast.info("Демо-режим: синхронизация недоступна");
  };

  const handleStartVisit = (building: typeof mockBuildings[0]) => {
    toast.info(`Начинаем визит: ${building.address}`);
    // В реальном приложении откроется мастер формы
  };

  return (
    <div className="space-y-4 p-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Сегодня</h1>
        <div className="flex gap-2">
          <Button variant="ghost" size="icon" onClick={handleSync}>
            <RefreshCw className="h-5 w-5" />
          </Button>
          <Button variant="ghost" size="icon">
            <Bell className="h-5 w-5" />
          </Button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-2">
        <Card>
          <CardContent className="pt-4 text-center">
            <div className="text-2xl font-bold text-primary">{todayTasks.length}</div>
            <p className="text-xs text-muted-foreground">Задач</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4 text-center">
            <div className="text-2xl font-bold text-success">2</div>
            <p className="text-xs text-muted-foreground">Выполнено</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4 text-center">
            <div className="text-2xl font-bold text-warning">1</div>
            <p className="text-xs text-muted-foreground">Осталось</p>
          </CardContent>
        </Card>
      </div>

      {/* Tasks */}
      <div className="space-y-3">
        <h2 className="text-lg font-semibold">Задачи на сегодня</h2>
        {todayTasks.length === 0 ? (
          <Card>
            <CardContent className="py-8 text-center text-muted-foreground">
              Нет задач на сегодня
            </CardContent>
          </Card>
        ) : (
          todayTasks.map((building) => (
            <Card key={building.id} className="overflow-hidden">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div className="space-y-1">
                    <Badge variant="outline">{building.type}</Badge>
                    <CardTitle className="text-base">{building.address}</CardTitle>
                    <p className="text-sm text-muted-foreground">
                      {building.city} • {building.district}
                    </p>
                  </div>
                  <Badge>{building.status}</Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Планируемое время:</span>
                  <span className="font-medium">10:00 - 12:00</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Ответственный:</span>
                  <span className="font-medium">{building.responsible}</span>
                </div>
                <Button 
                  className="w-full" 
                  onClick={() => handleStartVisit(building)}
                >
                  <Play className="mr-2 h-4 w-4" />
                  Старт визита
                </Button>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
