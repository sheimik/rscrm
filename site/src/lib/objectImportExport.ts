import type { ApiObject, ObjectCreatePayload } from "./types";

const DEFAULT_HEADERS = [
  "id",
  "address",
  "type",
  "status",
  "city_id",
  "city_name",
  "district_id",
  "district_name",
  "contact_name",
  "contact_phone",
  "visits_count",
  "last_visit_at",
];

const escapeCell = (value: unknown) =>
  `"${String(value ?? "").replace(/"/g, '""')}"`;

export function buildObjectsCsv(objects: ApiObject[]): string {
  const headerRow = DEFAULT_HEADERS.map(escapeCell).join(";");
  const dataRows = objects.map((obj) =>
    [
      obj.id,
      obj.address,
      obj.type,
      obj.status,
      obj.city_id,
      obj.city?.name,
      obj.district_id,
      obj.district?.name,
      obj.contact_name,
      obj.contact_phone,
      obj.visits_count,
      obj.last_visit_at,
    ]
      .map(escapeCell)
      .join(";"),
  );

  return [headerRow, ...dataRows].join("\n");
}

interface ImportOptions {
  typeNameToEnum: Record<string, string>;
  statusNameToEnum: Record<string, string>;
  createObject: (payload: ObjectCreatePayload) => Promise<unknown>;
}

export async function importObjectsFromCsv(
  file: File,
  { typeNameToEnum, statusNameToEnum, createObject }: ImportOptions,
): Promise<{ created: number; skipped: number }> {
  const text = await file.text();
  const lines = text.split(/\r?\n/).map((line) => line.trim()).filter(Boolean);

  if (lines.length <= 1) {
    return { created: 0, skipped: 0 };
  }

  const delimiter = lines[0].includes(";") ? ";" : ",";
  const headers = lines[0]
    .split(delimiter)
    .map((h) => h.trim().toLowerCase());

  let created = 0;
  let skipped = 0;

  for (const line of lines.slice(1)) {
    const cells = line
      .split(delimiter)
      .map((cell) => cell.replace(/^"|"$/g, "").trim());
    const record: Record<string, string> = {};
    headers.forEach((header, idx) => {
      record[header] = cells[idx] || "";
    });

    const address = record["address"] || record["адрес"];
    const cityId = record["city_id"] || record["город_id"];
    const typeRaw = record["type"] || record["тип"];

    if (!address || !cityId || !typeRaw) {
      skipped += 1;
      continue;
    }

    let typeValue = typeRaw.toUpperCase();
    if (typeNameToEnum[typeRaw.toLowerCase()]) {
      typeValue = typeNameToEnum[typeRaw.toLowerCase()];
    }

    const statusRaw = record["status"] || record["статус"] || "NEW";
    let statusValue = statusRaw.toUpperCase();
    if (statusNameToEnum[statusRaw.toLowerCase()]) {
      statusValue = statusNameToEnum[statusRaw.toLowerCase()];
    }

    try {
      await createObject({
        type: typeValue,
        address,
        city_id: cityId,
        district_id: record["district_id"] || record["район_id"] || undefined,
        status: statusValue,
        contact_name: record["contact_name"] || record["контакт"] || undefined,
        contact_phone: record["contact_phone"] || record["телефон"] || undefined,
      });
      created += 1;
    } catch {
      skipped += 1;
    }
  }

  return { created, skipped };
}
