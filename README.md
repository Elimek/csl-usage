# DataGuard

**Know exactly when you run out.**

A data usage dashboard that tells you not how much you've used, but **how much you have left** — and when it ends.

---

## What It Does

- **Scrapes** CSL portal every 6 hours
- **Predicts** days until data exhaustion
- **Warns** before you hit zero

## Stack

| Layer | Tech |
|-------|------|
| Frontend | HTML + CSS + JS (single file, zero deps) |
| Scraper | Python + Playwright |
| Scheduler | GitHub Actions |
| Hosting | GitHub Pages (free, forever) |

No React. No build step. No maintenance.

## Deploy

```bash
# 1. Fork this repo
# 2. Add secrets: CSL_USER, CSL_PASS
# 3. Enable GitHub Pages from /docs
# 4. Trigger workflow once
```

Live at `https://YOUR_NAME.github.io/csl-usage`

## Why This Exists

Most data apps tell you consumption.  
**DataGuard tells you scarcity.**

Scarcity drives action. Consumption drives nothing.

---

MIT
