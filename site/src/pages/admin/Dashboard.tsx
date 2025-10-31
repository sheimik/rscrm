import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Building2, ClipboardCheck, TrendingUp, Phone, Plus, FileDown, Upload } from "lucide-react";
import { toast } from "sonner";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

const objectSchema = z.object({
  type: z.string().min(1, "Выберите тип объекта"),
  address: z.string().min(5, "Укажите адрес (минимум 5 символов)"),
  city: z.string().min(2, "Укажите город"),
  district: z.string().min(2, "Укажите район"),
  gps: z.string().optional(),
  contact: z.string().optional(),
  notes: z.string().optional(),
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

  const form = useForm<ObjectFormData>({
    resolver: zodResolver(objectSchema),
    defaultValues: {
      type: "",
      address: "",
      city: "",
      district: "",
      gps: "",
      contact: "",
      notes: "",
    },
  });

  const handleAction = (action: string) => {
    toast.info(`Демо-режим: ${action}`);
  };

  const onSubmit = async (data: ObjectFormData) => {
    try {
      // Получаем города для поиска ID
      const cities = await api.getCities();
      const city = cities.find(c => c.name === data.city);
      if (!city) {
        toast.error("Город не найден");
        return;
      }
      
      // Получаем районы для поиска ID
      let districtId = undefined;
      if (data.district) {
        const districts = await api.getDistricts(city.id);
        const district = districts.find(d => d.name === data.district);
        districtId = district?.id;
      }
      
      // Парсим GPS координаты
      let gpsLat = undefined;
      let gpsLng = undefined;
      if (data.gps) {
        const coords = data.gps.split(',').map(s => s.trim());
        if (coords.length === 2) {
          gpsLat = parseFloat(coords[0]);
          gpsLng = parseFloat(coords[1]);
        }
      }
      
      await api.createObject({
        type: data.type === "МКД" ? "MKD" : data.type === "Бизнес-центр" ? "BUSINESS_CENTER" : "SHOPPING_CENTER",
        address: data.address,
        city_id: city.id,
        district_id: districtId,
        gps_lat: gpsLat,
        gps_lng: gpsLng,
        status: "NEW",
      });
      
      toast.success("Объект успешно создан");
      setDialogOpen(false);
      form.reset();
      
      // Обновляем данные
      window.location.reload();
    } catch (error: any) {
      toast.error(error.message || "Ошибка при создании объекта");
    }
  };

  return (
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
          <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
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
                        <Select onValueChange={field.onChange} defaultValue={field.value}>
                          <FormControl>
                            <SelectTrigger>
                              <SelectValue placeholder="Выберите тип" />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent>
                            <SelectItem value="МКД">МКД</SelectItem>
                            <SelectItem value="Коттеджный посёлок">Коттеджный посёлок</SelectItem>
                            <SelectItem value="Бизнес-центр">Бизнес-центр</SelectItem>
                            <SelectItem value="ТЦ">ТЦ</SelectItem>
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
                      name="city"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Город</FormLabel>
                          <FormControl>
                            <Input placeholder="Москва" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="district"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Район</FormLabel>
                          <FormControl>
                            <Input placeholder="Центральный" {...field} />
                          </FormControl>
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

                  <FormField
                    control={form.control}
                    name="contact"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Контактное лицо (опционально)</FormLabel>
                        <FormControl>
                          <Input placeholder="Иванов И.И., +7 (999) 123-45-67" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="notes"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Примечания (опционально)</FormLabel>
                        <FormControl>
                          <Textarea 
                            placeholder="Дополнительная информация об объекте" 
                            className="resize-none"
                            rows={3}
                            {...field} 
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <div className="flex justify-end gap-2">
                    <Button type="button" variant="outline" onClick={() => setDialogOpen(false)}>
                      Отмена
                    </Button>
                    <Button type="submit">
                      Создать объект
                    </Button>
                  </div>
                </form>
              </Form>
            </DialogContent>
          </Dialog>
          
          <Button variant="outline" onClick={() => handleAction("Импорт из Excel")}>
            <Upload className="mr-2 h-4 w-4" />
            Импорт из Excel
          </Button>
          <Button variant="outline" onClick={() => handleAction("Экспорт отчёта")}>
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
  );
}
