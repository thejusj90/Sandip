/* ==========================================================================
   Sandip Jadhav — main.js
   Shared site behaviour: mobile nav, FAQ accordion, footer year,
   analytics hook, CTA click tracking.
   ========================================================================== */

(function () {
  "use strict";

  /* ------------------------------------------------------------------
     Analytics — centralised event hook.
     Replace `sendAnalyticsEvent` internals with your real provider
     (GA4, Plausible, Meta Pixel, etc.) in ONE place only.
     No tracking IDs are wired up. Do not add real tracking IDs
     directly into page markup — configure them here.
  ------------------------------------------------------------------ */
  const ANALYTICS_CONFIG = {
    enabled: false, // flip to true once a real analytics provider is connected
    // providerId: "" // e.g. GA4 measurement ID — left blank intentionally
  };

  function sendAnalyticsEvent(eventName, payload) {
    payload = payload || {};
    if (!ANALYTICS_CONFIG.enabled) {
      // Development fallback — visible in console only.
      console.log("[analytics:stub]", eventName, payload);
      return;
    }
    // Example wiring for GA4, once enabled:
    // if (window.gtag) window.gtag('event', eventName, payload);
  }
  window.SJ_trackEvent = sendAnalyticsEvent;

  /* ------------------------------------------------------------------
     Mobile navigation
  ------------------------------------------------------------------ */
  function initNav() {
    const toggle = document.querySelector(".nav-toggle");
    const links = document.querySelector(".nav-links");
    if (!toggle || !links) return;

    toggle.addEventListener("click", function () {
      const isOpen = links.classList.toggle("open");
      toggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
      document.body.classList.toggle("nav-open", isOpen);
    });

    links.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () {
        links.classList.remove("open");
        toggle.setAttribute("aria-expanded", "false");
        document.body.classList.remove("nav-open");
      });
    });
  }

  /* ------------------------------------------------------------------
     FAQ accordion (accessible)
  ------------------------------------------------------------------ */
  function initFaq() {
    const items = document.querySelectorAll(".faq-item");
    items.forEach(function (item) {
      const btn = item.querySelector(".faq-question");
      const answer = item.querySelector(".faq-answer");
      if (!btn || !answer) return;

      btn.addEventListener("click", function () {
        const isOpen = item.getAttribute("data-open") === "true";
        item.setAttribute("data-open", isOpen ? "false" : "true");
        btn.setAttribute("aria-expanded", isOpen ? "false" : "true");
      });
    });
  }

  /* ------------------------------------------------------------------
     CTA click tracking — any element with [data-track] fires an event
  ------------------------------------------------------------------ */
  function initCtaTracking() {
    document.querySelectorAll("[data-track]").forEach(function (el) {
      el.addEventListener("click", function () {
        sendAnalyticsEvent(el.getAttribute("data-track"), {
          label: el.textContent.trim(),
          path: window.location.pathname
        });
      });
    });
  }

  /* ------------------------------------------------------------------
     Footer year
  ------------------------------------------------------------------ */
  function initFooterYear() {
    const el = document.querySelector("[data-year]");
    if (el) el.textContent = new Date().getFullYear();
  }

  document.addEventListener("DOMContentLoaded", function () {
    initNav();
    initFaq();
    initCtaTracking();
    initFooterYear();
  });
})();
