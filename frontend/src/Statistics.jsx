 import { useState } from "react";
 
 export default function Statistics({ routeLength }) {

    const [detailedStats, setDetailedStats] = useState(false);

    routeLength = Math.round(routeLength);

    if (detailedStats) {
        return (
                <div className="concise-stats">
                    <p style={{ textAlign: "center", color: "black", fontSize: "20px" }}>
                        {routeLength}m
                    </p>
                    <p> {String(detailedStats)}</p>
                    <button onClick={() => setDetailedStats(false)} >
                        Close statistics {detailedStats}
                    </button>
                </div>
        );
    }
    else {
        return (
                <div className="concise-stats">
                    <p style={{ textAlign: "center", color: "black", fontSize: "20px" }}>
                        {routeLength}m
                    </p>
                    <p> {String(detailedStats)}</p>
                    <button onClick={() => setDetailedStats(true)} >
                        See more statistics {detailedStats}
                    </button>
                </div>
        );
    }
}