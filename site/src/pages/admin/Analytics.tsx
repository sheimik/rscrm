import { useMemo } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart";
import { Bar, BarChart, CartesianGrid, Line, LineChart, XAxis, YAxis } from "recharts";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { OBJECT_STATUS_LABELS } from "@/lib/referenceData";

export default function Analytics() {
  const { data: objectsData } = useQuery({
    queryKey: ['objects', 'analytics'],
    queryFn: () => api.getObjects({ limit: 1000 }),
  });
  const { data: visitsData } = useQuery({
    queryKey: ['visits', 'analytics'],
    queryFn: () => api.getVisits({ limit: 1000 }),
  });

  const objects = objectsData?.items ?? [];
  const visits = visitsData?.items ?? [];

  const byStatus = useMemo(() => {
    const map = new Map<string, number>();
    objects.forEach((object: any) => {
      const status = object.status ?? "UNKNOWN";
      map.set(status, (map.get(status) ?? 0) + 1);
    });
    return Array.from(map.entries()).map(([status, value]) => ({
      name: OBJECT_STATUS_LABELS[status] ?? status,
      value,
    }));
  }, [objects]);

  const visitsPerDay = useMemo(() => {
    const map = new Map<string, number>();
    visits.forEach((visit: any) => {
      const date = visit.scheduled_at || visit.created_at;
      if (!date) {
        return;
      }
      const day = new Date(date).toISOString().slice(0, 10);
      map.set(day, (map.get(day) ?? 0) + 1);
    });
    return Array.from(map.entries())
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([day, count]) => ({ day, count }));
  }, [visits]);

  return (
    <div className="grid gap-4 md:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle>Объекты по статусам</CardTitle>
        </CardHeader>
        <CardContent>
          {byStatus.length === 0 ? (
            <p className="text-center text-muted-foreground">Нет данных для отображения</p>
          ) : (
            <ChartContainer config={{ value: { label: "Кол-во" } }} className="h-64">
              <BarChart data={byStatus}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis allowDecimals={false} />
                <Bar dataKey="value" fill="hsl(var(--primary))" />
                <ChartTooltip content={<ChartTooltipContent />} />
              </BarChart>
            </ChartContainer>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Динамика визитов</CardTitle>
        </CardHeader>
        <CardContent>
          {visitsPerDay.length === 0 ? (
            <p className="text-center text-muted-foreground">Нет данных для отображения</p>
          ) : (
            <ChartContainer config={{ count: { label: "Визиты" } }} className="h-64">
              <LineChart data={visitsPerDay}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="day" />
                <YAxis allowDecimals={false} />
                <Line type="monotone" dataKey="count" stroke="hsl(var(--primary))" strokeWidth={2} dot={false} />
                <ChartTooltip content={<ChartTooltipContent />} />
              </LineChart>
            </ChartContainer>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
