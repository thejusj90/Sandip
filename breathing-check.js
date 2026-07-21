/* ==========================================================================
   Sandip Jadhav — breathing-check.js
   Breathing Check funnel: 8 questions -> email gate -> result reveal.

   EDIT ZONE: questions, answers, scoring and result copy are grouped in
   the CONFIG object below so they can be updated without touching the
   flow logic underneath.
   ========================================================================== */

(function () {
  "use strict";

  /* ------------------------------------------------------------------
     CONFIG — safe to edit
  ------------------------------------------------------------------ */
  const CONFIG = {
    questions: [
      "Do you often feel the need to take a bigger or deeper breath?",
      "Do you frequently sigh without intentionally doing so?",
      "Do you often breathe through your mouth during the day?",
      "Do you wake up with a dry mouth?",
      "Does your breathing noticeably change when you feel stressed?",
      "Do you mainly notice movement in your upper chest when breathing?",
      "Do you sometimes feel unable to take a satisfying breath?",
      "Do you often become consciously aware of your breathing?"
    ],

    // Answer labels shown for every question, left to right.
    answers: [
      { label: "Rarely", value: 0 },
      { label: "Sometimes", value: 1 },
      { label: "Often", value: 2 }
    ],

    // Score ranges are inclusive. Edit thresholds here only.
    resultBands: [
      {
        min: 0,
        max: 4,
        tier: "low",
        title: "Few noticeable breathing habits",
        body:
          "Based on your answers, you don't notice many of the everyday signs people often associate with unhelpful breathing patterns. That doesn't rule anything out on its own \u2014 but it's a reasonable starting point. Understanding what a well-regulated breathing pattern actually looks like can still be worth exploring."
      },
      {
        min: 5,
        max: 9,
        tier: "mid",
        title: "Some breathing patterns worth noticing",
        body:
          "Your answers point to a few everyday habits \u2014 like sighing, mouth breathing or upper-chest breathing \u2014 that are common but often go unnoticed. On their own, none of these confirm anything. Together, they're often the kind of pattern Sandip works with people to understand more closely."
      },
      {
        min: 10,
        max: 16,
        tier: "high",
        title: "Your breathing pattern deserves a closer look",
        body:
          "Several of your answers reflect signs that are frequently associated with an established breathing pattern \u2014 the kind that tends to run in the background of someone's day without them noticing it. A closer, personalised look would likely be useful."
      }
    ],

    disclaimer:
      "The Breathing Check is an educational self-reflection tool and is not a medical diagnosis.",

    // Replace with a real endpoint (Formspree, serverless function, etc.)
    // before going live. Never place secret API keys in this file —
    // this is static, public, client-side JavaScript.
    leadEndpoint: "https://example.com/REPLACE-WITH-LEAD-ENDPOINT",

    consultationUrl: "book.html",
    pillarUrl: "breathing-pattern-correction.html"
  };

  /* ------------------------------------------------------------------
     STATE
  ------------------------------------------------------------------ */
  const state = {
    currentStep: 0, // 0 = intro, 1..8 = questions, 9 = email gate, 10 = result
    answers: new Array(CONFIG.questions.length).fill(null),
    submitted: false
  };

  const totalQuestionSteps = CONFIG.questions.length;
  const EMAIL_STEP = totalQuestionSteps + 1;
  const RESULT_STEP = totalQuestionSteps + 2;

  /* ------------------------------------------------------------------
     DOM refs (populated on init)
  ------------------------------------------------------------------ */
  let root, progressFill, progressLabel, panel;

  function qs(sel, ctx) { return (ctx || document).querySelector(sel); }
  function qsa(sel, ctx) { return Array.from((ctx || document).querySelectorAll(sel)); }

  /* ------------------------------------------------------------------
     Build question steps dynamically into the panel
  ------------------------------------------------------------------ */
  function buildQuestionSteps() {
    const container = qs("#quiz-questions");
    if (!container) return;

    CONFIG.questions.forEach(function (questionText, index) {
      const step = document.createElement("div");
      step.className = "quiz-step";
      step.setAttribute("data-step", String(index + 1));
      step.setAttribute("role", "group");
      step.setAttribute("aria-label", "Question " + (index + 1) + " of " + totalQuestionSteps);

      const num = document.createElement("div");
      num.className = "quiz-question-num";
      num.textContent = "Question " + (index + 1) + " of " + totalQuestionSteps;

      const text = document.createElement("div");
      text.className = "quiz-question-text";
      text.textContent = questionText;

      const options = document.createElement("div");
      options.className = "quiz-options";
      options.setAttribute("role", "radiogroup");

      CONFIG.answers.forEach(function (answer) {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "quiz-option";
        btn.setAttribute("role", "radio");
        btn.setAttribute("aria-pressed", "false");
        btn.dataset.value = String(answer.value);
        btn.dataset.question = String(index);

        const label = document.createElement("span");
        label.textContent = answer.label;
        const dot = document.createElement("span");
        dot.className = "dot";
        dot.setAttribute("aria-hidden", "true");

        btn.appendChild(label);
        btn.appendChild(dot);
        btn.addEventListener("click", function () {
          selectAnswer(index, answer.value, btn, options);
        });

        options.appendChild(btn);
      });

      const nav = document.createElement("div");
      nav.className = "quiz-nav";
      const back = document.createElement("button");
      back.type = "button";
      back.className = "btn-back";
      back.textContent = "\u2190 Back";
      back.addEventListener("click", function () { goToStep(state.currentStep - 1); });
      nav.appendChild(back);

      step.appendChild(num);
      step.appendChild(text);
      step.appendChild(options);
      step.appendChild(nav);
      container.appendChild(step);
    });
  }

  function selectAnswer(questionIndex, value, btnEl, optionsContainer) {
    state.answers[questionIndex] = value;

    qsa(".quiz-option", optionsContainer).forEach(function (opt) {
      opt.setAttribute("aria-pressed", "false");
    });
    btnEl.setAttribute("aria-pressed", "true");

    // Auto-advance after a short pause so the selection is visible.
    window.setTimeout(function () {
      goToStep(state.currentStep + 1);
    }, 260);
  }

  /* ------------------------------------------------------------------
     Step navigation
  ------------------------------------------------------------------ */
  function goToStep(stepIndex) {
    const maxStep = RESULT_STEP;
    if (stepIndex < 0) stepIndex = 0;
    if (stepIndex > maxStep) stepIndex = maxStep;

    // Guard: cannot jump into the email gate without all questions answered.
    if (stepIndex === EMAIL_STEP && state.answers.some(function (a) { return a === null; })) {
      return;
    }

    state.currentStep = stepIndex;
    renderStep();
  }

  function renderStep() {
    qsa(".quiz-step", panel).forEach(function (step) {
      const stepNum = step.getAttribute("data-step");
      const isActive =
        (stepNum === "intro" && state.currentStep === 0) ||
        (stepNum === String(state.currentStep)) ||
        (stepNum === "email" && state.currentStep === EMAIL_STEP) ||
        (stepNum === "result" && state.currentStep === RESULT_STEP);
      step.classList.toggle("active", isActive);
    });

    updateProgress();
    window.scrollTo({ top: root.offsetTop - 100, behavior: "smooth" });
  }

  function updateProgress() {
    if (!progressFill || !progressLabel) return;
    if (state.currentStep === 0) {
      progressFill.style.width = "0%";
      progressLabel.textContent = "Start";
      return;
    }
    if (state.currentStep >= 1 && state.currentStep <= totalQuestionSteps) {
      const pct = Math.round((state.currentStep / (totalQuestionSteps + 1)) * 100);
      progressFill.style.width = pct + "%";
      progressLabel.textContent = state.currentStep + " / " + totalQuestionSteps;
      return;
    }
    if (state.currentStep === EMAIL_STEP) {
      progressFill.style.width = "90%";
      progressLabel.textContent = "Almost done";
      return;
    }
    progressFill.style.width = "100%";
    progressLabel.textContent = "Complete";
  }

  /* ------------------------------------------------------------------
     Scoring
  ------------------------------------------------------------------ */
  function getScore() {
    return state.answers.reduce(function (sum, val) { return sum + (val || 0); }, 0);
  }

  function getResultBand(score) {
    return CONFIG.resultBands.find(function (band) {
      return score >= band.min && score <= band.max;
    }) || CONFIG.resultBands[CONFIG.resultBands.length - 1];
  }

  /* ------------------------------------------------------------------
     Email gate submission
  ------------------------------------------------------------------ */
  function initEmailForm() {
    const form = qs("#breathing-check-form");
    if (!form) return;

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (state.submitted) return;

      const firstName = qs("#bc-firstname", form).value.trim();
      const email = qs("#bc-email", form).value.trim();
      const phone = qs("#bc-phone", form) ? qs("#bc-phone", form).value.trim() : "";
      const consent = qs("#bc-consent", form).checked;

      let hasError = false;
      toggleError("#bc-firstname-error", firstName.length === 0);
      toggleError("#bc-email-error", !isValidEmail(email));
      toggleError("#bc-consent-error", !consent);
      hasError = firstName.length === 0 || !isValidEmail(email) || !consent;
      if (hasError) return;

      state.submitted = true;
      const submitBtn = qs("button[type='submit']", form);
      if (submitBtn) { submitBtn.disabled = true; submitBtn.textContent = "Unlocking your result\u2026"; }

      const score = getScore();
      const band = getResultBand(score);

      const params = new URLSearchParams(window.location.search);
      const lead = {
        firstName: firstName,
        email: email,
        phone: phone,
        score: score,
        resultCategory: band.title,
        answers: state.answers,
        source: "breathing-check",
        utm_source: params.get("utm_source") || "",
        utm_medium: params.get("utm_medium") || "",
        utm_campaign: params.get("utm_campaign") || "",
        timestamp: new Date().toISOString()
      };

      window.SJ_trackEvent && window.SJ_trackEvent("breathing_check_email_submit", {
        resultCategory: band.title
      });

      submitLead(lead)
        .catch(function (err) {
          // Fail open: still reveal the result to the user even if the
          // lead endpoint is unavailable, but surface it in console.
          console.warn("Lead submission failed:", err);
        })
        .finally(function () {
          renderResult(score, band, firstName);
          goToStep(RESULT_STEP);
          window.SJ_trackEvent && window.SJ_trackEvent("breathing_check_complete", {
            score: score,
            resultCategory: band.title
          });
        });
    });
  }

  function isValidEmail(value) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
  }

  function toggleError(selector, show) {
    const el = qs(selector);
    if (!el) return;
    el.classList.toggle("show", !!show);
  }

  /* ------------------------------------------------------------------
     Lead submission — placeholder endpoint.
     Swap CONFIG.leadEndpoint for a real Formspree / serverless /
     Brevo / MailerLite / Supabase endpoint. Never put secret keys here.
  ------------------------------------------------------------------ */
  function submitLead(lead) {
    if (!CONFIG.leadEndpoint || CONFIG.leadEndpoint.indexOf("example.com") !== -1) {
      console.log("[lead:stub] No live endpoint configured. Lead payload:", lead);
      return Promise.resolve({ stub: true });
    }
    return fetch(CONFIG.leadEndpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(lead)
    });
  }

  /* ------------------------------------------------------------------
     Result rendering
  ------------------------------------------------------------------ */
  function renderResult(score, band, firstName) {
    const maxScore = totalQuestionSteps * 2;
    qs("#result-badge").className = "result-badge " + band.tier;
    qs("#result-badge").textContent = band.title;
    qs("#result-score").innerHTML = score + '<span>/ ' + maxScore + '</span>';
    qs("#result-greeting").textContent = firstName ? firstName + ", here's your starting point." : "Here's your starting point.";
    qs("#result-body").textContent = band.body;
    qs("#result-disclaimer").textContent = CONFIG.disclaimer;
  }

  /* ------------------------------------------------------------------
     Consume homepage preview answers (if any) so nothing the visitor
     already answered on the homepage gets thrown away.
  ------------------------------------------------------------------ */
  function consumePreviewAnswers() {
    let stored = null;
    try {
      stored = sessionStorage.getItem("sj_bc_preview");
    } catch (e) { return; }
    if (!stored) return;
    try {
      const parsed = JSON.parse(stored);
      if (Array.isArray(parsed)) {
        parsed.forEach(function (val, i) {
          if (i < state.answers.length && (val === 0 || val === 1 || val === 2)) {
            state.answers[i] = val;
          }
        });
      }
      sessionStorage.removeItem("sj_bc_preview");
    } catch (e) { /* malformed — ignore, quiz still works standalone */ }
  }

  function markPreanswered() {
    const answered = state.answers.reduce(function (n, v) { return v !== null ? n + 1 : n; }, 0);
    if (!answered) return 0;
    // Reflect the pre-filled selections visually on those question steps.
    state.answers.forEach(function (val, index) {
      if (val === null) return;
      const step = qs('.quiz-step[data-step="' + (index + 1) + '"]');
      if (!step) return;
      qsa(".quiz-option", step).forEach(function (opt) {
        opt.setAttribute("aria-pressed", Number(opt.dataset.value) === val ? "true" : "false");
      });
    });
    return answered;
  }

  /* ------------------------------------------------------------------
     Init
  ------------------------------------------------------------------ */
  function init() {
    root = qs("#breathing-check-app");
    if (!root) return;
    panel = qs(".quiz-panel", root);
    progressFill = qs(".quiz-progress-fill", root);
    progressLabel = qs(".quiz-progress-label", root);

    buildQuestionSteps();
    consumePreviewAnswers();
    const preanswered = markPreanswered();
    initEmailForm();

    const startBtn = qs("#quiz-start-btn");
    if (startBtn) {
      startBtn.addEventListener("click", function () {
        window.SJ_trackEvent && window.SJ_trackEvent("breathing_check_start", {});
        goToStep(preanswered ? preanswered + 1 : 1);
      });
      if (preanswered) {
        startBtn.textContent = "Continue My Check \u2192";
        const introNote = document.createElement("p");
        introNote.className = "lede";
        introNote.style.marginTop = "0.75rem";
        introNote.style.fontSize = "0.85rem";
        introNote.textContent = "Your first " + preanswered + " answers carried over from the homepage.";
        startBtn.closest(".cta-row").insertAdjacentElement("beforebegin", introNote);
      }
    }

    const toEmailBtn = qs("#quiz-to-email-btn");
    if (toEmailBtn) {
      toEmailBtn.addEventListener("click", function () { goToStep(EMAIL_STEP); });
    }

    renderStep();
  }

  document.addEventListener("DOMContentLoaded", init);
})();
