import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Building2, ClipboardCheck, TrendingUp, Phone, Plus, FileDown, Upload } from "lucide-react";
import { toast } from "sonner";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { useMemo, useRef, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { buildObjectsCsv, importObjectsFromCsv } from "@/lib/objectImportExport";
import { OBJECT_STATUS_LABELS, OBJECT_TYPE_LABELS } from "@/lib/referenceData";
import type { ObjectCreatePayload } from "@/lib/types";

const objectSchema = z.object({
  type: z.string().min(1, "Выберите тип объекта"),
  status: z.string().min(1, "Выберите статус"),
  address: z.string().min(5, "Укажите адрес (минимум 5 символов)"),
  cityId: z.string().min(1, "Выберите город"),
  districtId: z.string().optional(),
  gps: z.string().optional(),
  contactName: z.string().optional(),
  contactPhone: z.string().optional(),
});

type ObjectFormData = z.infer<typeof objectSchema>;

export default function Dashboard() {
  const [dialogOpen, setDialogOpen] = useState(false);
  
  // Загружаем данные через API
  const { data: visitsData } = useQuery({
    queryKey: ['visits', 'dashboard'],
    queryFn: () => api.getVisits({ limit: 100 }),
  });
  
  const { data: customersData } = useQuery({
    queryKey: ['customers', 'dashboard'],
    queryFn: () => api.getCustomers({ limit: 100 }),
  });
  
  const { data: objectsData } = useQuery({
    queryKey: ['objects', 'dashboard'],
    queryFn: () => api.getObjects({ limit: 100 }),
  });
  
  const { data: summaryData } = useQuery({
    queryKey: ['analytics', 'summary'],
    queryFn: () => api.getSummary('month'),
  });
  
  const visits = visitsData?.items || [];
  const customers = customersData?.items || [];
  const objects = objectsData?.items || [];
  
  const totalVisits = visits.length;
  const completedVisits = visits.filter(v => v.status === "DONE").length;
  const avgRating = customers.length > 0
    ? customers.reduce((sum: number, c: any) => sum + (c.provider_rating || 0), 0) / customers.length
    : 0;
  const leadsToCall = customers.filter((c: any) => c.preferred_call_time).length;
  const queryClient = useQueryClient();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const typeNameToEnum = useMemo(() => {
    return Object.entries(OBJECT_TYPE_LABELS).reduce<Record<string, string>>(
      (acc, [value, label]) => {
        acc[label.toLowerCase()] = value;
        return acc;
      },
      {},
    );
  }, []);
  const statusNameToEnum = useMemo(() => {
    return Object.entries(OBJECT_STATUS_LABELS).reduce<Record<string, string>>(
      (acc, [value, label]) => {
        acc[label.toLowerCase()] = value;
        return acc;
      },
      {},
    );
  }, []);

  const form = useForm<ObjectFormData>({
    resolver: zodResolver(objectSchema),
    defaultValues: {
      type: "MKD",
      status: "NEW",
      address: "",
      cityId: "",
      districtId: "",
      gps: "",
      contactName: "",
      contactPhone: "",
    },
  });
  const selectedCityId = form.watch("cityId");
  const { data: cities = [] } = useQuery({
    queryKey: ['cities'],
    queryFn: () => api.getCities(),
  });
  const { data: districts = [] } = useQuery({
    queryKey: ['districts', selectedCityId, 'dashboard'],
    queryFn: () => api.getDistricts(selectedCityId),
    enabled: Boolean(selectedCityId),
  });
  const createMutation = useMutation({
    mutationFn: (payload: ObjectCreatePayload) => api.createObject(payload),
    onSuccess: () => {
      toast.success("Объект успешно создан");
      setDialogOpen(false);
      form.reset();
      queryClient.invalidateQueries({ queryKey: ['objects'] });
      queryClient.invalidateQueries({ queryKey: ['objects', 'dashboard'] });
      queryClient.invalidateQueries({ queryKey: ['analytics', 'summary'] });
    },
    onError: (error: any) => {
      toast.error(error?.message || "Ошибка при создании объекта");
    },
  });

  const handleAction = (action: string) => {
    toast.info(`Демо-режим: ${action}`);
  };

  const handleDialogChange = (open: boolean) => {
    setDialogOpen(open);
    if (!open) {
      form.reset();
    }
  };

  const onSubmit = (data: ObjectFormData) => {
    const payload: ObjectCreatePayload = {
      type: data.type,
      status: data.status,
      address: data.address.trim(),
      city_id: data.cityId,
      district_id: data.districtId || undefined,
      contact_name: data.contactName?.trim() || undefined,
      contact_phone: data.contactPhone?.trim() || undefined,
    };

    if (data.gps) {
      const coords = data.gps.split(",").map((coord) => coord.trim());
      if (coords.length === 2) {
        const [latRaw, lngRaw] = coords;
        const lat = parseFloat(latRaw);
        const lng = parseFloat(lngRaw);
        if (!Number.isNaN(lat) && !Number.isNaN(lng)) {
          payload.gps_lat = lat;
          payload.gps_lng = lng;
        } else {
          toast.error("GPS координаты должны быть числами вида 55.751244, 37.618423");
          return;
        }
      } else {
        toast.error("Укажите две координаты через запятую");
        return;
      }
    }

    createMutation.mutate(payload);
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
        await Promise.all([
          queryClient.invalidateQueries({ queryKey: ['objects'] }),
          queryClient.invalidateQueries({ queryKey: ['objects', 'dashboard'] }),
          queryClient.invalidateQueries({ queryKey: ['analytics', 'summary'] }),
        ]);
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
    <div className="space-y-6">
      {/* KPI Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Визиты за период
            </CardTitle>
            <ClipboardCheck className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{completedVisits}/{totalVisits}</div>
            <p className="text-xs text-muted-foreground">
              Завершено за октябрь
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Объекты в работе
            </CardTitle>
            <Building2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {objects.filter(b => b.status === "INTEREST").length}
            </div>
            <p className="text-xs text-muted-foreground">
              Из {objects.length} всего
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Средняя оценка
            </CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{avgRating.toFixed(1)}/5</div>
            <p className="text-xs text-muted-foreground">
              Удовлетворённость провайдерами
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Лиды к прозвону
            </CardTitle>
            <Phone className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{leadsToCall}</div>
            <p className="text-xs text-muted-foreground">
              Требуют внимания
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Быстрые действия</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-2">
          <Dialog open={dialogOpen} onOpenChange={handleDialogChange}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                Создать объект
              </Button>
            </DialogTrigger>
            <DialogContent className="max-h-[90vh] overflow-y-auto sm:max-w-[550px]">
              <DialogHeader>
                <DialogTitle>Создание нового объекта</DialogTitle>
              </DialogHeader>
              <Form {...form}>
                <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                  <FormField
                    control={form.control}
                    name="type"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Тип объекта</FormLabel>
                        <Select value={field.value} onValueChange={field.onChange}>
                          <FormControl>
                            <SelectTrigger>
                              <SelectValue placeholder="Выберите тип" />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent>
                            {Object.entries(OBJECT_TYPE_LABELS).map(([value, label]) => (
                              <SelectItem key={value} value={value}>
                                {label}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name="status"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Статус</FormLabel>
                        <Select value={field.value} onValueChange={field.onChange}>
                          <FormControl>
                            <SelectTrigger>
                              <SelectValue placeholder="Выберите статус" />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent>
                            {Object.entries(OBJECT_STATUS_LABELS).map(([value, label]) => (
                              <SelectItem key={value} value={value}>
                                {label}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="address"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Адрес</FormLabel>
                        <FormControl>
                          <Input placeholder="ул. Пушкина, д. 12" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <div className="grid gap-4 sm:grid-cols-2">
                    <FormField
                      control={form.control}
                      name="cityId"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Город</FormLabel>
                          <Select
                            value={field.value}
                            onValueChange={(value) => {
                              field.onChange(value);
                              form.setValue("districtId", "");
                            }}
                            disabled={!cities.length}
                          >
                            <FormControl>
                              <SelectTrigger>
                                <SelectValue placeholder="Выберите город" />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              {cities.map((city: any) => (
                                <SelectItem key={city.id} value={city.id}>
                                  {city.name}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="districtId"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Район</FormLabel>
                          <Select
                            value={field.value ?? ""}
                            onValueChange={field.onChange}
                            disabled={!selectedCityId || !districts.length}
                          >
                            <FormControl>
                              <SelectTrigger>
                                <SelectValue placeholder="Выберите район" />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              {districts.map((district: any) => (
                                <SelectItem key={district.id} value={district.id}>
                                  {district.name}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>

                  <FormField
                    control={form.control}
                    name="gps"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>GPS координаты (опционально)</FormLabel>
                        <FormControl>
                          <Input placeholder="55.751244, 37.618423" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <div className="grid gap-4 sm:grid-cols-2">
                    <FormField
                      control={form.control}
                      name="contactName"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Контактное лицо (опционально)</FormLabel>
                          <FormControl>
                            <Input placeholder="Иванов И.И." {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={form.control}
                      name="contactPhone"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Телефон контакта (опционально)</FormLabel>
                          <FormControl>
                            <Input placeholder="+7 (999) 123-45-67" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>

                  <div className="flex justify-end gap-2">
                    <Button type="button" variant="outline" onClick={() => handleDialogChange(false)}>
                      Отмена
                    </Button>
                    <Button type="submit" disabled={createMutation.isPending}>
                      {createMutation.isPending ? "Создание..." : "Создать объект"}
                    </Button>
                  </div>
                </form>
              </Form>
            </DialogContent>
          </Dialog>
          
          <Button variant="outline" onClick={handleImportClick}>
            <Upload className="mr-2 h-4 w-4" />
            Импорт из Excel
          </Button>
          <Button variant="outline" onClick={handleExport}>
            <FileDown className="mr-2 h-4 w-4" />
            Экспорт отчёта
          </Button>
        </CardContent>
      </Card>

      {/* Recent Activity */}
      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Последние визиты</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {visits.slice(0, 3).map((visit: any) => (
                <div key={visit.id} className="flex items-start justify-between border-b border-border pb-3 last:border-0">
                  <div className="space-y-1">
                    <p className="text-sm font-medium">{visit.object?.address || "Объект"}</p>
                    <p className="text-xs text-muted-foreground">
                      {visit.engineer?.full_name || "Инженер"} • {visit.scheduled_at ? new Date(visit.scheduled_at).toLocaleString('ru-RU') : '-'}
                    </p>
                  </div>
                  <span className={`text-xs font-medium ${
                    visit.status === "DONE" ? "text-green-500" : "text-yellow-500"
                  }`}>
                    {visit.status === "DONE" ? "Завершён" : visit.status === "PLANNED" ? "Запланирован" : visit.status}
                  </span>
                </div>
              ))}
              {visits.length === 0 && (
                <p className="text-sm text-muted-foreground">Нет визитов</p>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Клиенты с высоким интересом</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {customers.filter((c: any) => c.interests && c.interests.length > 2).slice(0, 3).map((customer: any) => (
                <div key={customer.id} className="flex items-start justify-between border-b border-border pb-3 last:border-0">
                  <div className="space-y-1">
                    <p className="text-sm font-medium">{customer.full_name || "Клиент"}</p>
                    <p className="text-xs text-muted-foreground">
                      {customer.object?.address || "Адрес"} • {customer.portrait_text || "-"}
                    </p>
                    <div className="flex flex-wrap gap-1">
                      {customer.interests?.map((interest: string) => (
                        <span key={interest} className="rounded-md bg-muted px-2 py-0.5 text-xs">
                          {interest}
                        </span>
                      ))}
                    </div>
                  </div>
                  <Button size="sm" variant="ghost" onClick={() => handleAction(`Позвонить ${customer.full_name}`)}>
                    <Phone className="h-4 w-4" />
                  </Button>
                </div>
              ))}
              {customers.filter((c: any) => c.interests && c.interests.length > 2).length === 0 && (
                <p className="text-sm text-muted-foreground">Нет клиентов с высоким интересом</p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
    </>
  );
}
