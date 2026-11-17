# Raventon Partners – Agency Website

A multi-page website for a performance marketing agency offering **Google Ads**, **Meta Ads**, **PPC management**, **lead generation** and **landing pages & CRO**.

## Pages
- Home, About Us, Services (+ one detail page per service), Blog (+ articles), Contact
- Privacy Policy, Terms & Conditions, 404

## Features
- Premium dark + emerald visual identity: Bebas Neue display headings, Montserrat body, Raleway navigation
- Dark hero with a quick-audit card (service + budget chips) that pre-fills the contact form
- Animated counters, platform marquee, 3D flip service cards, green FAQ accordions, slide-in mobile drawer menu
- Swipeable card carousels on phones
- Scroll reveal (fade-in-up with stagger) in plain JavaScript, no dependencies (respects `prefers-reduced-motion`)
- No build tools needed to view the site – it is plain HTML, CSS and JavaScript

## Run locally
```bash
python server.py          # site + accounts API on http://localhost:8000
python server.py dump     # list registered users and contact leads
```
`server.py` uses only the Python standard library. It serves the site and stores records in SQLite at `data/rvn.db` (git-ignored):
- `users`: advertiser and publisher accounts (passwords hashed with PBKDF2-SHA256)
- `sessions`: sign-in sessions (HttpOnly cookie, 1 or 30 days)
- `leads`: contact form submissions

Pages: login dropdown in the header → `advertiser-login.html`, `publisher-login.html`, `advertiser-register.html`, `publisher-register.html`, and `dashboard.html` after sign-in.
Opening the HTML files without `server.py` works for browsing, but sign-in and the contact form need the server.

## Editing content
Page content lives in `build.py`. After editing it, regenerate the pages:
```bash
python build.py
```
Styles and scripts are in `assets/`. Design tokens (colours, fonts, radius, shadow) live in the `:root` block at the top of `assets/style.css`.

## Notes
- `next-reference/Reveal.tsx` is a TypeScript/Next.js version of the reveal component, for a future port. It is not used by the static site.
- Company details, testimonials, clients and statistics are placeholders.
- Fonts load from Google Fonts; everything else is local.
