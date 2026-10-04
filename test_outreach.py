import csv
import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError, URLError
from urllib.robotparser import RobotFileParser

import outreach


def response(html="", status=200, source="https://agency.com/"):
    return io.BytesIO(json.dumps({"success": True, "data": {
        "html": html, "rawHtml": html,
        "metadata": {"statusCode": status, "url": source},
    }}).encode())


def http_error(status, headers=None):
    return HTTPError(outreach.API_URL, status, "error", headers or {}, io.BytesIO())


class CollectorTests(unittest.TestCase):
    def test_emails_and_contact_link(self):
        page = outreach.ContactPage()
        page.feed('''<script>secret@agency.com</script><!-- hidden@agency.com -->
            <style>x@agency.com</style><footer>HELLO@agency.com. info@agency.com</footer>
            <span hidden>private@agency.com</span><span style="display: none">hidden@agency.com</span>
            <a href="mailto:hello%40agency.com?subject=Hi">Email</a>
            <a href="mailto:owner@agency.com,office@agency.com?cc=ignored@agency.com">More</a>
            noreply@agency.com icon@agency.com.png test@example.com error@ingest.sentry.io
            <a href="https://elsewhere.com/contact">External</a>
            <a href="/contact-us#team">Contact</a>''')
        self.assertEqual(page.emails(), ["hello@agency.com", "info@agency.com", "office@agency.com", "owner@agency.com"])
        self.assertEqual(page.contact_url("https://agency.com/"), "https://agency.com/contact-us")

    def test_invalid_seed_urls(self):
        for url in ("file:///etc/passwd", "http://127.0.0.1/", "http://[::1]/", "http://localhost/",
                    "https://user:pass@agency.com/", "https://agency.com:8443/", "https://agency.example/"):
            with self.subTest(url=url), self.assertRaises(outreach.PageError):
                outreach.public_url(url)
        with patch("outreach.socket.getaddrinfo", return_value=[(0, 0, 0, "", ("10.0.0.1", 0))]):
            with self.assertRaises(outreach.PageError):
                outreach.check_public_host("https://agency.com/")

    def test_deduplication_sources_and_discovered_contact(self):
        with patch.object(outreach.Collector, "check_robots", return_value=0), \
                patch("outreach.time.sleep"), patch("outreach.urlopen", side_effect=[
                    response('<footer>hello@agency.com</footer><a href="/contact-us">Contact</a>'),
                    response("hello@agency.com owner@agency.com", source="https://agency.com/contact-us"),
                ]) as api:
            rows = list(outreach.Collector("fake-key").company_rows({
                "company": "Agency", "website": "https://agency.com/", "fit_notes": "Offers GHL services",
            }))
        self.assertEqual([row["email"] for row in rows], ["hello@agency.com", "owner@agency.com"])
        self.assertEqual(rows[0]["source_page"], "https://agency.com/")
        body = json.loads(api.call_args_list[1].args[0].data)
        self.assertEqual(body["url"], "https://agency.com/contact-us")
        self.assertEqual(body["formats"], ["html", "rawHtml"])
        self.assertFalse(body["onlyMainContent"])
        self.assertFalse(body["skipTlsVerification"])

    def test_robots_block_and_crawl_delay(self):
        collector = outreach.Collector("fake-key")
        policy = RobotFileParser()
        policy.parse(["User-agent: *", "Disallow: /contact", "Crawl-delay: 12"])
        collector.robots["https://agency.com"] = policy
        self.assertEqual(collector.check_robots("https://agency.com/"), 12)
        with patch("outreach.urlopen") as api, self.assertRaises(outreach.Blocked):
            collector.scrape("https://agency.com/contact")
        api.assert_not_called()

    def test_missing_robots_and_unavailable_robots(self):
        for outcome, allowed in ((http_error(404), True), (http_error(403), False), (URLError("offline"), False)):
            with self.subTest(allowed=allowed), patch("outreach.check_public_host"), \
                    patch("outreach.build_opener") as opener:
                opener.return_value.open.side_effect = outcome
                collector = outreach.Collector("fake-key")
                if allowed:
                    self.assertEqual(collector.check_robots("https://agency.com/"), 0)
                else:
                    with self.assertRaises(outreach.PageError):
                        collector.check_robots("https://agency.com/")
                try:
                    collector.check_robots("https://agency.com/contact")
                except outreach.PageError:
                    pass
                self.assertEqual(opener.return_value.open.call_count, 1)

    def test_one_bounded_rate_limit_retry(self):
        with patch.object(outreach.Collector, "check_robots", return_value=0), patch("outreach.time.sleep") as sleep, \
                patch("outreach.urlopen", side_effect=[http_error(429, {"Retry-After": "12"}), response("hi@agency.com")]) as api:
            page, _ = outreach.Collector("fake-key").scrape("https://agency.com/")
            self.assertEqual(page.emails(), ["hi@agency.com"])
            self.assertEqual(api.call_count, 2)
            sleep.assert_any_call(12)
        with patch.object(outreach.Collector, "check_robots", return_value=0), patch("outreach.time.sleep"), \
                patch("outreach.urlopen", side_effect=[http_error(429), http_error(429)]) as api:
            with self.assertRaises(outreach.PageError):
                outreach.Collector("fake-key").scrape("https://agency.com/")
            self.assertEqual(api.call_count, 2)

    def test_target_error_and_invalid_payload(self):
        for payload, exception in ((response("bad@agency.com", 403), outreach.Blocked),
                                   (response("bad@agency.com", 404), outreach.PageError),
                                   (io.BytesIO(b"not JSON"), outreach.PageError),
                                   (response("bad@elsewhere.com", source="https://elsewhere.com/"), outreach.PageError)):
            with self.subTest(exception=exception), patch.object(outreach.Collector, "check_robots", return_value=0), \
                    patch("outreach.urlopen", return_value=payload), self.assertRaises(exception):
                outreach.Collector("fake-key").scrape("https://agency.com/")

    def test_partial_output_and_secret_redaction(self):
        for status in (401, 402, 403):
            with self.subTest(status=status), tempfile.TemporaryDirectory() as directory:
                input_path = Path(directory) / "companies.csv"
                output_path = Path(directory) / "contacts.csv"
                input_path.write_text("company,website,fit_notes\nAgency,https://agency.com/,Offers GHL\nNext,https://next.com/,Offers n8n\n")
                stderr = io.StringIO()
                with patch.dict("os.environ", {"FIRECRAWL_API_KEY": "fake-secret"}), \
                        patch.object(outreach.Collector, "check_robots", return_value=0), patch("outreach.time.sleep"), \
                        patch("outreach.urlopen", side_effect=[response("hello@agency.com"), http_error(status)]) as api, \
                        redirect_stderr(stderr):
                    result = outreach.main([str(input_path), "--output", str(output_path)])
                self.assertEqual(result, 1)
                self.assertEqual(api.call_count, 2)
                with output_path.open(newline="") as file:
                    rows = list(csv.DictReader(file))
                self.assertEqual(rows[0]["email"], "hello@agency.com")
                self.assertEqual(rows[1]["result"], "error")
                self.assertNotIn("fake-secret", output_path.read_text() + stderr.getvalue())

    def test_no_overwrite_and_missing_key(self):
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "companies.csv"
            input_path.write_text("company,website,fit_notes\n")
            output_path = Path(directory) / "existing.csv"
            output_path.write_text("keep this")
            with patch.dict("os.environ", {"FIRECRAWL_API_KEY": "fake-key"}), redirect_stderr(io.StringIO()), patch("outreach.urlopen") as api:
                self.assertEqual(outreach.main([str(input_path), "--output", str(output_path)]), 1)
                api.assert_not_called()
            self.assertEqual(output_path.read_text(), "keep this")
            with patch.dict("os.environ", {"FIRECRAWL_API_KEY": ""}), redirect_stderr(io.StringIO()):
                missing = Path(directory) / "new.csv"
                self.assertEqual(outreach.main([str(input_path), "--output", str(missing)]), 1)
                self.assertFalse(missing.exists())

    def test_empty_pages_and_csv_formula_escaping(self):
        with patch.object(outreach.Collector, "scrape", side_effect=[
            (outreach.ContactPage(), "https://agency.com/"),
            (outreach.ContactPage(), "https://agency.com/contact"),
        ]):
            rows = list(outreach.Collector("fake-key").company_rows({
                "company": "Agency", "website": "https://agency.com/", "fit_notes": "GHL",
            }))
        self.assertEqual([row["result"] for row in rows], ["no_email", "no_email"])
        self.assertEqual(outreach.csv_cell("=HYPERLINK(\"url\")"), "'=HYPERLINK(\"url\")")
        self.assertEqual(outreach.csv_cell("hello@agency.com"), "hello@agency.com")

    def test_successful_cli_and_duplicate_seed(self):
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "companies.csv"
            output_path = Path(directory) / "contacts.csv"
            input_path.write_text("company,website,fit_notes\n=Agency,https://agency.com/,Offers GHL\n"
                                  "Duplicate,https://www.agency.com/,Other note\nBad,not-a-url,Missing website\n")
            stdout = io.StringIO()
            with patch.dict("os.environ", {"FIRECRAWL_API_KEY": "fake-key"}), \
                    patch.object(outreach.Collector, "check_robots", return_value=0), patch("outreach.time.sleep"), \
                    patch("outreach.urlopen", side_effect=[response("hello@agency.com"),
                          response("hello@agency.com", source="https://agency.com/contact")]) as api, \
                    redirect_stdout(stdout):
                self.assertEqual(outreach.main([str(input_path), "--output", str(output_path)]), 0)
            self.assertEqual(api.call_count, 2)
            with output_path.open(newline="") as file:
                rows = list(csv.DictReader(file))
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]["company"], "'=Agency")
            self.assertEqual(rows[0]["email"], "hello@agency.com")
            self.assertEqual(rows[1]["result"], "error")
            self.assertIn("1 candidate", stdout.getvalue())

    def test_separate_html_documents_and_optional_metadata(self):
        payload = io.BytesIO(json.dumps({"success": True, "data": {
            "html": "<script>unfinished", "rawHtml": "<footer>hello@agency.com</footer>",
        }}).encode())
        with patch.object(outreach.Collector, "check_robots", return_value=0), \
                patch("outreach.urlopen", return_value=payload):
            page, source = outreach.Collector("fake-key").scrape("https://agency.com/")
        self.assertEqual(page.emails(), ["hello@agency.com"])
        self.assertEqual(source, "https://agency.com/")

    def test_redirected_source_excluded_by_robots(self):
        collector = outreach.Collector("fake-key")
        policy = RobotFileParser()
        policy.parse(["User-agent: *", "Disallow: /private"])
        collector.robots["https://agency.com"] = policy
        with patch("outreach.urlopen", return_value=response("private@agency.com", source="https://agency.com/private")), \
                self.assertRaises(outreach.Blocked):
            collector.scrape("https://agency.com/")


if __name__ == "__main__":
    unittest.main()
