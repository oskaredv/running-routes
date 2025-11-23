import { useState } from "react";
import Map from './Map.jsx'
import Preferenceform from './PreferenceForm.jsx'
import Loading from './Loading.jsx'
import Statistics from "./Statistics.jsx";

export default function App() {

  // Input to route generator
  const [startCoords, setStartCoords] = useState(null);
  const [distance, setDistance] = useState(5000);
  const [elevation, setElevation] = useState("nopref");
  const [surface, setSurface] = useState("nopref");
  const [nature, setNature] = useState("nopref");
  const [lighting, setLighting] = useState("nopref");
  const [poi, setPoi] = useState("nopref");

  // Output from route generator
  const [routeCoords, setRouteCoords] = useState(null);
  const [routeLength, setRouteLength] = useState(null);

  const [loading, setLoading] = useState(false);

  async function handleGenerateRoute() {
    if (!startCoords) {
      alert("Select a start point on the map first");
      return;
    }

    setLoading(true)

    try {
      const res = await fetch("http://localhost:5000/route", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          coords: startCoords,
          distance: Number(distance),
          elevation: elevation,
          surface: surface,
          nature: nature,
          lighting: lighting,
          poi: poi,
        }),
      });

      const data = await res.json();

      if (!res.ok || data.error) {
        throw new Error(data.error || "Unknown error from backend");
      }

      setRouteCoords(data.route);
      setRouteLength(data.length)

    } catch (err) {
      console.error(err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }


  return (
    <>
      {loading && < Loading />}
      <div style={{ height: "5vh", width: "100vw" }}>
        <Preferenceform
          distance={distance}
          setDistance={setDistance}
          elevation={elevation}
          setElevation={setElevation}
          surface={surface}
          setSurface={setSurface}
          nature={nature}
          setNature={setNature}
          lighting={lighting}
          setLighting={setLighting}
          poi={poi}
          setPoi={setPoi}
          handleGenerateRoute={handleGenerateRoute}
        />
      </div>
      <div style={{ position: "relative", height: "95vh", width: "100vw" }}>
        <Map startCoords={startCoords} setStartCoords={setStartCoords} routeCoords={routeCoords} />
        {routeLength && < Statistics routeLength={routeLength} />}
      </div>
    </>
  );
}