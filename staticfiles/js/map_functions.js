let map, userMarker, vehicleMarkers, vehicleInfoWindow, polylines;
let vehicleRoutes = [];
let vehicleInfo = [];
let routeIndices = [];
let movementIntervals;

// Fetch vehicle data from the Django API
async function fetchVehicleData() {
    try {
        // Try both API endpoints - first the vehicles endpoint, then fallback to vehicle-data
        let response;
        try {
            response = await fetch('/api/vehicles/');
            if (!response.ok) {
                throw new Error('First endpoint failed');
            }
        } catch (e) {
            console.log('Trying fallback API endpoint');
            response = await fetch('/api/vehicle-data/');
            if (!response.ok) {
                throw new Error('Both API endpoints failed');
            }
        }
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching vehicle data:', error);
        return [];
    }
}

async function initMap() {
    const initialLocation = { lat: 37.7749, lng: -122.4194 };
    
    // Initialize the map
    map = new google.maps.Map(document.getElementById("map"), {
        center: initialLocation,
        zoom: 12,
    });
    
    // Create user marker
    userMarker = new google.maps.Marker({
        position: initialLocation,
        map: map,
        title: "Your Location",
    });
    
    // Fetch vehicle data from the Django backend
    const vehicles = await fetchVehicleData();
    
    if (vehicles.length > 0) {
        // Extract routes and vehicle information
        vehicleRoutes = vehicles.map(vehicle => vehicle.route);
        vehicleInfo = vehicles.map(vehicle => generateVehicleInfoHTML(vehicle));
        routeIndices = vehicles.map(() => 0);
        
        // Create vehicle markers
        vehicleMarkers = vehicles.map((vehicle, index) => {
            return new google.maps.Marker({
                position: vehicle.route[0],
                map: map,
                title: `Vehicle ${index + 1} Location`,
                icon: 'https://maps.google.com/mapfiles/kml/shapes/bus.png',
                draggable: true,
            });
        });
        
        // Create info window
        vehicleInfoWindow = new google.maps.InfoWindow({
            content: vehicleInfo[0],
        });
        
        // Add click listeners to markers
        vehicleMarkers.forEach((marker, index) => {
            marker.addListener('click', function () {
                seeVehicleInfo(index);
            });
        });
        
        // Create polylines for routes
        polylines = vehicleRoutes.map((route, index) => {
            return new google.maps.Polyline({
                path: route,
                geodesic: true,
                strokeColor: '#FF0000',
                strokeOpacity: 1.0,
                strokeWeight: 2,
                map: map,
            });
        });
        
        // Start vehicle movement
        movementIntervals = vehicleMarkers.map((marker, index) => {
            return setInterval(() => moveVehicle(index), 2000);
        });
    } else {
        // Fallback to hardcoded routes if API fails
        console.log("Using fallback vehicle data");
        setupFallbackVehicleData();
    }
}

function setupFallbackVehicleData() {
    // Fallback vehicle routes
    vehicleRoutes = [
        [
            { lat: 37.774, lng: -122.420 },
            { lat: 37.775, lng: -122.419 },
            { lat: 37.776, lng: -122.420 },
            { lat: 37.777, lng: -122.420 },
            { lat: 37.778, lng: -122.420 },
            { lat: 37.779, lng: -122.420 },
            { lat: 37.780, lng: -122.420 },
            { lat: 37.781, lng: -122.420 }
        ],
        [
            { lat: 37.770, lng: -122.400 },
            { lat: 37.771, lng: -122.401 },
            { lat: 37.772, lng: -122.402 },
            { lat: 37.773, lng: -122.403 },
            { lat: 37.774, lng: -122.404 },
            { lat: 37.774, lng: -122.405 },
            { lat: 37.773, lng: -122.406 },
            { lat: 37.773, lng: -122.407 }
        ]
    ];
    
    // Generate fallback vehicle info
    vehicleInfo = [
        generateVehicleInfoHTML({
            plateNumber: generateRandomPlateNumber(),
            driverName: generateRandomDriverName(),
            capacity: generateRandomCapacity()
        }),
        generateVehicleInfoHTML({
            plateNumber: generateRandomPlateNumber(),
            driverName: generateRandomDriverName(),
            capacity: generateRandomCapacity()
        })
    ];
    
    routeIndices = [0, 0];
    
    // Setup markers, polylines, etc. as in the original function
    vehicleMarkers = vehicleRoutes.map((route, index) => {
        return new google.maps.Marker({
            position: route[0],
            map: map,
            title: `Vehicle ${index + 1} Location`,
            icon: 'https://maps.google.com/mapfiles/kml/shapes/bus.png',
            draggable: true,
        });
    });
    
    vehicleInfoWindow = new google.maps.InfoWindow({
        content: vehicleInfo[0],
    });
    
    vehicleMarkers.forEach((marker, index) => {
        marker.addListener('click', function () {
            seeVehicleInfo(index);
        });
    });
    
    polylines = vehicleRoutes.map((route, index) => {
        return new google.maps.Polyline({
            path: route,
            geodesic: true,
            strokeColor: '#FF0000',
            strokeOpacity: 1.0,
            strokeWeight: 2,
            map: map,
        });
    });
    
    movementIntervals = vehicleMarkers.map((marker, index) => {
        return setInterval(() => moveVehicle(index), 2000);
    });
}

