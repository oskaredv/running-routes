import { MapContainer, TileLayer, useMapEvents } from "react-leaflet";

function ClickHandler({ setStartCoords }) {
  useMapEvents({
    click(e) {
      setStartCoords([e.latlng.lat, e.latlng.lng]); // 👈 skickar upp till App
    },
  });
  return null;
}

export default function Map({ setStartCoords }) {
    return (
        <MapContainer
          center={[59.444, 17.829]}
          zoom={13}
          style={{ height: "100%", width: "100%" }}
        >
          <TileLayer
            url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; OpenStreetMap contributors'
          />
          <ClickHandler setStartCoords={setStartCoords} />
        </MapContainer>
    );
}