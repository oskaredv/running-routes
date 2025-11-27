import { useState } from "react";


function InputSlider({ value, setValue, min, max, step }) {

  return (
    <>
      <label>
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={value}
          onChange={(e) => setValue(Number(e.target.value))}
        />
      </label>
    </>
  );
} 

export default function PreferencesForm({
  distance,
  setDistance,
  elevation,
  setElevation,
  surface,
  setSurface,
  nature,
  setNature,
  lighting,
  setLighting,
  poi,
  setPoi,
  handleGenerateRoute
}) {

  const [showPreferences, setShowPreferences] = useState(false);

  return (
    <div className="panel">
      <label>
        Test 1
        <InputSlider value={distance} setValue={setDistance} min={0} max={10000} step={1}/>
        Test 2
      </label>
      

      <label>
        Elevation:
        <select
          value={elevation}
          onChange={(e) => setElevation(e.target.value)}
        >
            <option value="nopref">No preference</option>
            <option value="hilly">Hilly</option>
            <option value="flat">Flat</option>
        </select>
      </label>

      <label>
        Surface:
        <select
          value={surface}
          onChange={(e) => setSurface(e.target.value)}
        >
            <option value="nopref">No preference</option>
            <option value="road">Road</option>
            <option value="trail">Trail</option>
        </select>
      </label>

      <label>
        Nature:
        <select
          value={nature}
          onChange={(e) => setNature(e.target.value)}
        >
            <option value="nopref">No preference</option>
            <option value="yes">Yes</option>
        </select>
      </label>

      <label>
        Lighting:
        <select
          value={lighting}
          onChange={(e) => setLighting(e.target.value)}
        >
            <option value="nopref">No preference</option>
            <option value="yes">Yes</option>
        </select>
      </label>
    
      <label>
        POI:
        <select
          value={poi}
          onChange={(e) => setPoi(e.target.value)}
        >
            <option value="nopref">No preference</option>
            <option value="tourism">Tourism</option>
            <option value="viewpoint">Viewpoint</option>
        </select>
      </label>
        <button onClick={handleGenerateRoute}>
          Generate Route
        </button>
    </div>
  );
}