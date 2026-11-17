"""Static site generator for Raventon Partners (performance marketing agency). Run: python build.py"""
import os
import glob

OUT = os.path.dirname(os.path.abspath(__file__))
BRAND = "Raventon Partners"
SITE = "https://www.raventonpartners.example"
FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 48 48'%3E"
           "%3Cpath d='M24 2.5 42.6 13.25v21.5L24 45.5 5.4 34.75v-21.5z' fill='%231F8A6D'/%3E"
           "%3Cpath d='M13.5 30.5 20 24l4.5 4.5L34 19M28 19h6v6' fill='none' stroke='white' stroke-width='3.6' "
           "stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E")
ORG_JSONLD = ('{"@context":"https://schema.org","@type":"ProfessionalService","name":"Raventon Partners",'
              '"description":"Performance marketing agency specialising in Google Ads, Meta Ads, PPC and lead generation.",'
              '"url":"https://www.raventonpartners.example","email":"hello@raventonpartners.example",'
              '"telephone":"+1-555-014-2290","priceRange":"$$",'
              '"address":{"@type":"PostalAddress","streetAddress":"221 Market Street, Suite 400",'
              '"addressLocality":"Austin","addressRegion":"TX","postalCode":"78701","addressCountry":"US"},'
              '"areaServed":"Worldwide",'
              '"sameAs":["https://www.linkedin.com/","https://www.facebook.com/","https://www.instagram.com/"]}')

# ---------- icon set (inline SVG, inherits currentColor) ----------
_P = {
    "search": '<circle cx="11" cy="11" r="7"/><path d="M16.5 16.5 21 21"/>',
    "megaphone": '<path d="M3.5 9.8 16.5 5v14L3.5 14.2z"/><path d="M6.8 13.1V18a1.6 1.6 0 0 0 3.2 0v-3.8"/><path d="M19.2 9.6a3.2 3.2 0 0 1 0 4.8"/>',
    "target": '<circle cx="12" cy="12" r="8.5"/><circle cx="12" cy="12" r="4.5"/><circle cx="12" cy="12" r="1.2" fill="currentColor" stroke="none"/>',
    "magnet": '<path d="M4 4v8a8 8 0 0 0 16 0V4h-5v8a3 3 0 0 1-6 0V4z"/><path d="M4 8.5h5"/><path d="M15 8.5h5"/>',
    "funnel": '<path d="M3.5 4.5h17l-6.5 8v7.5l-4-2.5v-5z"/>',
    "trend-up": '<path d="M3 17.5 9.5 11l4 4 7.5-7.5"/><path d="M15 7.5h6v6"/>',
    "trend-down": '<path d="M3 7.5 9.5 14l4-4 7.5 7.5"/><path d="M15 17.5h6v-6"/>',
    "user-plus": '<circle cx="9.5" cy="8" r="3.5"/><path d="M3 20.5c0-3.4 2.9-5.5 6.5-5.5 1.6 0 3 .4 4.2 1.1"/><path d="M18.5 14v6"/><path d="M15.5 17h6"/>',
    "scale": '<path d="M12 5.5v14"/><path d="M7.5 19.5h9"/><path d="M4 8.5h16"/><path d="M4 8.5 1.8 13.6a3.3 3.3 0 0 0 4.4 0z"/><path d="M20 8.5l-2.2 5.1a3.3 3.3 0 0 0 4.4 0z"/><circle cx="12" cy="4.2" r="1.3"/>',
    "checklist": '<path d="M9 4.5H7a2 2 0 0 0-2 2v12.5a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V6.5a2 2 0 0 0-2-2h-2"/><rect x="9" y="2.8" width="6" height="3.6" rx="1"/><path d="m8.8 13.4 2.1 2.1 4.3-4.3"/>',
    "building": '<path d="M3 21V9.8L12 3.5l9 6.3V21"/><path d="M9.5 21v-6h5v6"/><path d="M2 21h20"/>',
    "cart": '<circle cx="9.5" cy="19.5" r="1.5"/><circle cx="17.5" cy="19.5" r="1.5"/><path d="M2.5 4h2.6l2.4 11.2h10.4L20.5 7.6H6"/>',
    "medical": '<rect x="3.5" y="3.5" width="17" height="17" rx="3.5"/><path d="M12 8v8"/><path d="M8 12h8"/>',
    "graduation": '<path d="m2.5 9 9.5-4.5L21.5 9 12 13.5z"/><path d="M6.5 11.2V16c0 1.7 2.5 3 5.5 3s5.5-1.3 5.5-3v-4.8"/>',
    "wrench": '<path d="M20.4 7.3a5.2 5.2 0 0 1-6.6 6.6L6.6 21 3 17.4l7.1-7.2a5.2 5.2 0 0 1 6.6-6.6l-3.2 3.2.9 2.9 2.9.9z"/>',
    "card": '<rect x="2.5" y="5" width="19" height="14" rx="2.5"/><path d="M2.5 10h19"/><path d="M6 15h4"/>',
    "laptop": '<rect x="4" y="5" width="16" height="11" rx="1.5"/><path d="M2 19.5h20"/>',
    "plane": '<path d="M21.5 3.5 3 10.8l6.8 2.4L12.3 20z"/><path d="m9.8 13.2 11.7-9.7"/>',
    "globe": '<circle cx="12" cy="12" r="8.5"/><path d="M3.5 12h17"/><path d="M12 3.5c2.6 2.7 2.6 14.3 0 17-2.6-2.7-2.6-14.3 0-17z"/>',
    "compass": '<circle cx="12" cy="12" r="8.5"/><path d="m15.8 8.2-2.2 5.6-5.4 2.2 2.2-5.6z"/>',
    "pin": '<path d="M12 21.3s7-6.5 7-11.3a7 7 0 1 0-14 0c0 4.8 7 11.3 7 11.3z"/><circle cx="12" cy="10" r="2.6"/>',
    "mail": '<rect x="2.5" y="5" width="19" height="14" rx="2"/><path d="m3.5 7 8.5 6 8.5-6"/>',
    "phone": '<path d="M6.3 3h3.1l1.5 4-2 1.5a12.3 12.3 0 0 0 6.6 6.6l1.5-2 4 1.5v3.1a2 2 0 0 1-2.2 2A17.2 17.2 0 0 1 4.3 5.2 2 2 0 0 1 6.3 3z"/>',
    "clock": '<circle cx="12" cy="12" r="8.5"/><path d="M12 6.8v5.4l3.5 2"/>',
    "bars": '<path d="M4 20.5V12"/><path d="M10 20.5V4"/><path d="M16 20.5v-6"/><path d="M2 20.5h20"/>',
    "star": '<path d="m12 3.3 2.65 5.5 6 .85-4.35 4.2 1.05 6L12 16.95 6.65 19.85l1.05-6L3.35 9.65l6-.85z" fill="currentColor" stroke="none"/>',
    "arrow-right": '<path d="M4 12h15"/><path d="m13 6 6 6-6 6"/>',
    "arrow-left": '<path d="M20 12H5"/><path d="m11 6-6 6 6 6"/>',
    "arrow-up": '<path d="M12 20V5"/><path d="m6 11 6-6 6 6"/>',
}
_BRAND_P = {
    "linkedin": '<path d="M20.45 20.45h-3.56v-5.57c0-1.33-.02-3.04-1.85-3.04-1.85 0-2.14 1.45-2.14 2.94v5.67H9.35V9h3.41v1.56h.05c.48-.9 1.64-1.85 3.37-1.85 3.6 0 4.27 2.37 4.27 5.46v6.28zM5.34 7.43a2.07 2.07 0 1 1 0-4.13 2.07 2.07 0 0 1 0 4.13zm1.78 13.02H3.56V9h3.56v11.45zM22.22 0H1.77C.79 0 0 .77 0 1.73v20.54C0 23.23.79 24 1.77 24h20.45c.98 0 1.78-.77 1.78-1.73V1.73C24 .77 23.2 0 22.22 0z"/>',
    "facebook": '<path d="M24 12.07C24 5.44 18.63.07 12 .07S0 5.44 0 12.07c0 5.99 4.39 10.95 10.13 11.85v-8.38H7.08v-3.47h3.05V9.43c0-3.01 1.79-4.67 4.53-4.67 1.31 0 2.69.24 2.69.24v2.95h-1.52c-1.49 0-1.95.93-1.95 1.87v2.25h3.33l-.53 3.47h-2.8v8.38C19.61 23.02 24 18.06 24 12.07z"/>',
    "instagram": '<path d="M12 2.16c3.2 0 3.58.01 4.85.07 3.25.15 4.77 1.69 4.92 4.92.06 1.27.07 1.65.07 4.85s-.01 3.58-.07 4.85c-.15 3.23-1.66 4.77-4.92 4.92-1.27.06-1.64.07-4.85.07s-3.58-.01-4.85-.07c-3.26-.15-4.77-1.7-4.92-4.92-.06-1.27-.07-1.64-.07-4.85s.01-3.58.07-4.85c.15-3.23 1.66-4.77 4.92-4.92C8.42 2.17 8.8 2.16 12 2.16zM12 0C8.74 0 8.33.01 7.05.07c-4.36.2-6.78 2.62-6.98 6.98C.01 8.33 0 8.74 0 12s.01 3.67.07 4.95c.2 4.36 2.62 6.78 6.98 6.98 1.28.06 1.69.07 4.95.07s3.67-.01 4.95-.07c4.35-.2 6.78-2.62 6.98-6.98.06-1.28.07-1.69.07-4.95s-.01-3.67-.07-4.95c-.2-4.35-2.62-6.78-6.98-6.98C15.67.01 15.26 0 12 0zm0 5.84a6.16 6.16 0 1 0 0 12.32 6.16 6.16 0 0 0 0-12.32zM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 8zm6.41-11.85a1.44 1.44 0 1 0 0 2.89 1.44 1.44 0 0 0 0-2.89z"/>',
    "x": '<path d="M18.9 1.15h3.68l-8.04 9.19L24 22.85h-7.41l-5.8-7.58-6.63 7.58H.47l8.6-9.83L0 1.15h7.59l5.25 6.93 6.06-6.93zm-1.29 19.49h2.04L6.49 3.24H4.3l13.31 17.4z"/>',
}


