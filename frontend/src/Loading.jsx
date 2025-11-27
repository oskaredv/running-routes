import "./loading.css";

export default function Loading() {
  return (
    <div className="loading-wrapper">
      <div className="runner">
          <div className="head"></div>
          <div className="torso"></div>
          <div className="arm left">
              <div>
                  <div></div>
              </div>
          </div>
          <div className="arm right">
              <div>
                  <div></div>
              </div>
          </div>
          <div className="leg left">
              <div className="upper_leg">
                  <div className="lower_leg"></div>
              </div>
          </div>
          <div className="leg right">
              <div className="upper_leg">
                  <div className="lower_leg"></div>
              </div>
          </div>
      </div>
      <div className="shadow"></div>
      <p>Generating route...</p>
    </div>
  );
}