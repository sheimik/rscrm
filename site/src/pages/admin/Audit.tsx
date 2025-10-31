import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";
import { format } from "date-fns";

interface AuditLog {
  id: string;
  actor_id: string | null;
  actor_name: string | null;
  action: string;
  entity_type: string | null;
  entity_id: string | null;
  before_json: Record<string, any> | null;
  after_json: Record<string, any> | null;
  occurred_at: string;
}

interface AuditResponse {
  items: AuditLog[];
  page: number;
  limit: number;
  total: number;
  pages: number;
}

function formatDiff(before: Record<string, any> | null, after: Record<string, any> | null, action: string): string {
  if (action === "create") {
    if (!after) return "created";
    return "created";
  }
  
  if (action === "delete") {
    if (!before) return "deleted";
    return "deleted";
  }
  
  if (action === "update") {
    if (!before || !after) return "updated";
    
    const changes: string[] = [];
    
    // Сравниваем основные поля
    const fieldsToCheck = ["status", "type", "address", "responsible_user_id"];
    
    for (const field of fieldsToCheck) {
      if (before[field] !== undefined && after[field] !== undefined && before[field] !== after[field]) {
        const oldVal = before[field];
        const newVal = after[field];
        
        // Для статусов показываем более понятно
        if (field === "status") {
          changes.push(`${field}: ${oldVal} -> ${newVal}`);
        } else if (field === "responsible_user_id") {
          changes.push(`${field}: ${oldVal || "не назначен"} -> ${newVal || "не назначен"}`);
        } else {
          changes.push(`${field}: ${oldVal} -> ${newVal}`);
        }
      }
    }
    
    if (changes.length > 0) {
      return changes.join(", ");
    }
    
    return "updated";
  }
  
  return action;
}

export default function Audit() {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [pages, setPages] = useState(0);

  const loadAuditLogs = async () => {
    try {
      setLoading(true);
      const response = await api.getAuditLogs({
        page,
        limit: 50,
      }) as AuditResponse;
      
      setLogs(response.items);
      setTotal(response.total);
      setPages(response.pages);
    } catch (error) {
      console.error("Failed to load audit logs:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAuditLogs();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page]);

  const formatDate = (dateString: string) => {
    try {
      return format(new Date(dateString), "yyyy-MM-dd HH:mm");
    } catch {
      return dateString;
    }
  };

  const getEntityName = (entityType: string | null) => {
    if (!entityType) return "—";
    const map: Record<string, string> = {
      object: "Object",
      visit: "Visit",
      customer: "Customer",
      user: "User",
    };
    return map[entityType] || entityType;
  };

  const getActionName = (action: string) => {
    const map: Record<string, string> = {
      create: "create",
      update: "update",
      delete: "delete",
      export: "export",
      login: "login",
      logout: "logout",
    };
    return map[action] || action;
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>История изменений</CardTitle>
      </CardHeader>
      <CardContent className="overflow-x-auto">
        {loading ? (
          <div className="text-center py-8">Загрузка...</div>
        ) : logs.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">Нет записей</div>
        ) : (
          <>
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
                {logs.map((log) => (
                  <TableRow key={log.id} className="hover:bg-muted/50">
                    <TableCell>{getEntityName(log.entity_type)}</TableCell>
                    <TableCell>{log.entity_id ? log.entity_id.substring(0, 8) + "..." : "—"}</TableCell>
                    <TableCell>{getActionName(log.action)}</TableCell>
                    <TableCell>{log.actor_name || "Система"}</TableCell>
                    <TableCell>{formatDate(log.occurred_at)}</TableCell>
                    <TableCell className="text-muted-foreground">
                      {formatDiff(log.before_json, log.after_json, log.action)}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
            <div className="flex items-center justify-between mt-4">
              <div className="text-sm text-muted-foreground">
                Страница {page} из {pages} (всего: {total})
              </div>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                  disabled={page <= 1}
                >
                  Назад
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage(p => Math.min(pages, p + 1))}
                  disabled={page >= pages}
                >
                  Вперед
                </Button>
              </div>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}


