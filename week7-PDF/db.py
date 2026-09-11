from pathlib import Path
import sqlite3

DB_PATH = Path("report.db")

def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def getReportData() -> dict:
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Total books
    cursor.execute("SELECT COUNT(*) AS total_books FROM books;")
    total_books = cursor.fetchone()["total_books"]

    # 2. Average price
    cursor.execute("SELECT ROUND(AVG(price), 2) AS avg_price FROM books;")
    avg_price = cursor.fetchone()["avg_price"] or 0.0

    # 3. Top 5 most expensive books
    cursor.execute("""
        SELECT title, price, rating 
        FROM books 
        ORDER BY price DESC 
        LIMIT 5;
    """)
    top_5_expensive = [dict(row) for row in cursor.fetchall()]

    # 4. Number of books per star rating
    cursor.execute("""
        SELECT rating, COUNT(*) AS count 
        FROM books 
        GROUP BY rating 
        ORDER BY rating ASC;
    """)
    books_per_rating = [dict(row) for row in cursor.fetchall()]

    # 5. ALL 60 books (forces the PDF into 2+ pages)
    cursor.execute("SELECT id, title, price, rating FROM books ORDER BY id ASC;")
    all_books = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return {
        "total_books": total_books,
        "average_price": avg_price,
        "top_5_expensive": top_5_expensive,
        "books_per_rating": books_per_rating,
        "all_books": all_books
    }