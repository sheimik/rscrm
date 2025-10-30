import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";

export default function Notifications() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Уведомления</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between rounded-lg border p-3">
          <div>
            <Label className="text-base">Telegram напоминания</Label>
            <p className="text-sm text-muted-foreground">Фоллоу-апы, дедлайны, задачи</p>
          </div>
          <Switch checked readOnly aria-readonly />
        </div>
        <div className="flex items-center justify-between rounded-lg border p-3">
          <div>
            <Label className="text-base">E-mail уведомления</Label>
            <p className="text-sm text-muted-foreground">Отчёты и алерты</p>
          </div>
          <Switch />
        </div>
      </CardContent>
    </Card>
  );
}


