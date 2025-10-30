import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart";
import { Bar, BarChart, CartesianGrid, Line, LineChart, XAxis, YAxis } from "recharts";
import { mockBuildings, mockVisits } from "@/lib/mockData";

export default function Analytics() {
  const byStatus = Object.entries(
    mockBuildings.reduce<Record<string, number>>((acc, b) => {
      acc[b.status] = (acc[b.status] || 0) + 1;
      return acc;
    }, {})
  ).map(([name, value]) => ({ name, value }));

  const visitsPerDay = Object.entries(
    mockVisits.reduce<Record<string, number>>((acc, v) => {
      const day = v.date.split(" ")[0];
      acc[day] = (acc[day] || 0) + 1;
      return acc;
    }, {})
  )
    .sort(([a], [b]) => (a > b ? 1 : -1))
    .map(([day, count]) => ({ day, count }));

  return (
    <div className="grid gap-4 md:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle>Объекты по статусам</CardTitle>
        </CardHeader>
        <CardContent>
          <ChartContainer config={{ value: { label: "Кол-во" } }} className="h-64">
            <BarChart data={byStatus}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis allowDecimals={false} />
              <Bar dataKey="value" fill="hsl(var(--primary))" />
              <ChartTooltip content={<ChartTooltipContent />} />
            </BarChart>
          </ChartContainer>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Динамика визитов</CardTitle>
        </CardHeader>
        <CardContent>
          <ChartContainer config={{ count: { label: "Визиты" } }} className="h-64">
            <LineChart data={visitsPerDay}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="day" />
              <YAxis allowDecimals={false} />
              <Line type="monotone" dataKey="count" stroke="hsl(var(--primary))" strokeWidth={2} dot={false} />
              <ChartTooltip content={<ChartTooltipContent />} />
            </LineChart>
          </ChartContainer>
        </CardContent>
      </Card>
    </div>
  );
}