def ic(name, size=24, cls=""):
    """Inline SVG icon; strokes/fills inherit the surrounding colour."""
    c = f' class="{cls}"' if cls else ""
    return (f'<svg{c} width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">'
            f'{_P[name]}</svg>')


def brand_ic(name, size=16):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="currentColor" '
            f'aria-hidden="true" focusable="false">{_BRAND_P[name]}</svg>')


STARS = '<span class="stars" aria-label="5 out of 5">' + ic("star", 16) * 5 + "</span>"
ARR = ic("arrow-right", 17, "ia")

SERVICES = [
    dict(slug="google-ads", icon="search", name="Google Ads Management",
         short="Show up when customers are searching and turn high-intent clicks into leads and sales.",
         intro="People who search on Google already want what you sell. We build and manage Search, Performance Max, Shopping, Display and YouTube campaigns that put your offer in front of them at the right moment and the right cost.",
         points=["Account audits and conversion tracking setup", "Search, Shopping and Performance Max campaigns", "Keyword research and negative keyword control", "Ad copy testing and ad extensions", "Smart bidding and budget optimisation", "Weekly reporting with clear next steps"],
         tech=["Google Ads", "Google Analytics 4", "Tag Manager", "Merchant Center", "YouTube Ads", "Looker Studio"],
         kpis=["Cost per lead", "Conversion rate", "ROAS", "Impression share", "Quality Score", "Cost per acquisition"],
         faq=[("How fast can my Google Ads campaigns go live?", "After the audit and tracking setup, most campaigns launch within 5 to 10 working days. We start with a focused test budget and scale what works."),
              ("Do I own my Google Ads account?", "Yes. The account is always in your name. We are given access to manage it, and you can see everything at any time."),
              ("How do you decide the keywords to bid on?", "We start from your services and customer questions, then expand with search term data. Irrelevant searches are blocked early with negative keywords to protect your budget.")]),
    dict(slug="meta-ads", icon="megaphone", name="Meta Ads (Facebook & Instagram)",
         short="Reach the right audience on Facebook and Instagram with creative that stops the scroll.",
         intro="Meta's platforms let you reach people before they start searching. We plan the audiences, produce the creative and run the campaigns that generate leads, enquiries and sales across Facebook and Instagram.",
         points=["Audience research, lookalikes and retargeting", "Lead form and conversion campaigns", "Ad creative, video and copy testing", "Pixel and Conversions API setup", "Instagram Stories, Reels and feed placements", "Creative refresh cycles to fight ad fatigue"],
         tech=["Meta Ads Manager", "Meta Pixel", "Conversions API", "Instagram Ads", "Canva", "CapCut"],
         kpis=["Cost per lead", "Click-through rate", "Frequency", "Cost per purchase", "ROAS", "Lead quality score"],
         faq=[("Should I advertise on Meta or Google first?", "Google captures people who are already searching. Meta creates demand and reaches people earlier. Many businesses use both, and we can recommend the order based on your offer and budget."),
              ("Do you create the ad creative as well?", "Yes. We write the copy and produce static, carousel and short video ads, and we test several versions to find what performs."),
              ("Why do my Meta ads stop working after a while?", "Audiences get tired of seeing the same ad. We watch frequency and performance and refresh creative on a regular schedule.")]),
    dict(slug="ppc-management", icon="target", name="PPC Campaign Management",
         short="Full-funnel pay-per-click strategy across search, social and display, managed for profit.",
         intro="PPC works best when every channel has a clear job. We plan, launch and optimise paid campaigns across platforms, keep a close eye on your budget and report on the numbers that actually matter to your business.",
         points=["Multi-channel PPC strategy and budgeting", "Search, social, display and remarketing", "A/B testing of ads, audiences and offers", "Bid and budget optimisation", "Competitor and market analysis", "Transparent dashboards and monthly strategy calls"],
         tech=["Google Ads", "Meta Ads", "LinkedIn Ads", "TikTok Ads", "Microsoft Ads", "Looker Studio"],
         kpis=["Return on ad spend", "Cost per acquisition", "Click-through rate", "Conversion rate", "Customer lifetime value", "Wasted spend"],
         faq=[("What ad budget do I need?", "It depends on your market and goal. We work backwards from your target cost per lead or sale and the volume you want, then recommend a budget and a test plan."),
              ("How soon will I see results?", "You will see data in the first couple of weeks. Most accounts need a few weeks of learning and a couple of months of optimisation to reach stable results. We never guarantee specific numbers."),
              ("How do you report performance?", "You get a live dashboard, a weekly summary and a monthly call where we explain what changed, what we learned and what we will do next.")]),
    dict(slug="lead-generation", icon="magnet", name="Lead Generation",
         short="A steady flow of qualified enquiries, booked calls and appointments for your sales team.",
         intro="More leads only help if they are the right leads. We build complete lead generation systems, from the ad and the landing page to the form, follow-up and tracking, so your team spends time on people who are ready to buy.",
         points=["Lead funnels built around a clear offer", "Lead forms, landing pages and call tracking", "Lead qualification questions and scoring", "CRM and email or WhatsApp follow-up automation", "Cost per qualified lead tracking", "Feedback loop with your sales team to improve quality"],
         tech=["Google Ads", "Meta Lead Ads", "HubSpot", "Zapier", "WhatsApp Business", "CallRail", "Google Sheets"],
         kpis=["Cost per lead", "Cost per qualified lead", "Lead-to-sale rate", "Speed to first contact", "Booked calls", "Pipeline value"],
         faq=[("How do you make sure leads are good quality?", "We add qualifying questions to forms, target carefully and ask your sales team for feedback on every batch. We then optimise for qualified leads, not just the cheapest ones."),
              ("Can leads go straight into my CRM?", "Yes. We connect your ads and forms to your CRM, email or WhatsApp so every lead is captured and followed up quickly."),
              ("What industries do you generate leads for?", "We work with local service businesses, real estate, education, healthcare, finance and B2B companies, among others.")]),
    dict(slug="landing-pages-cro", icon="funnel", name="Landing Pages & CRO",
         short="High-converting landing pages and tests that make every ad click work harder.",
         intro="Great ads can still lose money on a weak page. We design fast, focused landing pages and run conversion rate optimisation so more of your paid traffic turns into leads and customers.",
         points=["Landing pages designed for a single goal", "Fast loading, mobile-first layouts", "Persuasive copy and clear calls to action", "A/B testing of headlines, offers and forms", "Heatmaps and session recordings analysis", "Tracking and thank-you page setup"],
         tech=["Webflow", "WordPress", "Next.js", "Hotjar", "VWO", "Figma"],
         kpis=["Conversion rate", "Bounce rate", "Page speed", "Form completion rate", "Cost per lead", "Revenue per visitor"],
         faq=[("Why do I need a separate landing page for ads?", "A page built for one offer and one action converts better than a general website page, which gives visitors many other things to do."),
              ("How long does a landing page take?", "A new landing page typically takes 1 to 2 weeks including copy, design, build and tracking."),
              ("Do you test the pages after launch?", "Yes. We run structured A/B tests and use behaviour data to keep improving the conversion rate.")]),
]

