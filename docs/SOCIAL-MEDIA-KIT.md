# Nutrisize Health — Social Media Kit

Everything needed to open the accounts in issue-tracker #7 (Instagram, Facebook, LinkedIn,
TikTok) plus recommended extras. Same identity everywhere: one handle, one logo, one voice.

## Identity

- **Handle (all platforms): `@nutrisizehealth`** — dots aren't allowed on TikTok/X and
  underscores read worse; one dotless handle keeps every profile URL identical. On Instagram,
  also grab `nutrisize.health` if free and let it redirect/sit reserved.
- **Display name:** `Nutrisize Health`
- **Category:** Health/Wellness app (FB: "App page"; IG: Business → "Health & wellness";
  LinkedIn: Company page → "Wellness and Fitness Services"; TikTok: Business account)
- **Link everywhere:** `https://nutrisize.health` (later: per-platform UTM, e.g. `?utm_source=instagram`)
- **Voice:** the site's voice — educational, factual, quietly confident. The site teaches; the
  app personalizes. Never salesy; numbers over adjectives (4,995 foods · 5,404 exercises ·
  201 parameters · local-first/no data collected).

## Assets (`assets/social/`)

| File | Use |
|---|---|
| `profile-1024.png` | Profile photo everywhere (crops safely to circle) |
| `facebook-cover.png` | Facebook Page cover (820×312 @2x) |
| `linkedin-banner.png` | LinkedIn company banner (1128×191 @2x) |
| `x-header.png` | X header (1500×500) |
| `youtube-banner.png` | YouTube channel art (2560×1440, safe-area centered) |

## Bios (within each platform's limit)

- **Instagram (≤150):**
  `Your health, computed 🥗 Personalized nutrition + exercise from 201 physiological parameters. Private — your data never leaves your device. ⬇️`
- **TikTok (≤80):**
  `Your health, computed 🥗 Private nutrition + fitness app. No cloud, no ads ⬇️`
- **Facebook intro (≤101):**
  `Personalized nutrition & exercise, computed on your device. Private by design.`
- **LinkedIn tagline (≤120):**
  `Local-first health app: personalized nutrition & exercise from 201 physiological parameters. Private by design.`
- **LinkedIn about:** Nutrisize Health, by EqualInformation, LLC, turns 201 physiological
  parameters, 4,995 foods, and 5,404 exercises into a personal nutrition and exercise plan —
  computed entirely on your device. No accounts, no cloud copies of your health records, no
  ads, no tracking; the App Store privacy label reads "no data collected." Free sample plans
  and the parameter reference live at nutrisize.health.
- **X (≤160):**
  `Your health, computed. Personalized nutrition + exercise from 201 physiological parameters — private, on your device. 🥗 nutrisize.health`
- **YouTube description:** LinkedIn about + link list (site, plans, parameters, App Store, Play).

## First three posts (reuse across platforms; vertical 9:16 video for TikTok/IG Reels)

1. **Intro** — "Most health apps upload your life. Nutrisize computes it — on your phone."
   30-sec app screen-recording tour ending on the privacy label. CTA: link in bio.
2. **Sample plan walk** — pick one demographic plan page, scroll the week, tap a meal, expand
   a food's nutrients. "A full week, every meal computed — free to study at nutrisize.health/plans."
3. **Know your numbers** — the 7 daily parameters from nutrisize.health/parameters as a
   carousel/short: one card per parameter with its healthy range. CTA: full list on the site.

Cadence to start: 2–3 posts/week, same content adapted per platform; recycle site content
(10 plans × 28 meals × parameter cards = months of material).

## Recommended additional platforms (priority order)

1. **YouTube (+ Shorts)** — same vertical videos as TikTok/Reels; searchable forever; channel
   art included. Handle `@nutrisizehealth`.
2. **Pinterest** — meal plans and "healthy ranges" cards are core Pinterest content; pins link
   straight to plan pages. Business account, boards per demographic.
3. **X/Twitter** — parameter-of-the-day cards; header image included.
4. **Threads** — free with the Instagram account, one extra checkbox.
5. **Reddit** — no brand page; participate honestly in r/nutrition, r/HealthyFood, r/QuantifiedSelf
   when relevant. Do not spam links.
6. Later: an email newsletter (the worksheet + plans make a natural lead magnet).

## Who does what

**Account creation needs a human** (phone/email verification, CAPTCHAs, 2FA) — that part is
yours. Sign up with `nutrisize.health@gmail.com` as the primary login everywhere — free and
permanent, so recovery never depends on the domain or Microsoft 365 staying alive, and not
published anywhere (less phishing surface). Recovery chain: `nutrisize.health@gmail.com` →
`nutrisize.universal@gmail.com` (the published contact) → `nutrisize.global@gmail.com`
(reserve). Where a platform supports a secondary/backup email, add the
`social-media@nutrisize.health` alias. Facebook and LinkedIn
are Pages created from your existing personal accounts, not new sign-ups. For YouTube, create
the Google account with "Use my current email address instead". Enable 2FA, use a password
manager. Per account: upload `profile-1024.png` + the platform's banner, paste the bio, set
category + link.

**Then hand back the handles and I do the rest:** footer social icons + `sameAs` JSON-LD on
the site (SEO knowledge-panel signal), per-platform UTM links, post-copy calendar, and
image/video-card generation from site content.
