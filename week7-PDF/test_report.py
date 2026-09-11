from db import getReportData
import json

if __name__ == "__main__":
    report_data = getReportData()
    print(json.dumps(report_data, indent=4))