POSTS = [
    dict(slug="google-ads-vs-meta-ads", t="t1", e="scale", title="Google Ads vs Meta Ads: Where Should You Spend First?", date="September 22, 2026", cat="PPC Strategy",
         desc="Search and social solve different problems. Here is how to choose the right starting point for your budget.",
         body=["Google Ads and Meta Ads are both powerful, but they work in very different ways. Google captures demand: people type what they need and your ad appears. Meta creates demand: your ad reaches people who were not searching yet but fit your ideal customer.",
               "If your customers already search for what you sell, such as an emergency plumber or an accountant, start with Google Search. Intent is high and leads tend to be ready to talk. If your product is visual, new or impulse-driven, Meta is often the better starting point.",
               "Most growing businesses end up using both. Meta introduces your brand and fills the top of the funnel, while Google captures people who are ready to act, and retargeting brings back those who did not convert the first time.",
               "Whichever you choose, set up conversion tracking first. Without clean data, neither platform can optimise toward the results you actually want."]),
    dict(slug="lower-cost-per-lead", t="t2", e="trend-down", title="7 Ways to Lower Your Cost Per Lead", date="September 5, 2026", cat="Lead Generation",
         desc="Practical changes that reduce wasted spend and improve lead quality without cutting your budget.",
         body=["A high cost per lead usually comes from a handful of fixable problems. Start by looking at where the money is going before you change anything.",
               "First, tighten your targeting: add negative keywords on Google and exclude poor audiences on Meta. Second, test your offer, because a clearer promise often beats a clever ad. Third, improve the landing page: faster loading, shorter forms and one clear action.",
               "Fourth, test new creative regularly. Fifth, use conversion-based bidding once you have enough data. Sixth, follow up quickly, since leads contacted within minutes are far more likely to respond. Seventh, track cost per qualified lead, not just cost per lead.",
               "Make one change at a time and give each test enough data to be meaningful. Small, steady improvements compound quickly."]),
    dict(slug="landing-page-checklist", t="t3", e="checklist", title="The Landing Page Checklist for Higher Conversions", date="August 18, 2026", cat="Conversion Optimisation",
         desc="Before you send more traffic, make sure your landing page is doing its job.",
         body=["Sending paid traffic to a weak page is the fastest way to waste ad spend. Before you scale a campaign, check the basics on your landing page.",
               "The headline should match the ad and state the main benefit in plain words. The offer should be clear and the main button should be visible without scrolling. Keep forms as short as you can while still qualifying the lead.",
               "Add proof near the call to action: reviews, logos or short case results. Make sure the page loads quickly on mobile, since most ad clicks come from phones. Finally, confirm your tracking fires correctly on the thank-you page.",
               "Once the basics are right, run A/B tests on one element at a time, such as the headline or the form, and let the data guide your next change."]),
]


_P.update({
    "plus": '<path d="M12 5v14"/><path d="M5 12h14"/>',
    "quote": '<path d="M10 6.5c-3.3 1-5.5 3.6-5.5 7.3V18h5.2v-5.2H7.2c.2-2 1.2-3.3 3.4-4.1z"/><path d="M19.5 6.5c-3.3 1-5.5 3.6-5.5 7.3V18h5.2v-5.2h-2.5c.2-2 1.2-3.3 3.4-4.1z"/>',
})

_P.update({
    "user": '<circle cx="12" cy="8" r="4"/><path d="M4 20.5c0-4 3.6-6.5 8-6.5s8 2.5 8 6.5"/>',
    "chev": '<path d="m6 9 6 6 6-6"/>',
    "lock": '<rect x="4.5" y="10.5" width="15" height="10" rx="2.5"/><path d="M8 10.5V7.5a4 4 0 0 1 8 0v3"/>',
    "logout": '<path d="M14 4.5h4a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2h-4"/><path d="M10 16.5 5.5 12 10 7.5"/><path d="M5.5 12H16"/>',
    "grid": '<rect x="3.5" y="3.5" width="7" height="7" rx="2"/><rect x="13.5" y="3.5" width="7" height="7" rx="2"/><rect x="3.5" y="13.5" width="7" height="7" rx="2"/><rect x="13.5" y="13.5" width="7" height="7" rx="2"/>',
    "eye": '<path d="M2.5 12S6 5.5 12 5.5 21.5 12 21.5 12 18 18.5 12 18.5 2.5 12 2.5 12z"/><circle cx="12" cy="12" r="3"/>',
    "shield": '<path d="M12 3 4.5 6v5.5c0 4.6 3.2 8.3 7.5 9.5 4.3-1.2 7.5-4.9 7.5-9.5V6z"/><path d="m8.8 12 2.2 2.2 4.2-4.4"/>',
    "check-sm": '<path d="m5 12.5 4.2 4.2L19 7"/>',
    "users": '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20c0-3.6 2.9-6 6.5-6s6.5 2.4 6.5 6"/><circle cx="17" cy="9" r="2.8"/><path d="M16.5 14.2c3 .2 5 2.3 5 5.3"/>',
    "user-plus2": '<circle cx="10" cy="8" r="4"/><path d="M3 20.5c0-4 3.1-6.5 7-6.5 1.4 0 2.7.3 3.8.9"/><path d="M18.5 14v6"/><path d="M15.5 17h6"/>',
})

NAV = [("index.html", "Home"), ("about.html", "About Us"), ("services.html", "Services"), ("blog.html", "Blog"), ("contact.html", "Contact")]
FONTS = ("https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Montserrat:wght@400;500;600;700;800"
         "&family=Raleway:wght@500;600;700&display=swap")
BUDGETS = ["Under $1,000", "$1,000 – $5,000", "$5,000 – $20,000", "$20,000+", "Not sure yet"]
TRAFFIC = ["Search", "Social media", "Email", "Native & display", "Other"]


def mark(uid, size=44):
    """Brand mark: emerald hexagon with a rising growth line."""
    return (f'<svg class="mark" width="{size}" height="{size}" viewBox="0 0 48 48" aria-hidden="true" focusable="false">'
            f'<defs><linearGradient id="{uid}" x1="6" y1="44" x2="42" y2="4" gradientUnits="userSpaceOnUse">'
            '<stop offset="0" stop-color="#003D31"/><stop offset=".55" stop-color="#1F8A6D"/><stop offset="1" stop-color="#9BE3C6"/></linearGradient></defs>'
            f'<path d="M24 2.5 42.6 13.25v21.5L24 45.5 5.4 34.75v-21.5z" fill="url(#{uid})"/>'
            '<path d="M24 7.2 38.5 15.6v16.8L24 40.8 9.5 32.4V15.6z" fill="none" stroke="#fff" stroke-opacity=".22"/>'
            '<path class="mk-line" d="M13.5 30.5 20 24l4.5 4.5L34 19" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'
            '<path class="mk-head" d="M28 19h6v6" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'
            '<circle cx="13.5" cy="30.5" r="2.3" fill="#9BE3C6"/></svg>')


def logo(uid):
    return f'<a href="index.html" class="logo" aria-label="{BRAND} home">{mark(uid)}<span class="wm"><b>Raventon</b><small>Partners</small></span></a>'


LOGIN_MENU = f"""<div class="dd" id="account">
<button class="dd-btn" type="button" aria-expanded="false" aria-haspopup="true">{ic("user", 16)}<span class="dd-label">Login</span>{ic("chev", 14, "chev")}</button>
<div class="dd-menu" role="menu">
<div class="dd-guest">
<small>Sign in</small>
<a role="menuitem" href="advertiser-login.html"><i>{ic("megaphone", 18)}</i><span>Advertiser Login<em>Campaigns, leads &amp; reports</em></span></a>
<a role="menuitem" href="publisher-login.html"><i>{ic("globe", 18)}</i><span>Publisher Login<em>Offers, traffic &amp; payouts</em></span></a>
<small>New here?</small>
<a role="menuitem" href="advertiser-register.html"><i>{ic("user-plus2", 18)}</i><span>Advertiser Register</span></a>
<a role="menuitem" href="publisher-register.html"><i>{ic("user-plus2", 18)}</i><span>Publisher Register</span></a>
</div>
<div class="dd-user" hidden>
<a role="menuitem" href="dashboard.html"><i>{ic("grid", 18)}</i><span>Dashboard</span></a>
<button role="menuitem" type="button" class="js-logout"><i>{ic("logout", 18)}</i><span>Sign out</span></button>
</div>
</div></div>"""


def head(title, desc, active, depth=""):
    links = ""
    for href, label in NAV:
        cls = ' class="active" aria-current="page"' if href == active else ""
        links += f'<a href="{href}"{cls}>{label}</a>'
    return f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} | {BRAND}</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#000000">
<link rel="icon" href="{FAVICON}">
<link rel="canonical" href="{SITE}/{active or 'index.html'}">
<meta property="og:type" content="website"><meta property="og:site_name" content="{BRAND}">
<meta property="og:title" content="{title} | {BRAND}"><meta property="og:description" content="{desc}">
<meta property="og:url" content="{SITE}/{active or 'index.html'}">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{title} | {BRAND}">
<meta name="twitter:description" content="{desc}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{FONTS}" rel="stylesheet">
<link rel="stylesheet" href="assets/style.css">
<script>(function(h){{h.classList.add('js');try{{if(sessionStorage.getItem('rvn-pre'))h.classList.add('no-pre');sessionStorage.setItem('rvn-pre','1')}}catch(e){{h.classList.add('no-pre')}}}})(document.documentElement)</script>
<script type="application/ld+json">{ORG_JSONLD}</script>
</head><body>
<div class="preloader" aria-hidden="true"><div class="pl-in">{mark("mk-pl", 72)}<span class="pl-name">Raventon <em>Partners</em></span><span class="pl-bar"><i></i></span></div></div>
<a class="skip" href="#main">Skip to content</a>
<div class="progress"></div>
<header class="nav"><div class="wrap">
{logo("mk-h")}
<button class="burger" aria-label="Menu" aria-expanded="false" aria-controls="menu"><span></span><span></span><span></span></button>
<nav class="menu" id="menu">{links}{LOGIN_MENU}<a href="contact.html" class="btn btn-primary">Free Audit</a></nav>
</div></header>
<main id="main">
"""


def foot():
    svc = "".join(f'<li><a href="services-{s["slug"]}.html">{s["name"]}</a></li>' for s in SERVICES)
    return f"""</main>
