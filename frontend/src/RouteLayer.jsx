import { Polyline, CircleMarker } from "react-leaflet";

export default function RouteLayer({ routeCoords }) {
  if (!routeCoords || routeCoords.length === 0) return null;

  return (
    <>
      <Polyline
        positions={routeCoords}
        pathOptions={{ color: "green", weight: 4 }}
      />
      <CircleMarker
        center={routeCoords[0]}
        radius={6}
        pathOptions={{ color: "green", fillColor: "green", fillOpacity: 1 }}
      />
    </>
  );
}