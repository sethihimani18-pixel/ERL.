// Use relative path instead of localhost
const API_URL = '/api';

const elements = {
    emergencyBtn: document.getElementById('emergencyBtn'),
    statusMessage: document.getElementById('statusMessage'),
    offlineMode: document.getElementById('offlineMode'),
    resultsContainer: document.getElementById('resultsContainer'),
    resourcesList: document.getElementById('resourcesList'),
    loadingSpinner: document.getElementById('loadingSpinner')
};

// Show status message
function showStatus(message, type) {
    elements.statusMessage.textContent = message;
    elements.statusMessage.className = `status-message ${type}`;
    elements.statusMessage.style.display = 'block';
}

// Hide all sections
function hideAllSections() {
    elements.offlineMode.style.display = 'none';
    elements.resultsContainer.style.display = 'none';
    elements.loadingSpinner.style.display = 'none';
    elements.statusMessage.style.display = 'none';
}

// Switch to offline mode
function activateOfflineMode(reason) {
    hideAllSections();
    showStatus(`${reason} - Switched to offline mode`, 'error');
    elements.offlineMode.style.display = 'block';
}

// Get user location
function getUserLocation() {
    return new Promise((resolve, reject) => {
        if (!navigator.geolocation) {
            reject('Geolocation not supported');
            return;
        }

        navigator.geolocation.getCurrentPosition(
            (position) => {
                resolve({
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude
                });
            },
            (error) => {
                let errorMessage;
                switch (error.code) {
                    case error.PERMISSION_DENIED:
                        errorMessage = 'Location permission denied';
                        break;
                    case error.POSITION_UNAVAILABLE:
                        errorMessage = 'Location unavailable';
                        break;
                    case error.TIMEOUT:
                        errorMessage = 'Location request timeout';
                        break;
                    default:
                        errorMessage = 'Location error';
                }
                reject(errorMessage);
            },
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 0
            }
        );
    });
}

// Fetch resources from backend
async function fetchResources(latitude, longitude) {
    const response = await fetch(`${API_URL}/resources`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            latitude,
            longitude
        })
    });

    if (!response.ok) {
        throw new Error('Server error');
    }

    return await response.json();
}

// Display resources
function displayResources(resources) {
    if (!resources || resources.length === 0) {
        elements.resourcesList.innerHTML =
            '<p style="text-align: center; color: #666;">No resources found nearby</p>';
        return;
    }

    elements.resourcesList.innerHTML = resources.map(resource => `
        <div class="resource-card">
            <h3>${resource.name}</h3>
            <p><strong>Type:</strong> ${resource.type}</p>
            <p><strong>Address:</strong> ${resource.address}</p>
            ${resource.phone ? 
                `<p><strong>Phone:</strong> 
                    <a href="tel:${resource.phone}" class="phone">
                        ${resource.phone}
                    </a>
                </p>` : ''}
            <p class="distance">📍 ${resource.distance.toFixed(2)} km away</p>
        </div>
    `).join('');
}

// Handle emergency button click
async function handleEmergency() {
    hideAllSections();
    elements.loadingSpinner.style.display = 'block';
    showStatus('Getting your location...', 'info');

    try {
        const location = await getUserLocation();
        showStatus('Location obtained. Fetching resources...', 'info');

        const data = await fetchResources(location.latitude, location.longitude);

        hideAllSections();
        showStatus(`Found ${data.resources.length} resources nearby`, 'success');
        elements.resultsContainer.style.display = 'block';
        displayResources(data.resources);

    } catch (error) {
        console.error('Error:', error);
        activateOfflineMode(error.message || error);
    }
}

// Event listener
elements.emergencyBtn.addEventListener('click', handleEmergency);

// Connectivity checks
window.addEventListener('load', () => {
    if (!navigator.onLine) {
        activateOfflineMode('No internet connection');
    }
});

window.addEventListener('offline', () => {
    activateOfflineMode('Connection lost');
});
