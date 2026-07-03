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
| `survey/` | User survey (Google Form embed — see comment in the file to activate) |
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

## Related

- Existing per-app pages (store listings point here today): https://equalinformation.com
  (`privacy-nutrisizehealth.html`, `support-nutrisizehealth.html`, `release-notes-nutrisizehealth.html`)
- App Store: https://apps.apple.com/us/app/nutrisize-health/id6762168316
- Google Play: https://play.google.com/store/apps/details?id=com.nutrisize.health
