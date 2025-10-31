import { useMemo, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

const statusMap: Record<string, string> = {
  "DONE": "Завершён",
  "IN_PROGRESS": "В процессе",
  "CANCELLED": "Отменён",
  "PLANNED": "Запланирован",
};

export default function Visits() {
  const [q, setQ] = useState("");
  const [status, setStatus] = useState<string>("Все");
  const [engineer, setEngineer] = useState<string>("Все");

  const { data: visitsData, isLoading } = useQuery({
    queryKey: ['visits', status !== "Все" ? status : null],
    queryFn: () => api.getVisits({
      status: status !== "Все" ? status as any : undefined,
      limit: 100,
    }),
  });

  const visits = visitsData?.items || [];
  
  const engineers = useMemo(() => Array.from(new Set(visits.map((v: any) => v.engineer?.full_name).filter(Boolean))), [visits]);
  const statuses = ["Все", "DONE", "IN_PROGRESS", "CANCELLED", "PLANNED"];

  const rows = useMemo(() => {
    const ql = q.trim().toLowerCase();
    return visits.filter((v: any) => {
      const byQ = !ql || [
        v.object?.address || "",
        v.unit?.unit_number || "",
        v.engineer?.full_name || ""
      ].some(x => x.toLowerCase().includes(ql));
      const byStatus = status === "Все" || v.status === status;
      const byEngineer = engineer === "Все" || v.engineer?.full_name === engineer;
      return byQ && byStatus && byEngineer;
    });
  }, [visits, q, status, engineer]);

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Фильтры</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-3 sm:grid-cols-3">
          <Input placeholder="Поиск по адресу/квартире/инженеру" value={q} onChange={e => setQ(e.target.value)} />
          <Select value={status} onValueChange={setStatus}>
            <SelectTrigger>
              <SelectValue placeholder="Статус" />
            </SelectTrigger>
            <SelectContent>
              {statuses.map(s => (
                <SelectItem key={s} value={s}>{s}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select value={engineer} onValueChange={setEngineer}>
            <SelectTrigger>
              <SelectValue placeholder="Инженер" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="Все">Все</SelectItem>
              {engineers.map(e => (
                <SelectItem key={e} value={e}>{e}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Визиты ({rows.length})</CardTitle>
        </CardHeader>
        <CardContent className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Дата</TableHead>
                <TableHead>Инженер</TableHead>
                <TableHead>Объект</TableHead>
                <TableHead>Квартира</TableHead>
                <TableHead>Статус</TableHead>
                <TableHead>Интерес</TableHead>
                <TableHead>След. действие</TableHead>
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
                    Нет визитов
                  </TableCell>
                </TableRow>
              ) : (
                rows.map((v: any) => (
                  <TableRow key={v.id} className="hover:bg-muted/50">
                    <TableCell>{v.scheduled_at ? new Date(v.scheduled_at).toLocaleString('ru-RU') : "-"}</TableCell>
                    <TableCell>{v.engineer?.full_name || "-"}</TableCell>
                    <TableCell>{v.object?.address || "-"}</TableCell>
                    <TableCell>{v.unit?.unit_number ?? "-"}</TableCell>
                    <TableCell>
                      <Badge variant={v.status === "DONE" ? "default" : v.status === "PLANNED" ? "secondary" : "outline"}>
                        {statusMap[v.status] || v.status}
                      </Badge>
                    </TableCell>
                    <TableCell className="space-x-1">
                      {v.interests?.map((i: string) => (
                        <Badge key={i} variant="outline">{i}</Badge>
                      )) || "-"}
                    </TableCell>
                    <TableCell>{v.next_action_due_at ? new Date(v.next_action_due_at).toLocaleDateString('ru-RU') : "-"}</TableCell>
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


