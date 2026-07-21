# Sandip Jadhav — Website

Static HTML/CSS/JavaScript website for Sandip Jadhav, Breathing Pattern Correction Practitioner. Built for GitHub Pages. No build step, no frameworks, no dependencies beyond a Google Fonts import.

---

## 1. What's in this repo

```
/
├── index.html                        Homepage
├── about.html                        About Sandip
├── breathing-pattern-correction.html Pillar page: what Breathing Pattern Correction is
├── consultation.html                 1:1 consultation details
├── breathing-check.html              The Breathing Check quiz funnel
├── learn.html                        Breathing Library (article index)
├── faq.html                          Full FAQ
├── contact.html                      Contact form (placeholder endpoint)
├── book.html                         Booking page (placeholder link/scheduler)
├── privacy-policy.html               Privacy policy (template — needs legal review)
├── disclaimer.html                   Medical/educational disclaimer
├── assets/
│   ├── css/styles.css                Single global stylesheet
│   ├── js/main.js                    Shared behaviour: nav, FAQ accordion, analytics hook
│   ├── js/breathing-check.js         Breathing Check quiz logic (questions, scoring, lead capture)
│   └── images/                       favicon.png and og-cover.jpg placeholders
├── robots.txt
├── sitemap.xml
└── README.md
```

---

## 2. Deploying to GitHub Pages

1. Create a new GitHub repository (or use an existing one).
2. Push the contents of this folder to the repository root (or to a `docs/` folder — either works, just match your Pages settings).
3. In the repo, go to **Settings → Pages**.
4. Under **Build and deployment**, set **Source** to "Deploy from a branch," pick your branch (e.g. `main`) and the folder (`/root` or `/docs`).
4. Save. GitHub will give you a URL like `https://your-username.github.io/your-repo/`.
5. Optional: add a custom domain under **Settings → Pages → Custom domain**, and add a `CNAME` file if GitHub doesn't create one automatically.

**Before going live**, replace every `https://example.com/` reference (canonical URLs, Open Graph URLs, sitemap.xml, robots.txt) with your real domain. A quick way:

```bash
# from the repo root, macOS/Linux
grep -rl "example.com" . | xargs sed -i '' 's/example\.com/yourdomain.com/g'
```

(On Linux, drop the `''` after `-i`.)

---

## 3. What's a placeholder right now

This is the **first production build**. The following are intentionally left as placeholders, since no real details were provided:

| Placeholder | Where | What to do |
|---|---|---|
| Sandip's photography | `index.html`, `about.html`, `breathing-pattern-correction.html` (`.placeholder-photo` blocks) | Replace the placeholder `<div>` with an `<img>` tag pointing to a real photo in `assets/images/`. |
| Credentials / bio / years of experience | `about.html` | Nothing has been invented. Add only verified, factual details. |
| Booking link / scheduler | `book.html` | Replace the placeholder button with a real Calendly/Cal.com embed or direct booking URL. |
| Contact form endpoint | `contact.html` | Currently just shows an alert. Wire it to Formspree, a serverless function, or your provider of choice. |
| Breathing Check lead endpoint | `assets/js/breathing-check.js` → `CONFIG.leadEndpoint` | Currently a placeholder URL. Point it to a real endpoint (see §5). |
| Analytics tracking IDs | `assets/js/main.js` → `ANALYTICS_CONFIG` | Currently disabled (logs to console only). Add a real provider and set `enabled: true`. |
| Favicon / OG image | `assets/images/favicon.png`, `assets/images/og-cover.jpg` | Simple generated placeholders. Swap for real brand assets. |
| Legal copy | `privacy-policy.html`, `disclaimer.html` | Template language. Have a qualified professional review before publishing. |
| Article content | `learn.html` and article cards site-wide | Card shells with placeholder copy and no linked article pages yet. Build out real articles using the template in §6. |

No testimonials, medical claims, success rates, or qualifications have been invented anywhere on the site, per the brand guardrails.

---

## 4. Editing the design system

Everything flows from CSS custom properties at the top of `assets/css/styles.css`:

```css
:root {
  --bg-dark: #0B0F14;
  --bg-dark-secondary: #111820;
  --blue-deep: #173B67;
  --blue-accent: #6EA8E5;
  --blue-muted: #AFC7DF;
  --off-white: #F4F2EC;
  --text-light: #F5F5F2;
  --text-muted: #B6BCC4;
  --text-dark: #151A1F;
}
```

