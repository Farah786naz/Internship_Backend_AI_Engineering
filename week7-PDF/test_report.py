from pathlib import Path
from db import getReportData
from htmlofreport import build_html_report, render_pdf

if __name__ == "__main__":
    print("1. Fetching report data from SQLite...")
    data = getReportData()

    print("2. Generating HTML template...")
    html = build_html_report(data)

    output_file = Path("reports/test.pdf")
    print(f"3. Rendering PDF to {output_file} via Playwright...")
    render_pdf(html, output_file)

    print(f"Success! Generated: {output_file.resolve()}")