let map, userMarker, vehicleMarkers = [], vehicleInfoWindow, polylines = [];
let vehicleRoutes = [];
let vehicleAnimations = [];
let vehicleInfo = [];
let activeInfoWindows = [];
let userLocationWatchId = null;
let selectedVehicleId = null;

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
    // Center on Manila, Philippines
    const manilaCenterPoint = { lat: 14.5870, lng: 120.9830 };
    
    // Initialize the map with a more appropriate styling
    map = new google.maps.Map(document.getElementById("map"), {
        center: manilaCenterPoint,
        zoom: 13,
        mapTypeId: google.maps.MapTypeId.ROADMAP,
        styles: [
            {
                featureType: "poi",
                elementType: "labels",
                stylers: [{ visibility: "off" }]
            }
        ]
    });
    
    // Create user marker with a better icon
    userMarker = new google.maps.Marker({
        position: manilaCenterPoint,
        map: map,
        title: "Your Location",
        icon: {
            path: google.maps.SymbolPath.CIRCLE,
            scale: 10,
            fillColor: "#4285F4",
            fillOpacity: 1,
            strokeColor: "#FFFFFF",
            strokeWeight: 2
        },
        zIndex: 999 // Make sure user is always on top
    });
    
    // Request user's geolocation
    getUserLocation();
    
    // Fetch vehicle data from the Django backend
    const vehicles = await fetchVehicleData();
    
    if (vehicles && vehicles.length > 0) {
        await setupVehicles(vehicles);
    } else {
        console.log("No vehicle data received, using fallback");
        setupFallbackVehicleData();
    }
    
    // Add UI event listeners
    setupUIEventListeners();
}

function setupUIEventListeners() {
    // Add click listeners for the buttons
    document.getElementById("view-route-button").addEventListener("click", viewRoute);
    document.getElementById("pay-fare-button").addEventListener("click", payFare);
    document.getElementById("vehicle-info-button").addEventListener("click", () => {
        if (selectedVehicleId !== null) {
            seeVehicleInfo(selectedVehicleId);
        } else {
            alert("Please select a vehicle first by clicking on it");
        }
    });
    document.getElementById("seat-availability-button").addEventListener("click", checkSeatAvailability);
}

function getUserLocation() {
    if (navigator.geolocation) {
        // Get initial location
        navigator.geolocation.getCurrentPosition(
            (position) => {
                const userLocation = {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude
                };
                userMarker.setPosition(userLocation);
                
                // Only center map on user if we're initializing for the first time
                if (!vehicleMarkers.length) {
                    map.setCenter(userLocation);
                }
            },
            (error) => {
                console.error("Error getting user location:", error);
            },
            { enableHighAccuracy: true }
        );
        
        // Watch for position changes (like when using Grab)
        userLocationWatchId = navigator.geolocation.watchPosition(
            (position) => {
                const userLocation = {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude
                };
                
                // Animate the movement
                animateMarkerTo(userMarker, userLocation, 500);
            },
            (error) => {
                console.error("Error watching user location:", error);
            },
            { enableHighAccuracy: true, timeout: 5000, maximumAge: 0 }
        );
    } else {
        console.log("Geolocation is not supported by this browser.");
    }
}

async function setupVehicles(vehicles) {
    // Extract routes and vehicle information
    vehicleRoutes = vehicles.map(vehicle => vehicle.route);
    vehicleInfo = vehicles.map(vehicle => generateVehicleInfoHTML(vehicle));
    
    // Create info window
    vehicleInfoWindow = new google.maps.InfoWindow();
    
    // Create polylines for routes with different colors
    polylines = vehicles.map((vehicle, index) => {
        return new google.maps.Polyline({
            path: vehicle.route,
            geodesic: true,
            strokeColor: vehicle.routeColor || getRouteColor(index),
            strokeOpacity: 0.7,
            strokeWeight: 4,
            map: map
        });
    });
    
    // Create markers for each vehicle at random positions along their routes
    vehicleMarkers = vehicles.map((vehicle, index) => {
        // Start at a random position on the route
        const routeLength = vehicle.route.length;
        const randomPosition = Math.floor(Math.random() * routeLength);
        
        const marker = new google.maps.Marker({
            position: vehicle.route[randomPosition],
            map: map,
            title: `${vehicle.routeName} Jeepney`,
            icon: {
                url: 'https://maps.google.com/mapfiles/kml/shapes/bus.png',
                scaledSize: new google.maps.Size(32, 32),
                anchor: new google.maps.Point(16, 16)
            },
            optimized: true, // Better performance for animations
            zIndex: 100
        });
        
        // Add click listener to marker
        marker.addListener('click', function() {
            selectedVehicleId = index;
            seeVehicleInfo(index);
        });
        
        return marker;
    });
    
    // Start smooth animations for each vehicle
    startVehicleAnimations(vehicles);
}

