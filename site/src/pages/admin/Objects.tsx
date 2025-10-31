import { useState, useMemo } from "react";
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
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { toast } from "sonner";
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

const statusMap: Record<string, string> = {
  "NEW": "Новый",
  "INTEREST": "В работе",
  "CALLBACK": "Ожидание",
  "DONE": "Завершён",
  "REJECTED": "Отказ",
};

const typeMap: Record<string, string> = {
  "MKD": "МКД",
  "BUSINESS_CENTER": "Бизнес-центр",
  "SHOPPING_CENTER": "ТЦ",
  "SCHOOL": "Школа",
  "HOSPITAL": "Больница",
};

export default function Objects() {
  const navigate = useNavigate();
  const [view, setView] = useState<"list" | "map">("list");
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCity, setSelectedCity] = useState<string>("all");
  const [selectedDistrict, setSelectedDistrict] = useState<string>("all");
  const [selectedType, setSelectedType] = useState<string>("all");
  const [selectedStatus, setSelectedStatus] = useState<string>("all");

  // Загружаем данные
  const { data: objectsData, isLoading } = useQuery({
    queryKey: ['objects', selectedCity !== "all" ? selectedCity : null, selectedDistrict !== "all" ? selectedDistrict : null, selectedStatus !== "all" ? selectedStatus : null, searchQuery],
    queryFn: () => api.getObjects({
      city_id: selectedCity !== "all" ? selectedCity : undefined,
      district_id: selectedDistrict !== "all" ? selectedDistrict : undefined,
      status: selectedStatus !== "all" ? selectedStatus as any : undefined,
      search: searchQuery || undefined,
      limit: 100,
    }),
  });

  const { data: citiesData } = useQuery({
    queryKey: ['cities'],
    queryFn: () => api.getCities(),
  });

  const { data: districtsData } = useQuery({
    queryKey: ['districts', selectedCity !== "all" ? selectedCity : null],
    queryFn: () => api.getDistricts(selectedCity !== "all" ? selectedCity : undefined),
    enabled: selectedCity !== "all",
  });

  const objects = objectsData?.items || [];
  const cities = citiesData || [];
  const districts = districtsData || [];

  const filteredBuildings = useMemo(() => {
    return objects.filter((obj: any) => {
      const matchesSearch = !searchQuery || obj.address.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesCity = selectedCity === "all" || obj.city_id === selectedCity;
      const matchesDistrict = selectedDistrict === "all" || obj.district_id === selectedDistrict;
      const matchesType = selectedType === "all" || obj.type === selectedType;
      const matchesStatus = selectedStatus === "all" || obj.status === selectedStatus;
      
      return matchesSearch && matchesCity && matchesDistrict && matchesType && matchesStatus;
    });
  }, [objects, searchQuery, selectedCity, selectedDistrict, selectedType, selectedStatus]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case "NEW": return "bg-blue-500";
      case "INTEREST": return "bg-yellow-500";
      case "CALLBACK": return "bg-orange-500";
      case "DONE": return "bg-green-500";
      case "REJECTED": return "bg-red-500";
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
                      {cities.map((city: any) => (
                        <SelectItem key={city.id} value={city.id}>
                          {city.name}
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
                      {districts.map((district: any) => (
                        <SelectItem key={district.id} value={district.id}>
                          {district.name}
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
                      <SelectItem value="MKD">МКД</SelectItem>
                      <SelectItem value="BUSINESS_CENTER">Бизнес-центр</SelectItem>
                      <SelectItem value="SHOPPING_CENTER">ТЦ</SelectItem>
                      <SelectItem value="SCHOOL">Школа</SelectItem>
                      <SelectItem value="HOSPITAL">Больница</SelectItem>
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
                      <SelectItem value="NEW">Новый</SelectItem>
                      <SelectItem value="INTEREST">В работе</SelectItem>
                      <SelectItem value="CALLBACK">Ожидание</SelectItem>
                      <SelectItem value="DONE">Завершён</SelectItem>
                      <SelectItem value="REJECTED">Отказ</SelectItem>
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
              {isLoading ? (
                <TableRow>
                  <TableCell colSpan={7} className="text-center text-muted-foreground">
                    Загрузка...
                  </TableCell>
                </TableRow>
              ) : filteredBuildings.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} className="text-center text-muted-foreground">
                    Нет данных. Измените фильтр или создайте запись.
                  </TableCell>
                </TableRow>
              ) : (
                filteredBuildings.map((building: any) => (
                  <TableRow
                    key={building.id}
                    className="cursor-pointer hover:bg-muted/50"
                    onClick={() => navigate(`/_admin/objects/${building.id}`)}
                  >
                    <TableCell>
                      <Badge variant="outline">{typeMap[building.type] || building.type}</Badge>
                    </TableCell>
                    <TableCell className="font-medium">{building.address}</TableCell>
                    <TableCell>
                      <div className="text-sm">
                        <div>{building.city?.name || "-"}</div>
                        <div className="text-muted-foreground">{building.district?.name || "-"}</div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge className={getStatusColor(building.status)}>
                        {statusMap[building.status] || building.status}
                      </Badge>
                    </TableCell>
                    <TableCell>{building.visits_count || 0}</TableCell>
                    <TableCell>{building.last_visit_at ? new Date(building.last_visit_at).toLocaleDateString('ru-RU') : "-"}</TableCell>
                    <TableCell>{building.responsible_user?.full_name || "-"}</TableCell>
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