function generateVehicleInfoHTML(vehicle) {
    return `
        <div>
            <strong>Jeepney Information</strong><br>
            <strong>Plate Number:</strong> ${vehicle.plateNumber}<br>
            <strong>Driver Name:</strong> ${vehicle.driverName}<br>
            <strong>Capacity:</strong> ${vehicle.capacity} passengers
        </div>
    `;
}

function generateRandomPlateNumber() {
    const letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    const numbers = '0123456789';
    const randomLetter = letters.charAt(Math.floor(Math.random() * letters.length));
    const randomNumbers = Math.floor(Math.random() * 1000);
    return `${randomLetter}${randomNumbers}`;
}

function generateRandomDriverName() {
    const firstNames = ['John', 'Jane', 'Robert', 'Alice', 'Michael', 'Emily'];
    const lastNames = ['Doe', 'Smith', 'Johnson', 'Brown', 'Lee'];
    const randomFirstName = firstNames[Math.floor(Math.random() * firstNames.length)];
    const randomLastName = lastNames[Math.floor(Math.random() * lastNames.length)];
    return `${randomFirstName} ${randomLastName}`;
}

function generateRandomCapacity() {
    return Math.floor(Math.random() * (20 - 10 + 1)) + 10;
}

function moveVehicle(index) {
    if (!vehicleRoutes[index] || !vehicleMarkers[index]) return;
    
    routeIndices[index] = (routeIndices[index] + 1) % vehicleRoutes[index].length;
    const newPosition = vehicleRoutes[index][routeIndices[index]];
    vehicleMarkers[index].setPosition(newPosition);
}

function seeVehicleInfo(index) {
    if (!vehicleMarkers[index] || !vehicleInfo[index]) return;
    
    vehicleInfoWindow.close();
    vehicleInfoWindow.setContent(vehicleInfo[index]);
    vehicleInfoWindow.open(map, vehicleMarkers[index]);
    
    vehicleMarkers.forEach((marker, i) => {
        if (i === index) {
            const highlightedIcon = {
                url: 'https://maps.google.com/mapfiles/kml/shapes/bus.png',
                scaledSize: new google.maps.Size(40, 40),
                anchor: new google.maps.Point(20, 40),
            };
            const highlightCircle = new google.maps.Circle({
                map: map,
                center: marker.getPosition(),
                radius: 20,
                fillColor: '#00FF00',
                fillOpacity: 0.5,
                strokeWeight: 0,
            });
            marker.setIcon(highlightedIcon);
            setTimeout(() => {
                highlightCircle.setMap(null);
            }, 3000);
        } else {
            marker.setIcon('https://maps.google.com/mapfiles/kml/shapes/bus.png');
        }
    });
}

function viewRoute() {
    if (vehicleMarkers && vehicleMarkers.length > 0) {
        map.panTo(vehicleMarkers[0].getPosition());
    }
}

function payFare() {
    const fareAmount = prompt("Enter fare amount:");
    if (fareAmount) {
        // In a real application, you would make an API call to process the payment
        alert(`Payment successful!\nFare Amount: ${fareAmount}`);
    }
}

function checkSeatAvailability() {
    const seatsAvailable = Math.floor(Math.random() * 10);
    alert(`Available Seats: ${seatsAvailable}`);
}