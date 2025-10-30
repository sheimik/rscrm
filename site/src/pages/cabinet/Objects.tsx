import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { MapIcon, List, Plus, Navigation } from "lucide-react";
import { mockBuildings } from "@/lib/mockData";
import { toast } from "sonner";

export default function CabinetObjects() {
  const [view, setView] = useState<"list" | "map">("list");
  const [searchQuery, setSearchQuery] = useState("");

  const filteredBuildings = mockBuildings.filter((building) =>
    building.address.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleAddObject = () => {
    toast.info("Демо-режим: добавление объекта");
  };

  const handleStartVisit = (address: string) => {
    toast.info(`Начинаем визит: ${address}`);
  };

  // Фиктивное расстояние
  const getDistance = () => `${(Math.random() * 5 + 0.5).toFixed(1)} км`;

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
          {filteredBuildings.map((building) => (
            <Card key={building.id}>
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div className="space-y-1">
                    <div className="flex gap-2">
                      <Badge variant="outline" className="text-xs">
                        {building.type}
                      </Badge>
                      <Badge className="text-xs">{building.status}</Badge>
                    </div>
                    <CardTitle className="text-base">{building.address}</CardTitle>
                    <p className="text-sm text-muted-foreground">
                      {building.city} • {building.district}
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
                  <span className="font-medium">{getDistance()}</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Визитов:</span>
                  <span className="font-medium">{building.visitsCount}</span>
                </div>
                <div className="flex gap-2">
                  <Button 
                    className="flex-1" 
                    size="sm"
                    onClick={() => handleStartVisit(building.address)}
                  >
                    Старт визита
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
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
