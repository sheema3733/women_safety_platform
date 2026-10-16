// Core Application JavaScript for Women Safety Platform

document.addEventListener("DOMContentLoaded", () => {
  // Mobile Nav Toggle
  const toggleBtn = document.querySelector(".mobile-toggle");
  const navLinks = document.querySelector(".nav-links");
  if (toggleBtn && navLinks) {
    toggleBtn.addEventListener("click", () => {
      navLinks.classList.toggle("open");
    });
  }

  // Auto-dismiss Flash Alerts after 6 seconds
  const alerts = document.querySelectorAll(".alert");
  alerts.forEach(alert => {
    setTimeout(() => {
      alert.style.transition = "opacity 0.5s ease";
      alert.style.opacity = "0";
      setTimeout(() => alert.remove(), 500);
    }, 6000);
  });

  // Modal Open/Close Event Handlers
  document.querySelectorAll("[data-modal-target]").forEach(btn => {
    btn.addEventListener("click", (e) => {
      e.preventDefault();
      const targetId = btn.getAttribute("data-modal-target");
      openModal(targetId);
    });
  });

  document.querySelectorAll(".modal-close, [data-modal-close]").forEach(btn => {
    btn.addEventListener("click", () => {
      const modal = btn.closest(".modal-backdrop");
      if (modal) modal.classList.remove("open");
    });
  });

  // Close modal when clicking backdrop
  document.querySelectorAll(".modal-backdrop").forEach(backdrop => {
    backdrop.addEventListener("click", (e) => {
      if (e.target === backdrop) backdrop.classList.remove("open");
    });
  });
});

function openModal(id) {
  const el = document.getElementById(id);
  if (el) el.classList.add("open");
}

function closeModal(id) {
  const el = document.getElementById(id);
  if (el) el.classList.remove("open");
}

// CSRF token retrieval helper
function getCsrfToken() {
  const meta = document.querySelector('input[name="csrf_token"]');
  return meta ? meta.value : "";
}

// Checklist Item Toggle Handler
function toggleChecklistItem(itemId, checkbox) {
  const isCompleted = checkbox.checked;
  const itemRow = document.getElementById(`checklist-item-${itemId}`);
  const csrfToken = getCsrfToken();

  fetch(`/checklist/toggle/${itemId}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRF-Token": csrfToken
    },
    body: JSON.stringify({ is_completed: isCompleted, csrf_token: csrfToken })
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      if (itemRow) {
        if (isCompleted) {
          itemRow.classList.add("completed");
        } else {
          itemRow.classList.remove("completed");
        }
      }
      // Update stats counters if present
      const statCompleted = document.getElementById("checklist-completed-count");
      const statPct = document.getElementById("checklist-pct");
      const progressFill = document.getElementById("checklist-progress-fill");
      if (statCompleted) statCompleted.textContent = data.stats.completed;
      if (statPct) statPct.textContent = `${data.stats.percentage}%`;
      if (progressFill) progressFill.style.width = `${data.stats.percentage}%`;

      // Update Readiness score display if present
      const readinessScoreNum = document.getElementById("readiness-score-val");
      if (readinessScoreNum) readinessScoreNum.textContent = `${data.readiness_score}%`;
    }
  })
  .catch(err => console.error("Error updating checklist item:", err));
}

// Mark Notification as Read
function markNotificationRead(notifId, el) {
  const csrfToken = getCsrfToken();
  fetch(`/notifications/read/${notifId}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRF-Token": csrfToken
    },
    body: JSON.stringify({ csrf_token: csrfToken })
  })
  .then(res => res.json())
  .then(data => {
    if (data.success && el) {
      el.classList.remove("unread");
      const badge = el.querySelector(".badge-unread");
      if (badge) badge.remove();
    }
  })
  .catch(err => console.error("Error marking notification:", err));
}
