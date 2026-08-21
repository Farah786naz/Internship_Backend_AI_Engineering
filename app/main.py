from fastapi import FastAPI
from pathlib import Path
import sys
import requests
app = FastAPI()


TARGET_URL = "https://books.toscrape.com/catalogue/page-1.html"
CACHE_DIR = Path("cache")
CACHE_FILE = CACHE_DIR / "catalogue-page-1.html"
USER_AGENT = "FlyRankInternshipA9/1.0 (+https://github.com/Farah786naz/Internship_Backend_AI_Engineering)"
TIMEOUT_SECONDS = 10

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


if __name__ == "__main__":
    fetch_and_cache_page()

@app.get("/")
def read_root():
    return {"status": "FastAPI is working!"}