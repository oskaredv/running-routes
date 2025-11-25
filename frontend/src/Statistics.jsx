 import { useState } from "react";
 
 function DetailedStats({ routeLength, routeElevation, showDetailedStats, setShowDetailedStats }) {
    return (
                <div className="detailed-stats">
                    <p style={{ textAlign: "center", color: "black", fontSize: "20px" }}>
                        Length: {routeLength}m
                    </p>
                    <p style={{ textAlign: "center", color: "black", fontSize: "20px" }}>
                        Elevation: {routeElevation}m
                    </p>
                    <button className="close-btn" onClick={() => setShowDetailedStats(false)}>×</button>
                </div>
    );    
 }
 
 export default function Statistics({ routeLength, routeElevation }) {

    const [showDetailedStats, setShowDetailedStats] = useState(false);

    routeLength = Math.round(routeLength);

    if (showDetailedStats) {
        return (<DetailedStats routeLength={routeLength} routeElevation={routeElevation} showDetailedStats={showDetailedStats} setShowDetailedStats={setShowDetailedStats}/>);
    }
    else {
        return (
                <div className="concise-stats">
                    <p style={{ textAlign: "center", color: "black", fontSize: "20px" }}>
                        {routeLength}m
                    </p>
                    <button onClick={() => setShowDetailedStats(true)} >
                        See more statistics {showDetailedStats}
                    </button>
                </div>
        );
    }
}