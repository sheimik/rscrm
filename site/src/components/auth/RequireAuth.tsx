import { PropsWithChildren, ReactNode } from "react";
import { Link, Navigate, useLocation } from "react-router-dom";
import { Loader2 } from "lucide-react";
import { useCurrentUser } from "@/hooks/use-current-user";

type RequireAuthProps = PropsWithChildren<{
  allowedRoles?: string[];
}>;

const DEFAULT_REDIRECT = "/auth/login";

export function RequireAuth({ children, allowedRoles }: RequireAuthProps) {
  const location = useLocation();
  const {
    data: currentUser,
    isLoading,
    isError,
    error,
  } = useCurrentUser();

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center bg-background">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (isError || !currentUser) {
    const message = error instanceof Error ? error.message.toLowerCase() : "";
    if (message.includes("401") || message.includes("unauthorized")) {
      return <Navigate to={DEFAULT_REDIRECT} replace state={{ from: location }} />;
    }

    return (
      <div className="flex h-screen flex-col items-center justify-center gap-4 bg-background px-4 text-center text-sm text-muted-foreground">
        <p>Не удалось получить данные пользователя.</p>
        <p>{error instanceof Error ? error.message : "Попробуйте повторить позже."}</p>
        <ButtonLink to={DEFAULT_REDIRECT}>На страницу входа</ButtonLink>
      </div>
    );
  }

  if (allowedRoles && !allowedRoles.includes(currentUser.role)) {
    const fallback =
      currentUser.role === "ENGINEER"
        ? "/cabinet/route"
        : "/_admin/dashboard";
    return <Navigate to={fallback} replace />;
  }

  return <>{children}</>;
}

function ButtonLink({ to, children }: { to: string; children: ReactNode }) {
  return (
    <Link
      to={to}
      className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition hover:bg-primary/90"
    >
      {children}
    </Link>
  );
}
