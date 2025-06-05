import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from fake_useragent import UserAgent


blocked_domains = ['youtube.com', 'facebook.com',
                   'twitter.com', 'x.com', 'instagram.com', 'linkedin.com',
                   'tiktok.com']


def google_search(query, retries=500):
    tries = 0
    page = 0
    results = []
    seen_links = set()

    ua = UserAgent()
    session = requests.Session()

    while tries <= retries and len(results) < 10:
        try:
            url = "https://www.google.com/search"
            params = {'q': query, 'gl': 'us', 'hl': 'en', 'start': page * 10}
            headers = {'User-Agent': ua.random,
                       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                       'Accept-Language': 'en-US,en;q=0.5',
                       'Accept-Encoding': 'gzip, deflate, br',
                       'DNT': '1',
                       'Connection': 'keep-alive',
                       'Upgrade-Insecure-Requests': '1',
                       'Sec-Fetch-Dest': 'document',
                       'Sec-Fetch-Mode': 'navigate',
                       'Sec-Fetch-Site': 'none',
                       'Sec-Fetch-User': '?1',
                       'Cache-Control': 'max-age=0'}
            response = session.get(url, headers=headers,
                                   params=params, timeout=5)

            soup = BeautifulSoup(response.text, 'html.parser')
            search_div = soup.find('div', id='search')
            if not search_div:
                raise Exception(
                    "Search container not found. Possible block or consent page.")

            found_page = 0

            for result in search_div.find_all('div', recursive=True):
                if len(results) > 10:
                    break

                title = result.find('h3')
                if not title:
                    continue
                title = title.text

                link = result.find('a', href=True)
                if not link:
                    continue
                link = link['href']

                if link.startswith('/url?q='):
                    clean_link = parse_qs(
                        urlparse(link).query).get('q', [None])[0]
                else:
                    clean_link = link

                if not clean_link:
                    continue

                parsed_url = urlparse(link)
                base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

                if parsed_url.scheme == 'https' and not any(parsed_url.netloc.endswith(domain) for domain in blocked_domains):
                    if clean_link not in seen_links:
                        site_info = {
                            'title': title,
                            'base_url': base_url,
                            'link': clean_link,
                            'result_number': len(results),
                        }
                        results.append(site_info)
                        seen_links.add(clean_link)
                        found_page += 1

            if found_page == 0:
                print(f"No new links found on page {page}. Stopping.")
                break

            print(f"✅ Scraped page {page}, total results: {len(results)}")
            page += 1
            time.sleep(0.6)

        except Exception as e:
            if tries % 50 == 0:
                print("Failed to scrape the page:", e)
                print("Retries left:", retries-tries)
            tries += 1
            time.sleep(0.6)

    if not results:
        raise Exception(f"Max retries exceeded: {retries}")

    return results
