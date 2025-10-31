import { useMemo } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { ArrowLeft, Edit, Plus, FileDown, Loader2, MapPin, Phone, User } from "lucide-react";
import { toast } from "sonner";
import { api } from "@/lib/api";
import {
  OBJECT_STATUS_LABELS,
  OBJECT_TYPE_LABELS,
  VISIT_STATUS_LABELS,
  INTEREST_LABELS,
  translateOrFallback,
} from "@/lib/referenceData";
import type { ApiCustomer, ApiObject, ApiVisit, PageResponse } from "@/lib/types";

export default function ObjectDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const {
    data: objectData,
    isLoading: isObjectLoading,
    isError: isObjectError,
    error: objectError,
  } = useQuery<ApiObject, Error>({
    queryKey: ["object", id],
    queryFn: async () => {
      const result = await api.getObject(id as string);
      return result as ApiObject;
    },
    enabled: Boolean(id),
  });

  const { data: visitsData, isLoading: isVisitsLoading } = useQuery<PageResponse<ApiVisit>, Error>({
    queryKey: ["object-visits", id],
    queryFn: () => api.getVisits({ object_id: id, limit: 100 }) as Promise<PageResponse<ApiVisit>>,
    enabled: Boolean(id),
    staleTime: 60_000,
  });

  const { data: customersData, isLoading: isCustomersLoading } = useQuery<PageResponse<ApiCustomer>, Error>({
    queryKey: ["object-customers", id],
    queryFn: () => api.getCustomers({ object_id: id, limit: 100 }) as Promise<PageResponse<ApiCustomer>>,
    enabled: Boolean(id),
    staleTime: 60_000,
  });

  const visits = visitsData?.items ?? [];
  const customers = customersData?.items ?? [];

  const uniqueUnits = useMemo(() => {
    const units = new Set<string>();
    customers.forEach((customer) => {
      if (customer.unit_id) {
        units.add(customer.unit_id);
      }
    });
    return Array.from(units);
  }, [customers]);

  const handleAction = (action: string) => {
    toast.info(`${action} пока недоступно`);
  };

  if (isObjectLoading) {
    return (
      <div className="flex h-[60vh] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (isObjectError || !objectData) {
    const message = objectError instanceof Error ? objectError.message : "";
    return (
      <div className="space-y-4 text-center">
        <p className="text-muted-foreground">
          {message.toLowerCase().includes("404") ? "Объект не найден" : "Не удалось загрузить объект"}
        </p>
        <Button onClick={() => navigate("/_admin/objects")}>
          <ArrowLeft className="mr-2 h-4 w-4" /> Вернуться к списку
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div className="space-y-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate("/_admin/objects")}
            className="mb-2"
          >
            <ArrowLeft className="mr-2 h-4 w-4" /> Назад к списку
          </Button>
          <h1 className="text-3xl font-bold">{objectData.address}</h1>
          <div className="flex flex-wrap gap-2 text-sm text-muted-foreground">
            <Badge variant="outline">
              {translateOrFallback(OBJECT_TYPE_LABELS, objectData.type)}
            </Badge>
            <Badge>{translateOrFallback(OBJECT_STATUS_LABELS, objectData.status)}</Badge>
            {objectData.city?.name && (
              <span className="flex items-center gap-1">
                <MapPin className="h-3 w-3" />
                {objectData.city?.name}
                {objectData.district?.name ? ` • ${objectData.district.name}` : ""}
              </span>
            )}
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => handleAction("Экспорт по объекту")}> <FileDown className="mr-2 h-4 w-4" /> Экспорт</Button>
          <Button onClick={() => handleAction("Редактировать")}> <Edit className="mr-2 h-4 w-4" /> Редактировать</Button>
        </div>
      </div>

      <Tabs defaultValue="general" className="w-full">
        <TabsList>
          <TabsTrigger value="general">Общее</TabsTrigger>
          <TabsTrigger value="visits">Визиты ({visits.length})</TabsTrigger>
          <TabsTrigger value="customers">Клиенты ({customers.length})</TabsTrigger>
        </TabsList>

        <TabsContent value="general" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Основная информация</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <InfoRow label="Адрес" value={objectData.address} />
                <InfoRow label="Тип" value={translateOrFallback(OBJECT_TYPE_LABELS, objectData.type)} />
                <InfoRow label="Статус" value={translateOrFallback(OBJECT_STATUS_LABELS, objectData.status)} />
                <InfoRow label="Город" value={objectData.city?.name || "—"} />
                <InfoRow label="Район" value={objectData.district?.name || "—"} />
                <InfoRow label="Ответственный" value={objectData.responsible_user?.full_name || "—"} />
                <InfoRow label="Контакт" value={objectData.contact_name || "—"} />
                <InfoRow label="Телефон контакта" value={objectData.contact_phone || "—"} />
                <InfoRow
                  label="Последний визит"
                  value={objectData.last_visit_at ? new Date(objectData.last_visit_at).toLocaleString("ru-RU") : "—"}
                />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Связанные данные</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <InfoRow label="Визитов" value={objectData.visits_count ?? 0} />
                <InfoRow label="Клиентов" value={customers.length} />
                <InfoRow label="Уникальных юнитов" value={uniqueUnits.length} />
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="visits">
          <Card>
            <CardHeader>
              <CardTitle>История визитов</CardTitle>
            </CardHeader>
            <CardContent>
              {isVisitsLoading ? (
                <div className="flex justify-center py-8 text-muted-foreground">Загрузка визитов...</div>
              ) : visits.length === 0 ? (
                <p className="text-center text-muted-foreground">Визиты отсутствуют</p>
              ) : (
                <div className="space-y-4">
                  {visits.map((visit) => (
                    <div key={visit.id} className="rounded-lg border border-border p-4">
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <div className="space-y-1">
                          <p className="text-sm text-muted-foreground">
                            {visit.scheduled_at
                              ? new Date(visit.scheduled_at).toLocaleString("ru-RU")
                              : "Дата не назначена"}
                          </p>
                          <p className="font-medium">
                            {visit.engineer?.full_name || "Инженер не указан"}
                          </p>
                        </div>
                        <Badge>{translateOrFallback(VISIT_STATUS_LABELS, visit.status)}</Badge>
                      </div>
                      {visit.customer?.full_name && (
                        <div className="mt-2 flex items-center gap-2 text-sm text-muted-foreground">
                          <User className="h-3 w-3" /> {visit.customer.full_name}
                        </div>
                      )}
                      {visit.customer?.phone && (
                        <div className="mt-1 flex items-center gap-2 text-sm text-muted-foreground">
                          <Phone className="h-3 w-3" /> {visit.customer.phone}
                        </div>
                      )}
                      {visit.interests && visit.interests.length > 0 && (
                        <div className="mt-3 flex flex-wrap gap-2">
                          {visit.interests.map((interest) => (
                            <Badge key={interest} variant="outline">
                              {translateOrFallback(INTEREST_LABELS, interest)}
                            </Badge>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="customers">
          <Card>
            <CardHeader>
              <CardTitle>Клиенты</CardTitle>
            </CardHeader>
            <CardContent className="overflow-x-auto">
              {isCustomersLoading ? (
                <div className="py-6 text-center text-muted-foreground">Загрузка клиентов...</div>
              ) : customers.length === 0 ? (
                <p className="text-center text-muted-foreground">Клиенты отсутствуют</p>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Имя</TableHead>
                      <TableHead>Телефон</TableHead>
                      <TableHead>Интересы</TableHead>
                      <TableHead>Обновлён</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {customers.map((customer) => (
                      <TableRow key={customer.id}>
                        <TableCell>{customer.full_name || "—"}</TableCell>
                        <TableCell>{customer.phone || "—"}</TableCell>
                        <TableCell>
                          <div className="flex flex-wrap gap-1">
                            {customer.interests && customer.interests.length > 0
                              ? customer.interests.map((interest) => (
                                  <Badge key={interest} variant="outline">
                                    {interest}
                                  </Badge>
                                ))
                              : "—"}
                          </div>
                        </TableCell>
                        <TableCell>
                          {customer.updated_at
                            ? new Date(customer.updated_at).toLocaleString("ru-RU")
                            : "—"}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

function InfoRow({ label, value }: { label: string; value: string | number | null | undefined }) {
  const displayValue =
    value === null || value === undefined || (typeof value === "string" && value.trim() === "")
      ? "—"
      : value;
  return (
    <div className="flex items-center justify-between text-sm">
      <span className="text-muted-foreground">{label}:</span>
      <span className="font-medium">{displayValue}</span>
    </div>
  );
}