<footer><div class="wrap">
<div class="fgrid">
<div>{logo("mk-f")}
<p>A performance marketing agency specialising in Google Ads, Meta Ads, PPC and lead generation for ambitious businesses.</p>
<div class="soc"><a href="#" aria-label="LinkedIn">{brand_ic("linkedin")}</a><a href="#" aria-label="Facebook">{brand_ic("facebook")}</a><a href="#" aria-label="Instagram">{brand_ic("instagram")}</a><a href="#" aria-label="X">{brand_ic("x")}</a></div></div>
<div><h4>Company</h4><ul><li><a href="index.html">Home</a></li><li><a href="about.html">About Us</a></li><li><a href="blog.html">Blog</a></li><li><a href="contact.html">Contact</a></li></ul></div>
<div><h4>Services</h4><ul>{svc}</ul></div>
<div><h4>Get in touch</h4><ul class="contact-list"><li>{ic("mail", 17)}<span>hello@raventonpartners.example</span></li><li>{ic("phone", 17)}<span>+1 (555) 014-2290</span></li><li>{ic("pin", 17)}<span>221 Market Street, Suite 400<br>Austin, TX 78701</span></li></ul>
<div class="f-acc"><a href="advertiser-login.html">Advertiser Login</a><a href="publisher-login.html">Publisher Login</a></div></div>
</div>
<div class="copy"><span>© 2026 {BRAND}. All rights reserved.</span><span><a href="privacy-policy.html">Privacy Policy</a> &nbsp;·&nbsp; <a href="terms-conditions.html">Terms &amp; Conditions</a></span></div>
</div><div class="fwm" aria-hidden="true">Raventon Partners</div></footer>
<button class="top" aria-label="Back to top">{ic("arrow-up", 18)}</button>
<script src="assets/main.js"></script>
</body></html>"""


def page_hero(title, sub, crumb):
    return f"""<div class="page-hero"><div class="ph-art" aria-hidden="true"><i></i><i></i><i></i></div><div class="wrap">
<div class="crumbs ld" style="--d:0"><a href="index.html">Home</a> / {crumb}</div>
<h1 class="ld" style="--d:1">{title}</h1><p class="ld" style="--d:2">{sub}</p></div></div>"""


def cta():
    return f"""<section class="cta-band"><div class="wrap"><div class="cta rv zoom"><i class="ring r1" aria-hidden="true"></i><i class="ring r2" aria-hidden="true"></i>
<h2>Ready to get more leads?</h2>
<p>Get a free audit of your ad account and a clear plan to lower your cost per lead. We reply within one business day.</p>
<a href="contact.html" class="btn btn-light">Get Your Free Audit {ARR}</a></div></div></section>"""


def svc_cards():
    return "".join(f"""<div class="flip rv" tabindex="0"><div class="flip-in">
<div class="face front"><div class="ico">{ic(s['icon'], 30)}</div><h3>{s['name']}</h3><span class="hint" aria-hidden="true">{ic("plus", 18)}</span></div>
<div class="face back"><h3>{s['name']}</h3><p>{s['short']}</p><a class="btn btn-light" href="services-{s['slug']}.html">Learn more {ARR}</a></div>
</div></div>""" for s in SERVICES)


def post_cards(posts):
    return "".join(f"""<article class="post rv"><a class="thumb {p['t']}" href="blog-{p['slug']}.html" tabindex="-1" aria-hidden="true">{ic(p['e'], 44)}</a><div class="body">
<div class="meta">{p['date']} · {p['cat']}</div><h3><a href="blog-{p['slug']}.html">{p['title']}</a></h3><p>{p['desc']}</p>
<a class="more" href="blog-{p['slug']}.html">Read article {ARR}</a></div></article>""" for p in posts)


def stats(items, cls=""):
    cells = "".join(f'<div class="rv"><b data-count="{n}" data-suffix="{suf}">0</b><span>{label}</span></div>' for n, suf, label in items)
    return f'<section class="stats{cls}"><div class="wrap grid g4">{cells}</div></section>'


def write(name, html):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(html)


# remove pages from the previous version of the site
for old in glob.glob(os.path.join(OUT, "services-*.html")) + glob.glob(os.path.join(OUT, "blog-*.html")):
    os.remove(old)

PLATFORMS = ["Google Ads", "Meta Ads", "LinkedIn Ads", "Google Analytics 4", "Tag Manager", "Looker Studio"]
PLAT = "".join(f"<span>{x}</span>" for x in PLATFORMS)
# the track is repeated so the marquee loops seamlessly; copies are hidden from screen readers
MARQUEE = f'<div class="marquee"><div class="marquee-track"><div class="mq-set">{PLAT}{PLAT}</div><div class="mq-set" aria-hidden="true">{PLAT}{PLAT}</div></div></div>'

# sample case studies: replace with real client results before publishing
WORKS = [("building", "Lumio Realty", "Real estate · Meta Lead Ads", "Lower cost per lead and more booked viewings"),
         ("cart", "Orbitly Store", "E-commerce · Google Shopping", "Stronger ROAS from Shopping and remarketing"),
         ("medical", "Kestrel Dental", "Healthcare · Google Search", "More appointment requests from local search")]
WORKS_HTML = "".join(f'<div class="work rv"><div class="big">{ic(i, 30)}</div><small class="tag">{c}</small><h3>{n}</h3><small>{r}</small><span class="go" aria-hidden="true">{ic("arrow-right", 18)}</span></div>' for i, n, c, r in WORKS)

HOME_FAQ = [("How much should I spend on ads?", "It depends on your market and what a lead or sale is worth. We work backwards from your target cost per lead and the volume you want, then recommend a budget and a clear test plan."),
            ("Should I use Google Ads or Meta Ads?", "Google Ads reaches people who are already searching for what you sell. Meta Ads reaches people earlier, based on interests and behaviour. Many businesses use both, and we will recommend the right starting point after a short audit."),
            ("How soon will I see results?", "You will see data within the first couple of weeks. Stable, optimised results usually take a couple of months. We do not promise specific numbers, but we do promise honest reporting."),
            ("Who owns the ad accounts?", "You do. Your ad accounts, pixels and data stay in your name and we are given access to manage them."),
            ("How do you report performance?", "You get a live dashboard, a weekly summary and a monthly strategy call covering results, learnings and next steps.")]
FAQ_HTML = "".join(f"<details class='rv'><summary>{q}</summary><p>{a}</p></details>" for q, a in HOME_FAQ)

QUOTE = f'<span class="qmark" aria-hidden="true">{ic("quote", 56)}</span>'

svc_tiles = "".join(f'<label class="q-tile"><input type="radio" name="service" value="{s["name"]}"{" checked" if i == 0 else ""}><span><i>{ic(s["icon"], 20)}</i><b>{s["name"].split(" (")[0]}</b><em aria-hidden="true">{ic("check-sm", 12)}</em></span></label>' for i, s in enumerate(SERVICES))
bud_chips = "".join(f'<label class="chip q-chip"><input type="radio" name="budget" value="{b}"{" checked" if i == 0 else ""}><span>{b}</span></label>' for i, b in enumerate(BUDGETS))

# ---------- HOME ----------
home = head("Google Ads, Meta Ads, PPC & Lead Generation", "Raventon Partners is a performance marketing agency specialising in Google Ads, Meta Ads, PPC and lead generation.", "index.html") + f"""
<section class="hero"><i class="glow g1" aria-hidden="true"></i><i class="glow g2" aria-hidden="true"></i><div class="wrap hero-grid">
<div><span class="eyebrow ld" style="--d:0">Performance marketing agency</span>
<h1 class="ld" style="--d:1">We turn advertising budgets into <span class="grad-text">measurable growth</span></h1>
<p class="lead ld" style="--d:2">Google Ads, Meta Ads, PPC and lead generation, managed by specialists who focus on one thing: more of the right customers at a lower cost.</p>
<div class="hero-btns ld" style="--d:3"><a href="contact.html" class="btn btn-primary">Get Free Ad Audit {ARR}</a><a href="services.html" class="btn btn-ghost">Our Services</a></div>
<div class="trust ld" style="--d:4"><span class="avs"><i>SM</i><i>DK</i><i>AR</i></span><span class="tr-t">{STARS}<small>4.9 client rating</small></span></div></div>
<form class="qcard ld" style="--d:2" action="contact.html" method="get" id="quickAudit">
<div class="q-top"><span class="q-badge">{ic("shield", 14)} Free audit</span><span class="q-count" aria-live="polite"><b>01</b> / 02</span></div>
<div class="qhead"><h3>Get Your Free Audit</h3><p>Tell us about your business and goals. We reply within one business day.</p></div>
<div class="q-prog" aria-hidden="true"><i></i></div>
<fieldset class="q-pane" data-step="1"><legend><b>1</b>Service</legend><div class="q-tiles">{svc_tiles}</div></fieldset>
<fieldset class="q-pane" data-step="2"><legend><b>2</b>Monthly ad budget</legend><div class="chips">{bud_chips}</div></fieldset>
<div class="q-nav"><button type="button" class="q-back" hidden>{ic("arrow-left", 16)} Back</button><button type="button" class="btn btn-primary q-next" hidden>Continue {ARR}</button><button class="btn btn-primary q-submit" type="submit">Request Free Audit {ARR}</button></div>
<div class="q-foot">{ic("lock", 14)} Private and secure. We reply within one business day.</div>
</form>
</div></section>

