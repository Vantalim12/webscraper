# Direct Contract Outreach

Find paid remote contract work with US agencies whose websites explicitly mention GHL or n8n services. Lead with website-to-GHL integration experience and full-stack development support; broader full-stack outreach is the secondary track. Work from the Philippines, offer 30–40 hours weekly, and agree US working-hour overlap with each client. USD $7/hour is the private minimum.

The collector reads researched company websites, extracts public contact candidates, and writes their source URLs to a new CSV. It does not discover companies, verify deliverability, write messages, or send emails. There are no dependencies beyond Python 3.11+.

## Start the manual pilot

1. Apply the portfolio wording in [the outreach plan](email-outreach-plan.md), create a separate professional Gmail inbox, and prepare the mailing address and opt-out footer.
2. Copy the templates below and manually review one public business inbox per agency. Check the tracker for earlier contact, replies, opt-outs, or bounces before sending.
3. Spend at most two hours weekly for two weeks: up to five new emails per week, with one follow-up seven days after each first message. Stop the sequence after any reply, opt-out, or bounce.
4. Record time and outcomes in the pilot log. Aim for one genuine discussion about paid work.

```bash
cp companies.example.csv companies.csv
cp outreach-tracker.template.csv outreach-tracker.csv
cp pilot-log.template.csv pilot-log.csv
```

Replace the example company before using the collector. `agency.example` is deliberately invalid and will never be scraped. Supply one company per site, with an absolute HTTP(S) website URL and fit notes containing a true observation and its evidence URL. The collector normalizes websites to their homepage, and processes repeated domains only once; the first valid seed wins.

## Use the optional collector

Use it if address-finding takes at least 30 minutes in **each** pilot week and a repeatable page-fetching step could shorten that work. Company research and message writing do not count toward that threshold.

Create a [Firecrawl account and API key](https://www.firecrawl.dev/). Its [current free plan](https://www.firecrawl.dev/pricing) offers 1,000 monthly credits without a card. Basic scraping costs one credit per page, including cached pages. Homepage plus contact page for five companies weekly is roughly 40–50 credits per month before retries. Quotas can change; check your dashboard before running.

Enter the key without putting it into shell history:

```bash
read -r -s -p 'Firecrawl API key: ' FIRECRAWL_API_KEY
export FIRECRAWL_API_KEY
printf '\n'
python outreach.py companies.csv --output contacts.csv
unset FIRECRAWL_API_KEY
```

The command refuses to overwrite output. For another run, choose a fresh path such as `--output contacts-next.csv`. Output is flushed after each row, including when interrupted or stopped by exhausted credits. Auth, permission, or credit failures return exit code 1; an interruption returns 130. Otherwise exit code 0 means processing completed, including any page errors recorded in the CSV.

| Output field | Meaning |
| --- | --- |
| `company`, `website`, `fit_notes` | Input company, normalized homepage, and your fit evidence |
| `email` | Candidate address, or blank for a failed/empty page |
| `source_page` | Page URL supplying the address, or requested URL on failure |
| `result` | `candidate`, `no_email`, `blocked`, or `error` |
| `error` | Failure reason, without API credentials |

Copy only a reviewed address into the outreach tracker. Duplicate addresses within a company keep their first source URL. Business aliases such as `hello@`, `info@`, and `contact@` are listed first; other publicly exposed addresses still require judgment. ASCII page text and `mailto:` links are supported; obfuscated addresses and image-based contacts need manual research. Script, style, template, and explicitly hidden markup are excluded; CSS classes are not evaluated.

The collector fetches the homepage and at most one contact page, choosing a same-site contact link when present and otherwise `/contact`. Cross-site redirects are reported for review instead of extracting addresses. It checks `robots.txt` once per origin before API requests; an unavailable policy causes the site to be skipped, while 404/410 means no robots file. Robots exclusions and target 401/403/429 responses stop collection for that company. Requests are sequential and separated by at least seven seconds, or a longer published crawl delay. A Firecrawl 429 gets one retry honoring a numeric `Retry-After` up to 60 seconds.

Firecrawl receives the selected URLs and returns rendered and raw HTML with footer content preserved. Its native two-day cache is used; there is no local HTML cache. See the [scrape API](https://docs.firecrawl.dev/api-reference/endpoint/scrape), [cache behavior](https://docs.firecrawl.dev/features/scrape#caching-and-maxage), and [error catalog](https://docs.firecrawl.dev/api-reference/errors). The local robots preflight covers requested URLs; source review remains necessary when the provider follows redirects.

CSV fields beginning with spreadsheet formula characters are prefixed with an apostrophe. If your CSV editor displays that prefix literally, remove it from the reviewed value before using it, and keep cells as text.

## Tracking

The collector never edits your manual tracker or pilot log.

- Tracker: one approved contact per agency. Use `ready`, `sent`, `followed_up`, `replied`, `interested`, `closed`, `opted_out`, or `bounced`. Dates use `YYYY-MM-DD`. Set `follow_up_date` to seven calendar days after `date_sent`, and fill `follow_up_sent` only after actually sending.
- Stop rules: any reply clears the planned follow-up; mark interest only when discussing paid work. For opt-outs/bounces, also set `suppression_status` to `opted_out`/`bounced` and record `suppression_date`. Never contact that address again through a new seed or another inbox.
- Pilot log: one row per company/session. Record minutes in the appropriate activity column and counts of actually sent messages and interested replies. Sum address-finding minutes separately for each week to evaluate the collector gate. Reduce new-email volume when replies/follow-ups use the budget.
- Follow-ups from week-two emails may fall after the initial two-week review; retain the same weekly time budget and stop rules. Close unanswered sequences seven days after their only follow-up. A closed sequence is not permission to restart outreach.
- Review inactive prospect research after 90 days. Delete research no longer needed; retain only the email, suppression reason, and suppression date needed to honor opt-outs/bounces for as long as outreach continues. Do not delete suppression records during routine cleanup.

## Verify offline

```bash
python -m unittest -v
```

Tests mock DNS, robots retrieval, API responses, and waiting. They send no emails, make no live scraping requests, and consume no credits. A live API smoke test requires your key and a deliberately selected site; none is run automatically.