function getRouteColor(index) {
    // Provide distinct colors for different routes
    const colors = ['#FF0000', '#0000FF', '#008000', '#FF00FF', '#FFA500', '#800080'];
    return colors[index % colors.length];
}

function generateVehicleInfoHTML(vehicle) {
    return `
        <div class="vehicle-info-popup">
            <h3>${vehicle.routeName} Jeepney</h3>
            <div class="vehicle-details">
                <p><strong>Plate Number:</strong> ${vehicle.plateNumber}</p>
                <p><strong>Driver:</strong> ${vehicle.driverName}</p>
                <p><strong>Capacity:</strong> ${vehicle.capacity} passengers</p>
                <p><strong>Route:</strong> ${vehicle.routeName}</p>
            </div>
            <div class="vehicle-actions">
                <button onclick="payFare(${vehicle.id})" class="fare-button">Pay Fare</button>
                <button onclick="checkSeatAvailability(${vehicle.id})" class="seat-button">Check Seats</button>
            </div>
        </div>
    `;
}

function startVehicleAnimations(vehicles) {
    vehicleAnimations = vehicles.map((vehicle, index) => {
        // Animation configuration
        const routePoints = vehicle.route;
        let currentPointIndex = Math.floor(Math.random() * routePoints.length); // Start at random point
        let nextPointIndex = (currentPointIndex + 1) % routePoints.length;
        let progress = 0;
        let speed = 0.01 + (Math.random() * 0.01); // Slightly different speeds
        
        // Setup animation interval
        const animation = {
            interval: setInterval(() => {
                // Calculate next position with easing for smooth movement
                const currentPoint = routePoints[currentPointIndex];
                const nextPoint = routePoints[nextPointIndex];
                
                // Linear interpolation between points
                const newPosition = {
                    lat: currentPoint.lat + (nextPoint.lat - currentPoint.lat) * progress,
                    lng: currentPoint.lng + (nextPoint.lng - currentPoint.lng) * progress
                };
                
                // Update marker position
                vehicleMarkers[index].setPosition(newPosition);
                
                // Update progress
                progress += speed;
                
                // Move to next segment when current one is complete
                if (progress >= 1) {
                    currentPointIndex = nextPointIndex;
                    nextPointIndex = (currentPointIndex + 1) % routePoints.length;
                    progress = 0;
                }
            }, 100), // Update every 100ms for smooth animation
            vehicle: vehicle
        };
        
        return animation;
    });
}