{stats([(250, "+", "Campaigns launched"), (120, "+", "Brands served"), (40, "%", "Avg. lower cost per lead"), (95, "%", "Client retention")])}

<div class="logos"><div class="wrap"><h2 class="rv">Certified expertise across the platforms that drive growth</h2></div>
{MARQUEE}</div>

<section class="dark band-alt"><div class="wrap split">
<div class="art rv zoom"><i class="orbit" aria-hidden="true"></i><div class="mini m1">{ic("target", 16)} Lead-focused</div><div class="badge"><b>8+</b>Years running paid ads</div><div class="mini m2">{ic("bars", 16)} Data-driven</div></div>
<div class="rv"><span class="eyebrow">About us</span><h2>Paid advertising built around your return</h2>
<p>Raventon Partners is a team of paid media specialists, creatives and analysts. We plan, launch and optimise Google Ads and Meta Ads campaigns, and we judge our work by one measure: the leads and sales it brings you.</p>
<ul class="checks"><li>Specialists in search, social and lead generation</li><li>Transparent reporting you can check any time</li><li>You own your ad accounts and your data</li></ul>
<a href="about.html" class="btn btn-primary">More about us {ARR}</a></div></div></section>

<section class="bg-soft"><div class="wrap">
<div class="sec-head center rv"><span class="eyebrow">What we do</span><h2>Services built to generate leads</h2><p>Everything you need to find, win and keep customers through paid advertising.</p></div>
<div class="grid g3 svc-grid snap">{svc_cards()}</div></div></section>

<section class="dark"><div class="wrap">
<div class="sec-head center rv"><span class="eyebrow">How we work</span><h2>A simple, proven process</h2><p>Clear steps from the first audit to scaling what works, with reporting at every stage.</p></div>
<div class="grid g4 steps">
<div class="step rv"><div class="n">01</div><h3>Audit &amp; strategy</h3><p>We review your accounts, set up tracking and agree goals, audiences and budget.</p></div>
<div class="step rv"><div class="n">02</div><h3>Launch &amp; test</h3><p>We launch focused campaigns and test ads, audiences and offers against each other.</p></div>
<div class="step rv"><div class="n">03</div><h3>Optimise</h3><p>We cut waste, improve lead quality and shift budget to what performs.</p></div>
<div class="step rv"><div class="n">04</div><h3>Scale &amp; report</h3><p>We scale winning campaigns and share clear reports and next steps.</p></div></div></div></section>

<section><div class="wrap">
<div class="sec-head center rv"><span class="eyebrow">Our work</span><h2>Sample campaign results</h2><p>The kinds of campaigns we plan and run for our clients across different industries.</p></div>
<div class="grid g3 snap">{WORKS_HTML}</div></div></section>

<section class="bg-soft"><div class="wrap">
<div class="sec-head center rv"><span class="eyebrow">Testimonials</span><h2>What our clients say</h2></div>
<div class="grid g3 snap">
<div class="quote rv">{QUOTE}{STARS}<p>"Our cost per lead dropped within two months and the leads we get now are actually ready to talk. Reporting is clear and honest."</p><div class="who"><i>SM</i><div><b>Sarah Mitchell</b><small>Marketing Director, Lumio</small></div></div></div>
<div class="quote rv">{QUOTE}{STARS}<p>"They fixed our tracking, rebuilt our campaigns and finally showed us which ads bring sales. We now know where every dollar goes."</p><div class="who"><i>DK</i><div><b>Daniel Kim</b><small>Founder, Orbitly</small></div></div></div>
<div class="quote rv">{QUOTE}{STARS}<p>"Our appointment bookings from Google and Instagram have become steady and predictable. The team responds quickly and always has a plan."</p><div class="who"><i>AR</i><div><b>Ana Rodriguez</b><small>Practice Manager, Kestrel</small></div></div></div>
</div></div></section>

<section><div class="wrap">
<div class="sec-head center rv"><span class="eyebrow">From the blog</span><h2>Latest insights</h2></div>
<div class="grid g3 snap">{post_cards(POSTS)}</div></div></section>

<section class="bg-soft"><div class="wrap">
<div class="sec-head center rv"><span class="eyebrow">FAQ</span><h2>Questions we often hear</h2></div>
<div class="faqs">{FAQ_HTML}</div></div></section>
{cta()}
""" + foot()
write("index.html", home)

# ---------- ABOUT ----------
about = head("About Us", "Learn about Raventon Partners, our mission, values and team.", "about.html") + page_hero("About Us", "We are a performance marketing agency on a mission to turn ad budgets into measurable growth.", "About Us") + f"""
<section><div class="wrap split">
<div class="rv left"><span class="eyebrow">Our story</span><h2>Built by marketers, driven by results</h2>
<p>Raventon Partners started in 2018 when a small group of paid media specialists got tired of agencies that reported clicks instead of customers. We set out to build an agency that is accountable for leads and sales.</p>
<p>Today we manage Google Ads, Meta Ads and lead generation campaigns for businesses across 12 countries. We stay close to the numbers, test constantly and share what we learn with our clients.</p>
<ul class="checks"><li>Founded in 2018, remote-first team</li><li>250+ campaigns launched</li><li>Specialists in search, social and lead generation</li></ul></div>
<div class="art rv zoom"><i class="orbit" aria-hidden="true"></i><div class="mini m1">{ic("globe", 16)} 12 countries</div><div class="badge"><b>25</b>Marketing specialists</div><div class="mini m2">{ic("star", 16)} 4.9 client rating</div></div></div></section>

<section class="bg-soft"><div class="wrap">
<div class="grid g2">
<div class="svc rv"><div class="ico">{ic("target", 30)}</div><h3>Our mission</h3><p>To help businesses grow through paid advertising that is transparent, accountable and tied to real revenue.</p></div>
<div class="svc svc-dark rv"><div class="ico">{ic("compass", 30)}</div><h3>Our vision</h3><p>To be the most trusted performance marketing partner for ambitious companies, known for honest reporting and lasting results.</p></div></div></div></section>

<section><div class="wrap">
<div class="sec-head center rv"><span class="eyebrow">Our values</span><h2>What guides us</h2></div>
<div class="grid g4">
<div class="step rv"><div class="n">01</div><h3>Results first</h3><p>We measure ourselves by leads, sales and return, not vanity metrics.</p></div>
<div class="step rv"><div class="n">02</div><h3>Honesty</h3><p>Clear numbers, plain language and no hidden fees or surprises.</p></div>
<div class="step rv"><div class="n">03</div><h3>Testing</h3><p>We test ads, audiences and offers constantly and let the data decide.</p></div>
<div class="step rv"><div class="n">04</div><h3>Partnership</h3><p>We work as an extension of your team and share what we learn.</p></div></div></div></section>

<section class="bg-soft"><div class="wrap">
<div class="sec-head center rv"><span class="eyebrow">Our journey</span><h2>How we got here</h2></div>
<div class="timeline">
<div class="tl rv"><b>2018</b><h3>Raventon Partners is founded</h3><p>We start by managing Google Ads for local service businesses.</p></div>
<div class="tl rv"><b>2020</b><h3>Paid social team launches</h3><p>We add Meta Ads specialists and creative production for Facebook and Instagram.</p></div>
<div class="tl rv"><b>2022</b><h3>Lead generation systems</h3><p>We build funnels with landing pages, CRM integrations and follow-up automation.</p></div>
<div class="tl rv"><b>2024</b><h3>Serving 12 countries</h3><p>The team grows to 25 specialists working across many industries.</p></div>
<div class="tl rv"><b>2026</b><h3>250+ campaigns launched</h3><p>Today we partner with brands on long-term, full-funnel paid growth.</p></div>
</div></div></section>

{stats([(250, "+", "Campaigns launched"), (120, "+", "Brands served"), (25, "", "Specialists on the team"), (8, "+", "Years in business")], " dark")}

