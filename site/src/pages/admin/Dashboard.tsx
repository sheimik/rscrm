import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Building2, ClipboardCheck, TrendingUp, Phone, Plus, FileDown, Upload } from "lucide-react";
import { mockBuildings, mockVisits, mockCustomers } from "@/lib/mockData";
import { toast } from "sonner";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { useState } from "react";

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
  const totalVisits = mockVisits.length;
  const completedVisits = mockVisits.filter(v => v.status === "Завершён").length;
  const avgRating = mockCustomers.reduce((sum, c) => sum + (c.rating || 0), 0) / mockCustomers.length;
  const leadsToCall = mockCustomers.filter(c => c.convenientTime).length;

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

  const onSubmit = (data: ObjectFormData) => {
    console.log("Новый объект:", data);
    toast.success("Объект успешно создан (демо)");
    setDialogOpen(false);
    form.reset();
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
              {mockBuildings.filter(b => b.status === "В работе").length}
            </div>
            <p className="text-xs text-muted-foreground">
              Из {mockBuildings.length} всего
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
              {mockVisits.slice(0, 3).map((visit) => (
                <div key={visit.id} className="flex items-start justify-between border-b border-border pb-3 last:border-0">
                  <div className="space-y-1">
                    <p className="text-sm font-medium">{visit.building}</p>
                    <p className="text-xs text-muted-foreground">
                      {visit.engineer} • {visit.date}
                    </p>
                  </div>
                  <span className={`text-xs font-medium ${
                    visit.status === "Завершён" ? "text-success" : "text-warning"
                  }`}>
                    {visit.status}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Клиенты с высоким интересом</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {mockCustomers.filter(c => c.interests.length > 2).map((customer) => (
                <div key={customer.id} className="flex items-start justify-between border-b border-border pb-3 last:border-0">
                  <div className="space-y-1">
                    <p className="text-sm font-medium">{customer.name}</p>
                    <p className="text-xs text-muted-foreground">
                      {customer.building} • кв. {customer.apartment}
                    </p>
                    <div className="flex flex-wrap gap-1">
                      {customer.interests.map((interest) => (
                        <span key={interest} className="rounded-md bg-muted px-2 py-0.5 text-xs">
                          {interest}
                        </span>
                      ))}
                    </div>
                  </div>
                  <Button size="sm" variant="ghost" onClick={() => handleAction(`Позвонить ${customer.name}`)}>
                    <Phone className="h-4 w-4" />
                  </Button>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
