import { useMemo, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from "@/components/ui/dialog";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Plus } from "lucide-react";
import { toast } from "sonner";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { ApiUser, UserCreatePayload, UserUpdatePayload } from "@/lib/types";
import { useCurrentUser } from "@/hooks/use-current-user";

const ROLE_LABELS: Record<string, string> = {
  ENGINEER: "Инженер",
  SUPERVISOR: "Супервайзер",
  ADMIN: "Админ",
};

const ROLE_FILTER_OPTIONS = [
  { value: "ALL", label: "Все" },
  { value: "ENGINEER", label: ROLE_LABELS.ENGINEER },
  { value: "SUPERVISOR", label: ROLE_LABELS.SUPERVISOR },
  { value: "ADMIN", label: ROLE_LABELS.ADMIN },
];

const userSchema = z.object({
  fullName: z.string().min(2, "ФИО должно содержать минимум 2 символа"),
  email: z.string().email("Укажите корректный email"),
  password: z.string().min(8, "Минимум 8 символов"),
  role: z.enum(["ENGINEER", "SUPERVISOR", "ADMIN"], {
    required_error: "Выберите роль",
  }),
  phone: z.string().optional(),
  cityId: z.string().optional(),
  districtId: z.string().optional(),
  isActive: z.boolean().default(true),
});

type UserFormData = z.infer<typeof userSchema>;

