import os
import json
import time
import logging
import requests
from groq import Groq
from config.config import SERP_API_KEY, GROQ_API_KEY

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def scrape_top_pages(keyword, num_results=5):
    logger.info(f"Scraping top {num_results} pages for keyword: {keyword}")
    try:
        url = "https://serpapi.com/search"
        params = {
            "engine": "google",
            "q": keyword,
            "num": num_results,
            "api_key": SERP_API_KEY,
        }
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        results = []
        if "organic_results" in data:
            for item in data.get("organic_results", [])[:num_results]:
                results.append(
                    {
                        "title": item.get("title", ""),
                        "url": item.get("link", ""),
                        "snippet": item.get("snippet", ""),
                        "position": item.get("position", 0),
                    }
                )

        logger.info(f"Found {len(results)} top pages")
        return results
    except Exception as e:
        logger.error(f"Error scraping top pages: {e}")
        return []


def find_content_gaps(keyword, competitor_pages, niche, location):
    logger.info(f"Finding content gaps for keyword: {keyword}")
    client = Groq(api_key=GROQ_API_KEY)

    prompt = f"""You are an SEO content strategist analyzing competitor content for a {niche} business targeting {location}.

Analyze these competitor pages for the keyword "{keyword}" and identify content gaps - topics and angles that your content should cover but competitors are missing.

Competitor data:
{json.dumps(competitor_pages, indent=2)}

Return a JSON object with:
- missing_topics: list of topics/keywords competitors don't cover well
- missing_angles: list of unique angles/perspectives missing
- subtopics_to_add: list of subtopics to include in your content
- content_type: recommended content type (e.g., "blog post", "landing page", "comparison guide")
- word_count_target: recommended word count (integer)

Return ONLY valid JSON. No markdown. No backticks. No explanation."""

    for attempt in range(2):
        try:
            logger.info(f"Groq content gaps attempt {attempt + 1}")
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                temperature=0.3,
                max_tokens=2000,
            )

            raw_response = chat_completion.choices[0].message.content
            logger.info("Received response from Groq")

            if "```" in raw_response:
                raw_response = raw_response.split("```")[1]
                if raw_response.startswith("json"):
                    raw_response = raw_response[4:]
                raw_response = raw_response.strip()

            gaps = json.loads(raw_response)
            logger.info("Successfully parsed content gaps")
            return gaps

        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error on attempt {attempt + 1}: {e}")
            if attempt < 1:
                time.sleep(3)
                continue
            return {}
        except Exception as e:
            logger.error(f"Error on attempt {attempt + 1}: {e}")
            if attempt < 1:
                time.sleep(3)
                continue
            return {}


def run_competitor_analysis(keyword, niche, location):
    print(f"\n📊 STEP 2: Competitor Analysis for '{keyword}'")
    print("=" * 60)

    logger.info(f"Starting competitor analysis for: {keyword}")

    competitors = scrape_top_pages(keyword)

    if not competitors:
        logger.error("No competitor data found")
        print("❌ No competitor data found")
        return {"competitors": [], "gaps": {}}

    time.sleep(1)

    gaps = find_content_gaps(keyword, competitors, niche, location)

    print(f"\n🏆 Top Competitors:")
    print("-" * 80)
    for comp in competitors:
        print(f"Position {comp.get('position')}: {comp.get('title')}")
        print(f"  URL: {comp.get('url')}")
        print(f"  Snippet: {comp.get('snippet', '')[:80]}...")
        print()

    if gaps:
        print(f"\n📋 Content Gaps Identified:")
        print("-" * 40)
        if gaps.get("missing_topics"):
            print(f"Missing Topics: {', '.join(gaps.get('missing_topics', []))}")
        if gaps.get("missing_angles"):
            print(f"Missing Angles: {', '.join(gaps.get('missing_angles', []))}")
        if gaps.get("subtopics_to_add"):
            print(f"Subtopics to Add: {', '.join(gaps.get('subtopics_to_add', []))}")
        print(f"Content Type: {gaps.get('content_type', 'N/A')}")
        print(f"Word Count Target: {gaps.get('word_count_target', 'N/A')}")

    print("-" * 40)
    logger.info("Competitor analysis complete")

    return {"competitors": competitors, "gaps": gaps}


if __name__ == "__main__":
    result = run_competitor_analysis(
        keyword="saas project management tool",
        niche="SaaS / project management",
        location="Bangalore, India",
    )
    print(f"\nCompetitors found: {len(result.get('competitors', []))}")
