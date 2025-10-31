import { useMemo } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { RefreshCw, Bell, Play } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { toast } from "sonner";
import { api } from "@/lib/api";
import { useCurrentUser } from "@/hooks/use-current-user";
import {
  INTEREST_LABELS,
  OBJECT_TYPE_LABELS,
  VISIT_STATUS_LABELS,
  translateOrFallback,
} from "@/lib/referenceData";
import { ApiVisit, PageResponse } from "@/lib/types";

const formatTime = (isoDate?: string | null) => {
  if (!isoDate) {
    return "—";
  }
  const date = new Date(isoDate);
  return date.toLocaleTimeString("ru-RU", { hour: "2-digit", minute: "2-digit" });
};

const formatDate = (isoDate?: string | null) => {
  if (!isoDate) {
    return "—";
  }
  const date = new Date(isoDate);
  return date.toLocaleDateString("ru-RU", { day: "numeric", month: "long" });
};

const isSameLocalDay = (first: Date, second: Date) =>
  first.getFullYear() === second.getFullYear() &&
  first.getMonth() === second.getMonth() &&
  first.getDate() === second.getDate();

export default function Route() {
  const { data: currentUser } = useCurrentUser();

  const {
    data: visitsData,
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery<PageResponse<ApiVisit>, Error>({
    queryKey: ["cabinet-today-visits"],
    queryFn: () => api.getVisits({ limit: 100 }) as Promise<PageResponse<ApiVisit>>,
    staleTime: 30_000,
  });

  const visits = visitsData?.items ?? [];

  const todayVisits = useMemo(() => {
    const today = new Date();
    return visits
      .filter((visit) => {
        if (!visit.scheduled_at) {
          return false;
        }
        const visitDate = new Date(visit.scheduled_at);
        return isSameLocalDay(visitDate, today);
      })
      .sort((a, b) => {
        const aTime = a.scheduled_at ? new Date(a.scheduled_at).getTime() : 0;
        const bTime = b.scheduled_at ? new Date(b.scheduled_at).getTime() : 0;
        return aTime - bTime;
      });
  }, [visits]);

  const totalTasks = todayVisits.length;
  const completedTasks = todayVisits.filter((visit) => visit.status === "DONE").length;
  const remainingTasks = totalTasks - completedTasks;

  const handleSync = async () => {
    const result = await refetch();
    if (result.error) {
      toast.error("Не удалось синхронизировать данные");
    } else {
      toast.success("Данные обновлены");
    }
  };

  const handleStartVisit = (visit: ApiVisit) => {
    toast.info(
      visit.status === "IN_PROGRESS"
        ? `Продолжаем визит по адресу ${visit.object?.address ?? "—"}`
        : `Начинаем визит по адресу ${visit.object?.address ?? "—"}`,
    );
  };

  return (
    <div className="space-y-4 p-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Сегодня</h1>
          {currentUser?.full_name && (
            <p className="text-sm text-muted-foreground">{currentUser.full_name}</p>
          )}
        </div>
        <div className="flex gap-2">
          <Button variant="ghost" size="icon" onClick={handleSync} disabled={isLoading}>
            <RefreshCw className={`h-5 w-5 ${isLoading ? "animate-spin" : ""}`} />
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
            <div className="text-2xl font-bold text-primary">{totalTasks}</div>
            <p className="text-xs text-muted-foreground">Задач</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4 text-center">
            <div className="text-2xl font-bold text-success">{completedTasks}</div>
            <p className="text-xs text-muted-foreground">Завершено</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4 text-center">
            <div className="text-2xl font-bold text-warning">{Math.max(remainingTasks, 0)}</div>
            <p className="text-xs text-muted-foreground">Осталось</p>
          </CardContent>
        </Card>
      </div>

      {/* Tasks */}
      <div className="space-y-3">
        <h2 className="text-lg font-semibold">Задачи на сегодня</h2>
        {isLoading ? (
          <Card>
            <CardContent className="py-8 text-center text-muted-foreground">
              Загружаем визиты...
            </CardContent>
          </Card>
        ) : isError ? (
          <Card>
            <CardContent className="space-y-3 py-6 text-center">
              <p className="text-muted-foreground">
                Не удалось получить список визитов{error?.message ? `: ${error.message}` : ""}
              </p>
              <Button variant="outline" onClick={() => refetch()}>
                Повторить запрос
              </Button>
            </CardContent>
          </Card>
        ) : todayVisits.length === 0 ? (
          <Card>
            <CardContent className="py-8 text-center text-muted-foreground">
              Нет задач на сегодня
            </CardContent>
          </Card>
        ) : (
          todayVisits.map((visit) => {
            const canStart = visit.status === "PLANNED" || visit.status === "IN_PROGRESS";
            return (
              <Card key={visit.id} className="overflow-hidden">
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <div className="space-y-1">
                      <div className="flex gap-2">
                        {visit.object?.type && (
                          <Badge variant="outline">
                            {translateOrFallback(OBJECT_TYPE_LABELS, visit.object.type)}
                          </Badge>
                        )}
                        <Badge>
                          {translateOrFallback(VISIT_STATUS_LABELS, visit.status)}
                        </Badge>
                      </div>
                      <CardTitle className="text-base">
                        {visit.object?.address || "Адрес не указан"}
                      </CardTitle>
                      <p className="text-sm text-muted-foreground">
                        {visit.customer?.full_name || "Клиент не указан"}
                      </p>
                    </div>
                    <span className="text-sm text-muted-foreground">
                      {formatDate(visit.scheduled_at)}
                    </span>
                  </div>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Время визита:</span>
                    <span className="font-medium">{formatTime(visit.scheduled_at)}</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Интересы:</span>
                    <span className="flex flex-wrap gap-1">
                      {visit.interests && visit.interests.length > 0 ? (
                        visit.interests.map((interest) => (
                          <Badge key={interest} variant="outline">
                            {translateOrFallback(INTEREST_LABELS, interest)}
                          </Badge>
                        ))
                      ) : (
                        <span className="font-medium">—</span>
                      )}
                    </span>
                  </div>
                  {visit.next_action_due_at && (
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Следующее действие:</span>
                      <span className="font-medium">
                        {formatDate(visit.next_action_due_at)}
                      </span>
                    </div>
                  )}
                  <Button
                    className="w-full"
                    onClick={() => handleStartVisit(visit)}
                    disabled={!canStart}
                  >
                    <Play className="mr-2 h-4 w-4" />
                    {visit.status === "IN_PROGRESS" ? "Продолжить визит" : "Старт визита"}
                  </Button>
                </CardContent>
              </Card>
            );
          })
        )}
      </div>
    </div>
  );
}
