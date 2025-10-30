import { useMemo, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { mockVisits } from "@/lib/mockData";

export default function Visits() {
  const [q, setQ] = useState("");
  const [status, setStatus] = useState<string>("Все");
  const [engineer, setEngineer] = useState<string>("Все");

  const engineers = useMemo(() => Array.from(new Set(mockVisits.map(v => v.engineer))), []);
  const statuses = ["Все", "Завершён", "В процессе", "Отменён", "Запланирован"];

  const rows = useMemo(() => {
    const ql = q.trim().toLowerCase();
    return mockVisits.filter(v => {
      const byQ = !ql || [v.building, v.apartment ?? "", v.engineer].some(x => x.toLowerCase().includes(ql));
      const byStatus = status === "Все" || v.status === (status as any);
      const byEngineer = engineer === "Все" || v.engineer === engineer;
      return byQ && byStatus && byEngineer;
    });
  }, [q, status, engineer]);

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
              {rows.map(v => (
                <TableRow key={v.id} className="hover:bg-muted/50">
                  <TableCell>{v.date}</TableCell>
                  <TableCell>{v.engineer}</TableCell>
                  <TableCell>{v.building}</TableCell>
                  <TableCell>{v.apartment ?? "-"}</TableCell>
                  <TableCell>
                    <Badge variant={v.status === "Завершён" ? "default" : v.status === "Запланирован" ? "secondary" : "outline"}>
                      {v.status}
                    </Badge>
                  </TableCell>
                  <TableCell className="space-x-1">
                    {v.interest.map(i => (
                      <Badge key={i} variant="outline">{i}</Badge>
                    ))}
                  </TableCell>
                  <TableCell>{v.nextAction ?? "-"}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}