function setupFallbackVehicleData() {
    // Define Manila-specific fallback routes
    const manilaCenterPoint = { lat: 14.5870, lng: 120.9830 };
    map.setCenter(manilaCenterPoint);
    
    const fallbackVehicles = [
        {
            id: 1,
            plateNumber: generateRandomPlateNumber(),
            driverName: generateRandomDriverName(),
            capacity: generateRandomCapacity(),
            routeName: 'Pasig-Quiapo',
            routeColor: '#FF0000',
            route: [
                {'lat': 14.569391, 'lng': 121.081547},
                {'lat': 14.567177, 'lng': 121.080232},
                {'lat': 14.566141, 'lng': 121.077492},
                {'lat': 14.566124, 'lng': 121.076063},
                {'lat': 14.566170, 'lng': 121.073506},
                {'lat': 14.566295, 'lng': 121.070878},
                {'lat': 14.565953, 'lng': 121.070183},
                {'lat': 14.563603, 'lng': 121.069252},
                {'lat': 14.562798, 'lng': 121.067493},
                {'lat': 14.563317, 'lng': 121.065379},
                {'lat': 14.567330, 'lng': 121.065935},
                {'lat': 14.570228, 'lng': 121.066436},
                {'lat': 14.576790, 'lng': 121.058694},
                {'lat': 14.587210, 'lng': 121.046462},
                {'lat': 14.588027, 'lng': 121.044851},
                {'lat': 14.589162, 'lng': 121.041724},
                {'lat': 14.589473, 'lng': 121.037087},
                {'lat': 14.589463, 'lng': 121.035330},
                {'lat': 14.590018, 'lng': 121.034726},
                {'lat': 14.590780, 'lng': 121.033214},
                {'lat': 14.591870, 'lng': 121.030752},
                {'lat': 14.593059, 'lng': 121.028474},
                {'lat': 14.594645, 'lng': 121.024300},
                {'lat': 14.596130, 'lng': 121.020436},
                {'lat': 14.595902, 'lng': 121.019916},
                {'lat': 14.597661, 'lng': 121.017623},
                {'lat': 14.597339, 'lng': 121.015964},
                {'lat': 14.597574, 'lng': 121.015540},
                {'lat': 14.600601, 'lng': 121.013482},
                {'lat': 14.602424, 'lng': 121.011635},
                {'lat': 14.601235, 'lng': 121.000645},
                {'lat': 14.601080, 'lng': 120.997996},
                {'lat': 14.600483, 'lng': 120.996119},
                {'lat': 14.601229, 'lng': 120.994140},
                {'lat': 14.601585, 'lng': 120.992512},
                {'lat': 14.600524, 'lng': 120.991123},
                {'lat': 14.597343, 'lng': 120.989440},
                {'lat': 14.596441, 'lng': 120.989538},
                {'lat': 14.594352, 'lng': 120.988239},
                {'lat': 14.592472, 'lng': 120.987129},
                {'lat': 14.593764, 'lng': 120.985286},
                {'lat': 14.596382, 'lng':120.983288},
                {'lat': 14.5977, 'lng': 120.9831}
            ]
        },
        {
            id: 2,
            plateNumber: generateRandomPlateNumber(),
            driverName: generateRandomDriverName(),
            capacity: generateRandomCapacity(),
            routeName: 'Punta-Quiapo',
            routeColor: '#0000FF',
            route: [
                {'lat': 14.585802, 'lng': 121.011084},
                {'lat': 14.586383, 'lng': 121.012381},
                {'lat': 14.587023, 'lng': 121.013234},
                {'lat': 14.587238, 'lng': 121.013948},
                {'lat': 14.587128, 'lng': 121.014309},
                {'lat': 14.587356, 'lng': 121.014725},
                {'lat': 14.587697, 'lng': 121.015830},
                {'lat': 14.587558, 'lng': 121.016139},
                {'lat': 14.587546, 'lng': 121.017678},
                {'lat': 14.587567, 'lng': 121.019645},
                {'lat': 14.587504, 'lng': 121.020328},
                {'lat': 14.587323, 'lng': 121.020776},
                {'lat': 14.589021, 'lng': 121.022425},
                {'lat': 14.590180, 'lng': 121.023781},
                {'lat': 14.591805, 'lng': 121.025858},
                {'lat': 14.593698, 'lng': 121.026965},
                {'lat': 14.594645, 'lng': 121.024300},
                {'lat': 14.596130, 'lng': 121.020436},
                {'lat': 14.595902, 'lng': 121.019916},
                {'lat': 14.597661, 'lng': 121.017623},
                {'lat': 14.597339, 'lng': 121.015964},
                {'lat': 14.597574, 'lng': 121.015540},
                {'lat': 14.600601, 'lng': 121.013482},
                {'lat': 14.602424, 'lng': 121.011635},
                {'lat': 14.601235, 'lng': 121.000645},
                {'lat': 14.601080, 'lng': 120.997996},
                {'lat': 14.600483, 'lng': 120.996119},
                {'lat': 14.601229, 'lng': 120.994140},
                {'lat': 14.601585, 'lng': 120.992512},
                {'lat': 14.600458, 'lng': 120.991087},
                {'lat': 14.600566, 'lng': 120.991205},
                {'lat': 14.599144, 'lng': 120.990271},
                {'lat': 14.599352, 'lng': 120.989687},
                {'lat': 14.599284, 'lng': 120.989306},
                {'lat': 14.599486, 'lng': 120.988810},
                {'lat': 14.599042, 'lng': 120.987940},
                {'lat': 14.598231, 'lng': 120.985832},
                {'lat': 14.597868, 'lng': 120.984886},
                {'lat': 14.597895960834517,'lng': 120.98467323114842}
            ]
        }
    ];
    
    // Set up with fallback data
    setupVehicles(fallbackVehicles);
}

