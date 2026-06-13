#!/usr/bin/env python3
"""Request Google indexing for the blog's posts.

Reads the blog sitemap, then asks the Google Indexing API to (re)crawl each URL.
Designed to run daily from a GitHub Action so new posts get pushed to Google
without anyone clicking "Request indexing" by hand.

Setup (one time) — see scripts/INDEXING-SETUP.md:
  1. Create a Google Cloud service account, enable the "Indexing API".
  2. Add the service account email as an OWNER of the Search Console property.
  3. Put the service-account JSON key in the GitHub secret GOOGLE_INDEXING_SA_JSON.

Env vars:
  GOOGLE_INDEXING_SA_JSON  service account JSON (required; skips cleanly if absent)
  BLOG_SITEMAP             sitemap URL (default: the blogspot sitemap)
  MAX_URLS                 cap per run (default 180; API quota is ~200/day)

Note: Google's Indexing API is officially supported for JobPosting and
BroadcastEvent pages. It frequently works for ordinary pages too, but Google
does not guarantee it — treat this as a best-effort accelerator on top of the
sitemap, not a replacement for good, distinct content.
"""
import os
import sys
import json
import xml.etree.ElementTree as ET
import urllib.request

SITEMAP = os.environ.get("BLOG_SITEMAP", "https://jejugrandebleuyacht.blogspot.com/sitemap.xml")
MAX_URLS = int(os.environ.get("MAX_URLS", "180"))
SA_JSON = os.environ.get("GOOGLE_INDEXING_SA_JSON", "").strip()
ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"
SCOPES = ["https://www.googleapis.com/auth/indexing"]
SITEMAP_NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"


def fetch_sitemap_urls(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (indexing-bot)"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = resp.read()
    root = ET.fromstring(data)
    # Handle both a urlset and a sitemap index (recurse one level).
    urls = [loc.text.strip() for loc in root.iter(f"{SITEMAP_NS}loc")]
    if root.tag.endswith("sitemapindex"):
        nested = []
        for sm in urls:
            try:
                nested += fetch_sitemap_urls(sm)
            except Exception as e:  # noqa: BLE001
                print(f"  (skip nested sitemap {sm}: {e})")
        return nested
    return urls


def main():
    if not SA_JSON:
        print("GOOGLE_INDEXING_SA_JSON not set — skipping (configure the secret to enable).")
        return 0
    try:
        from google.oauth2 import service_account
        from google.auth.transport.requests import AuthorizedSession
    except ImportError:
        print("Missing deps. Run: pip install google-auth requests")
        return 1

    creds = service_account.Credentials.from_service_account_info(
        json.loads(SA_JSON), scopes=SCOPES
    )
    session = AuthorizedSession(creds)

    urls = fetch_sitemap_urls(SITEMAP)
    print(f"Sitemap: {SITEMAP}\nFound {len(urls)} URLs; submitting up to {MAX_URLS}.")

    ok = err = 0
    for url in urls[:MAX_URLS]:
        try:
            r = session.post(ENDPOINT, json={"url": url, "type": "URL_UPDATED"}, timeout=30)
            if r.status_code == 200:
                ok += 1
                print(f"  OK  {url}")
            else:
                err += 1
                print(f"  ERR {r.status_code} {url} :: {r.text[:120]}")
        except Exception as e:  # noqa: BLE001
            err += 1
            print(f"  ERR exception {url} :: {e}")

    print(f"\nDone. submitted={ok} errors={err}")
    return 0 if err == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
