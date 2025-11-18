// Initialize map
var map = L.map("map").setView([59.444, 17.829], 13);

// Add OSM tile layer
L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

// Locate user
L.control.locate({
    position: 'topright',
    setView: 'once',
    flyTo: true,
    keepCurrentZoomLevel: false,
    enableHighAccuracy: true,
    initialZoomLevel: 16
}).addTo(map);

// Store coordinates of clicked marker
var clickedCoords = null;
var currentMarker = null;

var routePolyline = null;
var startCircle = null;
var currentChart = null

// Add marker to map when clicking
map.on("click", function (e) {
    clickedCoords = [e.latlng.lat, e.latlng.lng];
    console.log("Clicked:", clickedCoords);

    // Remove previous marker
    if (currentMarker) {
        map.removeLayer(currentMarker);
    }

    // Add new marker
    currentMarker = L.marker(e.latlng)
        .addTo(map)
        .bindPopup("Start point")
        .openPopup();
});

const loading = document.getElementById("loading");

function showLoading() {
    loading.style.display = "flex";
}

function hideLoading() {
    loading.style.display = "none";
}

// Send coordinates to backend when button clicked
document.getElementById("generateBtn").addEventListener("click", function () {
    if (!clickedCoords) {
        alert("You need to select a start point first by clicking on the map");
        return;
    }

    var routeLengthInput = document.getElementById("lengthInput").value;
    var routeLength = parseFloat(routeLengthInput);

    var elevation = document.getElementById("elevation").value;
    var surface = document.getElementById("surface").value;
    var nature = document.getElementById("nature").value;
    var lighting = document.getElementById("lighting").value;
    var poi = document.getElementById("poi").value;

    if (isNaN(routeLength) || routeLength <= 0) {
        alert("You need to enter a positive route length");
        return;
    }

    showLoading();

    fetch("/route", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            coords: clickedCoords,
            distance: routeLength,
            elevation: elevation,
            surface: surface,
            lighting: lighting,
            nature: nature,
            poi: poi,
        })
    })
        .then(res => res.json())
        .then(data => {
            if (data.error) {
                alert("Error: " + data.error);
                return;
            }

            const length = document.getElementById("length");
            length.style.display = "block";
            length.innerText = "Route length (m): " + Math.round(data.length);

            const elevationStat = document.getElementById("elevationStat");
            elevationStat.style.display = "block";
            elevationStat.innerText = "Elevation (m): " + data.elevation;

            // Remove previous route if exists
            if (routePolyline) map.removeLayer(routePolyline);

            // Draw new route
            routePolyline = L.polyline(data.route, { color: "green", weight: 4 }).addTo(map);

            if (startCircle) map.removeLayer(startCircle);

            startCircle = L.circleMarker(data.route[0], { radius: 6, color: "green", fillColor: "green", fillOpacity: 1 }).addTo(map);

            // Fit map to route bounds
            map.fitBounds(routePolyline.getBounds());

            const lengths = data.elevationOfRoute.map(segment => segment.length);
            const elevations = data.elevationOfRoute.map(segment => segment.elevation);

            if (currentChart) {
                currentChart.destroy();
            }

            const ctx = document.getElementById('elevationChartCanvas').getContext('2d');
            currentChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: lengths,  // x-axis values
                    datasets: [{
                        label: 'Elevation Profile',
                        data: elevations, // y-axis values
                        borderColor: 'blue',
                        backgroundColor: 'rgba(0, 0, 255, 0.1)',
                        tension: 0.3, // curve the line a bit
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        x: {
                            type: "linear",
                            title: {
                                display: true,
                                text: 'Length of route (m)',
                            }
                        },
                        y: {
                            type: "linear",
                            title: {
                                display: true,
                                text: 'Elevation (m)',
                            }
                        }
                    }
                }
            });
            hideLoading();

        })
        .catch(err => {
            console.error(err)
            hideLoading();
        });
});        