#!/usr/bin/env python3
"""Collect public contact candidates; never send outreach."""

import argparse
import csv
import ipaddress
import json
import os
import re
import socket
import sys
import time
from collections import Counter
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urljoin, urlsplit, urlunsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener, urlopen
from urllib.robotparser import RobotFileParser


API_URL = "https://api.firecrawl.dev/v2/scrape"
USER_AGENT = "OutreachContactCollector/1.0"
FIELDS = ("company", "website", "email", "source_page", "fit_notes", "result", "error")
EMAIL = re.compile(r"(?<![\w@])([A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,63})(?![\w@])", re.I)
BUSINESS_INBOXES = {"hello", "info", "contact", "office", "team", "business", "operations", "sales"}
JUNK_LOCALS = {"example", "test", "noreply", "no-reply", "donotreply", "sentry"}
JUNK_SUFFIXES = {"png", "jpg", "jpeg", "gif", "webp", "svg", "ico", "css", "js", "woff", "woff2"}


class PageError(Exception):
    pass


class Blocked(PageError):
    pass


class FatalError(Exception):
    pass


def public_url(value):
    """Accept absolute public-site URLs, without embedded credentials."""
    try:
        if not isinstance(value, str):
            raise ValueError
        parts = urlsplit(value.strip())
        host = parts.hostname or ""
        if (parts.scheme not in {"http", "https"} or not host
                or parts.username is not None or parts.password is not None
                or parts.port not in {None, 80, 443}
                or host.endswith((".localhost", ".local", ".test", ".invalid", ".example"))):
            raise ValueError
        try:
            address = ipaddress.ip_address(host)
        except ValueError:
            if "." not in host:
                raise ValueError
        else:
            if not address.is_global or address.is_multicast:
                raise ValueError
        return urlunsplit((parts.scheme, parts.netloc, parts.path or "/", parts.query, ""))
    except ValueError:
        raise PageError("Expected a public HTTP(S) URL without credentials or a nonstandard port") from None


def check_public_host(url):
    public_url(url)
    addresses = socket.getaddrinfo(urlsplit(url).hostname, None, type=socket.SOCK_STREAM)
    if not addresses or any(not ipaddress.ip_address(item[4][0]).is_global
                            or ipaddress.ip_address(item[4][0]).is_multicast for item in addresses):
        raise PageError("Host does not resolve exclusively to public addresses")


class PublicRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, newurl):
        check_public_host(newurl)
        return super().redirect_request(request, response, code, message, headers, newurl)


def same_site(first, second):
    return urlsplit(first).hostname.removeprefix("www.") == urlsplit(second).hostname.removeprefix("www.")