<section><div class="wrap">
<div class="sec-head center rv"><span class="eyebrow">Leadership</span><h2>Meet the team</h2></div>
<div class="grid g3 team">
<div class="quote rv"><div class="who"><i>JH</i><div><b>James Harlow</b><small>Founder &amp; CEO</small></div></div><p>Paid media strategist who leads the agency and works directly with our biggest accounts.</p></div>
<div class="quote rv"><div class="who"><i>PN</i><div><b>Priya Nair</b><small>Head of Paid Social</small></div></div><p>Leads Meta Ads strategy and creative testing across Facebook and Instagram.</p></div>
<div class="quote rv"><div class="who"><i>OB</i><div><b>Omar Bashir</b><small>Head of Search &amp; Analytics</small></div></div><p>Oversees Google Ads, tracking and reporting so every decision is backed by data.</p></div></div></div></section>
{cta()}
""" + foot()
write("about.html", about)

# ---------- SERVICES ----------
VISUALS = {
    "google-ads": '<div class="mock serp"><div class="sbar"><span>'+ic("search",16)+'</span> emergency plumber near me</div><div class="ad"><small><b>Ad</b> · example-plumbing.com</small><h5>24/7 Emergency Plumber – Fast Response</h5><p>Call now for a free quote. Licensed and insured.</p></div><div class="res"></div><div class="res short"></div></div>',
    "meta-ads": '<div class="mock phone"><div class="notch"></div><div class="ps"><div class="av"></div><div class="l1"></div><div class="l2"></div><div class="card adimg"></div><div class="cta-pill"></div><div class="pnav"><i></i><i></i><i></i><i></i></div></div></div>',
    "ppc-management": '<div class="mock browser"><div class="bt"><i></i><i></i><i></i><span>ads.raventonpartners.io</span></div><div class="bb"><div class="kp"><div><small>Clicks</small><b>12.4K</b></div><div><small>CPA</small><b>$18</b></div><div><small>ROAS</small><b>4.8x</b></div></div><div class="minibars"><i style="--h:40%"></i><i style="--h:62%"></i><i style="--h:50%"></i><i style="--h:80%"></i><i style="--h:70%"></i><i style="--h:100%"></i></div></div></div>',
    "lead-generation": '<div class="mock funnel"><div class="fu f1">Ad clicks</div><div class="fu f2">Leads</div><div class="fu f3">Qualified</div><div class="fu f4">Customers</div></div>',
    "landing-pages-cro": '<div class="mock browser"><div class="bt"><i></i><i></i><i></i><span>offer.yoursite.com</span></div><div class="bb"><div class="l1"></div><div class="l2"></div><div class="cols"><div></div><div></div><div></div></div><div class="l3"></div></div></div>',
}

rows = ""
for i, s in enumerate(SERVICES):
    pts = "".join(f"<li>{p}</li>" for p in s["points"][:4])
    tags = "".join(f"<span>{t}</span>" for t in s["tech"][:5])
    rev = " rev" if i % 2 else ""
    rows += f"""<div class="srow{rev}">
<div class="stext rv {'right' if i % 2 else 'left'}"><div class="snum">{i + 1:02d}</div><h2>{s['name']}</h2><p class="sint">{s['intro']}</p>
<ul class="checks">{pts}</ul><div class="tags">{tags}</div>
<a href="services-{s['slug']}.html" class="btn btn-dark">Explore {s['name'].split(' (')[0]} {ARR}</a></div>
<div class="svis rv zoom">{VISUALS[s['slug']]}</div></div>"""

INDUSTRIES = [("building", "Real Estate"), ("cart", "E-commerce"), ("medical", "Healthcare & Dental"), ("graduation", "Education"), ("wrench", "Home Services"), ("card", "Finance & Insurance"), ("laptop", "SaaS & B2B"), ("plane", "Travel & Hospitality")]
ind = "".join(f'<div class="ind rv"><span>{ic(e, 22)}</span><b>{n}</b></div>' for e, n in INDUSTRIES)

services = head("Our Services", "Google Ads, Meta Ads, PPC management, lead generation and landing page optimisation.", "services.html") + page_hero("Our Services", "Google Ads, Meta Ads, PPC and lead generation, managed by specialists who focus on your return.", "Services") + f"""
<section class="sv-intro"><div class="wrap"><div class="intro-grid">
<div class="rv left"><span class="eyebrow">What we do</span><h2>One partner for paid growth</h2></div>
<div class="rv right"><p>We help businesses find customers through paid advertising. Our team covers strategy, tracking, creative, campaign management and the landing pages that turn clicks into leads, so every part of the funnel works together.</p>
<div class="mini-stats"><div><b data-count="250" data-suffix="+">0</b><span>Campaigns</span></div><div><b data-count="12" data-suffix="">0</b><span>Countries</span></div><div><b data-count="95" data-suffix="%">0</b><span>Retention</span></div></div></div>
</div></div></section>

<section class="sv-rows"><div class="wrap">{rows}</div></section>

<section class="bg-soft"><div class="wrap">
<div class="sec-head center rv"><span class="eyebrow">Our approach</span><h2>From audit to scale</h2><p>The same clear process on every account, so you always know what happens next.</p></div>
<div class="flow">
<div class="fl rv"><div class="fn">1</div><h3>Audit</h3><p>Review accounts, tracking, offers and competitors.</p></div>
<div class="fl rv"><div class="fn">2</div><h3>Strategy</h3><p>Set goals, target cost per lead, audiences and budget.</p></div>
<div class="fl rv"><div class="fn">3</div><h3>Launch</h3><p>Build campaigns, creative and landing pages, then go live.</p></div>
<div class="fl rv"><div class="fn">4</div><h3>Optimise</h3><p>Test, cut waste and improve lead quality every week.</p></div>
<div class="fl rv"><div class="fn">5</div><h3>Scale</h3><p>Increase budget on what works and report on results.</p></div>
</div></div></section>

<section><div class="wrap">
<div class="sec-head center rv"><span class="eyebrow">Industries</span><h2>Experience across sectors</h2><p>We bring lessons from many industries to every new account.</p></div>
<div class="ind-grid">{ind}</div></div></section>

<section class="dark sv-why"><div class="wrap split">
<div class="rv left"><span class="eyebrow">Why Raventon Partners</span><h2>Built on trust and clear numbers</h2>
<p>Our clients stay with us because they always know what their money is doing.</p>
<ul class="checks"><li>Specialists in Google, Meta and lead generation</li><li>You own your ad accounts and data</li><li>Conversion tracking set up before spend scales</li><li>Weekly updates and a monthly strategy call</li><li>Focus on cost per qualified lead, not vanity metrics</li></ul></div>
<div class="why-cards">
<div class="wc rv"><b>24h</b><span>Average response time</span></div>
<div class="wc rv"><b>Weekly</b><span>Performance updates</span></div>
<div class="wc rv"><b>100%</b><span>Account ownership is yours</span></div>
<div class="wc rv"><b>Monthly</b><span>Strategy calls</span></div>
</div></div></section>
{cta()}
""" + foot()
write("services.html", services)

for s in SERVICES:
    others = "".join(f'<li><a href="services-{o["slug"]}.html" class="{"on" if o is s else ""}">{ic(o["icon"], 17)}<span>{o["name"]}</span></a></li>' for o in SERVICES)
    pts = "".join(f"<li>{p}</li>" for p in s["points"])
    tags = "".join(f"<span>{t}</span>" for t in s["tech"])
    kpis = "".join(f"<span>{k}</span>" for k in s["kpis"])
    faq = "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in s["faq"])
    html = head(s["name"], s["short"], "services.html") + page_hero(s["name"], s["short"], f'<a href="services.html">Services</a> / {s["name"]}') + f"""
<section><div class="wrap detail">
<div class="rv"><h2>Overview</h2><p class="sint">{s['intro']}</p>
<h2>What's included</h2><ul class="checks two-col">{pts}</ul>
<h2>How it works</h2><div class="grid g2 steps-mini">
<div class="step"><div class="n">01</div><h3>Audit &amp; setup</h3><p>Goals, tracking and a clear plan.</p></div>
<div class="step"><div class="n">02</div><h3>Launch &amp; test</h3><p>Focused campaigns with structured tests.</p></div>
<div class="step"><div class="n">03</div><h3>Optimise</h3><p>Cut waste and improve lead quality.</p></div>
<div class="step"><div class="n">04</div><h3>Scale &amp; report</h3><p>Grow what works and share the results.</p></div></div>
<h2>Frequently asked questions</h2>{faq}</div>
<aside class="side">
<div class="box"><h4>All services</h4><ul>{others}</ul></div>
<div class="box"><h4>Platforms &amp; tools</h4><div class="tags">{tags}</div></div>
<div class="box"><h4>KPIs we track</h4><div class="tags">{kpis}</div></div>
<div class="box cta-box"><h4>Want better results?</h4><p>Get a free audit of your ad account.</p><a href="contact.html" class="btn btn-light">Get Free Audit {ARR}</a></div>
</aside></div></section>
""" + foot()
    write(f"services-{s['slug']}.html", html)

# ---------- BLOG ----------
blog = head("Blog", "Insights on Google Ads, Meta Ads, PPC and lead generation.", "blog.html") + page_hero("Our Blog", "Practical articles on paid advertising and lead generation.", "Blog") + f"""
<section><div class="wrap"><div class="grid g3">{post_cards(POSTS)}</div></div></section>
""" + foot()
write("blog.html", blog)

for p in POSTS:
    body = "".join(f"<p>{x}</p>" for x in p["body"])
    html = head(p["title"], p["desc"], "blog.html") + page_hero(p["title"], f"{p['date']} · {p['cat']}", '<a href="blog.html">Blog</a> / Article') + f"""
