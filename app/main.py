from time import sleep

from fastapi import FastAPI
from pathlib import Path
import sys
import requests
app = FastAPI()
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup


TARGET_URL = "https://books.toscrape.com/catalogue/page-1.html"
CACHE_DIR = Path("cache")
CACHE_FILE = CACHE_DIR / "catalogue-page-1.html"
USER_AGENT = "FlyRankInternshipA9/1.0 (+https://github.com/Farah786naz/Internship_Backend_AI_Engineering)"
TIMEOUT_SECONDS = 10
REQUEST_DELAY_SECONDS = 1 

 # Delay between requests to avoid overwhelming the server
def fetch_and_cache_page()-> str:
    if CACHE_FILE.exists():
        html_content = CACHE_FILE.read_text(encoding="utf-8")
        size_bytes = len(html_content.encode("utf-8"))
        print(f"CACHE HIT: Read from {CACHE_FILE} ({size_bytes} bytes)")
        return html_content
    # 3. Cache Miss: Fetch from network
    print(f"FETCH: Requesting {TARGET_URL} ...")
    try:
        response = requests.get(TARGET_URL, headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT_SECONDS)
    except requests.exceptions.RequestException as e:
        print(f"Fetch failed due to network/timeout error: {e}")
        sys.exit(1)

    # 4. Strict status code check
    if response.status_code != 200:
        print(f"Fetch failed with HTTP status code: {response.status_code}")
        sys.exit(1)

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(response.text, encoding="utf-8")
    size_bytes = len(response.content)
    print(f"FETCH SUCCESS: Saved to {CACHE_FILE} ({size_bytes} bytes)")
    
    return response.text




#FETCH MULTIPLE PAGES
MAXPAGES=3
def fetch_multiple_pages(url: str,pagenum: int) -> tuple[str, bool]:

        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cachefile=CACHE_DIR / f"catalogue-page-{pagenum}.html"
        
        if cachefile.exists():
            html_content = cachefile.read_text(encoding="utf-8")
            size_bytes = len(html_content.encode("utf-8"))
            print(f"CACHE HIT: Read from {cachefile} ({size_bytes} bytes)")
            return html_content, True
        # 3. Cache Miss: Fetch from network
        print(f"FETCH: Requesting {TARGET_URL} ...")
        if pagenum>1:
            sleep(REQUEST_DELAY_SECONDS)  # Delay between requests to avoid overwhelming the server
        try:
            response = requests.get(TARGET_URL, headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT_SECONDS)
        except requests.exceptions.RequestException as e:
            print(f"Fetch failed due to network/timeout error: {e}")
            sys.exit(1)
    
        # 4. Strict status code check
        if response.status_code != 200:
            print(f"Fetch failed with HTTP status code: {response.status_code}")
            sys.exit(1)
    
        cachefile.write_text(response.text, encoding="utf-8")
        size_bytes = len(response.content)
        print(f"FETCH SUCCESS: Saved to {cachefile} ({size_bytes} bytes)")
        
        return response.text, False

#FETCH ALL BOOK URLS

def extract_book_links(html:str,current_page_url:str)-> list[str]:
    soup=BeautifulSoup(html, "html.parser")
    book_links=[]
    for article in soup.find_all("article", class_="product_pod"):
        
        relative_url=article.h3.a['href']
        absolute_url=urljoin(current_page_url, relative_url)
        book_links.append(absolute_url)
    return book_links

def find_next_page_url(html: str, current_page_url: str) -> str | None:
    """Finds the absolute URL for the 'next' catalogue page, if present."""
    soup = BeautifulSoup(html, "html.parser")
    next_tag = soup.find("li", class_="next")
    
    if next_tag and next_tag.a:
        relative_next = next_tag.a["href"]
        return urljoin(current_page_url, relative_next)
    
    return None


def crawl_catalogue():
    current_url = TARGET_URL
    pages_crawled = 0
    all_discovered_links = []

    while current_url and pages_crawled < MAXPAGES:
        page_num = pages_crawled + 1
        html, from_cache = fetch_multiple_pages(current_url, page_num)
        
        status_msg = "CACHE HIT" if from_cache else "FETCH"
        print(f"[{status_msg}] Page {page_num}: {current_url}")

        # Extract book links from this page
        links = extract_book_links(html, current_url)
        all_discovered_links.extend(links)
        pages_crawled += 1

        # Check for next page
        current_url = find_next_page_url(html, current_url)

    # Deduplicate URLs
    unique_links = set(all_discovered_links)

    # Checkpoint Output
    print(f"\ncatalogue_pages={pages_crawled} , discovered={len(all_discovered_links)} , unique_urls={len(unique_links)}")


if __name__ == "__main__":
    crawl_catalogue()
