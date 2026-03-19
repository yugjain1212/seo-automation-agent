import os
import json
import time
import logging
from datetime import date
from groq import Groq
from config.config import GROQ_API_KEY

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

os.makedirs("outputs/content", exist_ok=True)


def call_groq(prompt, temperature=0.3, max_tokens=4000):
    logger.info("Calling Groq API")
    client = Groq(api_key=GROQ_API_KEY)

    for attempt in range(2):
        try:
            logger.info(f"Groq attempt {attempt + 1}")
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                temperature=temperature,
                max_tokens=max_tokens,
            )

            raw_response = chat_completion.choices[0].message.content
            logger.info("Received response from Groq")

            if raw_response and "```" in raw_response:
                parts = raw_response.split("```")
                raw_response = parts[1] if len(parts) > 1 else raw_response
                if raw_response.startswith("json"):
                    raw_response = raw_response[4:]
                raw_response = raw_response.strip()

            result = json.loads(raw_response)
            logger.info("Successfully parsed JSON from Groq")
            return result

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

    return {}


def generate_website_page(keyword, gaps, niche, location):
    logger.info(f"Generating website page content for: {keyword}")

    missing_topics = gaps.get("missing_topics", [])
    subtopics = gaps.get("subtopics_to_add", [])

    prompt = f"""Generate SEO-optimized website page content for a {niche} business targeting {location}.

Target Keyword: {keyword}
Missing Topics from competitors: {", ".join(missing_topics)}
Subtopics to add: {", ".join(subtopics)}

Return a JSON object with:
- title: SEO title (50-60 characters, must contain keyword)
- meta_description: Meta description (150-160 characters)
- h1: Compelling H1 (different from title)
- content: Full HTML body content (800-1200 words with h2/h3 subheadings, covering ALL missing_topics)
- schema_markup: JSON-LD schema as string (SoftwareApplication type)
- focus_keyword: the main target keyword
- secondary_keywords: list of 5 secondary keywords

IMPORTANT: Content must be specific to {niche} in {location}. NEVER generic. Cover all the missing topics.

Return ONLY valid JSON. No markdown. No backticks. No explanation."""

    return call_groq(prompt, temperature=0.4, max_tokens=6000)


def generate_gmb_post(keyword, niche, location):
    logger.info(f"Generating GMB post for: {keyword}")

    prompt = f"""Generate a Google My Business post for a {niche} business targeting {location}.

Target Keyword: {keyword}

Return a JSON object with:
- post_text: 150-300 words, localized content mentioning Bangalore, India
- cta_type: one of "learn_more", "book", "sign_up", "call"
- category: one of "update", "offer", "event"

Make it engaging and specific to {niche} in Bangalore.

Return ONLY valid JSON. No markdown. No backticks. No explanation."""

    return call_groq(prompt, temperature=0.5, max_tokens=1500)


def generate_linkedin_post(keyword, niche, location):
    logger.info(f"Generating LinkedIn post for: {keyword}")

    prompt = f"""Generate a LinkedIn post for a {niche} business targeting {location}.

Target Keyword: {keyword}

Return a JSON object with:
- post_text: 200-350 words, starts with a strong hook, professional tone
- hashtags: list of 5 hashtags WITHOUT the # symbol
- first_comment: follow-up comment for engagement

Make it specific to {niche} in {location}. Professional and engaging.

Return ONLY valid JSON. No markdown. No backticks. No explanation."""

    return call_groq(prompt, temperature=0.5, max_tokens=2000)


def run_content_generator(keyword, gaps, niche, location):
    print(f"\n✍️ STEP 3: Content Generation for '{keyword}'")
    print("=" * 60)

    logger.info(f"Starting content generation for: {keyword}")

    website_content = generate_website_page(keyword, gaps, niche, location)
    time.sleep(1)

    gmb_content = generate_gmb_post(keyword, niche, location)
    time.sleep(1)

    linkedin_content = generate_linkedin_post(keyword, niche, location)

    result = {
        "website": website_content,
        "gmb": gmb_content,
        "linkedin": linkedin_content,
    }

    today = date.today().strftime("%Y%m%d")
    safe_keyword = keyword.replace(" ", "_")[:20]
    output_file = f"outputs/content/{safe_keyword}_{today}.json"

    with open(output_file, "w") as f:
        json.dump(result, f, indent=2)

    print(f"\n📝 Content Generated:")
    print("-" * 40)
    print(f"✅ Website Page: {website_content.get('title', 'N/A')}")
    print(f"✅ GMB Post: {gmb_content.get('cta_type', 'N/A')} CTA")
    print(f"✅ LinkedIn Post: {len(linkedin_content.get('post_text', ''))} chars")
    print("-" * 40)
    print(f"✅ Saved to {output_file}")

    logger.info("Content generation complete")
    return result


if __name__ == "__main__":
    result = run_content_generator(
        keyword="saas project management tool",
        gaps={
            "missing_topics": ["pricing", "integrations"],
            "subtopics_to_add": ["team collaboration"],
        },
        niche="SaaS / project management",
        location="Bangalore, India",
    )
    print(f"\nContent generated: {bool(result.get('website'))}")
