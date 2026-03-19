import os
import json
import time
import logging
import requests
from datetime import date
from groq import Groq
from config.config import SERP_API_KEY, GROQ_API_KEY

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

os.makedirs("outputs/keywords", exist_ok=True)


def fetch_autocomplete_keywords(seed_keyword):
    logger.info(f"Fetching autocomplete keywords for: {seed_keyword}")
    try:
        url = "https://serpapi.com/search"
        params = {
            "engine": "google_autocomplete",
            "q": seed_keyword,
            "api_key": SERP_API_KEY,
        }
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        keywords = []
        if "results" in data:
            for result in data.get("results", []):
                if "phrase" in result:
                    keywords.append(result["phrase"])

        logger.info(f"Found {len(keywords)} autocomplete keywords")
        return keywords
    except Exception as e:
        logger.error(f"Error fetching autocomplete keywords: {e}")
        return []


def fetch_related_searches(seed_keyword):
    logger.info(f"Fetching related searches for: {seed_keyword}")
    try:
        url = "https://serpapi.com/search"
        params = {
            "engine": "google",
            "q": seed_keyword,
            "num": 10,
            "api_key": SERP_API_KEY,
        }
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        keywords = []
        if "related_searches" in data:
            for item in data.get("related_searches", []):
                if "query" in item:
                    keywords.append(item["query"])

        logger.info(f"Found {len(keywords)} related search keywords")
        return keywords
    except Exception as e:
        logger.error(f"Error fetching related searches: {e}")
        return []


def score_keywords_with_groq(keywords, niche, location):
    logger.info(f"Scoring {len(keywords)} keywords with Groq")
    client = Groq(api_key=GROQ_API_KEY)

    prompt = f"""You are an SEO expert analyzing keywords for a {niche} business targeting {location}.

Analyze the following keywords and return a JSON array with each keyword scored. For each keyword, provide:
- keyword: the exact keyword string
- intent: "informational", "commercial", or "transactional"
- competition: "low", "medium", or "high"
- priority_score: integer 1-10 (10 = highest priority)
- reasoning: brief explanation (1-2 sentences)

Keywords to analyze:
{json.dumps(keywords)}

Return ONLY valid JSON. No markdown. No backticks. No explanation."""

    for attempt in range(2):
        try:
            logger.info(f"Groq scoring attempt {attempt + 1}")
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                temperature=0.3,
                max_tokens=4000,
            )

            raw_response = chat_completion.choices[0].message.content
            logger.info("Received response from Groq")

            if "```" in raw_response:
                raw_response = raw_response.split("```")[1]
                if raw_response.startswith("json"):
                    raw_response = raw_response[4:]
                raw_response = raw_response.strip()

            scored_keywords = json.loads(raw_response)
            logger.info(f"Successfully parsed {len(scored_keywords)} scored keywords")
            return scored_keywords

        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error on attempt {attempt + 1}: {e}")
            if attempt < 1:
                time.sleep(3)
                continue
            return []
        except Exception as e:
            logger.error(f"Error on attempt {attempt + 1}: {e}")
            if attempt < 1:
                time.sleep(3)
                continue
            return []


def run_keyword_research(seed_keyword, niche, location):
    print(f"\n🔍 STEP 1: Keyword Research for '{seed_keyword}'")
    print("=" * 60)

    logger.info(f"Starting keyword research for: {seed_keyword}")

    keywords = fetch_autocomplete_keywords(seed_keyword)
    time.sleep(1)

    related = fetch_related_searches(seed_keyword)
    time.sleep(1)

    all_keywords = list(set(keywords + related))
    logger.info(f"Total unique keywords after dedup: {len(all_keywords)}")

    if not all_keywords:
        logger.warning("No keywords found")
        print("❌ No keywords found")
        return []

    scored = score_keywords_with_groq(all_keywords, niche, location)

    if not scored:
        logger.error("Failed to score keywords")
        print("❌ Failed to score keywords")
        return []

    filtered = [k for k in scored if k.get("priority_score", 0) >= 6]
    filtered.sort(key=lambda x: x.get("priority_score", 0), reverse=True)

    for kw in filtered:
        intent = kw.get("intent", "")
        if intent == "transactional":
            kw["best_platform"] = "website"
        elif intent == "commercial":
            kw["best_platform"] = "gmb"
        else:
            kw["best_platform"] = "linkedin"

    today = date.today().strftime("%Y%m%d")
    safe_keyword = seed_keyword.replace(" ", "_")[:20]
    output_file = f"outputs/keywords/{safe_keyword}_{today}.json"

    with open(output_file, "w") as f:
        json.dump(filtered, f, indent=2)

    print(f"\n📊 Ranked Keywords (Priority >= 6):")
    print("-" * 80)
    print(f"{'Keyword':<35} {'Score':<8} {'Intent':<15} {'Platform':<12}")
    print("-" * 80)
    for kw in filtered[:15]:
        print(
            f"{kw.get('keyword', ''):<35} {kw.get('priority_score', ''):<8} {kw.get('intent', ''):<15} {kw.get('best_platform', ''):<12}"
        )
    print("-" * 80)
    print(f"✅ Saved {len(filtered)} keywords to {output_file}")

    logger.info(
        f"Keyword research complete. Found {len(filtered)} high-priority keywords"
    )
    return filtered


if __name__ == "__main__":
    result = run_keyword_research(
        seed_keyword="saas project management tool",
        niche="SaaS / project management",
        location="Bangalore, India",
    )
    print(f"\nTotal keywords found: {len(result)}")
