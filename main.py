import os
import shutil
import json
import logging
from datetime import date
from modules.keyword_research import run_keyword_research
from modules.competitor_analysis import run_competitor_analysis
from modules.content_generator import run_content_generator
from modules.seo_audit import run_seo_audit
from modules.auto_deploy import run_auto_deploy
from modules.rank_report import generate_rank_report

for folder in ["__pycache__", "config/__pycache__", "modules/__pycache__"]:
    if os.path.exists(folder):
        shutil.rmtree(folder)

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

os.makedirs("outputs/keywords", exist_ok=True)
os.makedirs("outputs/content", exist_ok=True)
os.makedirs("outputs/reports", exist_ok=True)


def run_seo_agent(seed_keyword, your_website_url, niche, location):
    print("\n" + "=" * 60)
    print("🚀 SEO AUTOMATION AGENT - STARTING")
    print("=" * 60)
    print(f"Seed Keyword: {seed_keyword}")
    print(f"Website: {your_website_url}")
    print(f"Niche: {niche}")
    print(f"Location: {location}")
    print("=" * 60 + "\n")

    logger.info(f"Starting SEO agent for keyword: {seed_keyword}")

    report = {
        "seed_keyword": seed_keyword,
        "website_url": your_website_url,
        "niche": niche,
        "location": location,
        "date": date.today().isoformat(),
        "steps": {},
    }

    try:
        print("🔍 STEP 1: Keyword Research")
        keywords = run_keyword_research(seed_keyword, niche, location)
        report["steps"]["keyword_research"] = {
            "status": "success",
            "keywords_found": len(keywords),
        }
    except Exception as e:
        logger.error(f"Keyword research failed: {e}")
        report["steps"]["keyword_research"] = {"status": "error", "error": str(e)}
        keywords = []

    if not keywords:
        print("❌ No keywords found. Cannot continue pipeline.")
        report["error"] = "No keywords found"
        return report

    top_keyword = keywords[0].get("keyword", seed_keyword)

    try:
        print("\n📊 STEP 2: Competitor Analysis")
        competitor_data = run_competitor_analysis(top_keyword, niche, location)
        report["steps"]["competitor_analysis"] = {
            "status": "success",
            "competitors_found": len(competitor_data.get("competitors", [])),
        }
    except Exception as e:
        logger.error(f"Competitor analysis failed: {e}")
        report["steps"]["competitor_analysis"] = {"status": "error", "error": str(e)}
        competitor_data = {"competitors": [], "gaps": {}}

    try:
        print("\n✍️ STEP 3: Content Generation")
        content_data = run_content_generator(
            top_keyword, competitor_data.get("gaps", {}), niche, location
        )
        report["steps"]["content_generation"] = {"status": "success"}
    except Exception as e:
        logger.error(f"Content generation failed: {e}")
        report["steps"]["content_generation"] = {"status": "error", "error": str(e)}
        content_data = {}

    try:
        print("\n🔎 STEP 4: SEO Audit")
        audit_result = run_seo_audit(your_website_url, top_keyword)
        report["steps"]["seo_audit"] = {
            "status": "success",
            "score": audit_result.get("seo_score", 0),
        }
    except Exception as e:
        logger.error(f"SEO audit failed: {e}")
        report["steps"]["seo_audit"] = {"status": "error", "error": str(e)}
        audit_result = {}

    try:
        print("\n🚀 STEP 5: Auto-Deploy")
        if content_data:
            deploy_result = run_auto_deploy(content_data, top_keyword)
            report["steps"]["auto_deploy"] = {
                "status": "success" if deploy_result.get("success") else "failed",
                "url": deploy_result.get("github_url", ""),
            }
        else:
            report["steps"]["auto_deploy"] = {
                "status": "skipped",
                "reason": "No content generated",
            }
    except Exception as e:
        logger.error(f"Auto-deploy failed: {e}")
        report["steps"]["auto_deploy"] = {"status": "error", "error": str(e)}

    try:
        print("\n📈 STEP 6: Rank Report")
        rank_data = generate_rank_report(your_website_url, [top_keyword])
        report["steps"]["rank_report"] = {
            "status": "success",
            "keywords_tracked": len(rank_data.get("changes", [])),
        }
    except Exception as e:
        logger.error(f"Rank report failed: {e}")
        report["steps"]["rank_report"] = {"status": "error", "error": str(e)}

    today = date.today().strftime("%Y%m%d")
    output_file = f"outputs/reports/full_report_{today}.json"

    with open(output_file, "w") as f:
        json.dump(report, f, indent=2)

    print("\n" + "=" * 60)
    print("📋 FINAL SUMMARY")
    print("=" * 60)
    print(f"{'Step':<30} {'Status':<20} {'Details':<30}")
    print("-" * 80)

    for step_name, step_data in report["steps"].items():
        status = step_data.get("status", "unknown")
        details = ""
        if "keywords_found" in step_data:
            details = f"{step_data['keywords_found']} keywords"
        elif "competitors_found" in step_data:
            details = f"{step_data['competitors_found']} competitors"
        elif "score" in step_data:
            details = f"Score: {step_data['score']}/100"
        elif "url" in step_data and step_data.get("url"):
            details = "Deployed ✓"
        elif "keywords_tracked" in step_data:
            details = f"{step_data['keywords_tracked']} tracked"

        status_icon = (
            "✅" if status == "success" else "❌" if status == "error" else "⏭️"
        )
        print(
            f"{step_name.replace('_', ' ').title():<30} {status_icon} {status:<18} {details:<30}"
        )

    print("-" * 80)
    print(f"✅ Full report saved to: {output_file}")
    print("=" * 60)

    logger.info("SEO agent complete")
    return report


if __name__ == "__main__":
    run_seo_agent(
        seed_keyword="saas project management tool",
        your_website_url="https://example.com",
        niche="SaaS / project management",
        location="Bangalore, India",
    )
