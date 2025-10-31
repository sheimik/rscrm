import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

/**
 * Хук для получения сведений о текущем пользователе.
 * Кэшируем результат, чтобы переиспользовать между страницами кабинета.
 */
export function useCurrentUser() {
  return useQuery({
    queryKey: ["current-user"],
    queryFn: () => api.getCurrentUser(),
    staleTime: 5 * 60 * 1000,
  });
}
