import { useMemo, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";
import {
  INTEREST_LABELS,
  translateOrFallback,
} from "@/lib/referenceData";
import { ApiCustomer, PageResponse } from "@/lib/types";

export default function Customers() {
  const [search, setSearch] = useState("");

  const {
    data: customersData,
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery<PageResponse<ApiCustomer>, Error>({
    queryKey: ["cabinet-customers"],
    queryFn: () => api.getCustomers({ limit: 200 }) as Promise<PageResponse<ApiCustomer>>,
    staleTime: 60_000,
  });

  const customers = customersData?.items ?? [];

  const rows = useMemo(() => {
    const query = search.trim().toLowerCase();
    if (!query) {
      return customers;
    }
    return customers.filter((customer) => {
      const fullName = customer.full_name?.toLowerCase() ?? "";
      const phone = customer.phone?.toLowerCase() ?? "";
      const address = customer.object?.address?.toLowerCase() ?? "";
      return (
        fullName.includes(query) ||
        phone.includes(query) ||
        address.includes(query)
      );
    });
  }, [customers, search]);

  return (
    <div className="space-y-4 p-4">
      <Card>
        <CardHeader>
          <CardTitle>Клиенты</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <Input
              placeholder="Поиск по имени, телефону или адресу"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="sm:max-w-xs"
            />
            <Button variant="outline" onClick={() => refetch()} disabled={isLoading}>
              Обновить
            </Button>
          </div>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Имя</TableHead>
                  <TableHead>Телефон</TableHead>
                  <TableHead>Адрес</TableHead>
                  <TableHead>Интересы</TableHead>
                  <TableHead>Провайдер</TableHead>
                  <TableHead>Обновлён</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {isLoading ? (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center text-muted-foreground">
                      Загружаем клиентов...
                    </TableCell>
                  </TableRow>
                ) : isError ? (
                  <TableRow>
                    <TableCell colSpan={6} className="space-y-2 text-center text-muted-foreground">
                      <div>
                        Не удалось загрузить клиентов{error?.message ? `: ${error.message}` : ""}
                      </div>
                      <Button variant="outline" size="sm" onClick={() => refetch()}>
                        Повторить запрос
                      </Button>
                    </TableCell>
                  </TableRow>
                ) : rows.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center text-muted-foreground">
                      Клиентов не найдено
                    </TableCell>
                  </TableRow>
                ) : (
                  rows.map((customer) => (
                    <TableRow key={customer.id} className="hover:bg-muted/50">
                      <TableCell>{customer.full_name || "—"}</TableCell>
                      <TableCell>{customer.phone || "—"}</TableCell>
                      <TableCell>{customer.object?.address || "—"}</TableCell>
                      <TableCell className="space-x-1">
                        {customer.interests && customer.interests.length > 0 ? (
                          customer.interests.map((interest) => (
                            <Badge key={interest} variant="outline">
                              {translateOrFallback(INTEREST_LABELS, interest)}
                            </Badge>
                          ))
                        ) : (
                          "—"
                        )}
                      </TableCell>
                      <TableCell>{customer.current_provider || "—"}</TableCell>
                      <TableCell>
                        {customer.updated_at
                          ? new Date(customer.updated_at).toLocaleDateString("ru-RU")
                          : "—"}
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
