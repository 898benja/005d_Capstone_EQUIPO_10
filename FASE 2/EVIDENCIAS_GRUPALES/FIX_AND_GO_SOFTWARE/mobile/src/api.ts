/** Contrato compartido con Django: todas las rutas terminan en /. */
export const apiUrl = process.env.EXPO_PUBLIC_API_URL?.replace(/\/+$/, "");
export type User = {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  role: "CLIENT" | "PROVIDER";
  phone: string;
  default_address: string;
  default_commune: number | null;
};
export type Session = { token: string; user: User };
export type Option = { id: number; name: string; slug: string };
export type Provider = {
  avatar?: string;
  avg_rating?: number | null;
  rating_count?: number;
  latitude: number | null;
  longitude: number | null;
  map_visible: boolean;
  distance_km?: number | null;
  requested_point?: { latitude: number; longitude: number };
  id: number;
  user_id: number;
  display_name: string;
  description: string;
  years_experience: number | null;
  phone: string;
  categories: Option[];
  communes: Option[];
  is_active: boolean;
};
export type Quote = {
  id: number;
  description: string;
  price: number;
  status: string;
  notes: string;
};
export type RequestItem = {
  id: number;
  description: string;
  category_name: string;
  commune_name: string;
  client_name: string;
  provider_name: string;
  status: string;
  status_display: string;
  address?: string;
  quote?: Quote | null;
};
export type Rating = { id: number; score: number; comment: string };
export type Page<T> = {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
};
export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
  ) {
    super(message);
  }
}
function describe(value: unknown): string {
  if (typeof value === "string") return value;
  if (Array.isArray(value)) return value.map(describe).join(" ");
  if (value && typeof value === "object")
    return Object.entries(value)
      .map(([key, item]) => `${key}: ${describe(item)}`)
      .join("\n");
  return "No se pudo completar la operación.";
}
export async function api<T>(
  path: string,
  token?: string,
  method = "GET",
  body?: unknown,
): Promise<T> {
  if (!apiUrl)
    throw new Error(
      "Configura EXPO_PUBLIC_API_URL en mobile/.env con la IP del Mac.",
    );
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 12000);
  try {
    const response = await fetch(`${apiUrl}/api/v1/${path}`, {
      method,
      signal: controller.signal,
      headers: {
        Accept: "application/json",
        ...(body === undefined ? {} : { "Content-Type": "application/json" }),
        ...(token ? { Authorization: `Token ${token}` } : {}),
      },
      ...(body === undefined ? {} : { body: JSON.stringify(body) }),
    });
    const text = await response.text();
    let data: any;
    try {
      data = text ? JSON.parse(text) : null;
    } catch {
      throw new ApiError(
        "El servidor devolvió una respuesta inesperada.",
        response.status,
      );
    }
    if (!response.ok)
      throw new ApiError(
        response.status === 401
          ? "Tu sesión terminó. Vuelve a ingresar."
          : describe(data?.detail ?? data),
        response.status,
      );
    return data as T;
  } catch (error) {
    if (error instanceof ApiError) throw error;
    throw new Error(
      "No pudimos conectar con FIX&GO. Comprueba la red e inténtalo otra vez.",
    );
  } finally {
    clearTimeout(timeout);
  }
}
export async function checkHealth() {
  const health = await api<{
    status: string;
    database: string;
    service: string;
  }>("health/");
  if (
    health.status !== "ok" ||
    health.database !== "ok" ||
    health.service !== "fix-and-go-api"
  )
    throw new Error("La API de FIX&GO no está disponible.");
  return health;
}
/** Catálogos pequeños: recorrer páginas sin enviar tokens a URLs recibidas del servidor. */
export async function options(path: string): Promise<Option[]> {
  const rows: Option[] = [];
  for (let page = 1; ; page++) {
    const result = await api<Page<Option>>(
      `${path}?page=${page}&page_size=100`,
    );
    rows.push(...result.results);
    if (!result.next) return rows;
  }
}
