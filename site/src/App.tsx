import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AdminLayout } from "./components/layouts/AdminLayout";
import { CabinetLayout } from "./components/layouts/CabinetLayout";
import Login from "./pages/auth/Login";
import Dashboard from "./pages/admin/Dashboard";
import Objects from "./pages/admin/Objects";
import ObjectDetail from "./pages/admin/ObjectDetail";
import Visits from "./pages/admin/Visits";
import Customers from "./pages/admin/Customers";
import Reports from "./pages/admin/Reports";
import Analytics from "./pages/admin/Analytics";
import Users from "./pages/admin/Users";
import Audit from "./pages/admin/Audit";
import Notifications from "./pages/admin/Notifications";
// import Settings from "./pages/admin/Settings";
import RoutePage from "./pages/cabinet/Route";
import CabinetObjects from "./pages/cabinet/Objects";
import Profile from "./pages/cabinet/Profile";
import CabinetAdd from "./pages/cabinet/Add";
import CabinetCustomers from "./pages/cabinet/Customers";
import NotFound from "./pages/NotFound";
import { RequireAuth } from "./components/auth/RequireAuth";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
      refetchOnWindowFocus: false,
    },
  },
});

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner position="top-center" />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Navigate to="/auth/login" replace />} />
          <Route path="/auth/login" element={<Login />} />
          
          {/* Admin Routes */}
          <Route
            path="/_admin"
            element={
              <RequireAuth allowedRoles={["ADMIN", "SUPERVISOR"]}>
                <AdminLayout />
              </RequireAuth>
            }
          >
            <Route index element={<Navigate to="/_admin/dashboard" replace />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="objects" element={<Objects />} />
            <Route path="objects/:id" element={<ObjectDetail />} />
            <Route path="visits" element={<Visits />} />
            <Route path="customers" element={<Customers />} />
            <Route path="reports" element={<Reports />} />
            <Route path="analytics" element={<Analytics />} />
            <Route path="users" element={<Users />} />
            <Route path="audit" element={<Audit />} />
            <Route path="notifications" element={<Notifications />} />
            {/* <Route path="settings" element={<Settings />} /> */}
          </Route>

          {/* Cabinet Routes */}
          <Route
            path="/cabinet"
            element={
              <RequireAuth allowedRoles={["ENGINEER"]}>
                <CabinetLayout />
              </RequireAuth>
            }
          >
            <Route index element={<Navigate to="/cabinet/route" replace />} />
            <Route path="route" element={<RoutePage />} />
            <Route path="objects" element={<CabinetObjects />} />
            <Route path="add" element={<CabinetAdd />} />
            <Route path="customers" element={<CabinetCustomers />} />
            <Route path="profile" element={<Profile />} />
          </Route>

          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