function generateRandomPlateNumber() {
    const letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    const numbers = '0123456789';
    const randomLetter = letters.charAt(Math.floor(Math.random() * letters.length));
    const randomNumbers = Math.floor(Math.random() * 1000);
    return `${randomLetter}${randomNumbers}`;
}

function generateRandomDriverName() {
    const firstNames = ['Juan', 'Pedro', 'Ricardo', 'Manuel', 'Carlo', 'Eduardo', 'Francisco', 'Jose'];
    const lastNames = ['Santos', 'Reyes', 'Cruz', 'Garcia', 'Mendoza', 'Dela Cruz', 'Bautista', 'Gonzales'];
    const randomFirstName = firstNames[Math.floor(Math.random() * firstNames.length)];
    const randomLastName = lastNames[Math.floor(Math.random() * lastNames.length)];
    return `${randomFirstName} ${randomLastName}`;
}

function generateRandomCapacity() {
    return Math.floor(Math.random() * (22 - 16 + 1)) + 16;
}

function animateMarkerTo(marker, newPosition, duration) {
    const startPosition = marker.getPosition();
    const startLat = startPosition.lat();
    const startLng = startPosition.lng();
    const latDiff = newPosition.lat - startLat;
    const lngDiff = newPosition.lng - startLng;
    const startTime = Date.now();
    
    const animate = () => {
        const elapsed = Date.now() - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Easing function for smooth movement (ease-out)
        const easeProgress = 1 - Math.pow(1 - progress, 3);
        
        const currentPosition = {
            lat: startLat + latDiff * easeProgress,
            lng: startLng + lngDiff * easeProgress
        };
        
        marker.setPosition(currentPosition);
        
        if (progress < 1) {
            requestAnimationFrame(animate);
        }
    };
    
    requestAnimationFrame(animate);
}

function seeVehicleInfo(index) {
    if (!vehicleMarkers[index] || !vehicleInfo[index]) return;
    
    // Close any open info windows
    if (vehicleInfoWindow) {
        vehicleInfoWindow.close();
    }
    
    // Set content and open new info window
    vehicleInfoWindow.setContent(vehicleInfo[index]);
    vehicleInfoWindow.open(map, vehicleMarkers[index]);
    
    // Highlight selected vehicle
    vehicleMarkers.forEach((marker, i) => {
        if (i === index) {
            // Highlight the selected marker
            marker.setIcon({
                url: 'https://maps.google.com/mapfiles/kml/shapes/bus.png',
                scaledSize: new google.maps.Size(40, 40), 
                anchor: new google.maps.Point(20, 20)
            });
            
            // Add a visible highlight effect
            const highlightCircle = new google.maps.Circle({
                map: map,
                center: marker.getPosition(),
                radius: 50,
                fillColor: '#4285F4',
                fillOpacity: 0.3,
                strokeColor: '#4285F4',
                strokeWeight: 2,
                strokeOpacity: 0.8
            });
            
            // Remove highlight effect after 2 seconds
            setTimeout(() => {
                highlightCircle.setMap(null);
            }, 2000);
            
            // Pan to the vehicle
            map.panTo(marker.getPosition());
            
            // Zoom in slightly
            if (map.getZoom() < 15) {
                map.setZoom(15);
            }
        } else {
            // Reset other markers
            marker.setIcon({
                url: 'https://maps.google.com/mapfiles/kml/shapes/bus.png',
                scaledSize: new google.maps.Size(32, 32),
                anchor: new google.maps.Point(16, 16)
            });
        }
    });
    
    // Set selected vehicle ID
    selectedVehicleId = index;
}

