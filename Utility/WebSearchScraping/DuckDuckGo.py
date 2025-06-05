import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from fake_useragent import UserAgent

blocked_domains = ['youtube.com', 'facebook.com',
                   'twitter.com', 'x.com', 'instagram.com', 'linkedin.com',
                   'tiktok.com']


def duckduckgo_search(query, max_results=10, retries=100):
    tries = 0
    results = []
    seen_links = set()

    ua = UserAgent()
    session = requests.Session()

    while tries <= retries and len(results) < max_results:
        try:
            url = "https://duckduckgo.com/html/"
            params = {'q': query, 'kl': 'us-en'}
            headers = {'User-Agent': ua.random}
            response = session.get(url, headers=headers,
                                   params=params, timeout=5)

            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.find_all(
                'a', attrs={'class': 'result__a'}, href=True)
            if not links:
                raise Exception(
                    "No links found — possibly blocked or unexpected page structure.")

            if len(links) < max_results:
                print(
                    f"Less links than max_results, setting max_results to {len(links)}.")
                max_results = len(links)

            for link in links:
                url = link['href']
                title = link.get_text(strip=True)

                parsed_url = urlparse(url)
                if not parsed_url.scheme or not parsed_url.netloc:
                    continue

                base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

                if not any(parsed_url.netloc.endswith(domain) for domain in blocked_domains):
                    if url not in seen_links:
                        seen_links.add(url)
                        results.append({
                            'title': title,
                            'base_url': base_url,
                            'link': url
                        })
                        if len(results) >= max_results:
                            break
            tries += 1
            time.sleep(0.6)

        except Exception as e:
            print("Failed to scrape the page:", e)
            print("Retries left:", retries-tries)
            tries += 1
            time.sleep(0.6)

    if len(results) == 0:
        raise Exception(f"Max retries exceeded: {retries}")

    return results
