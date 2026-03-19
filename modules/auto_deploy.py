import os
import json
import base64
import logging
import requests
from config.config import GITHUB_TOKEN, GITHUB_OWNER, GITHUB_REPO

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def build_html_page(content_data, keyword):
    logger.info(f"Building HTML page for keyword: {keyword}")

    website = content_data.get("website", {})

    title = website.get("title", keyword)
    meta_desc = website.get("meta_description", "")
    h1 = website.get("h1", keyword)
    content = website.get("content", "")
    schema = website.get("schema_markup", "")
    focus_keyword = website.get("focus_keyword", keyword)
    secondary = website.get("secondary_keywords", [])

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{meta_desc}">
    <meta name="keywords" content="{", ".join(secondary)}">
    <script type="application/ld+json">{schema}</script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        header {{ background: #1a1a2e; color: white; padding: 40px 20px; text-align: center; }}
        h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        .subtitle {{ font-size: 1.2em; opacity: 0.9; }}
        main {{ padding: 40px 20px; }}
        h2 {{ color: #1a1a2e; font-size: 1.8em; margin: 30px 0 15px; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
        h3 {{ color: #333; font-size: 1.4em; margin: 20px 0 10px; }}
        p {{ margin-bottom: 15px; }}
        ul, ol {{ margin: 15px 0 15px 30px; }}
        li {{ margin-bottom: 8px; }}
        .cta {{ background: #e94560; color: white; padding: 15px 30px; border-radius: 5px; text-decoration: none; display: inline-block; margin: 20px 0; font-weight: bold; }}
        .cta:hover {{ background: #d63851; }}
        footer {{ background: #1a1a2e; color: white; text-align: center; padding: 20px; margin-top: 40px; }}
    </style>
</head>
<body>
    <header>
        <div class="container">
            <h1>{h1}</h1>
            <p class="subtitle">{meta_desc}</p>
        </div>
    </header>
    <main class="container">
        {content}
        <a href="#" class="cta">Get Started Today</a>
    </main>
    <footer>
        <p>&copy; 2026. All rights reserved.</p>
    </footer>
</body>
</html>"""

    logger.info("HTML page built successfully")
    return html


def deploy_to_github(filename, html_content, keyword):
    logger.info(f"Deploying {filename} to GitHub")

    if not GITHUB_TOKEN or not GITHUB_OWNER or not GITHUB_REPO:
        logger.error("GitHub configuration missing")
        return {"success": False, "error": "GitHub credentials not configured"}

    api_url = (
        f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/contents/{filename}"
    )

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }

    try:
        get_response = requests.get(api_url, headers=headers, timeout=30)

        sha = None
        if get_response.status_code == 200:
            sha = get_response.json().get("sha")
            logger.info(f"File exists, will update. SHA: {sha}")
        elif get_response.status_code != 404:
            get_response.raise_for_status()

        encoded_content = base64.b64encode(html_content.encode("utf-8")).decode("utf-8")

        data = {
            "message": f"Add SEO content for keyword: {keyword}",
            "content": encoded_content,
        }

        if sha:
            data["sha"] = sha

        put_response = requests.put(api_url, headers=headers, json=data, timeout=30)
        put_response.raise_for_status()

        result = put_response.json()
        github_url = result.get("content", {}).get("html_url", "")

        logger.info(f"Successfully deployed to GitHub: {github_url}")
        return {"success": True, "github_url": github_url}

    except requests.exceptions.HTTPError as e:
        logger.error(f"GitHub API error: {e}")
        return {"success": False, "error": f"GitHub API error: {str(e)}"}
    except Exception as e:
        logger.error(f"Error deploying to GitHub: {e}")
        return {"success": False, "error": str(e)}


def run_auto_deploy(content_data, keyword):
    print(f"\n🚀 STEP 5: Auto-Deploy to GitHub")
    print("=" * 60)

    logger.info(f"Starting auto-deploy for keyword: {keyword}")

    html_content = build_html_page(content_data, keyword)

    safe_keyword = keyword.replace(" ", "-").lower()[:30]
    filename = f"pages/{safe_keyword}.html"

    result = deploy_to_github(filename, html_content, keyword)

    if result.get("success"):
        print(f"\n✅ Deployment Successful!")
        print(f"   URL: {result.get('github_url')}")
    else:
        print(f"\n❌ Deployment Failed: {result.get('error')}")

    logger.info("Auto-deploy complete")
    return result


if __name__ == "__main__":
    sample_content = {
        "website": {
            "title": "Best Project Management Tool for SaaS",
            "meta_description": "Manage your projects efficiently with our SaaS project management tool. Built for teams in Bangalore.",
            "h1": "Streamline Your Projects with Our SaaS Tool",
            "content": "<p>Content goes here</p>",
            "focus_keyword": "project management",
            "secondary_keywords": ["task management", "team collaboration"],
        }
    }
    result = run_auto_deploy(sample_content, "test-keyword")
    print(f"\nSuccess: {result.get('success')}")
