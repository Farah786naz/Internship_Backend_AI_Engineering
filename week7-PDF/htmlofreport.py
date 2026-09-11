from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright

def build_html_report(data: dict) -> str:
    """Builds an HTML document string from the report data dictionary."""
    today_str = datetime.now().strftime("%B %d, %Y")

    # Build Top 5 table rows
    top_5_rows = "".join(
        f"<tr><td>{book['title']}</td><td>£{book['price']:.2f}</td><td>{book['rating']} / 5</td></tr>"
        for book in data["top_5_expensive"]
    )

    # Build All 60 books table rows
    all_books_rows = "".join(
        f"<tr><td>{book['id']}</td><td>{book['title']}</td><td>£{book['price']:.2f}</td><td>{book['rating']} / 5</td></tr>"
        for book in data["all_books"]
    )

    # Clean HTML template with CSS print rules
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Bookstore Inventory Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
            margin: 24px;
            color: #1a202c;
            font-size: 12px;
        }}
        h1 {{
            color: #2d3748;
            margin-bottom: 4px;
        }}
        .subtitle {{
            color: #718096;
            margin-bottom: 20px;
        }}
        .metrics-grid {{
            display: flex;
            gap: 16px;
            margin-bottom: 24px;
        }}
        .metric-card {{
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            padding: 12px 16px;
            background-color: #f7fafc;
            min-width: 140px;
        }}
        .metric-label {{
            font-size: 11px;
            color: #718096;
            text-transform: uppercase;
            font-weight: bold;
        }}
        .metric-value {{
            font-size: 22px;
            font-weight: bold;
            color: #2b6cb0;
            margin-top: 4px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 28px;
        }}
        th, td {{
            border: 1px solid #e2e8f0;
            padding: 7px 10px;
            text-align: left;
        }}
        th {{
            background-color: #edf2f7;
            font-weight: 600;
            color: #4a5568;
        }}

        /* 🎯 PRINT CSS: Page-break traps resolved here */
        thead {{
            display: table-header-group; /* Repeats the table header on every printed page */
        }}
        tr {{
            break-inside: avoid;        /* Prevents a table row from being sliced in half */
            page-break-inside: avoid;
        }}
    </style>
</head>
<body>
    <h1>Catalogue Inventory Report</h1>
    <div class="subtitle">Generated on {today_str} · Source: books.toscrape.com</div>

    <div class="metrics-grid">
        <div class="metric-card">
            <div class="metric-label">Total Books</div>
            <div class="metric-value">{data['total_books']}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Average Price</div>
            <div class="metric-value">£{data['average_price']:.2f}</div>
        </div>
    </div>

    <h2>Top 5 Most Expensive Books</h2>
    <table>
        <thead>
            <tr>
                <th>Title</th>
                <th>Price</th>
                <th>Rating</th>
            </tr>
        </thead>
        <tbody>
            {top_5_rows}
        </tbody>
    </table>

    <h2>Complete Inventory ({data['total_books']} Titles)</h2>
    <table>
        <thead>
            <tr>
                <th>#</th>
                <th>Title</th>
                <th>Price</th>
                <th>Rating</th>
            </tr>
        </thead>
        <tbody>
            {all_books_rows}
        </tbody>
    </table>
</body>
</html>"""
    return html


def render_pdf(html_content: str, output_path: Path):
    """Launches headless Chromium via Playwright and renders HTML into a PDF file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with sync_playwright() as p:
        # 1. Launch a headless browser
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # 2. Set the HTML string as page content
        page.set_content(html_content, wait_until="networkidle")

        # 3. Print to PDF
        page.pdf(
            path=str(output_path),
            format="A4",
            print_background=True,
            margin={"top": "15mm", "bottom": "15mm", "left": "10mm", "right": "10mm"}
        )

        browser.close()