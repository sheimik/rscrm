import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

const mockAudit = [
  { id: 1, entity: "Object", entityId: "1", action: "update", user: "Админ", time: "2025-10-28 16:20", diff: "status: Новый -> В работе" },
  { id: 2, entity: "Visit", entityId: "3", action: "create", user: "Иванов", time: "2025-10-28 10:00", diff: "created" },
];

export default function Audit() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>История изменений</CardTitle>
      </CardHeader>
      <CardContent className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Сущность</TableHead>
              <TableHead>ID</TableHead>
              <TableHead>Действие</TableHead>
              <TableHead>Сотрудник</TableHead>
              <TableHead>Время</TableHead>
              <TableHead>Diff</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {mockAudit.map(r => (
              <TableRow key={r.id} className="hover:bg-muted/50">
                <TableCell>{r.entity}</TableCell>
                <TableCell>{r.entityId}</TableCell>
                <TableCell>{r.action}</TableCell>
                <TableCell>{r.user}</TableCell>
                <TableCell>{r.time}</TableCell>
                <TableCell className="text-muted-foreground">{r.diff}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}


