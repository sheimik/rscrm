import { useMemo, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { mockCustomers, services } from "@/lib/mockData";

export default function Customers() {
  const [q, setQ] = useState("");
  const [service, setService] = useState<string>("Все");

  const rows = useMemo(() => {
    const ql = q.trim().toLowerCase();
    return mockCustomers.filter(c => {
      const byQ = !ql || [c.name, c.phone, c.building, c.apartment].some(x => x.toLowerCase().includes(ql));
      const byService = service === "Все" || c.interests.includes(service);
      return byQ && byService;
    });
  }, [q, service]);

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
              {rows.map(c => (
                <TableRow key={c.id} className="hover:bg-muted/50">
                  <TableCell>{c.name}</TableCell>
                  <TableCell>{c.phone}</TableCell>
                  <TableCell>{c.building}, кв. {c.apartment}</TableCell>
                  <TableCell>{c.currentProvider ?? "-"}</TableCell>
                  <TableCell>{c.rating ?? "-"}</TableCell>
                  <TableCell className="space-x-1">
                    {c.interests.map(i => (
                      <Badge key={i} variant="outline">{i}</Badge>
                    ))}
                  </TableCell>
                  <TableCell>{c.updatedAt}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}