export default function Users() {
  const [q, setQ] = useState("");
  const [roleFilter, setRoleFilter] = useState<string>("ALL");
  const [dialogOpen, setDialogOpen] = useState(false);
  const [updatingId, setUpdatingId] = useState<string | null>(null);
  const queryClient = useQueryClient();
  const { data: currentUser } = useCurrentUser();
  const defaultValues: UserFormData = {
    fullName: "",
    email: "",
    password: "",
    role: "ENGINEER",
    phone: "",
    cityId: "",
    districtId: "",
    isActive: true,
  };

  const form = useForm<UserFormData>({
    resolver: zodResolver(userSchema),
    defaultValues,
  });
  const selectedCityId = form.watch("cityId");
  const { data: usersData, isLoading, isError, error } = useQuery<ApiUser[]>({
    queryKey: ['users'],
    queryFn: () => api.getUsers(),
  });
  const users = usersData ?? [];
  const { data: cities = [] } = useQuery({
    queryKey: ['cities'],
    queryFn: () => api.getCities(),
  });
  const { data: districts = [] } = useQuery({
    queryKey: ['districts', selectedCityId, 'users'],
    queryFn: () => api.getDistricts(selectedCityId as string),
    enabled: Boolean(selectedCityId),
  });
  const createMutation = useMutation({
    mutationFn: (payload: UserCreatePayload) => api.createUser(payload),
    onSuccess: () => {
      toast.success("Сотрудник успешно добавлен");
      queryClient.invalidateQueries({ queryKey: ['users'] });
      setDialogOpen(false);
      form.reset({ ...defaultValues });
    },
    onError: (error: any) => {
      toast.error(error?.message || "Ошибка при добавлении сотрудника");
    },
  });
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: UserUpdatePayload }) =>
      api.updateUser(id, data),
    onMutate: ({ id }) => {
      setUpdatingId(id);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      toast.success("Статус сотрудника обновлён");
    },
    onError: (error: any) => {
      toast.error(error?.message || "Не удалось обновить пользователя");
    },
    onSettled: () => {
      setUpdatingId(null);
    },
  });
  const handleDialogChange = (open: boolean) => {
    setDialogOpen(open);
    if (!open) {
      form.reset({ ...defaultValues });
    }
  };

  const onSubmit = (data: UserFormData) => {
    const payload: UserCreatePayload = {
      email: data.email.trim(),
      password: data.password,
      full_name: data.fullName.trim(),
      role: data.role,
      is_active: data.isActive,
      phone: data.phone?.trim() ? data.phone.trim() : undefined,
      city_id: data.cityId ? data.cityId : undefined,
      district_id: data.districtId ? data.districtId : undefined,
    };

    createMutation.mutate(payload);
  };

  const handleToggleActive = (user: ApiUser, nextValue: boolean) => {
    if (currentUser?.role !== "ADMIN") {
      toast.error("Недостаточно прав для изменения статуса");
      return;
    }

    updateMutation.mutate({ id: user.id, data: { is_active: nextValue } });
  };

  const canManageUsers = currentUser?.role === "ADMIN";
  

  const rows = useMemo(() => {
    const ql = q.trim().toLowerCase();
    return users.filter((user) => {
      const snapshot = [
        user.full_name,
        user.email,
        user.city?.name ?? "",
        user.district?.name ?? "",
        user.phone ?? "",
      ];
      const byQ = !ql || snapshot.some((value) => value.toLowerCase().includes(ql));
      const byRole = roleFilter === "ALL" || user.role === roleFilter;
      return byQ && byRole;
    });
  }, [q, roleFilter, users]);


  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Фильтры</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-3 sm:grid-cols-2">
          <Input placeholder="Поиск по имени/email/городу" value={q} onChange={e => setQ(e.target.value)} />
          <Select value={roleFilter} onValueChange={setRoleFilter}>
            <SelectTrigger>
              <SelectValue placeholder="Роль" />
            </SelectTrigger>
            <SelectContent>
              {ROLE_FILTER_OPTIONS.map(option => (
                <SelectItem key={option.value} value={option.value}>
                  {option.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle>Сотрудники ({rows.length})</CardTitle>
          <Dialog open={dialogOpen} onOpenChange={handleDialogChange}>
            <DialogTrigger asChild>
              <Button disabled={!canManageUsers}>
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
                  <div className="grid gap-4 sm:grid-cols-2">
                    <FormField
                      control={form.control}
                      name="fullName"
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
                      name="email"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Email</FormLabel>
                          <FormControl>
                            <Input type="email" placeholder="user@example.com" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>

                  <div className="grid gap-4 sm:grid-cols-2">
                    <FormField
                      control={form.control}
                      name="password"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Пароль</FormLabel>
                          <FormControl>
                            <Input type="password" placeholder="Минимум 8 символов" {...field} />
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
                          <Select value={field.value} onValueChange={field.onChange}>
                            <FormControl>
                              <SelectTrigger>
                                <SelectValue placeholder="Выберите роль" />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              {Object.entries(ROLE_LABELS).map(([value, label]) => (
                                <SelectItem key={value} value={value}>
                                  {label}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>

                  <FormField
                    control={form.control}
                    name="phone"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Телефон (необязательно)</FormLabel>
                        <FormControl>
                          <Input type="tel" placeholder="+7 (999) 123-45-67" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <div className="grid gap-4 sm:grid-cols-2">
                    <FormField
                      control={form.control}
                      name="cityId"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Город</FormLabel>
                          <Select
                            value={field.value}
                            onValueChange={(value) => {
                              field.onChange(value);
                              form.setValue("districtId", "");
                            }}
                            disabled={!cities.length}
                          >
                            <FormControl>
                              <SelectTrigger>
                                <SelectValue placeholder="Выберите город" />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              {cities.map((city: any) => (
                                <SelectItem key={city.id} value={city.id}>
                                  {city.name}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={form.control}
                      name="districtId"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Район (необязательно)</FormLabel>
                          <Select
                            value={field.value ?? ""}
                            onValueChange={field.onChange}
                            disabled={!selectedCityId || !districts.length}
                          >
                            <FormControl>
                              <SelectTrigger>
                                <SelectValue placeholder="Выберите район" />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              {districts.map((district: any) => (
                                <SelectItem key={district.id} value={district.id}>
                                  {district.name}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>

                  <FormField
                    control={form.control}
                    name="isActive"
                    render={({ field }) => (
                      <FormItem className="flex flex-row items-center justify-between rounded-lg border p-3">
                        <div className="space-y-0.5">
                          <FormLabel>Активен</FormLabel>
                        </div>
                        <FormControl>
                          <Switch checked={field.value} onCheckedChange={field.onChange} />
                        </FormControl>
                      </FormItem>
                    )}
                  />

                  <DialogFooter>
                    <Button type="button" variant="outline" onClick={() => handleDialogChange(false)}>
                      Отмена
                    </Button>
                    <Button type="submit" disabled={!canManageUsers || createMutation.isPending}>
                      {createMutation.isPending ? "Добавление..." : "Добавить"}
                    </Button>
                  </DialogFooter>
                </form>
              </Form>
            </DialogContent>
          </Dialog>
        </CardHeader>
        {!canManageUsers && (
          <p className="px-6 text-sm text-muted-foreground">
            У вас нет прав на редактирование. Обратитесь к администратору.
          </p>
        )}
        <CardContent className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>ФИО</TableHead>
                <TableHead>Email</TableHead>
                <TableHead>Роль</TableHead>
                <TableHead>Город</TableHead>
                <TableHead>Район</TableHead>
                <TableHead>Телефон</TableHead>
                <TableHead>Последний вход</TableHead>
                <TableHead>Активен</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                <TableRow>
                  <TableCell colSpan={8} className="text-center text-muted-foreground">
                    Загрузка...
                  </TableCell>
                </TableRow>
              ) : isError ? (
                <TableRow>
                  <TableCell colSpan={8} className="space-y-1 text-center text-muted-foreground">
                    <div>Не удалось загрузить сотрудников.</div>
                    <div>{error instanceof Error ? error.message : "Попробуйте позже."}</div>
                  </TableCell>
                </TableRow>
              ) : rows.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={8} className="text-center text-muted-foreground">
                    Нет сотрудников
                  </TableCell>
                </TableRow>
              ) : (
                rows.map((user) => (
                  <TableRow key={user.id} className="hover:bg-muted/50">
                    <TableCell className="font-medium">{user.full_name}</TableCell>
                    <TableCell>{user.email}</TableCell>
                    <TableCell>
                      <Badge variant="outline">{ROLE_LABELS[user.role] ?? user.role}</Badge>
                    </TableCell>
                    <TableCell>{user.city?.name || "-"}</TableCell>
                    <TableCell>{user.district?.name || "-"}</TableCell>
                    <TableCell>{user.phone || "-"}</TableCell>
                    <TableCell>
                      {user.last_login_at
                        ? new Date(user.last_login_at).toLocaleString('ru-RU')
                        : "-"}
                    </TableCell>
                    <TableCell>
                      <Switch
                        checked={user.is_active}
                        disabled={!canManageUsers || updatingId === user.id}
                        onCheckedChange={(checked) => handleToggleActive(user, checked)}
                        aria-label={"Переключить статус пользователя"}
                      />
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
