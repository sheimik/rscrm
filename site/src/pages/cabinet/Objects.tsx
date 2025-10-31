import { useMemo, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { MapIcon, List, Plus, Navigation } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { toast } from "sonner";
import { api } from "@/lib/api";
import { useCurrentUser } from "@/hooks/use-current-user";
import {
  OBJECT_STATUS_LABELS,
  OBJECT_TYPE_LABELS,
  getObjectStatusBadgeClass,
  translateOrFallback,
} from "@/lib/referenceData";
import { ApiObject, PageResponse } from "@/lib/types";

export default function CabinetObjects() {
  const [view, setView] = useState<"list" | "map">("list");
  const [searchQuery, setSearchQuery] = useState("");

  const { data: currentUser } = useCurrentUser();

  const {
    data: objectsData,
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery<PageResponse<ApiObject>, Error>({
    queryKey: ["cabinet-objects"],
    queryFn: () => api.getObjects({ limit: 200 }) as Promise<PageResponse<ApiObject>>,
    staleTime: 60_000,
  });

  const objects = objectsData?.items ?? [];

  const objectsForUser = useMemo(() => {
    if (currentUser?.role === "ENGINEER") {
      const assigned = objects.filter((obj) => {
        const responsibleId = obj.responsible_user_id || obj.responsible_user?.id;
        return responsibleId ? responsibleId === currentUser.id : false;
      });
      return assigned.length > 0 ? assigned : objects;
    }
    return objects;
  }, [objects, currentUser]);

  const filteredBuildings = useMemo(() => {
    const q = searchQuery.trim().toLowerCase();
    if (!q) {
      return objectsForUser;
    }
    return objectsForUser.filter((building) => {
      const address = building.address?.toLowerCase() ?? "";
      const city = building.city?.name?.toLowerCase() ?? "";
      const district = building.district?.name?.toLowerCase() ?? "";
      return address.includes(q) || city.includes(q) || district.includes(q);
    });
  }, [objectsForUser, searchQuery]);

  const handleAddObject = () => {
    toast.info("Демо-режим: добавление объекта");
  };

  const handleStartVisit = (object: ApiObject) => {
    toast.info(`Начинаем визит: ${object.address}`);
  };

  const getDistance = (object: ApiObject) => {
    if (object.gps_lat && object.gps_lng) {
      return "GPS сохранён";
    }
    return "—";
  };

  return (
    <div className="space-y-4 p-4">
      {/* Header */}
      <div className="space-y-4">
        <h1 className="text-2xl font-bold">Объекты</h1>

        {/* View Toggle */}
        <div className="flex gap-2">
          <Button
            variant={view === "list" ? "default" : "outline"}
            className="flex-1"
            onClick={() => setView("list")}
          >
            <List className="mr-2 h-4 w-4" />
            Список
          </Button>
          <Button
            variant={view === "map" ? "default" : "outline"}
            className="flex-1"
            onClick={() => setView("map")}
          >
            <MapIcon className="mr-2 h-4 w-4" />
            Карта
          </Button>
        </div>

        {/* Search */}
        <Input
          placeholder="Поиск по адресу..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      {/* Content */}
      {view === "list" ? (
        <div className="space-y-3">
          {isLoading ? (
            <Card>
              <CardContent className="py-10 text-center text-muted-foreground">
                Загружаем объекты...
              </CardContent>
            </Card>
          ) : isError ? (
            <Card>
              <CardContent className="space-y-3 py-6 text-center">
                <p className="text-muted-foreground">
                  Не удалось загрузить список объектов{error?.message ? `: ${error.message}` : ""}
                </p>
                <Button variant="outline" onClick={() => refetch()}>
                  Повторить запрос
                </Button>
              </CardContent>
            </Card>
          ) : filteredBuildings.length === 0 ? (
            <Card>
              <CardContent className="py-10 text-center text-muted-foreground">
                Нет объектов по заданным условиям
              </CardContent>
            </Card>
          ) : (
            filteredBuildings.map((building) => (
              <Card key={building.id}>
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <div className="space-y-1">
                      <div className="flex gap-2">
                        <Badge variant="outline" className="text-xs">
                          {translateOrFallback(OBJECT_TYPE_LABELS, building.type)}
                        </Badge>
                        <Badge
                          className={`text-xs text-white ${getObjectStatusBadgeClass(building.status)}`}
                        >
                          {translateOrFallback(OBJECT_STATUS_LABELS, building.status)}
                        </Badge>
                      </div>
                      <CardTitle className="text-base">{building.address}</CardTitle>
                      <p className="text-sm text-muted-foreground">
                        {building.city?.name || "—"} • {building.district?.name || "—"}
                      </p>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="flex items-center text-muted-foreground">
                      <Navigation className="mr-1 h-3 w-3" />
                      Расстояние:
                    </span>
                    <span className="font-medium">{getDistance(building)}</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Визитов:</span>
                    <span className="font-medium">{building.visits_count ?? 0}</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Ответственный:</span>
                    <span className="font-medium">
                      {building.responsible_user?.full_name || "—"}
                    </span>
                  </div>
                  {(building.contact_name || building.contact_phone) && (
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Контактное лицо:</span>
                      <span className="flex flex-col items-end">
                        {building.contact_name && (
                          <span className="font-medium">{building.contact_name}</span>
                        )}
                        {building.contact_phone && (
                          <span className="text-xs text-muted-foreground">
                            {building.contact_phone}
                          </span>
                        )}
                      </span>
                    </div>
                  )}
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Последний визит:</span>
                    <span className="font-medium">
                      {building.last_visit_at
                        ? new Date(building.last_visit_at).toLocaleDateString("ru-RU")
                        : "—"}
                    </span>
                  </div>
                  <div className="flex gap-2">
                    <Button className="flex-1" size="sm" onClick={() => handleStartVisit(building)}>
                      Старт визита
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>
      ) : (
        <Card className="flex h-[calc(100vh-16rem)] items-center justify-center">
          <div className="text-center">
            <MapIcon className="mx-auto h-16 w-16 text-muted-foreground" />
            <p className="mt-4 text-sm text-muted-foreground">
              Карта с текущей локацией
            </p>
            <p className="text-xs text-muted-foreground">(заглушка)</p>
          </div>
        </Card>
      )}

      {/* Add Object FAB */}
      <Button
        className="fixed bottom-20 right-4 z-40 h-14 w-14 rounded-full shadow-lg"
        size="icon"
        onClick={handleAddObject}
      >
        <Plus className="h-6 w-6" />
      </Button>
    </div>
  );
}
