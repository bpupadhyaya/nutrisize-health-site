# nutrisize-health-site

Marketing and branding website for the **Nutrisize Health** mobile app, served at
**https://nutrisize.health** via GitHub Pages (project site under `bpupadhyaya`).

## Structure

| Path | Page |
|------|------|
| `index.html` | Home — hero, stats, features, KPIs, privacy, store links |
| `about/` | About the app and EqualInformation, LLC |
| `privacy/` | Privacy policy (mirrors equalinformation.com/privacy-nutrisizehealth.html) |
| `support/` | Support contact + FAQ (store-listing support URL) |
| `disclaimer/` | Medical/educational disclaimer |
| `survey/` | User survey (embedded Google Form — see "Survey form" below) |
| `assets/` | `css/style.css`, icons (`img/`) |
| `CNAME` | `nutrisize.health` — the custom-domain binding for GitHub Pages |

Plain static HTML/CSS — no build step. Edit, commit, push to `main`; GitHub Pages deploys automatically.

## One-time setup checklist

1. **GitHub → repo Settings → Pages**: Source = `main` branch, `/ (root)`.
2. **GitHub → account Settings → Pages → Verified domains**: add `nutrisize.health`,
   copy the TXT record it gives you.
3. **GoDaddy DNS for nutrisize.health** (do NOT use GoDaddy "Domain Forwarding";
   do NOT touch the existing MX records — they carry bpupadhyaya@nutrisize.health email):

   | Type | Name | Value |
   |------|------|-------|
   | A | `@` | `185.199.108.153` |
   | A | `@` | `185.199.109.153` |
   | A | `@` | `185.199.110.153` |
   | A | `@` | `185.199.111.153` |
   | CNAME | `www` | `bpupadhyaya.github.io` |
   | TXT | `_github-pages-challenge-bpupadhyaya` | (value from step 2) |

4. Back in **repo Settings → Pages**: Custom domain = `nutrisize.health` → Save.
   Wait for the DNS check + TLS certificate (minutes to ~1 hour), then check **Enforce HTTPS**.

## Fallback property

Content lives permanently in this repo. If the `nutrisize.health` domain ever lapses,
remove the `CNAME` file (and the custom-domain setting) and the site serves again at
`bpupadhyaya.github.io/nutrisize-health-site` — a one-line recovery.

## Survey form

- **Responder URL:** https://docs.google.com/forms/d/e/1FAIpQLSfQCadgkoIfG-nIWPj9Bu2bGz2BlscbCuCdZriiuQtbRR_26A/viewform
- Embedded at https://nutrisize.health/survey via the same URL with `?embedded=true`.
- Form "Nutrisize Health — User Survey" is owned by **nutrisize.universal@gmail.com**;
  responses auto-append to the "Nutrisize Health — User Survey (Responses)" Google Sheet
  in that account's Drive (edit form / see responses from that account at forms.google.com).
- Anonymous: no sign-in required, no email collection, all questions optional.

## Related

- Existing per-app pages (store listings point here today): https://equalinformation.com
  (`privacy-nutrisizehealth.html`, `support-nutrisizehealth.html`, `release-notes-nutrisizehealth.html`)
- App Store: https://apps.apple.com/us/app/nutrisize-health/id6762168316
- Google Play: https://play.google.com/store/apps/details?id=com.nutrisize.health
