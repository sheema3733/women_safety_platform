// SOS Center Interactivity and Emergency Geolocation

document.addEventListener("DOMContentLoaded", () => {
  const triggerModal = document.getElementById("sos-trigger-modal");
  const latField = document.getElementById("sos-lat");
  const lngField = document.getElementById("sos-lng");
  const locationStatus = document.getElementById("sos-location-status");

  // Attempt to fetch GPS coordinates when on SOS trigger pages
  if (latField && lngField && navigator.geolocation) {
    if (locationStatus) locationStatus.textContent = "Acquiring GPS location...";
    navigator.geolocation.getCurrentPosition(
      (position) => {
        latField.value = position.coords.latitude;
        lngField.value = position.coords.longitude;
        if (locationStatus) {
          locationStatus.innerHTML = `<span style="color: var(--color-forest-mint);">✓ Location captured (${position.coords.latitude.toFixed(4)}, ${position.coords.longitude.toFixed(4)})</span>`;
        }
      },
      (error) => {
        if (locationStatus) {
          locationStatus.textContent = "Location permission denied or unavailable. General area can be entered manually.";
        }
      },
      { timeout: 8000, enableHighAccuracy: true }
    );
  }
});
