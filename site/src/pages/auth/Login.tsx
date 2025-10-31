import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { api } from "@/lib/api";

export default function Login() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    const form = e.currentTarget as HTMLFormElement;
    const formData = new FormData(form);
    const email = formData.get("email") as string;
    const password = formData.get("password") as string;
    
    try {
      await api.login(email, password);
      toast.success("Успешный вход");
      
      // Получаем информацию о пользователе
      const user = await api.getCurrentUser();
      
      // Перенаправляем в зависимости от роли
      if (user.role === "ADMIN" || user.role === "SUPERVISOR") {
        navigate("/_admin/dashboard");
      } else {
        navigate("/cabinet/route");
      }
    } catch (error: any) {
      toast.error(error.message || "Ошибка входа. Проверьте email и пароль.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-background p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-2 text-center">
          <CardTitle className="text-3xl font-bold">CRM Система</CardTitle>
          <CardDescription>Технологии в каждом решении</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleLogin} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email">Email или логин</Label>
              <Input
                id="email"
                name="email"
                type="text"
                placeholder="admin@example.com"
                required
                disabled={loading}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Пароль</Label>
              <Input
                id="password"
                name="password"
                type="password"
                placeholder="••••••••"
                required
                disabled={loading}
              />
            </div>
            <Button type="submit" className="w-full" size="lg" disabled={loading}>
              {loading ? "Вход..." : "Войти"}
            </Button>
            <button
              type="button"
              className="w-full text-center text-sm text-muted-foreground hover:text-foreground"
              onClick={() => toast.info("Демо-режим: восстановление пароля не реализовано")}
            >
              Забыли пароль?
            </button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
