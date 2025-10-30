/*
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";

export default function Settings() {
  const save = () => toast.success("Сохранено (демо)");

  return (
    <div className="grid gap-4 md:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle>Telegram</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="space-y-1">
            <Label>Bot token</Label>
            <Input placeholder="123:ABC..." />
          </div>
          <div className="space-y-1">
            <Label>Webhook URL</Label>
            <Input placeholder="https://example.com/api/telegram/webhook" />
          </div>
          <Button onClick={save}>Сохранить</Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>E-mail SMTP</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="space-y-1">
            <Label>Host</Label>
            <Input placeholder="smtp.example.com" />
          </div>
          <div className="grid gap-3 grid-cols-2">
            <div className="space-y-1">
              <Label>Port</Label>
              <Input placeholder="465" />
            </div>
            <div className="space-y-1">
              <Label>SSL</Label>
              <Input placeholder="true/false" />
            </div>
          </div>
          <div className="grid gap-3 grid-cols-2">
            <div className="space-y-1">
              <Label>Login</Label>
              <Input placeholder="noreply@example.com" />
            </div>
            <div className="space-y-1">
              <Label>Password</Label>
              <Input type="password" placeholder="••••••" />
            </div>
          </div>
          <Button onClick={save}>Сохранить</Button>
        </CardContent>
      </Card>
    </div>
  );
}
*/


