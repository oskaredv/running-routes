export default function PreferencesForm({
  distance,
  setDistance,
  elevation,
  setElevation,
  surface,
  setSurface
}) {
  return (
    <div className="panel">
      <label>
        Distance:
        <input
          type="number"
          value={distance}
          onChange={(e) => setDistance(e.target.value)}
        />
      </label>

      <label>
        Elevation:
        <select
          value={elevation}
          onChange={(e) => setElevation(e.target.value)}
        >
          <option value="any">Any</option>
          <option value="flat">Flat</option>
          <option value="hilly">Hilly</option>
        </select>
      </label>

      <label>
        Surface:
        <select
          value={surface}
          onChange={(e) => setSurface(e.target.value)}
        >
          <option value="any">Any</option>
          <option value="road">Road</option>
          <option value="trail">Trail</option>
        </select>
      </label>
    </div>
  );
}