function viewRoute() {
    // If a vehicle is selected, focus on its route
    if (selectedVehicleId !== null && vehicleMarkers[selectedVehicleId]) {
        map.panTo(vehicleMarkers[selectedVehicleId].getPosition());
        
        // Adjust zoom to show more of the route
        map.setZoom(14);
        
        // Highlight the route
        polylines.forEach((polyline, index) => {
            if (index === selectedVehicleId) {
                polyline.setOptions({
                    strokeWeight: 6,
                    strokeOpacity: 1.0
                });
            } else {
                polyline.setOptions({
                    strokeWeight: 3,
                    strokeOpacity: 0.5
                });
            }
        });
    } else {
        // No vehicle selected, show overview of all routes
        // Find bounds that include all routes
        const bounds = new google.maps.LatLngBounds();
        
        vehicleRoutes.forEach(route => {
            route.forEach(point => {
                bounds.extend(new google.maps.LatLng(point.lat, point.lng));
            });
        });
        
        map.fitBounds(bounds);
        
        // Reset all route styles
        polylines.forEach(polyline => {
            polyline.setOptions({
                strokeWeight: 4,
                strokeOpacity: 0.7
            });
        });
    }
}

function payFare(vehicleId = null) {
    // If vehicleId is not provided, use the selected vehicle
    const id = vehicleId !== null ? vehicleId : selectedVehicleId;
    
    if (id === null) {
        alert("Please select a vehicle first by clicking on it");
        return;
    }
    
    // In a real application, you would fetch the standard fare for this route
    const standardFare = (Math.floor(Math.random() * 3) + 1) * 5; // Random fare between 5 and 15 pesos
    
    const fareAmount = prompt(`Enter fare amount for ${vehicleAnimations[id].vehicle.routeName} (Standard: ₱${standardFare}):`);
    
    if (fareAmount) {
        // In a real application, you would make an API call to process the payment
        const paymentAmount = parseFloat(fareAmount);
        
        if (isNaN(paymentAmount) || paymentAmount <= 0) {
            alert("Please enter a valid amount");
            return;
        }
        
        // Show payment processing UI feedback
        const loadingOverlay = document.createElement("div");
        loadingOverlay.style.position = "fixed";
        loadingOverlay.style.top = "0";
        loadingOverlay.style.left = "0";
        loadingOverlay.style.width = "100%";
        loadingOverlay.style.height = "100%";
        loadingOverlay.style.backgroundColor = "rgba(0,0,0,0.5)";
        loadingOverlay.style.display = "flex";
        loadingOverlay.style.justifyContent = "center";
        loadingOverlay.style.alignItems = "center";
        loadingOverlay.style.zIndex = "1000";
        loadingOverlay.innerHTML = `<div style="background:white;padding:20px;border-radius:10px;text-align:center;">
            <p>Processing payment...</p>
            <div style="width:50px;height:50px;border:5px solid #f3f3f3;border-top:5px solid #3498db;border-radius:50%;animation:spin 1s linear infinite;margin:10px auto;"></div>
            <style>@keyframes spin{0%{transform:rotate(0deg)}100%{transform:rotate(360deg)}}</style>
        </div>`;
        
        document.body.appendChild(loadingOverlay);
        
        // Simulate API call with a timeout
        setTimeout(() => {
            document.body.removeChild(loadingOverlay);
            
            // Here you would call your backend API
            // fetch('/api/pay-fare/', {
            //     method: 'POST',
            //     headers: { 'Content-Type': 'application/json' },
            //     body: JSON.stringify({
            //         amount: paymentAmount,
            //         vehicle_id: vehicleAnimations[id].vehicle.id
            //     })
            // })
            
            // Show confirmation dialog
            alert(`Payment successful!\nFare Amount: ₱${paymentAmount.toFixed(2)}\nRoute: ${vehicleAnimations[id].vehicle.routeName}\nThank you for your payment!`);
            
            // Add a payment animation to the vehicle
            const paymentIndicator = new google.maps.Marker({
                position: vehicleMarkers[id].getPosition(),
                map: map,
                icon: {
                    path: google.maps.SymbolPath.CIRCLE,
                    scale: 10,
                    fillColor: "#4CAF50",
                    fillOpacity: 1,
                    strokeColor: "#FFFFFF",
                    strokeWeight: 2
                },
                optimized: true,
                zIndex: 1000
            });
            
            // Animate the payment indicator
            let opacity = 1.0;
            const fadeInterval = setInterval(() => {
                opacity -= 0.05;
                paymentIndicator.setOpacity(opacity);
                
                if (opacity <= 0) {
                    clearInterval(fadeInterval);
                    paymentIndicator.setMap(null);
                }
            }, 50);
        }, 1500);
    }
}