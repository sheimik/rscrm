import { useMemo, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

const services = ["INTERNET", "TV", "CCTV", "BABY_MONITOR"];

export default function Customers() {
  const [q, setQ] = useState("");
  const [service, setService] = useState<string>("Все");

  const { data: customersData, isLoading } = useQuery({
    queryKey: ['customers', q, service !== "Все" ? service : null],
    queryFn: () => api.getCustomers({
      q: q || undefined,
      interests: service !== "Все" ? service : undefined,
      limit: 100,
    }),
  });

  const customers = customersData?.items || [];

  const rows = useMemo(() => {
    return customers.filter((c: any) => {
      const byService = service === "Все" || c.interests?.includes(service);
      return byService;
    });
  }, [customers, service]);

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Фильтры</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-3 sm:grid-cols-2">
          <Input placeholder="Поиск по имени/телефону/адресу" value={q} onChange={e => setQ(e.target.value)} />
          <Select value={service} onValueChange={setService}>
            <SelectTrigger>
              <SelectValue placeholder="Интерес" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="Все">Все</SelectItem>
              {services.map(s => (
                <SelectItem key={s} value={s}>{s}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Клиенты ({rows.length})</CardTitle>
        </CardHeader>
        <CardContent className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Имя</TableHead>
                <TableHead>Телефон</TableHead>
                <TableHead>Адрес</TableHead>
                <TableHead>Провайдер</TableHead>
                <TableHead>Оценка</TableHead>
                <TableHead>Интересы</TableHead>
                <TableHead>Обновлено</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                <TableRow>
                  <TableCell colSpan={7} className="text-center text-muted-foreground">
                    Загрузка...
                  </TableCell>
                </TableRow>
              ) : rows.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} className="text-center text-muted-foreground">
                    Нет клиентов
                  </TableCell>
                </TableRow>
              ) : (
                rows.map((c: any) => (
                  <TableRow key={c.id} className="hover:bg-muted/50">
                    <TableCell>{c.full_name || "-"}</TableCell>
                    <TableCell>{c.phone || "-"}</TableCell>
                    <TableCell>{c.object?.address || "-"}, {c.portrait_text || "-"}</TableCell>
                    <TableCell>{c.current_provider ?? "-"}</TableCell>
                    <TableCell>{c.provider_rating ?? "-"}</TableCell>
                    <TableCell className="space-x-1">
                      {c.interests?.map((i: string) => (
                        <Badge key={i} variant="outline">{i}</Badge>
                      )) || "-"}
                    </TableCell>
                    <TableCell>{c.updated_at ? new Date(c.updated_at).toLocaleDateString('ru-RU') : "-"}</TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}


