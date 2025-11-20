import { useState } from "react";
import Map from './Map.jsx'
import Preferenceform from './PreferenceForm.jsx'

export default function App() {

  const [startCoords, setStartCoords] = useState(null);
  const [distance, setDistance] = useState(5000);
  const [elevation, setElevation] = useState("any");
  const [surface, setSurface] = useState("any");


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
        />
      </div>
      <div style={{ height: "95vh", width: "100vw" }}>
        <Map startCoords={startCoords} setStartCoords={setStartCoords} />
      </div>
    </>
  );
}