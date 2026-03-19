import os
import json
import logging
import requests
from datetime import date
from bs4 import BeautifulSoup

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

os.makedirs("outputs/reports", exist_ok=True)


def audit_page(url, target_keyword):
    logger.info(f"Auditing page: {url}")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    issues = []
    passed = []
    seo_score = 100

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        title_tag = soup.find("title")
        title = title_tag.get_text().strip() if title_tag else ""

        if not title_tag:
            issues.append("Title tag missing")
            seo_score -= 20
            print("  ❌ Title tag missing (-20)")
        else:
            passed.append("Title tag present")
            print("  ✅ Title tag present")

            if 30 <= len(title) <= 60:
                passed.append(f"Title length optimal ({len(title)} chars)")
                print(f"  ✅ Title length optimal ({len(title)} chars)")
            else:
                issues.append(f"Title length not 30-60 chars ({len(title)} chars)")
                seo_score -= 10
                print(f"  ❌ Title length not 30-60 chars ({len(title)} chars) (-10)")

            if target_keyword.lower() in title.lower():
                passed.append("Target keyword in title")
                print(f"  ✅ Target keyword in title")
            else:
                issues.append("Target keyword not in title")
                seo_score -= 10
                print(f"  ❌ Target keyword not in title (-10)")

        meta_desc = ""
        meta_tag = soup.find("meta", attrs={"name": "description"})
        if meta_tag and meta_tag.get("content"):
            meta_desc = meta_tag["content"].strip()

        if not meta_tag or not meta_desc:
            issues.append("Meta description missing")
            seo_score -= 15
            print("  ❌ Meta description missing (-15)")
        else:
            passed.append("Meta description present")
            print("  ✅ Meta description present")

            if 120 <= len(meta_desc) <= 160:
                passed.append(
                    f"Meta description length optimal ({len(meta_desc)} chars)"
                )
                print(f"  ✅ Meta description length optimal ({len(meta_desc)} chars)")
            else:
                issues.append(
                    f"Meta description length not 120-160 chars ({len(meta_desc)} chars)"
                )
                seo_score -= 5
                print(
                    f"  ❌ Meta description length not 120-160 chars ({len(meta_desc)} chars) (-5)"
                )

        h1_tags = soup.find_all("h1")

        if not h1_tags:
            issues.append("H1 tag missing")
            seo_score -= 15
            print("  ❌ H1 tag missing (-15)")
        else:
            passed.append(f"H1 tag present ({len(h1_tags)} found)")
            print(f"  ✅ H1 tag present ({len(h1_tags)} found)")

            if len(h1_tags) > 1:
                issues.append("Multiple H1 tags found")
                seo_score -= 5
                print(f"  ❌ Multiple H1 tags found (-5)")
            else:
                passed.append("Single H1 tag (optimal)")
                print(f"  ✅ Single H1 tag (optimal)")

        images = soup.find_all("img")
        images_without_alt = sum(1 for img in images if not img.get("alt"))

        if images_without_alt > 0:
            issues.append(f"{images_without_alt} images missing alt text")
            seo_score -= 5
            print(f"  ❌ {images_without_alt} images missing alt text (-5)")
        else:
            passed.append("All images have alt text")
            print(f"  ✅ All images have alt text")

        schema_tags = soup.find_all("script", type="application/ld+json")

        if not schema_tags:
            issues.append("Schema markup (JSON-LD) missing")
            seo_score -= 10
            print("  ❌ Schema markup missing (-10)")
        else:
            passed.append("Schema markup present")
            print(f"  ✅ Schema markup present ({len(schema_tags)} found)")

        text_content = soup.get_text(separator=" ", strip=True)
        word_count = len(text_content.split())

        if word_count < 300:
            issues.append(f"Word count under 300 ({word_count} words)")
            seo_score -= 10
            print(f"  ❌ Word count under 300 ({word_count} words) (-10)")
        else:
            passed.append(f"Word count adequate ({word_count} words)")
            print(f"  ✅ Word count adequate ({word_count} words)")

        h2_tags = soup.find_all("h2")

        if len(h2_tags) < 2:
            issues.append(f"Fewer than 2 H2 subheadings ({len(h2_tags)} found)")
            seo_score -= 5
            print(f"  ❌ Fewer than 2 H2 subheadings ({len(h2_tags)} found) (-5)")
        else:
            passed.append(f"Multiple H2 subheadings ({len(h2_tags)} found)")
            print(f"  ✅ Multiple H2 subheadings ({len(h2_tags)} found)")

        h1_text = h1_tags[0].get_text().strip() if h1_tags else ""

        seo_score = max(0, seo_score)

        if seo_score >= 90:
            grade = "A"
        elif seo_score >= 75:
            grade = "B"
        elif seo_score >= 60:
            grade = "C"
        else:
            grade = "D"

        result = {
            "url": url,
            "target_keyword": target_keyword,
            "seo_score": seo_score,
            "grade": grade,
            "issues": issues,
            "passed": passed,
            "word_count": word_count,
            "title": title,
            "h1": h1_text,
        }

        logger.info(f"Audit complete. Score: {seo_score}/{100}, Grade: {grade}")
        return result

    except requests.exceptions.Timeout:
        logger.error(f"Timeout accessing {url}")
        return {
            "url": url,
            "error": "Timeout",
            "seo_score": 0,
            "grade": "F",
            "issues": ["Page timeout"],
            "passed": [],
        }
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error accessing {url}: {e}")
        return {
            "url": url,
            "error": str(e),
            "seo_score": 0,
            "grade": "F",
            "issues": ["HTTP error"],
            "passed": [],
        }
    except Exception as e:
        logger.error(f"Error auditing page: {e}")
        return {
            "url": url,
            "error": str(e),
            "seo_score": 0,
            "grade": "F",
            "issues": [str(e)],
            "passed": [],
        }


def run_seo_audit(url, keyword):
    print(f"\n🔎 STEP 4: SEO Audit for '{url}'")
    print("=" * 60)

    logger.info(f"Starting SEO audit for: {url}")

    result = audit_page(url, keyword)

    today = date.today().strftime("%Y%m%d")
    output_file = f"outputs/reports/audit_{today}.json"

    with open(output_file, "w") as f:
        json.dump(result, f, indent=2)

    print(f"\n📊 SEO Audit Results:")
    print("-" * 40)
    print(
        f"Score: {result.get('seo_score', 0)}/100 (Grade: {result.get('grade', 'N/A')})"
    )
    print(f"Word Count: {result.get('word_count', 0)}")
    print(f"Issues Found: {len(result.get('issues', []))}")
    print(f"Passed Checks: {len(result.get('passed', []))}")
    print("-" * 40)
    print(f"✅ Saved to {output_file}")

    logger.info("SEO audit complete")
    return result


if __name__ == "__main__":
    result = run_seo_audit(url="https://example.com", keyword="project management")
    print(f"\nAudit score: {result.get('seo_score')}")
