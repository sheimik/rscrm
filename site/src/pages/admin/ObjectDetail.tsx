import { useParams, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ArrowLeft, Edit, Plus, FileDown } from "lucide-react";
import { mockBuildings, mockVisits, mockCustomers } from "@/lib/mockData";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { toast } from "sonner";

export default function ObjectDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const building = mockBuildings.find(b => b.id === id);

  if (!building) {
    return (
      <div className="text-center">
        <p className="text-muted-foreground">Объект не найден</p>
        <Button onClick={() => navigate("/_admin/objects")} className="mt-4">
          Вернуться к списку
        </Button>
      </div>
    );
  }

  const buildingVisits = mockVisits.filter(v => v.building === building.address);
  const buildingCustomers = mockCustomers.filter(c => c.building === building.address);

  const handleAction = (action: string) => {
    toast.info(`Демо-режим: ${action}`);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="space-y-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate("/_admin/objects")}
            className="mb-2"
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            Назад к списку
          </Button>
          <h1 className="text-3xl font-bold">{building.address}</h1>
          <div className="flex flex-wrap gap-2">
            <Badge variant="outline">{building.type}</Badge>
            <Badge>{building.status}</Badge>
            <Badge variant="secondary">{building.city} • {building.district}</Badge>
          </div>
        </div>
        <div className="flex gap-2">
          <Button onClick={() => handleAction("Редактировать")}>
            <Edit className="mr-2 h-4 w-4" />
            Редактировать
          </Button>
          <Button onClick={() => handleAction("Добавить визит")}>
            <Plus className="mr-2 h-4 w-4" />
            Добавить визит
          </Button>
          <Button variant="outline" onClick={() => handleAction("Экспорт по объекту")}>
            <FileDown className="mr-2 h-4 w-4" />
            Экспорт
          </Button>
        </div>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="general" className="w-full">
        <TabsList>
          <TabsTrigger value="general">Общее</TabsTrigger>
          <TabsTrigger value="apartments">Квартиры/Юниты</TabsTrigger>
          <TabsTrigger value="visits">Визиты</TabsTrigger>
          <TabsTrigger value="comments">Комментарии</TabsTrigger>
          <TabsTrigger value="files">Файлы</TabsTrigger>
          <TabsTrigger value="history">История</TabsTrigger>
        </TabsList>

        <TabsContent value="general" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Основная информация</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Адрес:</span>
                  <span className="font-medium">{building.address}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Город:</span>
                  <span className="font-medium">{building.city}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Район:</span>
                  <span className="font-medium">{building.district}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Тип:</span>
                  <span className="font-medium">{building.type}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Квартир/Юнитов:</span>
                  <span className="font-medium">{building.apartmentsCount || "—"}</span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Статистика</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Всего визитов:</span>
                  <span className="font-medium">{building.visitsCount}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Последний визит:</span>
                  <span className="font-medium">{building.lastVisit}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Ответственный:</span>
                  <span className="font-medium">{building.responsible}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Статус:</span>
                  <Badge>{building.status}</Badge>
                </div>
              </CardContent>
            </Card>
          </div>

          {building.gps && (
            <Card>
              <CardHeader>
                <CardTitle>GPS координаты</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Широта: {building.gps.lat}, Долгота: {building.gps.lng}
                </p>
                <div className="mt-4 flex h-64 items-center justify-center rounded-lg bg-muted">
                  <p className="text-muted-foreground">Карта (заглушка)</p>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="apartments">
          <Card>
            <CardHeader>
              <CardTitle>Список квартир/юнитов</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <ApartmentsTable buildingAddress={building.address} />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="visits">
          <Card>
            <CardHeader>
              <CardTitle>История визитов ({buildingVisits.length})</CardTitle>
            </CardHeader>
            <CardContent>
              {buildingVisits.length === 0 ? (
                <p className="text-center text-muted-foreground">Визиты отсутствуют</p>
              ) : (
                <div className="space-y-4">
                  {buildingVisits.map((visit) => (
                    <div key={visit.id} className="border-b border-border pb-4 last:border-0">
                      <div className="flex items-start justify-between">
                        <div className="space-y-1">
                          <p className="font-medium">{visit.date}</p>
                          <p className="text-sm text-muted-foreground">
                            {visit.engineer} • кв. {visit.apartment}
                          </p>
                          {visit.notes && (
                            <p className="text-sm">{visit.notes}</p>
                          )}
                          {visit.interest.length > 0 && (
                            <div className="flex flex-wrap gap-1">
                              {visit.interest.map((i) => (
                                <Badge key={i} variant="secondary">{i}</Badge>
                              ))}
                            </div>
                          )}
                        </div>
                        <Badge>{visit.status}</Badge>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="comments">
          <Card>
            <CardHeader>
              <CardTitle>Комментарии</CardTitle>
            </CardHeader>
            <CardContent>
              <CommentsPanel />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="files">
          <Card>
            <CardHeader>
              <CardTitle>Файлы</CardTitle>
            </CardHeader>
            <CardContent>
              <FilesList />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="history">
          <Card>
            <CardHeader>
              <CardTitle>История изменений</CardTitle>
            </CardHeader>
            <CardContent>
              <HistoryTable />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

function ApartmentsTable({ buildingAddress }: { buildingAddress: string }) {
  const [q, setQ] = useState("");
  const units = Array.from(new Set(
    mockCustomers
      .filter(c => c.building === buildingAddress)
      .map(c => c.apartment)
  ));
  const rows = units.filter(u => !q || u.toLowerCase().includes(q.toLowerCase()));
  return (
    <div className="space-y-3">
      <Input placeholder="Поиск по номеру" value={q} onChange={e => setQ(e.target.value)} />
      <div className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Номер</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {rows.map(u => (
              <TableRow key={u}>
                <TableCell>{u}</TableCell>
              </TableRow>
            ))}
            {rows.length === 0 && (
              <TableRow>
                <TableCell className="text-muted-foreground">Нет данных</TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}

function CommentsPanel() {
  const [items, setItems] = useState<{ id: number; author: string; text: string; time: string }[]>([
    { id: 1, author: "Админ", text: "Проверить подъезд А", time: "2025-10-28 12:00" },
  ]);
  const [text, setText] = useState("");
  const add = (e: React.FormEvent) => {
    e.preventDefault();
    if (!text.trim()) return;
    setItems(prev => [{ id: Date.now(), author: "Вы", text: text.trim(), time: new Date().toISOString().slice(0,16).replace('T',' ') }, ...prev]);
    setText("");
  };
  return (
    <div className="space-y-3">
      <form onSubmit={add} className="flex gap-2">
        <Input placeholder="Добавить комментарий" value={text} onChange={e => setText(e.target.value)} />
        <Button type="submit">Отправить</Button>
      </form>
      <div className="space-y-3">
        {items.map(i => (
          <div key={i.id} className="rounded-lg border p-3">
            <div className="flex items-center justify-between text-sm text-muted-foreground">
              <span>{i.author}</span>
              <span>{i.time}</span>
            </div>
            <p className="mt-1">{i.text}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

function FilesList() {
  const files = [
    { name: "photo_entrance.jpg", size: "1.2 MB" },
    { name: "contract_sample.pdf", size: "320 KB" },
  ];
  return (
    <div className="space-y-2">
      {files.map(f => (
        <div key={f.name} className="flex items-center justify-between rounded-lg border p-3">
          <span className="font-medium">{f.name}</span>
          <span className="text-sm text-muted-foreground">{f.size}</span>
        </div>
      ))}
    </div>
  );
}

function HistoryTable() {
  const rows = [
    { time: "2025-10-28 16:20", user: "Админ", action: "update", diff: "status: Новый -> В работе" },
    { time: "2025-10-27 09:10", user: "Иванов", action: "create", diff: "created" },
  ];
  return (
    <div className="overflow-x-auto">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Время</TableHead>
            <TableHead>Сотрудник</TableHead>
            <TableHead>Действие</TableHead>
            <TableHead>Изменения</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {rows.map((r, idx) => (
            <TableRow key={idx} className="hover:bg-muted/50">
              <TableCell>{r.time}</TableCell>
              <TableCell>{r.user}</TableCell>
              <TableCell>{r.action}</TableCell>
              <TableCell className="text-muted-foreground">{r.diff}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
