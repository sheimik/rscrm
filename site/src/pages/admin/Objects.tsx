import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Plus, FileDown, Upload, Filter, MapIcon, List } from "lucide-react";
import { mockBuildings, Building, statuses, cities, districts, buildingTypes } from "@/lib/mockData";
import { useNavigate } from "react-router-dom";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { toast } from "sonner";

export default function Objects() {
  const navigate = useNavigate();
  const [view, setView] = useState<"list" | "map">("list");
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCity, setSelectedCity] = useState<string>("all");
  const [selectedDistrict, setSelectedDistrict] = useState<string>("all");
  const [selectedType, setSelectedType] = useState<string>("all");
  const [selectedStatus, setSelectedStatus] = useState<string>("all");

  const filteredBuildings = mockBuildings.filter((building) => {
    const matchesSearch = building.address.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         building.city.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCity = selectedCity === "all" || building.city === selectedCity;
    const matchesDistrict = selectedDistrict === "all" || building.district === selectedDistrict;
    const matchesType = selectedType === "all" || building.type === selectedType;
    const matchesStatus = selectedStatus === "all" || building.status === selectedStatus;
    
    return matchesSearch && matchesCity && matchesDistrict && matchesType && matchesStatus;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case "Новый": return "bg-blue-500";
      case "В работе": return "bg-yellow-500";
      case "Ожидание": return "bg-orange-500";
      case "Завершён": return "bg-green-500";
      case "Отказ": return "bg-red-500";
      default: return "bg-gray-500";
    }
  };

  const handleAction = (action: string) => {
    toast.info(`Демо-режим: ${action}`);
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex flex-1 gap-2">
          <Input
            placeholder="Поиск по адресу или городу..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="max-w-sm"
          />
          <Sheet>
            <SheetTrigger asChild>
              <Button variant="outline">
                <Filter className="mr-2 h-4 w-4" />
                Фильтры
              </Button>
            </SheetTrigger>
            <SheetContent>
              <SheetHeader>
                <SheetTitle>Фильтры</SheetTitle>
                <SheetDescription>
                  Настройте параметры для поиска объектов
                </SheetDescription>
              </SheetHeader>
              <div className="mt-6 space-y-4">
                <div className="space-y-2">
                  <Label>Город</Label>
                  <Select value={selectedCity} onValueChange={setSelectedCity}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">Все города</SelectItem>
                      {cities.map((city) => (
                        <SelectItem key={city} value={city}>
                          {city}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Район</Label>
                  <Select value={selectedDistrict} onValueChange={setSelectedDistrict}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">Все районы</SelectItem>
                      {districts.map((district) => (
                        <SelectItem key={district} value={district}>
                          {district}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Тип объекта</Label>
                  <Select value={selectedType} onValueChange={setSelectedType}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">Все типы</SelectItem>
                      {buildingTypes.map((type) => (
                        <SelectItem key={type} value={type}>
                          {type}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Статус</Label>
                  <Select value={selectedStatus} onValueChange={setSelectedStatus}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">Все статусы</SelectItem>
                      {statuses.map((status) => (
                        <SelectItem key={status} value={status}>
                          {status}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </SheetContent>
          </Sheet>
        </div>
        <div className="flex gap-2">
          <Button
            variant={view === "list" ? "default" : "outline"}
            size="icon"
            onClick={() => setView("list")}
          >
            <List className="h-4 w-4" />
          </Button>
          <Button
            variant={view === "map" ? "default" : "outline"}
            size="icon"
            onClick={() => setView("map")}
          >
            <MapIcon className="h-4 w-4" />
          </Button>
          <Button onClick={() => handleAction("Добавить объект")}>
            <Plus className="mr-2 h-4 w-4" />
            Добавить
          </Button>
          <Button variant="outline" onClick={() => handleAction("Импорт")}>
            <Upload className="mr-2 h-4 w-4" />
            Импорт
          </Button>
          <Button variant="outline" onClick={() => handleAction("Экспорт")}>
            <FileDown className="mr-2 h-4 w-4" />
            Экспорт
          </Button>
        </div>
      </div>

      {/* Content */}
      {view === "list" ? (
        <Card>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Тип</TableHead>
                <TableHead>Адрес/Название</TableHead>
                <TableHead>Город/Район</TableHead>
                <TableHead>Статус</TableHead>
                <TableHead>Визиты</TableHead>
                <TableHead>Последний визит</TableHead>
                <TableHead>Ответственный</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredBuildings.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} className="text-center text-muted-foreground">
                    Нет данных. Измените фильтр или создайте запись.
                  </TableCell>
                </TableRow>
              ) : (
                filteredBuildings.map((building) => (
                  <TableRow
                    key={building.id}
                    className="cursor-pointer hover:bg-muted/50"
                    onClick={() => navigate(`/_admin/objects/${building.id}`)}
                  >
                    <TableCell>
                      <Badge variant="outline">{building.type}</Badge>
                    </TableCell>
                    <TableCell className="font-medium">{building.address}</TableCell>
                    <TableCell>
                      <div className="text-sm">
                        <div>{building.city}</div>
                        <div className="text-muted-foreground">{building.district}</div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge className={getStatusColor(building.status)}>
                        {building.status}
                      </Badge>
                    </TableCell>
                    <TableCell>{building.visitsCount}</TableCell>
                    <TableCell>{building.lastVisit}</TableCell>
                    <TableCell>{building.responsible}</TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </Card>
      ) : (
        <Card className="flex h-[600px] items-center justify-center">
          <div className="text-center">
            <MapIcon className="mx-auto h-16 w-16 text-muted-foreground" />
            <p className="mt-4 text-lg font-medium text-muted-foreground">
              Карта (заглушка)
            </p>
            <p className="text-sm text-muted-foreground">
              Здесь будет отображаться карта с маркерами объектов
            </p>
          </div>
        </Card>
      )}
    </div>
  );
}
