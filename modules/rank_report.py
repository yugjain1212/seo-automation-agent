import os
import json
import logging
from datetime import date, datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

os.makedirs("outputs/reports", exist_ok=True)


def get_search_console_service():
    logger.info("Initializing Google Search Console service")

    try:
        credentials = service_account.Credentials.from_service_account_file(
            "credentials.json",
            scopes=["https://www.googleapis.com/auth/webmasters.readonly"],
        )
        service = build("searchconsole", "v1", credentials=credentials)
        logger.info("Search Console service initialized")
        return service
    except FileNotFoundError:
        logger.error(
            "credentials.json not found. Please download from Google Cloud Console"
        )
        print("\n❌ credentials.json not found!")
        print("To get credentials:")
        print("1. Go to Google Cloud Console")
        print("2. Create a service account")
        print("3. Download the JSON key file as credentials.json")
        print("4. Add the service account to Search Console property")
        return None
    except Exception as e:
        logger.error(f"Error initializing Search Console: {e}")
        return None


def fetch_keyword_rankings(site_url, keywords, days=28):
    logger.info(f"Fetching keyword rankings for: {keywords}")

    service = get_search_console_service()
    if not service:
        return []

    end_date = date.today()
    start_date = end_date - timedelta(days=days)

    try:
        request = {
            "startDate": start_date.isoformat(),
            "endDate": end_date.isoformat(),
            "dimensions": ["query", "page"],
            "rowLimit": 100,
        }

        response = (
            service.searchanalytics().query(siteUrl=site_url, body=request).execute()
        )

        results = []
        if "rows" in response:
            for row in response["rows"]:
                query = row["keys"][0]
                if query.lower() in [kw.lower() for kw in keywords]:
                    results.append(
                        {
                            "keyword": query,
                            "clicks": row.get("clicks", 0),
                            "impressions": row.get("impressions", 0),
                            "ctr": round(row.get("ctr", 0) * 100, 2),
                            "position": round(row.get("position", 0), 1),
                        }
                    )

        logger.info(f"Found {len(results)} keyword rankings")
        return results

    except Exception as e:
        logger.error(f"Error fetching rankings: {e}")
        return []


def generate_rank_report(site_url, keywords):
    print(f"\n📈 STEP 6: Google Search Console Rank Report")
    print("=" * 60)

    logger.info(f"Generating rank report for keywords: {keywords}")

    service = get_search_console_service()
    if not service:
        print("❌ Search Console not available (missing credentials)")
        print("   Skipping rank report generation")
        return {"current_week": [], "previous_week": [], "changes": []}

    current_data = fetch_keyword_rankings(site_url, keywords, days=7)
    previous_data = fetch_keyword_rankings(site_url, keywords, days=14)[
        : len(current_data)
    ]

    previous_map = {p["keyword"]: p for p in previous_data}

    changes = []
    for curr in current_data:
        keyword = curr["keyword"]
        prev = previous_map.get(keyword, {})

        position_change = prev.get("position", curr["position"]) - curr["position"]

        changes.append(
            {
                "keyword": keyword,
                "current_position": curr["position"],
                "previous_position": prev.get("position", 0),
                "position_change": position_change,
                "clicks": curr["clicks"],
                "impressions": curr["impressions"],
                "ctr": curr["ctr"],
            }
        )

    changes.sort(key=lambda x: x["current_position"])

    today = date.today().strftime("%Y%m%d")
    output_file = f"outputs/reports/rank_report_{today}.json"

    report = {
        "current_week": current_data,
        "previous_week": previous_data,
        "changes": changes,
        "generated": today,
    }

    with open(output_file, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n📊 Rank Report:")
    print("-" * 90)
    print(
        f"{'Keyword':<30} {'Current':<10} {'Previous':<10} {'Change':<10} {'Clicks':<10} {'Impr.':<10}"
    )
    print("-" * 90)

    for item in changes:
        change_symbol = (
            "↑"
            if item["position_change"] > 0
            else "↓"
            if item["position_change"] < 0
            else "→"
        )
        print(
            f"{item['keyword']:<30} {item['current_position']:<10} {item['previous_position']:<10} {change_symbol}{abs(item['position_change']):<9} {item['clicks']:<10} {item['impressions']:<10}"
        )

    print("-" * 90)
    print(f"✅ Saved to {output_file}")

    logger.info("Rank report complete")
    return report


if __name__ == "__main__":
    result = generate_rank_report(
        site_url="https://example.com", keywords=["project management", "saas tools"]
    )
    print(f"\nKeywords tracked: {len(result.get('changes', []))}")
