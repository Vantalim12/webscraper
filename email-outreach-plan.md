# Direct Contract Outreach Plan

Find paid remote contract work with US-based direct clients. GHL and n8n automation are the primary outreach track, supported by full-stack development; broader full-stack work is the secondary track. Build the contact collector now, but use it only when measured address-finding effort justifies it.

## Target and Offer

The first batch targets US agencies whose websites explicitly mention GHL or n8n services, prioritizing cold outreach without advertised openings. Agencies advertising relevant opportunities are secondary. An agency that contracts with Jasper directly is a direct client.

Offer work from home in the Philippines, with 30–40 available hours per week and flexible hours. Agree a sustainable US-overlap schedule with each client rather than promising availability across every US time zone. Ongoing full-time contracts, part-time contracts, and individual projects are acceptable. USD $7/hour is the private minimum; discuss the actual scope and rate after interest.

Use one publicly listed business inbox per agency, preferring a relevant role inbox. Collect only company details, the selected address, its source page, fit evidence, and outreach history. Named work addresses require manual review of their published business purpose; do not guess addresses or acquire personal/leaked lists. Vendor directories can help identify companies, but directory presence does not establish a hiring need. Use company websites as the contact source; do not automate logged-in platforms or access blocked pages.

## Evidence and Portfolio Readiness