class ContactPage(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.text = []
        self.links = []
        self.mailto = []
        self.stack = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        style = (attrs.get("style") or "").lower().replace(" ", "")
        ignored = (bool(self.stack and self.stack[-1][1])
                   or tag in {"head", "script", "style", "template"}
                   or "hidden" in attrs or attrs.get("aria-hidden") == "true"
                   or "display:none" in style or "visibility:hidden" in style)
        if tag not in {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}:
            self.stack.append((tag, ignored))
        if ignored or tag != "a":
            return
        href = attrs.get("href") or ""
        if href.lower().startswith("mailto:"):
            self.mailto.append(unquote(href[7:].split("?", 1)[0]))
        else:
            self.links.append(href)

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break

    def handle_data(self, data):
        if not self.stack or not self.stack[-1][1]:
            self.text.append(data)

    def emails(self):
        # ponytail: ASCII text and mailto only; obfuscated addresses need manual review.
        found = set()
        for email in EMAIL.findall(" ".join(self.text + self.mailto)):
            email = email.lower()
            local, domain = email.rsplit("@", 1)
            if (local.split("+", 1)[0] in JUNK_LOCALS or local.startswith(".")
                    or local.endswith(".") or ".." in email
                    or domain.rsplit(".", 1)[-1] in JUNK_SUFFIXES
                    or domain in {"example.com", "example.org", "example.net"}
                    or domain == "sentry.io" or domain.endswith(".sentry.io")):
                continue
            found.add(email)
        return sorted(found, key=lambda value: (value.split("@", 1)[0] not in BUSINESS_INBOXES, value))

    def contact_url(self, homepage):
        for href in self.links:
            try:
                target = public_url(urljoin(homepage, href))
            except PageError:
                continue
            path = unquote(urlsplit(target).path).lower()
            if same_site(homepage, target) and ("contact" in path or "get-in-touch" in path):
                if target != homepage:
                    return target
        return urljoin(homepage, "/contact")


class Collector:
    def __init__(self, key):
        self.key = key
        self.robots = {}
        self.last_request = None
        self.company_sites = set()

    def wait(self, delay=7):
        if self.last_request is not None:
            time.sleep(max(0, delay - (time.monotonic() - self.last_request)))
        self.last_request = time.monotonic()

    def check_robots(self, url):
        parts = urlsplit(url)
        origin = urlunsplit((parts.scheme, parts.netloc, "", "", ""))
        if origin not in self.robots:
            robots_url = origin + "/robots.txt"
            try:
                check_public_host(robots_url)
                request = Request(robots_url, headers={"User-Agent": USER_AGENT})
                self.wait()
                with build_opener(PublicRedirect()).open(request, timeout=10) as response:
                    text = response.read().decode("utf-8", errors="replace")
                policy = RobotFileParser(robots_url)
                policy.parse(text.splitlines())
                self.robots[origin] = policy
            except HTTPError as error:
                error.close()
                if error.code in {404, 410}:
                    self.robots[origin] = None
                elif error.code in {401, 403}:
                    self.robots[origin] = Blocked("Access to robots.txt denied")
                else:
                    self.robots[origin] = PageError(f"Cannot check robots.txt (HTTP {error.code})")
            except (OSError, URLError, PageError, ValueError):
                self.robots[origin] = PageError("Cannot check robots.txt; skipped this site")
        policy = self.robots[origin]
        if isinstance(policy, Exception):
            raise policy
        if policy is not None:
            agents = (USER_AGENT, "FirecrawlAgent", "*")
            if any(not policy.can_fetch(agent, url) for agent in agents):
                raise Blocked("Excluded by robots.txt")
            return max((policy.crawl_delay(agent) or 0 for agent in agents), default=0)
        return 0

    def scrape(self, url):
        delay = max(7, self.check_robots(url))
        request = Request(API_URL, data=json.dumps({
            "url": url, "formats": ["html", "rawHtml"], "onlyMainContent": False,
            "timeout": 30000, "skipTlsVerification": False,
        }).encode(), headers={"Authorization": f"Bearer {self.key}", "Content-Type": "application/json"})
        for attempt in range(2):
            self.wait(delay)
            try:
                with urlopen(request, timeout=45) as response:
                    payload = json.load(response)
            except HTTPError as error:
                error.close()
                if error.code in {401, 402, 403}:
                    reason = {401: "invalid API key", 402: "credits exhausted", 403: "API permission denied"}[error.code]
                    raise FatalError(f"Firecrawl: {reason}; completed rows were preserved") from None
                if error.code == 429 and attempt == 0:
                    try:
                        retry_after = float((error.headers or {}).get("Retry-After", "7"))
                    except (TypeError, ValueError):
                        retry_after = 7
                    if not 0 <= retry_after <= 60:
                        raise PageError("Firecrawl rate limit; retry later") from None
                    time.sleep(max(7, retry_after))
                    continue
                raise PageError(f"Firecrawl request failed (HTTP {error.code})") from None
            except (OSError, URLError, ValueError):
                raise PageError("Firecrawl request failed or returned invalid JSON") from None
            if not isinstance(payload, dict) or payload.get("success") is not True or not isinstance(payload.get("data"), dict):
                raise PageError("Firecrawl returned an unsuccessful response")
            data = payload["data"]
            metadata = data.get("metadata") or {}
            if not isinstance(metadata, dict):
                raise PageError("Firecrawl returned invalid page metadata")
            try:
                status = int(metadata.get("statusCode", 200))
            except (TypeError, ValueError):
                raise PageError("Firecrawl returned an invalid target status") from None
            if status in {401, 403, 429}:
                raise Blocked(f"Target site refused access (HTTP {status})")
            if not 200 <= status < 300:
                raise PageError(f"Target page failed (HTTP {status})")
            source = public_url(metadata.get("url") or metadata.get("sourceURL") or url)
            if not same_site(url, source):
                raise PageError("Page redirected to another site; review and update the seed URL")
            self.check_robots(source)
            page = ContactPage()
            html = [data.get(name) for name in ("html", "rawHtml") if isinstance(data.get(name), str)]
            if not html:
                raise PageError("Firecrawl returned no HTML")
            for content in dict.fromkeys(html):
                parsed = ContactPage()
                parsed.feed(content)
                parsed.close()
                page.text.extend(parsed.text)
                page.links.extend(parsed.links)
                page.mailto.extend(parsed.mailto)
            return page, source

    def company_rows(self, seed):
        base = {name: seed.get(name, "") or "" for name in ("company", "website", "fit_notes")}
        try:
            if not base["company"].strip() or not base["fit_notes"].strip():
                raise PageError("Company and fit_notes must be nonempty")
            website = public_url(base["website"])
            parts = urlsplit(website)
            website = urlunsplit((parts.scheme, parts.netloc, "/", "", ""))
        except PageError as error:
            yield dict(base, email="", source_page=base["website"], result="error", error=str(error))
            return
        base["website"] = website
        site = urlsplit(website).hostname.removeprefix("www.")
        if site in self.company_sites:
            return
        self.company_sites.add(site)
        url = website
        seen = set()
        for index in range(2):
            try:
                page, source = self.scrape(url)
            except FatalError as error:
                yield dict(base, email="", source_page=url, result="error", error=str(error))
                raise
            except PageError as error:
                yield dict(base, email="", source_page=url,
                           result="blocked" if isinstance(error, Blocked) else "error", error=str(error))
                if isinstance(error, Blocked):
                    break
            else:
                emails = page.emails()
                if not emails:
                    yield dict(base, email="", source_page=source, result="no_email", error="")
                for email in emails:
                    if email not in seen:
                        seen.add(email)
                        yield dict(base, email=email, source_page=source, result="candidate", error="")
                if index == 0:
                    url = page.contact_url(source)
                    if url == source:
                        break
                    continue
            url = urljoin(website, "/contact")


def csv_cell(value):
    # CSV quoting alone does not prevent spreadsheet formula evaluation.
    return "'" + value if value.startswith(("=", "+", "-", "@", "\t", "\r", "\n")) else value


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("companies", help="CSV with company,website,fit_notes columns")
    parser.add_argument("--output", required=True, help="New output CSV path (never overwritten)")
    args = parser.parse_args(argv)
    key = os.environ.get("FIRECRAWL_API_KEY", "").strip()
    if not key:
        print("Set FIRECRAWL_API_KEY before collecting contacts", file=sys.stderr)
        return 1
    counts = Counter()
    try:
        with open(args.companies, newline="", encoding="utf-8-sig") as input_file:
            reader = csv.DictReader(input_file)
            required = {"company", "website", "fit_notes"}
            if not required.issubset(reader.fieldnames or []):
                raise PageError("Input CSV must have company,website,fit_notes columns")
            with open(args.output, "x", newline="", encoding="utf-8") as output_file:
                writer = csv.DictWriter(output_file, fieldnames=FIELDS)
                writer.writeheader()
                output_file.flush()
                collector = Collector(key)
                for seed in reader:
                    for row in collector.company_rows(seed):
                        writer.writerow({name: csv_cell(row[name]) for name in FIELDS})
                        output_file.flush()
                        counts[row["result"]] += 1
    except (OSError, csv.Error, PageError, FatalError) as error:
        print(f"Stopped: {error}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("Interrupted; completed output rows were preserved", file=sys.stderr)
        return 130
    print("Completed: " + ", ".join(f"{counts[name]} {name}" for name in ("candidate", "no_email", "blocked", "error")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
