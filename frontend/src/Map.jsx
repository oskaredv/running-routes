import { MapContainer, TileLayer, useMapEvents, Marker, Popup } from "react-leaflet";
import RouteLayer from './RouteLayer.jsx'

function ClickHandler({ setStartCoords }) {
  useMapEvents({
    click(e) {
      setStartCoords([e.latlng.lat, e.latlng.lng]);
    },
  });
  return null;
}

function StartMarker({ startCoords}) {
    if (!startCoords) return null;

    return (
        <Marker position={startCoords}>
            <Popup>
                Start point
            </Popup>
        </Marker>
    );
}

export default function Map({ startCoords, setStartCoords, routeCoords }) {
    return (
        <MapContainer
          center={[59.444, 17.829]}
          zoom={13}
          style={{ height: "100%", width: "100%" }}
        >
            <TileLayer
                url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            />
            <ClickHandler setStartCoords={setStartCoords} />
            <StartMarker startCoords={startCoords} />
            <RouteLayer routeCoords={routeCoords} />
        </MapContainer>
    );
}