The user reports building [Legacy Rides](https://legacyrides.rentals/) for a US client and connecting its rental inquiry form to GoHighLevel. The [portfolio project listing](https://jaspergumora.is-pinoy.dev/projects) associates the site with GHL. The public website shows the rental request and follow-up process.

The supplied workflow screenshot shows form/tag triggers, contact and opportunity creation, tagging, and a Conversation AI step. It does not establish that Jasper configured every action or the AI component. Avoid claims about booking improvements, response-time savings, or AI results without evidence.

n8n experience includes self-hosting on a VPS and user-reported tender automation. The tender workflow's trigger, actions, contribution, and outcomes have not been described; omit those details and quantified delivery claims from outreach until supplied. Self-hosting is supporting experience, not a substitute for a demonstrated automation case study.

Before sending, update the live [portfolio](https://jaspergumora.is-pinoy.dev/) internship availability wording and add the contribution explanation below. This repository supplies copy; the live site has not been edited.

**Availability copy**

> Available for paid remote contract work from the Philippines. My focus is GHL integrations and n8n automation, with full-stack development support. I can work 30–40 hours per week with flexible hours and US-time overlap.

**Legacy Rides contribution copy**

> I built the Legacy Rides rental website for a US-based client and connected its inquiry form to GoHighLevel, so submitted renter details are sent into GHL for follow-up.

## Launch Checklist

- [ ] Apply the portfolio availability and contribution wording.
- [ ] Create a separate professional Gmail outreach inbox with a clean display name.
- [ ] Check that messages and replies work using a normal test message to an address you control.
- [ ] Prepare a valid mailing address and reply-based opt-out footer. Do not send placeholder address text.
- [ ] Copy the seed, tracker, and pilot-log templates described in [README.md](README.md).
- [ ] Research the first agencies, note true fit evidence and its URL, and manually approve one contact each.

## Two-Week Manual Pilot

Spend at most two hours per week on research, finding addresses, writing, sending, tracking, follow-ups, and reply handling. Cap new outreach at five emails per week; send fewer when the time budget requires it. There is no automated sending, scheduling, or reply monitoring.

| Timing | Action |
| --- | --- |
| Day 0 | Review contact and suppression history, personalize, send manually, log the send and follow-up date |
| Day 7 | One short manual follow-up, only if there has been no reply, opt-out, or bounce |
| Day 14 | Close an unanswered sequence; send no further reminders |

Stop the sequence after any reply, opt-out, or bounce. Handle an interested reply as a conversation, not as another scheduled cold follow-up. Week-two sends may have their one follow-up after the two-week pilot review; those tasks stay within the same weekly budget.

The pilot target is at least one genuine discussion about paid work. Record all replies separately: rejections and automatic responses do not count as interest. A signed contract is the eventual goal, not a two-week completion requirement. Review counts and time spent rather than treating a small-sample reply percentage as a dependable benchmark.

At the review, examine targeting, fit evidence, message clarity, and contact suitability. Keep the initial batch focused on the automation track; evaluate broader full-stack outreach as a separate later batch rather than mixing its results into this pilot.

## Messages

Use one specific, true observation and one clear ask. Keep the first message under 120 words including the footer, link to the portfolio, and use no first-contact attachments. Count words again after personalizing and replacing the mailing address. Do not imply a vacancy exists or that their internal process is broken without evidence.

**First email draft**

Subject: `GHL integration support for [Agency]`

```text
Hi [Name/Agency team],

I saw [specific GHL/n8n service and honest observation]. I'm a Philippines-based
full-stack developer available for remote contract work.

For Legacy Rides, I built the rental website and connected its inquiry form
to GHL so renter details flow into its follow-up workflow.

Would website and GHL integration support be useful for your upcoming work?

Jasper Gumora
https://jaspergumora.is-pinoy.dev/
[Valid mailing address]
Contract services advertisement. Reply "no thanks" and I won't follow up.
```

Use the GHL-specific draft for agencies with GHL evidence. For n8n-only agencies, use the following version; add a tender example only once its actual scope is available.

**n8n agency draft**

Subject: `Integration support for [Agency]`

```text
Hi [Name/Agency team],

I saw [specific n8n service and honest observation]. I'm a Philippines-based
full-stack developer available for remote contract work, and I self-host n8n
on a VPS.

For Legacy Rides, I built its rental website and connected its inquiry form
to GHL. I'd like to support your website and integration work.

Would additional integration support be useful for upcoming projects?

Jasper Gumora
https://jaspergumora.is-pinoy.dev/
[Valid mailing address]
Contract services advertisement. Reply "no thanks" and I won't follow up.
```

**Only follow-up draft**

```text
Hi [Name/Agency team],

Following up once on my contract-services inquiry. [One new, true detail
relevant to their published work.] Would integration support be useful?

Jasper Gumora
https://jaspergumora.is-pinoy.dev/
[Valid mailing address]
Contract services advertisement.
Reply "no thanks" and I won't contact you again.
```

## Contact Collector

See [README.md](README.md) for setup and CSV interfaces. Use Firecrawl's basic page-fetching API for a selected homepage and one contact page, with HTML/raw HTML and footer content. Keep manual fit research and address approval. There is no deliverability verification, email guessing, database, inbox integration, or automatic outreach.

Use the helper only when address-finding consumes at least 30 minutes in each pilot week and a repeatable collection step could save that effort. Researching suitable companies and writing emails do not count toward the threshold. The [current Firecrawl free tier](https://www.firecrawl.dev/pricing) provides 1,000 monthly credits; basic and cached pages cost one credit each. Check current usage before a run. If credits are exhausted, return to manual collection rather than enabling paid usage automatically.

Check robots policies, honor exclusions and crawl delays, stop on blocked pages, and preserve source URLs. The [single-page API](https://docs.firecrawl.dev/api-reference/endpoint/scrape) does not document an automatic robots guarantee, so the collector performs its own requested-URL preflight. Its native [two-day cache](https://docs.firecrawl.dev/features/scrape#caching-and-maxage) avoids maintaining local HTML copies.

## Contact Handling

Check the tracker before every initial message and follow-up. An old CSV export, another inbox, or a newly collected address must not restart an opted-out or bounced contact. Store the email, reason, and date in suppression fields. A rejection closes the sequence as well.

Review inactive prospect research after 90 days and delete details no longer needed. Retain minimal suppression records while outreach continues, including when deleting other research or fulfilling a removal request; assess any conflict with a request rather than silently recontacting someone after deletion.

For planning these contractor pitches, use a commercial-email footer and accurate sender/subject information. The [FTC guide](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business) covers commercial email beyond bulk sends, including B2B messages, and requires a valid postal address and opt-out. Keep the reply-based opt-out usable for at least 30 days and honor requests promptly, within its ten-business-day limit. Manual sending and low volume do not settle applicability.

Published personal information is not unrestricted data. The Philippine NPC's [2023-016 opinion](https://privacy.gov.ph/wp-content/uploads/2023/11/Advisory-Opinion-No.-2023-016.pdf) distinguishes consent from legitimate interest; silence or failure to opt out is not consent. Where records identify individuals, assess purpose, necessity, and individual rights using the [NPC implementing rules](https://privacy.gov.ph/implementing-rules-regulations-data-privacy-act-2012/) before collecting or using them. A business-looking address and an opt-out alone do not establish a lawful basis.

## Completion Criteria

- Collector accepts the seed CSV, exports reviewable candidates with source URLs, reports empty/blocked/error pages, and preserves completed rows on failure.
- Offline tests pass for extraction, duplicate removal, contact discovery, robots exclusions, rate limits, credential/credit failures, and overwrite protection.
- Portfolio copy, inbox setup instructions, tracking templates, and manual message drafts are ready; live portfolio/inbox/address prerequisites remain explicit.
- The pilot is complete only after its two weeks of tracked work and outcome review. Software completion does not imply emails were sent or a contract obtained.
