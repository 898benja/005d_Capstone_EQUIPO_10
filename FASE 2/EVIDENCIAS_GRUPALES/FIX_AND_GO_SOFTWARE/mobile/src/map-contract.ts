/** Área aproximada de Santiago, alineada con catalog/geo.py. */
export type Point = { latitude: number; longitude: number };
export const SANTIAGO: Point = { latitude: -33.4489, longitude: -70.6693 };
export function validPoint(value: unknown): value is Point {
  if (!value || typeof value !== 'object') return false;
  const p = value as Point;
  return typeof p.latitude === 'number' && typeof p.longitude === 'number'
    && Number.isFinite(p.latitude) && Number.isFinite(p.longitude)
    && p.latitude >= -33.85 && p.latitude <= -33.1
    && p.longitude >= -71.1 && p.longitude <= -70.35;
}
export type MapMarker = Point & { id: number; name: string; description: string };
export type MapProps = {
  point: Point | null;
  markers: MapMarker[];
  onPoint: (point: Point) => void;
  onSelect?: (id: number) => void;
  readOnly?: boolean;
  actionLabel?: string;
  height?: number;
  immersive?: boolean;
  selectedId?: number | null;
};
export function handleMapMessage(raw: unknown, props: MapProps) {
  let data: any;
  try { data = typeof raw === 'string' ? JSON.parse(raw) : raw; } catch { return; }
  if (data?.source !== 'fixgo-map') return;
  if (!props.readOnly && data.type === 'point' && validPoint(data.point)) props.onPoint(data.point);
  if (data.type === 'provider' && Number.isInteger(data.id)
      && props.markers.some(p => p.id === data.id)) props.onSelect?.(data.id);
}
