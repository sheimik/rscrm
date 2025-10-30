import { useMemo, useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from "@/components/ui/dialog";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { mockUsers, User, cities, districts } from "@/lib/mockData";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Plus } from "lucide-react";
import { toast } from "sonner";

const userSchema = z.object({
  name: z.string().min(2, "ФИО должно содержать минимум 2 символа"),
  role: z.enum(["Инженер", "Супервайзер", "Админ"], {
    required_error: "Выберите роль",
  }),
  city: z.string().min(2, "Укажите город"),
  zone: z.string().optional(),
  isActive: z.boolean().default(true),
});

type UserFormData = z.infer<typeof userSchema>;

export default function Users() {
  const [q, setQ] = useState("");
  const [role, setRole] = useState<string>("Все");
  const [dialogOpen, setDialogOpen] = useState(false);
  const [users, setUsers] = useState<User[]>(mockUsers);

  const roles = ["Все", "Инженер", "Супервайзер", "Админ"];

  const form = useForm<UserFormData>({
    resolver: zodResolver(userSchema),
    defaultValues: {
      name: "",
      role: "Инженер",
      city: "",
      zone: undefined,
      isActive: true,
    },
  });

  const rows = useMemo(() => {
    const ql = q.trim().toLowerCase();
    return users.filter(u => {
      const byQ = !ql || [u.name, u.city, u.zone ?? ""].some(x => x.toLowerCase().includes(ql));
      const byRole = role === "Все" || u.role === role;
      return byQ && byRole;
    });
  }, [q, role, users]);

  useEffect(() => {
    if (!dialogOpen) {
      form.reset({
        name: "",
        role: "Инженер",
        city: "",
        zone: undefined,
        isActive: true,
      });
    }
  }, [dialogOpen, form]);

  const onSubmit = (data: UserFormData) => {
    try {
      const newUser: User = {
        id: String(users.length + 1),
        name: data.name,
        role: data.role,
        city: data.city,
        zone: data.zone || undefined,
        lastLogin: "-",
        isActive: data.isActive,
      };
      setUsers([...users, newUser]);
      toast.success("Сотрудник успешно добавлен");
      setDialogOpen(false);
      form.reset({
        name: "",
        role: "Инженер",
        city: "",
        zone: undefined,
        isActive: true,
      });
    } catch (error) {
      console.error("Ошибка при добавлении сотрудника:", error);
      toast.error("Ошибка при добавлении сотрудника");
    }
  };

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Фильтры</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-3 sm:grid-cols-2">
          <Input placeholder="Поиск по имени/городу/зоне" value={q} onChange={e => setQ(e.target.value)} />
          <Select value={role} onValueChange={setRole}>
            <SelectTrigger>
              <SelectValue placeholder="Роль" />
            </SelectTrigger>
            <SelectContent>
              {roles.map(r => (
                <SelectItem key={r} value={r}>{r}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle>Сотрудники ({rows.length})</CardTitle>
          <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                Добавить сотрудника
              </Button>
            </DialogTrigger>
            <DialogContent className="max-h-[90vh] overflow-y-auto sm:max-w-[550px]">
              <DialogHeader>
                <DialogTitle>Добавление нового сотрудника</DialogTitle>
              </DialogHeader>
              <Form {...form}>
                <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                  <FormField
                    control={form.control}
                    name="name"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>ФИО</FormLabel>
                        <FormControl>
                          <Input placeholder="Иванов Иван Иванович" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="role"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Роль</FormLabel>
                        <Select onValueChange={field.onChange} value={field.value}>
                          <FormControl>
                            <SelectTrigger>
                              <SelectValue placeholder="Выберите роль" />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent>
                            <SelectItem value="Инженер">Инженер</SelectItem>
                            <SelectItem value="Супервайзер">Супервайзер</SelectItem>
                            <SelectItem value="Админ">Админ</SelectItem>
                          </SelectContent>
                        </Select>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="city"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Город</FormLabel>
                        <Select onValueChange={field.onChange} value={field.value}>
                          <FormControl>
                            <SelectTrigger>
                              <SelectValue placeholder="Выберите город" />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent>
                            {cities.map(city => (
                              <SelectItem key={city} value={city}>{city}</SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="zone"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Зона (необязательно)</FormLabel>
                        <Select 
                          onValueChange={(value) => {
                            field.onChange(value);
                          }} 
                          value={field.value || undefined}
                        >
                          <FormControl>
                            <SelectTrigger>
                              <SelectValue placeholder="Выберите зону (необязательно)" />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent>
                            {districts.map(zone => (
                              <SelectItem key={zone} value={zone}>{zone}</SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control} 
                    name="isActive"
                    render={({ field }) => (
                      <FormItem className="flex flex-row items-center justify-between rounded-lg border p-3">
                        <div className="space-y-0.5">
                          <FormLabel>Активен</FormLabel>
                        </div>
                        <FormControl>
                          <Switch
                            checked={field.value}
                            onCheckedChange={field.onChange}
                          />
                        </FormControl>
                      </FormItem>
                    )}
                  />

                  <DialogFooter>
                    <Button type="button" variant="outline" onClick={() => {
                      setDialogOpen(false);
                      form.reset();
                    }}>
                      Отмена
                    </Button>
                    <Button type="submit">Добавить</Button>
                  </DialogFooter>
                </form>
              </Form>
            </DialogContent>
          </Dialog>
        </CardHeader>
        <CardContent className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>ФИО</TableHead>
                <TableHead>Роль</TableHead>
                <TableHead>Город</TableHead>
                <TableHead>Зона</TableHead>
                <TableHead>Последний вход</TableHead>
                <TableHead>Активен</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {rows.map(u => (
                <TableRow key={u.id} className="hover:bg-muted/50">
                  <TableCell>{u.name}</TableCell>
                  <TableCell>
                    <Badge variant="outline">{u.role}</Badge>
                  </TableCell>
                  <TableCell>{u.city}</TableCell>
                  <TableCell>{u.zone ?? "-"}</TableCell>
                  <TableCell>{u.lastLogin}</TableCell>
                  <TableCell>
                    <Switch checked={u.isActive} disabled aria-readonly />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}


