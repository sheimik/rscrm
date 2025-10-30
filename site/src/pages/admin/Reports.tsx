import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { cities } from "@/lib/mockData";
import { toast } from "sonner";

export default function Reports() {
  const handleExport = (scope: string) => () => toast.info(`Демо-экспорт: ${scope} (XLSX)`);

  return (
    <div className="grid gap-4 md:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle>Экспорт по объекту/дому</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <Input placeholder="Адрес объекта" />
          <Button onClick={handleExport("Объект")}>Скачать XLSX</Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Экспорт по городу</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <Select>
            <SelectTrigger>
              <SelectValue placeholder="Выбери город" />
            </SelectTrigger>
            <SelectContent>
              {cities.map((c) => (
                <SelectItem key={c} value={c}>{c}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Button onClick={handleExport("Город")}>Скачать XLSX</Button>
        </CardContent>
      </Card>

      <Card className="md:col-span-2">
        <CardHeader>
          <CardTitle>Кастомная выборка</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-3 md:grid-cols-4">
          <Input placeholder="Фильтр: интерес/статус/дата..." className="md:col-span-3" />
          <Button onClick={handleExport("Кастомная выборка")}>Скачать XLSX</Button>
        </CardContent>
      </Card>
    </div>
  );
}


