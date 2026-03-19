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
    missing_angles = gaps.get("missing_angles", [])
    subtopics = gaps.get("subtopics_to_add", [])

    prompt = f"""You are an expert SEO copywriter for a {niche} startup in {location}. You are writing for founders and tech teams who need project management solutions.

Target keyword: "{keyword}"
Location context: This page targets {location} specifically — mention local startup ecosystem, tech hubs like Koramangala/Indiranagar where relevant, and India-specific pricing in INR.

Your competitors rank #1-5 but are MISSING these topics — you MUST cover all of them to outrank them:
{json.dumps(missing_topics, indent=2)}

These unique angles no competitor uses — include them:
{json.dumps(missing_angles, indent=2)}

Subtopics to add:
{json.dumps(subtopics, indent=2)}

Write content that sounds like it was written by a {location} startup founder, not a generic AI. Include specific examples, real pain points of Indian SaaS teams, and actionable advice. Use terms like "starting at ₹X/month", mention Bangalore-based teams, and reference the local tech ecosystem.

Return a JSON object with:
- title: SEO title (50-60 characters, must contain keyword)
- meta_description: Meta description (150-160 characters)
- h1: Compelling H1 (different from title)
- content: Full HTML body content (800-1200 words with h2/h3 subheadings, covering ALL missing_topics from competitors)
- schema_markup: JSON-LD schema as string (SoftwareApplication type)
- focus_keyword: the main target keyword
- secondary_keywords: list of 5 secondary keywords

Return ONLY valid JSON. No markdown. No backticks. No explanation."""

    return call_groq(prompt, temperature=0.4, max_tokens=6000)


def generate_gmb_post(keyword, niche, location):
    logger.info(f"Generating GMB post for: {keyword}")

    prompt = f"""You are a {niche} business owner in {location}. Write a Google My Business post that feels authentic and local.

Target Keyword: {keyword}

Write like a real {location} startup founder. Mention:
- Local Bangalore context (tech hubs, startup culture, India-specific benefits)
- Pricing in INR ("starting at ₹X/month")
- Why this matters for Indian teams and businesses
- Genuine local relevance, not generic corporate speak

Return a JSON object with:
- post_text: 150-300 words, localized content mentioning {location}
- cta_type: one of "learn_more", "book", "sign_up", "call"
- category: one of "update", "offer", "event"

Return ONLY valid JSON. No markdown. No backticks. No explanation."""

    return call_groq(prompt, temperature=0.5, max_tokens=1500)


def generate_linkedin_post(keyword, niche, location):
    logger.info(f"Generating LinkedIn post for: {keyword}")

    prompt = f"""You are a tech entrepreneur from {location} sharing insights on LinkedIn. Your audience is Indian tech founders, product managers, and SaaS enthusiasts.

Target Keyword: {keyword}

Write a LinkedIn post that:
- Starts with a compelling hook that stops the scroll
- Sounds like a real {location} founder, not a content marketer
- Includes India-specific context (Bangalore startup ecosystem, Indian tech teams, INR pricing)
- Has genuine insights and actionable takeaways
- Ends with engagement-driving content

Return a JSON object with:
- post_text: 200-350 words, starts with a strong hook, professional but authentic tone
- hashtags: list of 5 hashtags WITHOUT the # symbol (use relevant Indian tech hashtags)
- first_comment: follow-up comment that drives engagement (ask a question or spark discussion)

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
            "missing_angles": ["Bangalore startup focus"],
            "subtopics_to_add": ["team collaboration"],
        },
        niche="SaaS / project management",
        location="Bangalore, India",
    )
    print(f"\nContent generated: {bool(result.get('website'))}")