Change a value here and it updates everywhere. Typography is set the same way (`--font-serif` for headings, `--font-sans` for everything else). There is one stylesheet for the whole site — do not create page-specific CSS files unless something genuinely can't be handled with a utility class or a new component block.

---

## 5. The Breathing Check funnel

Flow: landing → 8 questions → email gate → immediate result reveal → lead sent to your endpoint.

- **Questions, answers and scoring** live in `assets/js/breathing-check.js`, inside the `CONFIG` object at the top of the file. Edit `CONFIG.questions`, `CONFIG.answers`, or `CONFIG.resultBands` directly — the quiz UI rebuilds itself from this config, so you don't need to touch any HTML in `breathing-check.html` to change question wording or scoring thresholds.
- **Email is only requested after all 8 questions are answered**, per the required flow. The result is revealed immediately after submission — the page does not wait on email delivery.
- **Lead payload shape** sent to `CONFIG.leadEndpoint`:

```json
{
  "firstName": "",
  "email": "",
  "phone": "",
  "score": 0,
  "resultCategory": "",
  "answers": [],
  "source": "breathing-check",
  "utm_source": "",
  "utm_medium": "",
  "utm_campaign": "",
  "timestamp": ""
}
```

- **To connect a real backend**, set `CONFIG.leadEndpoint` in `breathing-check.js` to a POST endpoint from one of:
  - Formspree (simplest — no backend code needed)
  - Brevo or MailerLite (embed/API)
  - Supabase or Firebase (serverless-friendly)
  - Your own serverless function (Cloudflare Workers, Vercel, Netlify Functions)

  **Never put a secret API key directly in `breathing-check.js` or any other front-end file** — this is a static site and everything in it is publicly readable. If a provider requires a secret key, put the key server-side (in a serverless function) and call that function from the front end instead.

- **Actual email delivery and the 4-email automation sequence** (immediate result email, Day 2, Day 5, Day 8) should be configured in your email platform, not in this codebase — the site only submits the lead; the platform handles scheduling and sending.

---

## 6. Adding a new article to the Breathing Library

There isn't a CMS here — each article should be a new static HTML file (e.g. `mouth-breathing.html`) built from the same header/footer shell as the other pages, using this front matter set as guidance:

- title, meta title, meta description, canonical URL
- one clear `<h1>`
- author, publication date, updated date, reading time (display as plain text near the top)
- category (matches one of: Breathing Habits, Breathing Questions, Breathing and Everyday Life, Better Breathing)
- featured image
- body content inside `.prose`
- an FAQ section if relevant (use the `.faq-item` markup from `faq.html`)
- related articles
- a Breathing Check CTA and a consultation CTA near the end

Add `Article` / `BlogPosting` structured data (JSON-LD) in the `<head>`, following the pattern already used for `Person`, `WebSite`, and `BreadcrumbList` in the existing pages. Then link the new article from its `.article-card` on `learn.html`, `index.html`, and any relevant pillar/habit pages, and add its URL to `sitemap.xml`.

---

## 7. Analytics events

Hooks are already wired into the markup via `data-track` attributes and fire through `window.SJ_trackEvent()` in `assets/js/main.js`. Events currently firing:

```
breathing_check_start
breathing_check_complete
breathing_check_email_submit
consultation_cta_click
booking_click
contact_submit
```

To activate real analytics, set `ANALYTICS_CONFIG.enabled = true` in `main.js` and wire the provider call inside `sendAnalyticsEvent()`. Until then, events log to the browser console only — nothing is sent anywhere.

---

## 8. Working on the site going forward

1. Inspect the existing code before changing it.
2. Reuse the existing design system and component classes (`.card-grid`, `.article-card`, `.info-row`, `.process-track`, etc.) rather than inventing new patterns for the same kind of content.
3. Test any layout change at 320px, 375px, 390px, 430px, 768px, 1024px, and 1440px widths.
4. Keep one `<h1>` per page and check that meta title/description stay unique.
5. Don't invent credentials, testimonials, medical claims, or success rates — use `[Placeholder: ...]` markers instead, matching the convention already used throughout.
