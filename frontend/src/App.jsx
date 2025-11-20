import { useState } from "react";
import Map from './Map.jsx'
import Preferenceform from './PreferenceForm.jsx'

export default function App() {

  const [startCoords, setStartCoords] = useState(null);
  const [distance, setDistance] = useState(5000);
  const [elevation, setElevation] = useState("any");
  const [surface, setSurface] = useState("any");
  const [nature, setNature] = useState("any");
  const [lighting, setLighting] = useState("any");
  const [poi, setPoi] = useState("any");

  async function handleGenerateRoute() {
  if (!startCoords) {
    alert("Select a start point on the map first");
    return;
  }

  setLoading(true);
  setError("");

  try {
    const res = await fetch("http://localhost:5000/route", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        coords: startCoords,
        distance: distance,
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

    // print result som test
    alert(route)
    //setRouteCoords(data.route);
    //setLengthStat(Math.round(data.length));
    //setElevationStat(data.elevation);
    //setElevationProfile(data.elevationOfRoute || []);
  } catch (err) {
    console.error(err);
    setError(err.message);
  } finally {
    setLoading(false);
  }
}


  return (
    <>
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
        />
      </div>
      <div style={{ height: "95vh", width: "100vw" }}>
        <Map startCoords={startCoords} setStartCoords={setStartCoords} />
      </div>
    </>
  );
}