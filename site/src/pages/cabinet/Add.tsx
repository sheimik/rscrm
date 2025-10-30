import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { cities, services } from "@/lib/mockData";
import { MapPin } from "lucide-react";
import { toast } from "sonner";

export default function Add() {
  const [coords, setCoords] = useState<{ lat: number; lng: number } | null>(null);

  const detectGeo = () => {
    if (!navigator.geolocation) {
      toast.error("Геолокация недоступна");
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const c = { lat: +pos.coords.latitude.toFixed(5), lng: +pos.coords.longitude.toFixed(5) };
        setCoords(c);
        toast.success("Координаты сохранены");
      },
      () => toast.error("Не удалось определить местоположение"),
      { enableHighAccuracy: true, timeout: 5000 }
    );
  };

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    toast.success("Сохранено (офлайн очередь — демо)");
  };

  return (
    <form onSubmit={submit} className="space-y-4 p-4">
      <Card>
        <CardHeader>
          <CardTitle>Объект</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="space-y-1">
            <Label>Город</Label>
            <Select>
              <SelectTrigger>
                <SelectValue placeholder="Выбери город" />
              </SelectTrigger>
              <SelectContent>
                {cities.map(c => (<SelectItem key={c} value={c}>{c}</SelectItem>))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-1">
            <Label>Адрес</Label>
            <Input placeholder="ул. Пример, д. 1" required />
          </div>
          <Button type="button" variant="secondary" onClick={detectGeo} className="gap-2">
            <MapPin className="h-4 w-4" /> Определить моё местоположение {coords ? `(${coords.lat}, ${coords.lng})` : ""}
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Визит</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <Label>Квартира/Номер</Label>
              <Input placeholder="45" />
            </div>
            <div className="space-y-1">
              <Label>Телефон</Label>
              <Input placeholder="+7 (___) ___-__-__" />
            </div>
          </div>
          <div className="space-y-1">
            <Label>Портрет клиента</Label>
            <Input placeholder="Например: мужчина ~40 лет, работает из дома" />
          </div>
          <div className="space-y-2">
            <Label>Чем пользуется</Label>
            <div className="grid grid-cols-2 gap-2">
              {services.map(s => (
                <label key={s} className="flex items-center gap-2">
                  <Checkbox /> <span>{s}</span>
                </label>
              ))}
            </div>
          </div>
          <div className="space-y-1">
            <Label>Интерес к услугам (ввод через запятую)</Label>
            <Input placeholder="Интернет, Видеонаблюдение" />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <Label>Удобное время для связи</Label>
              <Input placeholder="18:00-20:00" />
            </div>
            <div className="space-y-1">
              <Label>Желаемая цена</Label>
              <Input placeholder="800 руб/мес" />
            </div>
          </div>
          <div className="space-y-1">
            <Label>Примечание</Label>
            <Input placeholder="Короткое примечание" />
          </div>
          <Button type="submit" className="w-full">Сохранить</Button>
        </CardContent>
      </Card>
    </form>
  );
}


