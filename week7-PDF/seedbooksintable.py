import json
from pathlib import Path
import sqlite3

DB_PATH = Path("report.db")
BOOKS_JSON_PATH = Path("output/books.json")

RATING_MAP = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}

def seed_database():
    if not BOOKS_JSON_PATH.exists():
        raise FileNotFoundError(f"Source data not found at {BOOKS_JSON_PATH}")

    with open(BOOKS_JSON_PATH, "r", encoding="utf-8") as f:
        books_data = json.load(f)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create books table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            price REAL NOT NULL,
            rating INTEGER NOT NULL,
            url TEXT NOT NULL
        );
    """)

    # Clear table for idempotency
    cursor.execute("DELETE FROM books;")

    insert_rows = []
    for item in books_data:
        numeric_rating = RATING_MAP.get(item.get("rating_text"), 0)
        insert_rows.append((
            item["title"],
            float(item["price_gbp"]),
            numeric_rating,
            item["url"]
        ))

    cursor.executemany(
        "INSERT INTO books (title, price, rating, url) VALUES (?, ?, ?, ?);",
        insert_rows
    )

    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM books;")
    total_inserted = cursor.fetchone()[0]
    conn.close()

    print(f"Database seeded successfully. Total books in table: {total_inserted}")

if __name__ == "__main__":
    seed_database()