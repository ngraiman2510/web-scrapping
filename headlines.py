"""
Print the Top 5 Headlines from a News Site

Reads the news URL from config.json, fetches it with requests, parses the
HTML with BeautifulSoup and prints the top 5 headlines, numbered 1 to 5.

"""

import json
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup

CONFIG_FILE = Path(__file__).resolve().with_name("config.json")
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}
TOP_N = 5

# CSS selectors to try, most specific first.
# BBC's current layout puts each card headline in an <h2> (or <h3>) with
# data-testid="card-headline". If BBC changes its markup, inspect a headline
# in your browser (right-click > Inspect) and update/add a selector here.
SELECTORS = [
    '[data-testid="card-headline"]',
    "h2[data-testid]",
    "main h2",
    "h2",
]


def load_url():
    """Load the target news URL from the external configuration file."""
    try:
        with CONFIG_FILE.open("r", encoding="utf-8") as config_file:
            config = json.load(config_file)
    except FileNotFoundError:
        sys.exit(f"Configuration file not found: {CONFIG_FILE}")
    except json.JSONDecodeError as err:
        sys.exit(f"Invalid JSON in {CONFIG_FILE}: {err}")

    url = config.get("news_url")
    if not isinstance(url, str) or not url.strip():
        sys.exit(f'Missing "news_url" in {CONFIG_FILE}')

    return url.strip()


def fetch_page(url):
    """Download the page and return its HTML. Exit cleanly on failure."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
    except requests.RequestException as err:
        sys.exit(f"Request failed: {err}")

    # Check the status code before parsing anything.
    if response.status_code != 200:
        sys.exit(f"Could not fetch page. Status code: {response.status_code}")

    return response.text


def extract_headlines(html, limit=TOP_N):
    """Return up to `limit` unique, non-empty headlines from the HTML."""
    soup = BeautifulSoup(html, "html.parser")

    for selector in SELECTORS:
        headlines = []
        seen = set()

        for element in soup.select(selector):
            text = element.get_text(strip=True)  # strip whitespace
            if not text or text in seen:  # skip empty / duplicate entries
                continue
            seen.add(text)
            headlines.append(text)
            if len(headlines) == limit:
                break

        if headlines:
            return headlines

    return []


def main():
    url = load_url()
    html = fetch_page(url)
    headlines = extract_headlines(html)

    if not headlines:
        print("No headlines found. The page may load them with JavaScript, "
              "or the site's HTML structure has changed.")
        return

    for i, headline in enumerate(headlines, 1):
        print(f"{i}. {headline}")

    if len(headlines) < TOP_N:
        print(f"\n(Only {len(headlines)} headline(s) found.)")


if __name__ == "__main__":
    main()