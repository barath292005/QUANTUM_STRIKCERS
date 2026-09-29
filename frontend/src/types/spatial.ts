/**
 * Future-ready GeoJSON contract for spatial overlays.
 * The current map does not fabricate features; collections stay empty until
 * a real backend layer (e.g. GET /api/v1/geospatial/layers) exists.
 */
export interface GeoJsonGeometry {
  type: string;
  coordinates: unknown;
}

export interface GeoJsonFeature {
  type: 'Feature';
  geometry: GeoJsonGeometry | null;
  properties: Record<string, unknown> | null;
}

export interface GeoJsonFeatureCollection {
  type: 'FeatureCollection';
  features: GeoJsonFeature[];
}

export const EMPTY_SPATIAL_LAYERS: GeoJsonFeatureCollection = {
  type: 'FeatureCollection',
  features: [],
};

export function hasSpatialFeatures(collection: GeoJsonFeatureCollection | null | undefined): boolean {
  return Boolean(collection && collection.features.length > 0);
}
