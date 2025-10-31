import { useMemo, useRef, useState } from "react";
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
import { Plus, FileDown, Upload, Filter, MapIcon, List, UserPlus } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { ObjectCreatePayload, ApiObject, PageResponse, ApiCity, ApiDistrict, ApiUser } from "@/lib/types";
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
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { toast } from "sonner";
import { buildObjectsCsv, importObjectsFromCsv } from "@/lib/objectImportExport";

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
  "HOTEL": "Отель",
  "CAFE": "Кафе",
  "OTHER": "Другое",
};

export default function Objects() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [view, setView] = useState<"list" | "map">("list");
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCity, setSelectedCity] = useState<string>("all");
  const [selectedDistrict, setSelectedDistrict] = useState<string>("all");
  const [selectedType, setSelectedType] = useState<string>("all");
  const [selectedStatus, setSelectedStatus] = useState<string>("all");
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [createForm, setCreateForm] = useState({
    type: "MKD",
    status: "NEW",
    address: "",
    cityId: "",
    districtId: "",
    contactName: "",
    contactPhone: "",
  });
  const [createCityId, setCreateCityId] = useState<string>("");
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [delegationModal, setDelegationModal] = useState<{ open: boolean; objectId: string | null }>({
    open: false,
    objectId: null,
  });

  // Загружаем данные
  const { data: objectsData, isLoading } = useQuery<PageResponse<ApiObject>>({
    queryKey: ['objects', selectedCity !== "all" ? selectedCity : null, selectedDistrict !== "all" ? selectedDistrict : null, selectedStatus !== "all" ? selectedStatus : null, searchQuery],
    queryFn: async () => {
      const result = await api.getObjects({
        city_id: selectedCity !== "all" ? selectedCity : undefined,
        district_id: selectedDistrict !== "all" ? selectedDistrict : undefined,
        status: selectedStatus !== "all" ? selectedStatus as any : undefined,
        search: searchQuery || undefined,
        limit: 100,
      });
      return result as PageResponse<ApiObject>;
    },
  });

  const { data: citiesData } = useQuery<ApiCity[]>({
    queryKey: ['cities'],
    queryFn: async () => {
      const result = await api.getCities();
      return result as ApiCity[];
    },
  });

  const { data: districtsData } = useQuery<ApiDistrict[]>({
    queryKey: ['districts', selectedCity !== "all" ? selectedCity : null],
    queryFn: async () => {
      const result = await api.getDistricts(selectedCity !== "all" ? selectedCity : undefined);
      return result as ApiDistrict[];
    },
    enabled: selectedCity !== "all",
  });

  const { data: createDistricts = [] } = useQuery<ApiDistrict[]>({
    queryKey: ['districts', createCityId, 'create'],
    queryFn: async () => {
      const result = await api.getDistricts(createCityId);
      return result as ApiDistrict[];
    },
    enabled: Boolean(createCityId),
  });

  const objects: ApiObject[] = objectsData?.items || [];
  const cities: ApiCity[] = citiesData || [];
  const districts: ApiDistrict[] = districtsData || [];
  const resetCreateForm = () => {
    setCreateForm({
      type: "MKD",
      status: "NEW",
      address: "",
      cityId: "",
      districtId: "",
      contactName: "",
      contactPhone: "",
    });
    setCreateCityId("");
  };

  const createMutation = useMutation({
    mutationFn: (payload: ObjectCreatePayload) => api.createObject(payload),
    onSuccess: () => {
      toast.success("Объект создан");
      setIsCreateOpen(false);
      resetCreateForm();
      queryClient.invalidateQueries({ queryKey: ['objects'] });
    },
    onError: (error: any) => {
      toast.error(error?.message || "Не удалось создать объект");
    },
  });

  const filteredBuildings = useMemo(() => {
    return objects.filter((obj: ApiObject) => {
      const matchesSearch = !searchQuery || obj.address.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesCity = selectedCity === "all" || obj.city_id === selectedCity;
      const matchesDistrict = selectedDistrict === "all" || obj.district_id === selectedDistrict;
      const matchesType = selectedType === "all" || obj.type === selectedType;
      const matchesStatus = selectedStatus === "all" || obj.status === selectedStatus;
      
      return matchesSearch && matchesCity && matchesDistrict && matchesType && matchesStatus;
    });
  }, [objects, searchQuery, selectedCity, selectedDistrict, selectedType, selectedStatus]);

  const typeNameToEnum = useMemo(() => {
    return Object.entries(typeMap).reduce<Record<string, string>>((acc, [enumValue, label]) => {
      acc[label.toLowerCase()] = enumValue;
      return acc;
    }, {});
  }, []);

  const statusNameToEnum = useMemo(() => {
    return Object.entries(statusMap).reduce<Record<string, string>>((acc, [enumValue, label]) => {
      acc[label.toLowerCase()] = enumValue;
      return acc;
    }, {});
  }, []);

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
  const handleCreateDialogChange = (open: boolean) => {
    setIsCreateOpen(open);
    if (!open) {
      resetCreateForm();
    }
  };

  const handleCreateSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!createForm.address.trim()) {
      toast.error("Укажите адрес");
      return;
    }
    if (!createForm.cityId) {
      toast.error("Выберите город");
      return;
    }

    createMutation.mutate({
      type: createForm.type,
      address: createForm.address.trim(),
      city_id: createForm.cityId,
      district_id: createForm.districtId || undefined,
      status: createForm.status,
      contact_name: createForm.contactName.trim() || undefined,
      contact_phone: createForm.contactPhone.trim() || undefined,
    });
  };

  const handleImportClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileSelected = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }

    try {
      const { created, skipped } = await importObjectsFromCsv(file, {
        typeNameToEnum,
        statusNameToEnum,
        createObject: api.createObject.bind(api),
      });

      if (created > 0) {
        await queryClient.invalidateQueries({ queryKey: ['objects'] });
      }

      if (created === 0 && skipped === 0) {
        toast.info("Файл не содержит данных");
      } else {
        toast.success(`Импорт завершён. Успешно: ${created}, пропущено: ${skipped}`);
      }
    } catch (error: any) {
      toast.error(error?.message || "Не удалось импортировать файл");
    } finally {
      event.target.value = "";
    }
  };

  const handleExport = () => {
    if (!objects.length) {
      toast.info("Нет данных для экспорта");
      return;
    }

    const csvContent = buildObjectsCsv(objects);

    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `objects_${new Date().toISOString().slice(0, 10)}.csv`;
    document.body.appendChild(anchor);
    anchor.click();
    document.body.removeChild(anchor);
    URL.revokeObjectURL(url);

    toast.success("Экспорт выполнен");
  };

  return (
    <>
      <input
        ref={fileInputRef}
        type="file"
        accept=".csv"
        className="hidden"
        onChange={handleFileSelected}
      />
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
                      {districts.map((district) => (
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
                      <SelectItem value="HOTEL">Отель</SelectItem>
                      <SelectItem value="CAFE">Кафе</SelectItem>
                      <SelectItem value="OTHER">Другое</SelectItem>
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
          <Dialog open={isCreateOpen} onOpenChange={handleCreateDialogChange}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                Добавить
              </Button>
            </DialogTrigger>
            <DialogContent className="max-h-[90vh] overflow-y-auto sm:max-w-[520px]">
              <DialogHeader>
                <DialogTitle>Новый объект</DialogTitle>
              </DialogHeader>
              <form onSubmit={handleCreateSubmit} className="space-y-4">
                <div className="space-y-2">
                  <Label>Тип объекта</Label>
                  <Select
                    value={createForm.type}
                    onValueChange={(value) =>
                      setCreateForm((prev) => ({ ...prev, type: value }))
                    }
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="MKD">МКД</SelectItem>
                      <SelectItem value="BUSINESS_CENTER">Бизнес-центр</SelectItem>
                      <SelectItem value="SHOPPING_CENTER">ТЦ</SelectItem>
                      <SelectItem value="SCHOOL">Школа</SelectItem>
                      <SelectItem value="HOSPITAL">Больница</SelectItem>
                      <SelectItem value="HOTEL">Отель</SelectItem>
                      <SelectItem value="CAFE">Кафе</SelectItem>
                      <SelectItem value="OTHER">Другое</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Статус</Label>
                  <Select
                    value={createForm.status}
                    onValueChange={(value) =>
                      setCreateForm((prev) => ({ ...prev, status: value }))
                    }
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="NEW">Новый</SelectItem>
                      <SelectItem value="INTEREST">В работе</SelectItem>
                      <SelectItem value="CALLBACK">Ожидание</SelectItem>
                      <SelectItem value="DONE">Завершён</SelectItem>
                      <SelectItem value="REJECTED">Отказ</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Адрес</Label>
                  <Input
                    placeholder="ул. Пушкина, д. 12"
                    value={createForm.address}
                    onChange={(event) =>
                      setCreateForm((prev) => ({ ...prev, address: event.target.value }))
                    }
                  />
                </div>
                <div className="grid gap-4 sm:grid-cols-2">
                  <div className="space-y-2">
                    <Label>Город</Label>
                    <Select
                      value={createForm.cityId}
                      onValueChange={(value) => {
                        setCreateForm((prev) => ({ ...prev, cityId: value, districtId: "" }));
                        setCreateCityId(value);
                      }}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Выберите город" />
                      </SelectTrigger>
                      <SelectContent>
                        {cities.map((city) => (
                          <SelectItem key={city.id} value={city.id}>
                            {city.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Район</Label>
                    <Select
                      value={createForm.districtId}
                      onValueChange={(value) =>
                        setCreateForm((prev) => ({ ...prev, districtId: value }))
                      }
                      disabled={!createCityId}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Выберите район" />
                      </SelectTrigger>
                      <SelectContent>
                        {createDistricts.map((district) => (
                          <SelectItem key={district.id} value={district.id}>
                            {district.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div className="grid gap-4 sm:grid-cols-2">
                  <div className="space-y-2">
                    <Label>Контактное лицо</Label>
                    <Input
                      placeholder="ФИО"
                      value={createForm.contactName}
                      onChange={(event) =>
                        setCreateForm((prev) => ({ ...prev, contactName: event.target.value }))
                      }
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Телефон контакта</Label>
                    <Input
                      placeholder="+7 (___) ___-__-__"
                      value={createForm.contactPhone}
                      onChange={(event) =>
                        setCreateForm((prev) => ({ ...prev, contactPhone: event.target.value }))
                      }
                    />
                  </div>
                </div>
                <div className="flex justify-end gap-2">
                  <Button type="button" variant="outline" onClick={() => handleCreateDialogChange(false)}>
                    Отмена
                  </Button>
                  <Button type="submit" disabled={createMutation.isPending}>
                    {createMutation.isPending ? "Создание..." : "Создать"}
                  </Button>
                </div>
              </form>
            </DialogContent>
          </Dialog>
          <Button variant="outline" onClick={handleImportClick}>
            <Upload className="mr-2 h-4 w-4" />
            Импорт
          </Button>
          <Button variant="outline" onClick={handleExport}>
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
                <TableHead>Контакт</TableHead>
                <TableHead>Действия</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                <TableRow>
                  <TableCell colSpan={9} className="text-center text-muted-foreground">
                    Загрузка...
                  </TableCell>
                </TableRow>
              ) : filteredBuildings.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={9} className="text-center text-muted-foreground">
                    Нет данных. Измените фильтр или создайте запись.
                  </TableCell>
                </TableRow>
              ) : (
                filteredBuildings.map((building: any) => (
                  <TableRow
                    key={building.id}
                    className="hover:bg-muted/50"
                  >
                    <TableCell
                      className="cursor-pointer"
                      onClick={() => navigate(`/_admin/objects/${building.id}`)}
                    >
                      <Badge variant="outline">{typeMap[building.type] || building.type}</Badge>
                    </TableCell>
                    <TableCell
                      className="font-medium cursor-pointer"
                      onClick={() => navigate(`/_admin/objects/${building.id}`)}
                    >
                      {building.address}
                    </TableCell>
                    <TableCell
                      className="cursor-pointer"
                      onClick={() => navigate(`/_admin/objects/${building.id}`)}
                    >
                      <div className="text-sm">
                        <div>{building.city?.name || "-"}</div>
                        <div className="text-muted-foreground">{building.district?.name || "-"}</div>
                      </div>
                    </TableCell>
                    <TableCell
                      className="cursor-pointer"
                      onClick={() => navigate(`/_admin/objects/${building.id}`)}
                    >
                      <Badge className={getStatusColor(building.status)}>
                        {statusMap[building.status] || building.status}
                      </Badge>
                    </TableCell>
                    <TableCell
                      className="cursor-pointer"
                      onClick={() => navigate(`/_admin/objects/${building.id}`)}
                    >
                      {building.visits_count || 0}
                    </TableCell>
                    <TableCell
                      className="cursor-pointer"
                      onClick={() => navigate(`/_admin/objects/${building.id}`)}
                    >
                      {building.last_visit_at ? new Date(building.last_visit_at).toLocaleDateString('ru-RU') : "-"}
                    </TableCell>
                    <TableCell
                      className="cursor-pointer"
                      onClick={() => navigate(`/_admin/objects/${building.id}`)}
                    >
                      {building.responsible_user?.full_name || "-"}
                    </TableCell>
                    <TableCell
                      className="cursor-pointer"
                      onClick={() => navigate(`/_admin/objects/${building.id}`)}
                    >
                      <div className="text-sm">
                        <div>{building.contact_name || "-"}</div>
                        <div className="text-muted-foreground text-xs">{building.contact_phone || ""}</div>
                      </div>
                    </TableCell>
                    <TableCell onClick={(e) => e.stopPropagation()}>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setDelegationModal({ open: true, objectId: building.id })}
                      >
                        <UserPlus className="h-4 w-4 mr-1" />
                        Обход
                      </Button>
                    </TableCell>
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

      {/* Модальное окно делегирования */}
      <DelegationModal
        open={delegationModal.open}
        objectId={delegationModal.objectId}
        onClose={() => setDelegationModal({ open: false, objectId: null })}
        onSuccess={() => {
          setDelegationModal({ open: false, objectId: null });
          queryClient.invalidateQueries({ queryKey: ['objects'] });
        }}
      />
    </div>
    </>
  );
}

// Компонент модального окна делегирования
function DelegationModal({
  open,
  objectId,
  onClose,
  onSuccess,
}: {
  open: boolean;
  objectId: string | null;
  onClose: () => void;
  onSuccess: () => void;
}) {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedSupervisor, setSelectedSupervisor] = useState<string | null>(null);

  const { data: supervisors, isLoading } = useQuery<ApiUser[]>({
    queryKey: ['supervisors', searchQuery],
    queryFn: async () => {
      const result = await api.searchSupervisors(searchQuery || undefined);
      return result as ApiUser[];
    },
    enabled: open,
  });

  const delegateMutation = useMutation({
    mutationFn: (supervisorId: string) => {
      if (!objectId) throw new Error("Object ID is required");
      return api.delegateObject(objectId, supervisorId);
    },
    onSuccess: () => {
      toast.success("Объект успешно делегирован супервайзеру");
      onSuccess();
    },
    onError: (error: any) => {
      toast.error(error?.message || "Не удалось делегировать объект");
    },
  });

  const handleDelegate = () => {
    if (selectedSupervisor) {
      delegateMutation.mutate(selectedSupervisor);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Делегировать объект супервайзеру</DialogTitle>
        </DialogHeader>
        <div className="space-y-4">
          <div className="space-y-2">
            <Label>Поиск супервайзера</Label>
            <Input
              placeholder="Введите имя или email..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>

          <div className="space-y-2">
            <Label>Выберите супервайзера</Label>
            <div className="border rounded-md max-h-[300px] overflow-y-auto">
              {isLoading ? (
                <div className="p-4 text-center text-muted-foreground">
                  Загрузка...
                </div>
              ) : supervisors && supervisors.length > 0 ? (
                <div className="divide-y">
                  {supervisors.map((supervisor) => (
                    <div
                      key={supervisor.id}
                      className={`p-3 cursor-pointer hover:bg-muted ${
                        selectedSupervisor === supervisor.id ? "bg-muted" : ""
                      }`}
                      onClick={() => setSelectedSupervisor(supervisor.id)}
                    >
                      <div className="font-medium">{supervisor.full_name}</div>
                      <div className="text-sm text-muted-foreground">
                        {supervisor.email}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="p-4 text-center text-muted-foreground">
                  {searchQuery ? "Супервайзеры не найдены" : "Начните вводить для поиска"}
                </div>
              )}
            </div>
          </div>

          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={onClose}>
              Отмена
            </Button>
            <Button
              onClick={handleDelegate}
              disabled={!selectedSupervisor || delegateMutation.isPending}
            >
              {delegateMutation.isPending ? "Делегирование..." : "Делегировать"}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
