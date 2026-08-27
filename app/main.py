from datetime import datetime
import hashlib
import json
from time import sleep
from typing import Optional

from fastapi import FastAPI
from pathlib import Path
import sys
from pydantic import BaseModel, field_validator
from pydantic_core import ValidationError
import requests
app = FastAPI()
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup


TARGET_URL = "https://books.toscrape.com/catalogue/category/books_1/index.html"
CACHE_DIR = Path("cache")
CACHE_FILE = CACHE_DIR / "catalogue-page-1.html"
USER_AGENT = "FlyRankInternshipA9/1.0 (+https://github.com/Farah786naz/Internship_Backend_AI_Engineering)"
TIMEOUT_SECONDS = 10
REQUEST_DELAY_SECONDS = 1
OUTPUT_DIR = Path("output")
BOOKS_OUTPUT_FILE = OUTPUT_DIR / "books.json"
ERRORS_OUTPUT_FILE = OUTPUT_DIR /"errors.json"

class BookRecord(BaseModel):
    title: str
    url: str
    price_text: str
    price_gbp: float
    availability_text: str
    rating_text: str
    description: Optional[str] = None
    source_page: str
    fetched_at: str

    @field_validator("url", "source_page")
    @classmethod
    def ensure_https(cls, value: str) -> str:
        if not value.startswith("https://"):
            raise ValueError("URL must start with https://")
        return value

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
        absolute_url = absolute_url.replace("/catalogue/category/books_1/", "/catalogue/")
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


def extract_catalogue_page_number(html: str) -> int | None:
    soup = BeautifulSoup(html, "html.parser")
    current_tag = soup.select_one("ul.pager li.current")
    if not current_tag:
        return None

    current_text = " ".join(current_tag.get_text(strip=True).split())
    parts = current_text.split()
    if len(parts) >= 2 and parts[0].lower() == "page" and parts[1].isdigit():
        return int(parts[1])
    return None


def crawl_catalogue()->set[tuple[str, str]]:
    current_url = TARGET_URL
    pages_crawled = 0
    all_discovered_links = []
    seen_page_urls = set()

    while current_url and pages_crawled < MAXPAGES:
        if current_url in seen_page_urls:
            print(f"Stopping crawl due to repeated page URL: {current_url}")
            break
        seen_page_urls.add(current_url)

        page_num = pages_crawled + 1

        # If cache file exists but claims a different page number, drop it and refetch.
        cachefile = CACHE_DIR / f"catalogue-page-{page_num}.html"
        if cachefile.exists():
            cached_html = cachefile.read_text(encoding="utf-8")
            cached_page_num = extract_catalogue_page_number(cached_html)
            if cached_page_num is not None and cached_page_num != page_num:
                print(
                    f"CACHE INVALID: {cachefile} has page {cached_page_num}, "
                    f"expected page {page_num}. Refetching."
                )
                cachefile.unlink()

        html, from_cache = fetch_multiple_pages(current_url, page_num)

        detected_page_num = extract_catalogue_page_number(html)
        if detected_page_num is not None and detected_page_num != page_num:
            print(
                f"Page mismatch for {current_url}: expected page {page_num}, "
                f"got page {detected_page_num}. Stopping crawl."
            )
            break
        
        status_msg = "CACHE HIT" if from_cache else "FETCH"
        print(f"[{status_msg}] Page {page_num}: {current_url}")

        # Extract book links from this page
        links = extract_book_links(html, current_url)
        all_discovered_links.extend(links)
        pages_crawled += 1

        # Check for next page
        current_url = find_next_page_url(html, current_url)

    # Deduplicate by book URL while keeping the first observed source page.
    unique_by_url = {}
    for book_url, source_page in all_discovered_links:
        if book_url not in unique_by_url:
            unique_by_url[book_url] = source_page
    unique_links = {(book_url, source_page) for book_url, source_page in unique_by_url.items()}

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
    product_availability=product_page.find("p",class_="instock availability").text.strip() or "None"
    star_tag = product_page.find("p", class_="star-rating")
    classes = star_tag.get("class", [])
    rating_text= classes[1] if len(classes) > 1 else "None"
    product_description_tag = product_page.find("div", id="product_description")
    product_description_text = None

    if product_description_tag:
        product_description_paragraph = product_description_tag.find_next_sibling("p")
        if product_description_paragraph:
            product_description_text = product_description_paragraph.text.strip() if product_description_paragraph.text.strip() else "None"

    normalized_price = product_price.replace("£", "").replace("Â", "").strip()
    normalized_price = "".join(ch for ch in normalized_price if ch.isdigit() or ch == ".")
    if not normalized_price:
        raise ValueError(f"Unable to parse price from text: {product_price}")

    return {
        
        "title": product_title,
        "url": url,
        "price_text": product_price,
        "price_gbp": float(normalized_price),
        "availability_text": product_availability,
        "rating_text": rating_text,
        "description": product_description_text,
        "source_page": source_url,
        "fetched_at": datetime.now().isoformat()
    }

def crawl_products_from_every_page():

    unique_book_urls = crawl_catalogue()
    print(f"Total unique book URLs to process: {len(unique_book_urls)}")
    unified_book_details = []
    total_books = len(unique_book_urls)
    seen_urls=set()
    validated_records=[]
    validation_errors=[]
    

    for index, (url, source_url) in enumerate(unique_book_urls, start=1):
        url_hash = hashlib.md5(url.encode("utf-8")).hexdigest()
        cache_path = CACHEDIR_BOOKS / f"{url_hash}.html"
        if cache_path.exists():
            html_content = cache_path.read_text(encoding="utf-8")
            
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

        
        if url in seen_urls:
            continue  # Skip duplicate URLs
        seen_urls.add(url)
        try:
            product_details = get_each_product_page_detail(url, source_url, html_content)
        except ValueError as err:
            validation_errors.append({
                "url": url,
                "error": str(err),
                "timestamp": datetime.now().isoformat()
            })
            continue
        try:
            
            # Pydantic Schema Validation
            record = BookRecord(**product_details)
            validated_records.append(record.model_dump())
        except (ValidationError, ValueError, Exception) as err:
            validation_errors.append({
                "url": url,
                "error": str(err),
                "timestamp": datetime.now().isoformat()
            })

        if product_details:
            unified_book_details.append(product_details)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(BOOKS_OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(validated_records, f, indent=2, ensure_ascii=False)
            print(f"Saved {len(validated_records)} validated records to {BOOKS_OUTPUT_FILE}")
    
    with open(ERRORS_OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(validation_errors, f, indent=2, ensure_ascii=False)
            print(f"Saved {len(validation_errors)} validation errors to {ERRORS_OUTPUT_FILE}")
    return unified_book_details


if __name__ == "__main__":
    crawl_products_from_every_page()

@app.get("/")
async def root():
    products = crawl_products_from_every_page()
    return {"message": "Products crawled successfully.", "products": products[:5]}  # Return only the first 5 products for brevity


from dotenv import load_dotenv
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

# Load environment variables from .env
load_dotenv()

from week7.router import router as llm_router

app = FastAPI(
    title="Book Enrichment API",
    description="API for enriching scraped book records with structured AI metadata"
)

# Custom exception handler: Return 400 Bad Request naming the offending field
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    first_error = errors[0] if errors else {}
    field_name = " -> ".join(str(loc) for loc in first_error.get("loc", []))
    msg = first_error.get("msg", "Invalid input")
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": f"Validation error on field '{field_name}': {msg}"}
    )

# Attach the router
app.include_router(llm_router)