<section><div class="wrap legal article rv"><div class="thumb post-hero {p['t']}">{ic(p['e'], 64)}</div>
{body}<a href="blog.html" class="btn btn-dark">{ic("arrow-left", 17, "ia")} Back to blog</a></div></section>
""" + foot()
    write(f"blog-{p['slug']}.html", html)

# ---------- CONTACT ----------
opts = "".join(f"<option>{s['name']}</option>" for s in SERVICES) + "<option>Not sure yet</option>"
bud_opts = "".join(f"<option>{b}</option>" for b in BUDGETS)
contact = head("Contact Us", "Get a free ad account audit from Raventon Partners.", "contact.html") + page_hero("Get Your Free Audit", "Tell us about your business and goals. We reply within one business day.", "Contact") + f"""
<section><div class="wrap contact">
<div class="info rv left"><i class="glow" aria-hidden="true"></i>
<div class="it"><div class="ico">{ic("pin")}</div><div><b>Visit us</b><span>221 Market Street, Suite 400, Austin, TX 78701</span></div></div>
<div class="it"><div class="ico">{ic("mail")}</div><div><b>Email</b><span>hello@raventonpartners.example</span></div></div>
<div class="it"><div class="ico">{ic("phone")}</div><div><b>Phone</b><span>+1 (555) 014-2290</span></div></div>
<div class="it"><div class="ico">{ic("clock")}</div><div><b>Working hours</b><span>Mon – Fri, 9:00 AM – 6:00 PM</span></div></div></div>
<form class="f rv right" id="contactForm">
<div class="two"><label>Full name<input name="full_name" required autocomplete="name" placeholder="John Doe"></label><label>Email<input type="email" name="email" required autocomplete="email" placeholder="you@company.com"></label></div>
<div class="two"><label>Phone<input name="phone" autocomplete="tel" placeholder="+1 555 000 0000"></label><label>Service<select name="service">{opts}</select></label></div>
<div class="two"><label>Website<input name="website" placeholder="https://yourwebsite.com"></label><label>Monthly ad budget<select name="budget">{bud_opts}</select></label></div>
<label>Your goals<textarea name="goals" required placeholder="Tell us what you want to achieve with paid ads..."></textarea></label>
<div class="form-msg" role="alert" hidden></div><div class="ok" id="formOk" role="status">Thank you! Your request has been received. We will contact you shortly.</div>
<button class="btn btn-primary" type="submit">Request Free Audit {ARR}</button></form></div></section>
""" + foot()
write("contact.html", contact)

# ---------- LEGAL ----------
def legal(name, file, sections):
    body = "".join(f"<h2>{h}</h2><p>{t}</p>" for h, t in sections)
    write(file, head(name, f"{name} for {BRAND}.", "") + page_hero(name, "Last updated: October 1, 2026", name) + f'<section><div class="wrap legal">{body}</div></section>' + foot())

legal("Privacy Policy", "privacy-policy.html", [
    ("Information we collect", "We collect information you give us directly, such as your name, email, website and business details when you contact us, plus basic usage data such as pages visited."),
    ("Cookies and tracking", "Our website may use cookies and analytics tools to understand how visitors use it. You can control cookies through your browser settings."),
    ("How we use it", "We use your information to respond to enquiries, deliver our services, improve our website and send updates you have asked for."),
    ("Sharing and security", "We do not sell personal data. We share it only with trusted providers who help us operate, and we use reasonable measures to protect it."),
    ("Your rights", "You may request access to, correction of or deletion of your personal data at any time by emailing hello@raventonpartners.example."),
])
legal("Terms & Conditions", "terms-conditions.html", [
    ("Use of this website", "By using this website you agree to these terms. Content is provided for general information and may change without notice."),
    ("Services", "Scope, management fees and reporting are defined in a written agreement or proposal signed by both parties."),
    ("Ad spend and accounts", "Ad spend is paid directly to advertising platforms such as Google and Meta, and is separate from our management fees. Ad accounts remain the property of the client."),
    ("No guaranteed results", "Advertising performance depends on many factors outside our control. We work to improve results but do not guarantee specific outcomes."),
    ("Liability", "To the extent permitted by law, we are not liable for indirect or consequential losses arising from use of this website."),
])

# ---------- ACCOUNTS (login / register / dashboard) ----------
ROLE_COPY = {
    "advertiser": dict(label="Advertiser", h1="Grow With", h2="Raventon Partners",
                       side_p="Track your campaigns, leads and reports in one secure place.",
                       extra=("Monthly ad budget", BUDGETS)),
    "publisher": dict(label="Publisher", h1="Monetise", h2="Your Traffic",
                      side_p="Access offers, payouts and performance for your traffic sources.",
                      extra=("Main traffic source", TRAFFIC)),
}

# orbiting globe illustration for the auth screens (pure SVG, no images)
GLOBE = """<svg class="globe" viewBox="0 0 560 560" aria-hidden="true" focusable="false">
<defs>
<radialGradient id="gSphere" cx="38%" cy="32%" r="75%"><stop offset="0" stop-color="#173c31"/><stop offset=".45" stop-color="#0a1d17"/><stop offset="1" stop-color="#020605"/></radialGradient>
<radialGradient id="gHalo" cx="50%" cy="50%" r="50%"><stop offset=".72" stop-color="#2fbf8f" stop-opacity="0"/><stop offset=".8" stop-color="#2fbf8f" stop-opacity=".45"/><stop offset="1" stop-color="#2fbf8f" stop-opacity="0"/></radialGradient>
<linearGradient id="gRim" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#9BE3C6" stop-opacity=".9"/><stop offset=".5" stop-color="#2A7E68" stop-opacity=".25"/><stop offset="1" stop-color="#9BE3C6" stop-opacity=".6"/></linearGradient>
<pattern id="gDots" width="9" height="9" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.05" fill="#9BE3C6"/></pattern>
<clipPath id="gClip"><circle cx="280" cy="280" r="200"/></clipPath>
<mask id="gLand"><rect width="560" height="560" fill="#000"/>
<path fill="#fff" d="M150 170c30-30 80-40 110-28 18 8 12 30 34 34 26 5 40-18 66-6 22 10 14 36 0 48-18 16-46 8-60 26-12 16 6 36-8 52-16 18-44 6-60 22-18 18-4 48-24 64-22 16-52-6-62-30-10-24 6-48-6-70-10-18-34-24-30-48 3-20 22-48 50-64z"/>
<path fill="#fff" d="M330 300c20-12 48-6 62 12 14 18 8 44 22 60 12 14 34 18 32 38-2 22-30 34-52 30-26-5-34-34-54-48-18-12-42-14-48-34-6-22 18-46 38-58z"/>
<path fill="#fff" d="M120 300c18 0 34 14 36 32 2 20-14 34-14 54 0 18 16 34 6 48-10 12-30 6-40-8-14-20-10-46-14-70-3-22 6-56 26-56z"/>
</mask>
</defs>
<circle class="g-halo" cx="280" cy="280" r="250" fill="url(#gHalo)"/>
<circle cx="280" cy="280" r="200" fill="url(#gSphere)"/>
<g clip-path="url(#gClip)">
<rect class="g-land" width="560" height="560" fill="url(#gDots)" mask="url(#gLand)" opacity=".55"/>
<g class="g-grid" fill="none" stroke="#9BE3C6" stroke-opacity=".13">
<ellipse cx="280" cy="280" rx="200" ry="200"/><ellipse cx="280" cy="280" rx="150" ry="200"/><ellipse cx="280" cy="280" rx="95" ry="200"/><ellipse cx="280" cy="280" rx="35" ry="200"/>
<ellipse cx="280" cy="280" rx="200" ry="60"/><ellipse cx="280" cy="280" rx="200" ry="130"/><path d="M80 280h400"/>
</g></g>
<circle cx="280" cy="280" r="200" fill="none" stroke="url(#gRim)" stroke-width="2"/>
<g class="g-orbits" fill="none" stroke="#9BE3C6" stroke-opacity=".22">
<ellipse id="gO1" cx="280" cy="280" rx="262" ry="96" transform="rotate(-24 280 280)"/>
<ellipse id="gO2" cx="280" cy="280" rx="240" ry="150" transform="rotate(32 280 280)"/>
</g>
<circle r="4" fill="#9BE3C6" class="g-node"><animateMotion dur="14s" repeatCount="indefinite" rotate="auto"><mpath href="#gO1"/></animateMotion></circle>
<circle r="3.4" fill="#9BE3C6" class="g-node"><animateMotion dur="20s" repeatCount="indefinite" begin="-6s"><mpath href="#gO2"/></animateMotion></circle>
<circle cx="408" cy="196" r="3" fill="#9BE3C6" class="g-ping"/><circle cx="176" cy="392" r="3" fill="#9BE3C6" class="g-ping p2"/>
</svg>"""


def auth_head(title):
    return f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} | {BRAND}</title>
<meta name="description" content="{title} for {BRAND}.">
<meta name="robots" content="noindex">
<meta name="theme-color" content="#000000">
<link rel="icon" href="{FAVICON}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{FONTS}&family=Manrope:wght@400;500;600;700;800" rel="stylesheet">
<link rel="stylesheet" href="assets/style.css">
<script>document.documentElement.classList.add('js','no-pre')</script>
</head><body class="lp-body">
<main class="lp" id="main">"""


