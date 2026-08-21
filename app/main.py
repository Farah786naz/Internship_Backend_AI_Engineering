from datetime import datetime
import hashlib
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
        print(f"FETCH: Requesting {url} ...")
        if pagenum>1:
            sleep(REQUEST_DELAY_SECONDS)  # Delay between requests to avoid overwhelming the server
        try:
            response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT_SECONDS)
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

def extract_book_links(html:str,current_page_url:str)-> list[tuple[str, str]]:
    soup=BeautifulSoup(html, "html.parser")
    book_links=[]
    for article in soup.find_all("article", class_="product_pod"):
        
        relative_url=article.h3.a['href']
        absolute_url=urljoin(current_page_url, relative_url)
        book_links.append((absolute_url, current_page_url))
    return book_links

def find_next_page_url(html: str, current_page_url: str) -> str | None:
    """Finds the absolute URL for the 'next' catalogue page, if present."""
    soup = BeautifulSoup(html, "html.parser")
    next_tag = soup.find("li", class_="next")
    
    if next_tag and next_tag.a:
        relative_next = next_tag.a["href"]
        return urljoin(current_page_url, relative_next)
    
    return None


def crawl_catalogue()->set[tuple[str, str]]:
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
    print(f"\ncatalogue_pages={pages_crawled} , discovered={len(all_discovered_links)} , unique_urls={len(unique_links)} , unique_urls_sample={list(unique_links)[:5]}\n")

    return unique_links

#TASK OF GETTING EACH PRODUCT PAGE DETAIL

CACHEDIR_BOOKS = Path("cache/books")
CACHEDIR_BOOKS.mkdir(parents=True, exist_ok=True)

def get_each_product_page_detail(url, source_url, html_content):
    soup=BeautifulSoup(html_content, "html.parser")
    product_page = soup.find("article", class_="product_page")
    if not product_page:
        print(f"Product page structure not found for {url}")
        return
    product_title=product_page.find("div",class_="col-sm-6 product_main").h1.text.strip() 
    product_price=product_page.find("p",class_="price_color").text.strip()
    product_availability=product_page.find("p",class_="instock availability").text.strip()
    star_tag = product_page.find("p", class_="star-rating")
    classes = star_tag.get("class", [])
    rating_text= classes[1] if len(classes) > 1 else "None"
    product_description_tag = product_page.find("div", id="product_description")
    product_description_text = None

    if product_description_tag:
        product_description_paragraph = product_description_tag.find_next_sibling("p")
        if product_description_paragraph:
            product_description_text = product_description_paragraph.text.strip() if product_description_paragraph.text.strip() else "None"

    return {
        
        "title": product_title,
        "url": url,
        "price": product_price,
        "availability": product_availability,
        "rating": rating_text,
        "description": product_description_text,
        "source_url": source_url,
        "timestamp": datetime.now().isoformat()
    }

def crawl_products_from_every_page():

    unique_book_urls = crawl_catalogue()
    unified_book_details = []
    total_books = len(unique_book_urls)
    for index, (url, source_url) in enumerate(unique_book_urls, start=1):
        url_hash = hashlib.md5(url.encode("utf-8")).hexdigest()
        cache_path = CACHEDIR_BOOKS / f"{url_hash}.html"

        if cache_path.exists():
            html_content = cache_path.read_text(encoding="utf-8")
            print(f"[CACHE HIT] {index}: {url} -> {cache_path}")
        else:
            sleep(REQUEST_DELAY_SECONDS)  # Delay between requests to avoid overwhelming the server
            try:
                response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT_SECONDS)
            except requests.exceptions.RequestException as e:
                print(f"Fetch failed for {url} due to network/timeout error: {e}")
                continue
            if response.status_code != 200:
                print(f"Fetch failed for {url} with HTTP status code: {response.status_code}")
                continue

            html_content = response.text
            cache_path.write_text(html_content, encoding="utf-8")
            print(f"[{index}/{total_books}] [FETCH] {url}")
        product_details = get_each_product_page_detail(url, source_url, html_content)
        if product_details:
            unified_book_details.append(product_details)

    return unified_book_details


if __name__ == "__main__":
    crawl_products_from_every_page()

@app.get("/")
async def root():
    products = crawl_products_from_every_page()
    return {"message": "Products crawled successfully.", "products": products[:5]}  # Return only the first 5 products for brevity

