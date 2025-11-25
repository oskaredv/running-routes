import { Polyline, CircleMarker, useMap } from "react-leaflet";
import { latLngBounds } from "leaflet";
import { useEffect } from "react";

export default function RouteLayer({ routeCoords }) {
  if (!routeCoords || routeCoords.length === 0) return null;

  const map = useMap()

  useEffect(() => {
    const bounds = latLngBounds(routeCoords);
    map.fitBounds(bounds, {
      padding: [40, 40],
      animate: true
    });
  }, [routeCoords]);

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