// Core Application JavaScript for Women Safety Platform

document.addEventListener("DOMContentLoaded", () => {
  // Mobile Nav Toggle with Accessible Keyboard & Outside Click Handling
  const toggleBtn = document.querySelector(".mobile-toggle");
  const navLinks = document.querySelector(".nav-links");
  if (toggleBtn && navLinks) {
    toggleBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      const isOpen = navLinks.classList.toggle("open");
      toggleBtn.setAttribute("aria-expanded", isOpen ? "true" : "false");
    });

    document.addEventListener("click", (e) => {
      if (navLinks.classList.contains("open") && !navLinks.contains(e.target) && e.target !== toggleBtn) {
        navLinks.classList.remove("open");
        toggleBtn.setAttribute("aria-expanded", "false");
      }
    });

    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && navLinks.classList.contains("open")) {
        navLinks.classList.remove("open");
        toggleBtn.setAttribute("aria-expanded", "false");
      }
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

  // Show/Hide Password Toggle
  document.querySelectorAll(".btn-toggle-password").forEach(btn => {
    btn.addEventListener("click", () => {
      const targetId = btn.getAttribute("data-toggle-target");
      const input = document.getElementById(targetId);
      if (input) {
        if (input.type === "password") {
          input.type = "text";
          btn.textContent = "🙈";
          btn.setAttribute("aria-label", "Hide password");
        } else {
          input.type = "password";
          btn.textContent = "👁️";
          btn.setAttribute("aria-label", "Show password");
        }
      }
    });
  });

  // Registration Live Password Policy & Strength Meter
  const regPassword = document.getElementById("password");
  const regConfirm = document.getElementById("confirm_password");
  const strengthFill = document.getElementById("strength-fill");
  const ruleLength = document.getElementById("rule-length");
  const ruleUpper = document.getElementById("rule-upper");
  const ruleLower = document.getElementById("rule-lower");
  const ruleNumber = document.getElementById("rule-number");
  const matchStatus = document.getElementById("confirm-match-status");

  if (regPassword && strengthFill) {
    const updateStrength = () => {
      const val = regPassword.value || "";
      const hasLength = val.length >= 8;
      const hasUpper = /[A-Z]/.test(val);
      const hasLower = /[a-z]/.test(val);
      const hasNum = /[0-9]/.test(val);

      if (ruleLength) {
        ruleLength.textContent = hasLength ? "✓ Min 8 chars" : "✗ Min 8 chars";
        ruleLength.classList.toggle("valid", hasLength);
      }
      if (ruleUpper) {
        ruleUpper.textContent = hasUpper ? "✓ Uppercase" : "✗ Uppercase";
        ruleUpper.classList.toggle("valid", hasUpper);
      }
      if (ruleLower) {
        ruleLower.textContent = hasLower ? "✓ Lowercase" : "✗ Lowercase";
        ruleLower.classList.toggle("valid", hasLower);
      }
      if (ruleNumber) {
        ruleNumber.textContent = hasNum ? "✓ Number" : "✗ Number";
        ruleNumber.classList.toggle("valid", hasNum);
      }

      const score = [hasLength, hasUpper, hasLower, hasNum].filter(Boolean).length;
      strengthFill.className = "strength-fill";
      if (score === 1) strengthFill.classList.add("weak");
      else if (score === 2) strengthFill.classList.add("fair");
      else if (score === 3) strengthFill.classList.add("good");
      else if (score === 4) strengthFill.classList.add("strong");
    };

    regPassword.addEventListener("input", updateStrength);
    // Initialize if prefilled
    if (regPassword.value) updateStrength();
  }

  if (regConfirm && regPassword && matchStatus) {
    const checkMatch = () => {
      if (!regConfirm.value) {
        matchStatus.style.display = "none";
        regConfirm.classList.remove("is-valid", "is-invalid");
        return;
      }
      matchStatus.style.display = "block";
      if (regPassword.value === regConfirm.value) {
        matchStatus.textContent = "✓ Passwords match";
        matchStatus.style.color = "var(--color-forest-mint)";
        regConfirm.classList.add("is-valid");
        regConfirm.classList.remove("is-invalid");
      } else {
        matchStatus.textContent = "✗ Passwords do not match";
        matchStatus.style.color = "var(--color-muted-coral)";
        regConfirm.classList.add("is-invalid");
        regConfirm.classList.remove("is-valid");
      }
    };
    regConfirm.addEventListener("input", checkMatch);
    regPassword.addEventListener("input", checkMatch);
  }

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

  // Close modal with Escape key
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      document.querySelectorAll(".modal-backdrop.open").forEach(modal => {
        modal.classList.remove("open");
      });
    }
  });

  // Relationship Quick-Select Tags
  document.querySelectorAll(".btn-tag-pill").forEach(btn => {
    btn.addEventListener("click", () => {
      const relationInput = document.getElementById("relationship");
      if (relationInput) {
        relationInput.value = btn.getAttribute("data-relation");
        relationInput.focus();
        relationInput.dispatchEvent(new Event("input", { bubbles: true }));
      }
    });
  });

  // Client-Side Phone Number Format Live Feedback
  const phoneInput = document.getElementById("phone");
  const phoneStatus = document.getElementById("phone-format-status");
  if (phoneInput && phoneStatus) {
    const phoneRegex = /^\+?[0-9\s\-()]{7,25}$/;
    phoneInput.addEventListener("input", () => {
      const val = phoneInput.value.trim();
      if (!val) {
        phoneStatus.style.display = "none";
        phoneInput.classList.remove("is-valid", "is-invalid");
        return;
      }
      phoneStatus.style.display = "block";
      if (phoneRegex.test(val)) {
        phoneStatus.textContent = "✓ Valid phone format";
        phoneStatus.style.color = "var(--color-forest-mint)";
        phoneInput.classList.add("is-valid");
        phoneInput.classList.remove("is-invalid");
      } else {
        phoneStatus.textContent = "✗ Invalid phone format (must be 7-25 digits/symbols)";
        phoneStatus.style.color = "var(--color-muted-coral)";
        phoneInput.classList.add("is-invalid");
        phoneInput.classList.remove("is-valid");
      }
    });
  }

  // Copy Emergency Resource Details
  const copyResourceBtn = document.getElementById("btn-copy-resource-info");
  const copyResourceFeedback = document.getElementById("copy-resource-feedback");
  if (copyResourceBtn) {
    copyResourceBtn.addEventListener("click", () => {
      const text = copyResourceBtn.getAttribute("data-copy-text");
      if (text && navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
          if (copyResourceFeedback) {
            copyResourceFeedback.style.display = "inline";
            setTimeout(() => { copyResourceFeedback.style.display = "none"; }, 3000);
          }
        });
      }
    });
  }
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
