/**
 * Общие справочники и вспомогательные функции для отображения данных из API
 */

export const OBJECT_STATUS_LABELS: Record<string, string> = {
  NEW: "Новый",
  INTEREST: "В работе",
  CALLBACK: "Ожидание",
  DONE: "Завершён",
  REJECTED: "Отказ",
};

export const OBJECT_TYPE_LABELS: Record<string, string> = {
  MKD: "МКД",
  BUSINESS_CENTER: "Бизнес-центр",
  SHOPPING_CENTER: "ТЦ",
  SCHOOL: "Школа",
  HOSPITAL: "Больница",
  HOTEL: "Отель",
  CAFE: "Кафе",
  OTHER: "Другое",
};

export const VISIT_STATUS_LABELS: Record<string, string> = {
  PLANNED: "Запланирован",
  IN_PROGRESS: "В процессе",
  DONE: "Завершён",
  CANCELLED: "Отменён",
};

export const INTEREST_LABELS: Record<string, string> = {
  INTERNET: "Интернет",
  TV: "ТВ",
  CCTV: "Видеонаблюдение",
  BABY_MONITOR: "Интернет-няня",
  OTHER: "Другое",
};

export function translateOrFallback(
  dictionary: Record<string, string>,
  value: string | null | undefined,
): string {
  if (!value) {
    return "-";
  }
  return dictionary[value] ?? value;
}

export function getObjectStatusBadgeClass(status: string): string {
  switch (status) {
    case "NEW":
      return "bg-blue-500";
    case "INTEREST":
      return "bg-yellow-500";
    case "CALLBACK":
      return "bg-orange-500";
    case "DONE":
      return "bg-green-500";
    case "REJECTED":
      return "bg-red-500";
    default:
      return "bg-gray-500";
  }
}
