// SOS Center Interactivity, Live Crisis Timer, and Geolocation Services

function fetchGpsLocation(isManual = false) {
  const latField = document.getElementById("sos-lat");
  const lngField = document.getElementById("sos-lng");
  const locationStatus = document.getElementById("sos-location-status");
  const detectBtn = document.getElementById("btn-detect-gps");

  if (!navigator.geolocation) {
    if (locationStatus) {
      locationStatus.textContent = "Geolocation is not supported by your browser. Please enter area manually.";
    }
    return;
  }

  if (locationStatus) {
    locationStatus.innerHTML = '<span style="color: var(--color-primary);">⏳ Acquiring precise GPS coordinates...</span>';
  }
  if (detectBtn) {
    detectBtn.disabled = true;
    detectBtn.textContent = "📍 Detecting...";
  }

  navigator.geolocation.getCurrentPosition(
    (position) => {
      const lat = position.coords.latitude;
      const lng = position.coords.longitude;
      const accuracy = Math.round(position.coords.accuracy || 0);

      if (latField) latField.value = lat;
      if (lngField) lngField.value = lng;

      if (locationStatus) {
        locationStatus.innerHTML = `<span style="color: var(--color-forest-mint); font-weight: 600;">✓ GPS Captured: ${lat.toFixed(5)}, ${lng.toFixed(5)} (±${accuracy}m accuracy)</span>`;
      }
      if (detectBtn) {
        detectBtn.disabled = false;
        detectBtn.textContent = "✓ Location Updated";
        setTimeout(() => { detectBtn.textContent = "📍 Refresh Location"; }, 3000);
      }
    },
    (error) => {
      let msg = "Location unavailable. Please specify landmark manually.";
      if (error.code === error.PERMISSION_DENIED) {
        msg = "Location permission denied. Please allow location access or type area manually.";
      } else if (error.code === error.TIMEOUT) {
        msg = "GPS request timed out. Please retry or enter area manually.";
      }
      if (locationStatus) {
        locationStatus.innerHTML = `<span style="color: var(--color-secondary-text);">${msg}</span>`;
      }
      if (detectBtn) {
        detectBtn.disabled = false;
        detectBtn.textContent = "📍 Retry GPS";
      }
    },
    { timeout: 10000, enableHighAccuracy: true, maximumAge: 0 }
  );
}

document.addEventListener("DOMContentLoaded", () => {
  const latField = document.getElementById("sos-lat");
  const lngField = document.getElementById("sos-lng");
  const detectBtn = document.getElementById("btn-detect-gps");

  // Initial GPS detection on SOS trigger views
  if (latField && lngField) {
    fetchGpsLocation(false);
  }

  // Manual GPS detection button listener
  if (detectBtn) {
    detectBtn.addEventListener("click", (e) => {
      e.preventDefault();
      fetchGpsLocation(true);
    });
  }

  // Live Active SOS Elapsed Timer
  const timerEl = document.getElementById("sos-live-timer");
  if (timerEl) {
    const createdAtStr = timerEl.getAttribute("data-created-at");
    if (createdAtStr) {
      const startTime = new Date(createdAtStr).getTime();
      const updateTimer = () => {
        const now = Date.now();
        const diffMs = Math.max(0, now - startTime);
        const totalSecs = Math.floor(diffMs / 1000);
        const hours = String(Math.floor(totalSecs / 3600)).padStart(2, "0");
        const minutes = String(Math.floor((totalSecs % 3600) / 60)).padStart(2, "0");
        const seconds = String(totalSecs % 60).padStart(2, "0");
        timerEl.textContent = `⏱️ Active: ${hours}:${minutes}:${seconds}`;
      };

      updateTimer();
      setInterval(updateTimer, 1000);
    }
  }

  // One-Click GPS Coordinates Copy
  const copyBtn = document.getElementById("btn-copy-coords");
  const copyFeedback = document.getElementById("copy-coords-feedback");
  if (copyBtn) {
    copyBtn.addEventListener("click", () => {
      const coords = copyBtn.getAttribute("data-coords");
      if (coords && navigator.clipboard) {
        navigator.clipboard.writeText(coords).then(() => {
          if (copyFeedback) {
            copyFeedback.style.display = "inline";
            setTimeout(() => { copyFeedback.style.display = "none"; }, 3000);
          }
        }).catch(err => {
          console.error("Failed to copy coordinates:", err);
        });
      }
    });
  }
});