AUTH_FOOT = '</main><script src="assets/main.js"></script></body></html>'


def auth_page(role, mode):
    c = ROLE_COPY[role]
    other = "publisher" if role == "advertiser" else "advertiser"
    is_login = mode == "login"
    title = f"{c['label']} {'Login' if is_login else 'Register'}"
    eye = f'<button type="button" class="pw-toggle" aria-label="Show password">{ic("eye", 18)}</button>'
    if is_login:
        fields = f"""<label class="lp-f">Email<input type="email" name="email" required autocomplete="email" placeholder="Email"></label>
<label class="lp-f">Password<span class="pw"><input type="password" name="password" required autocomplete="current-password" placeholder="Password">{eye}</span></label>
<label class="check lp-check"><input type="checkbox" name="remember"><span>Remember device for 30 days.</span></label>"""
        heading = "Login your account"
        btn = "Sign In"
        links = f'<div class="lp-links"><a href="contact.html">Forgot Password?</a><a href="{role}-register.html">Create New Account?</a></div>'
    else:
        lbl, opts = c["extra"]
        options = "".join(f"<option>{o}</option>" for o in opts)
        req = '<b class="req">*</b>'

        def f(label, icon, inp, required=False):
            return f'<label class="lp-f"><span>{label}{req if required else ""}</span><span class="iw"><span class="fi">{ic(icon, 17)}</span>{inp}</span></label>'
        codes = "".join(f'<option value="{v}">{t}</option>' for v, t in [("+1", "US +1"), ("+44", "UK +44"), ("+61", "AU +61"), ("+971", "AE +971"), ("+91", "IN +91"), ("+92", "PK +92"), ("+49", "DE +49")])
        fields = f"""<h3 class="lp-sub">Account Type{req}</h3>
<div class="lp-types"><label><input type="radio" name="account_type" value="Individual" checked><span>{ic("user", 26)}Individual</span></label><label><input type="radio" name="account_type" value="Business Entity"><span>{ic("users", 26)}Business Entity</span></label></div>
{f("First Name", "user", '<input name="first_name" required autocomplete="given-name" placeholder="First Name">', True)}
{f("Last Name", "user", '<input name="last_name" required autocomplete="family-name" placeholder="Last Name">', True)}
<label class="lp-f">Phone Number<span class="iw tel"><select name="phone_code" aria-label="Country code">{codes}</select><input name="phone" type="tel" autocomplete="tel-national" placeholder="(201) 555-0123"></span></label>
{f("Email", "mail", '<input type="email" name="email" required autocomplete="email" placeholder="abc@mail.com">', True)}
{f("Company Name", "building", '<input name="company" required autocomplete="organization" placeholder="Company Name">', True)}
{f("Website", "globe", '<input name="website" placeholder="https://yourwebsite.com">')}
{f(lbl, "bars", f'<select name="details">{options}</select>')}
{f("Street Address", "pin", '<input name="address" autocomplete="street-address" placeholder="Street Address">')}
{f("City", "building", '<input name="city" autocomplete="address-level2" placeholder="City">')}
{f("State", "compass", '<input name="state" autocomplete="address-level1" placeholder="State">')}
{f("Country", "globe", '<input name="country" required autocomplete="country-name" placeholder="Country">', True)}
<h3 class="lp-sub">Security</h3>
{f("Password", "lock", f'<span class="pw"><input type="password" name="password" required minlength="8" autocomplete="new-password" placeholder="At least 8 characters">{eye}</span>', True)}
{f("Confirm Password", "lock", '<input type="password" name="confirm" required minlength="8" autocomplete="new-password" placeholder="Repeat password">', True)}
<label class="check lp-check"><input type="checkbox" name="marketing"><span>I agree to receive marketing updates from {BRAND} by email or phone. You can unsubscribe at any time.</span></label>
<label class="check lp-check"><input type="checkbox" name="agree" required><span>I agree to the <a href="terms-conditions.html">Terms</a> and <a href="privacy-policy.html">Privacy Policy</a>.</span></label>"""
        heading = "Personal Information"
        btn = "Create Account"
        links = f'<div class="lp-links center"><span>Already have an account?</span><a href="{role}-login.html">Sign In</a></div>'
    html = auth_head(title) + f"""
<section class="lp-art{' sticky' if not is_login else ''}">
<div class="lp-cap">Performance<br>Marketing<br>Agency<i></i></div>
<div class="lp-globe">{GLOBE}<a href="index.html" class="lp-center" aria-label="{BRAND} home">{mark("mk-g", 76)}<span class="wm"><b>Raventon</b><small>Partners</small></span></a></div>
<div class="lp-copy"><h1>{c['h1']}<span>{c['h2']}</span></h1><i></i><p>{c['side_p']}</p>
<div class="lp-stats"><div><b>250+</b><small>Campaigns launched</small></div><div><b>120+</b><small>Brands served</small></div><div><b>95%</b><small>Client retention</small></div></div></div>
</section>
<section class="lp-panel">
<a href="index.html" class="lp-back">{ic("arrow-left", 16)} Back to website</a>
<form class="lp-form{' reg' if not is_login else ''}" data-auth="{mode}" data-role="{role}" novalidate>
<a href="index.html" class="lp-logo" aria-label="{BRAND} home">{mark("mk-lp", 58)}<span class="wm"><b>Raventon</b><small>Partners</small></span></a>
<div class="lp-role"><a href="{role}-{mode}.html" class="on">{c['label']}</a><a href="{other}-{mode}.html">{ROLE_COPY[other]['label']}</a></div>
<h2>{heading}</h2>
{fields}
<div class="form-msg" role="alert" hidden></div>
<button class="lp-btn" type="submit"><span>{btn}</span></button>
{links}
</form>
</section>
""" + AUTH_FOOT
    write(f"{role}-{mode}.html", html)


for _r in ROLE_COPY:
    auth_page(_r, "login")
    auth_page(_r, "register")

dashboard = head("Dashboard", f"Your {BRAND} account.", "") + f"""
<section class="dash"><i class="glow a1" aria-hidden="true"></i><div class="wrap">
<div class="dash-loading" id="dashLoading"><span class="spinner"></span>Loading your account…</div>
<div class="dash-guest" id="dashGuest" hidden><h1>Please sign in</h1><p>Your session has ended or you are not signed in.</p>
<div class="hero-btns"><a class="btn btn-primary" href="advertiser-login.html">Advertiser Login {ARR}</a><a class="btn btn-ghost" href="publisher-login.html">Publisher Login</a></div></div>
<div id="dashApp" hidden>
<div class="dash-top"><div><span class="eyebrow" data-f="role_label"></span><h1>Welcome, <span data-f="first_name"></span></h1><p>Member since <span data-f="since"></span></p></div>
<button type="button" class="btn btn-ghost js-logout">{ic("logout", 17)} Sign out</button></div>
<div class="dash-grid">
<div class="dcard"><h3>{ic("user", 20)} Account details</h3><dl>
<dt>Account type</dt><dd data-f="account_type"></dd><dt>Full name</dt><dd data-f="full_name"></dd><dt>Company</dt><dd data-f="company"></dd><dt>Email</dt><dd data-f="email"></dd>
<dt>Phone</dt><dd data-f="phone"></dd><dt>Website</dt><dd data-f="website"></dd><dt data-f="details_label"></dt><dd data-f="details"></dd><dt>Location</dt><dd data-f="location"></dd></dl></div>
<div class="dcard dcard-g"><h3>{ic("bars", 20)} Performance reporting</h3><p>Your reporting will appear here once your account manager connects your ad accounts and tracking.</p>
<a class="btn btn-light" href="contact.html">Book your free audit {ARR}</a></div>
<div class="dcard"><h3>{ic("checklist", 20)} Next steps</h3><ul class="checks"><li>Complete your profile details</li><li>Share access to your ad accounts</li><li>Agree goals and reporting with your manager</li></ul></div>
</div></div>
</div></section>
""" + foot()
write("dashboard.html", dashboard)

# ---------- 404 ----------
write("404.html", head("Page Not Found", "Page not found.", "") + """
<div class="nf"><div class="ph-art" aria-hidden="true"><i></i><i></i><i></i></div><div class="nf-in"><h1 class="ld" style="--d:0">404</h1><h2 class="ld" style="--d:1">Page not found</h2><p class="ld" style="--d:2">The page you are looking for does not exist or has moved.</p>
<a href="index.html" class="btn btn-primary ld" style="--d:3">Back to Home</a></div></div>
""" + foot())

print("Built", len(os.listdir(OUT)), "items in", OUT)
