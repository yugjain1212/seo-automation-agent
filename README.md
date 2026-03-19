# SEO Automation Agent

An end-to-end SEO automation pipeline for SaaS/tech products targeting Bangalore, India. The system takes a seed keyword as input and automatically handles keyword research, competitor analysis, AI content generation, on-page auditing, GitHub deployment, and rank reporting.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        SEO Automation Agent                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────┐    ┌──────────────────┐                  │
│  │  Keyword         │───▶│  Competitor       │                  │
│  │  Research        │    │  Analysis         │                  │
│  │  (SerpAPI)       │    │  (SerpAPI + Groq) │                  │
│  └────────┬─────────┘    └────────┬─────────┘                  │
│           │                        │                             │
│           ▼                        ▼                             │
│  ┌──────────────────┐    ┌──────────────────┐                  │
│  │  Content         │───▶│  SEO Audit       │                  │
│  │  Generator       │    │  (BeautifulSoup) │                  │
│  │  (Groq)          │    │                  │                  │
│  └────────┬─────────┘    └────────┬─────────┘                  │
│           │                        │                             │
│           ▼                        ▼                             │
│  ┌──────────────────┐    ┌──────────────────┐                  │
│  │  Auto Deploy     │    │  Rank Report    │                  │
│  │  (GitHub API)    │    │  (Search Console)│                  │
│  └──────────────────┘    └──────────────────┘                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Quickstart

```bash
# Clone and navigate to project
git clone <repo-url>
cd seo-automation-agent

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment variables
cp .env.example .env
# Edit .env with your API keys

# Run the SEO agent
python main.py
```

## API Keys Required

| Key | Purpose | Where to Get |
|-----|---------|--------------|
| GROQ_API_KEY | AI content generation | groq.com |
| SERP_API_KEY | Keyword research & competitor data | serpapi.com |
| GITHUB_TOKEN | Auto-deploy generated pages | github.com/settings/tokens |
| GITHUB_OWNER | Your GitHub username | - |
| GITHUB_REPO | Target repository name | - |

## Project Structure

```
seo-automation-agent/
├── main.py                 # Orchestrator - runs all 6 steps
├── requirements.txt        # Python dependencies
├── config/
│   └── config.py          # Environment variable loader
├── modules/
│   ├── keyword_research.py    # SerpAPI autocomplete + related searches
│   ├── competitor_analysis.py # Top 5 competitors + gap analysis
│   ├── content_generator.py   # Website, GMB, LinkedIn content
│   ├── seo_audit.py           # On-page SEO scoring (0-100)
│   ├── auto_deploy.py         # GitHub REST API deployment
│   └── rank_report.py         # Google Search Console integration
├── dashboard/
│   └── index.html        # HTML dashboard for viewing reports
└── outputs/
    ├── keywords/        # JSON keyword data
    ├── content/         # Generated content
    └── reports/         # Audit & rank reports
```

## Module Breakdown

1. **keyword_research.py** - Fetches keywords from SerpAPI autocomplete and related searches, then uses Groq to score and rank them by priority.

2. **competitor_analysis.py** - Scrapes top 5 Google results and identifies content gaps using Groq AI.

3. **content_generator.py** - Generates SEO-optimized content for 3 platforms: website pages, Google My Business posts, and LinkedIn posts.

4. **seo_audit.py** - Audits any URL for on-page SEO issues (title, meta, headings, schema, word count) and scores it out of 100.

5. **auto_deploy.py** - Builds HTML from generated content and pushes to GitHub repository.

6. **rank_report.py** - Pulls real ranking data from Google Search Console API and shows week-over-week changes.

## Sample Output

```
🔍 STEP 1: Keyword Research for 'saas project management tool'
============================================================
📊 Ranked Keywords (Priority >= 6):
--------------------------------------------------------------------------------
Keyword                               Score    Intent           Platform   
--------------------------------------------------------------------------------
saas project management tool         9        commercial       gmb       
best project management software      8        commercial       gmb       
project management software for teams 8        commercial       website   
free project management tool          8        transactional    website   
project management tool for startup   7        commercial       website   
agile project management tool        7        transactional    website   
--------------------------------------------------------------------------------

✅ Saved 12 keywords to outputs/keywords/...
```

## Error Handling

- **Retry Logic**: All Groq API calls have 2 attempts with 3-second delay between retries
- **Graceful Failures**: If any step fails, the pipeline logs the error and continues to the next step
- **Logging**: Every function logs at INFO level, errors at ERROR level with full exception details

## Running Individual Modules

```bash
# Test keyword research only
python -m modules.keyword_research

# Test competitor analysis
python -m modules.competitor_analysis

# Test content generation
python -m modules.content_generator

# Test SEO audit
python -m modules.seo_audit

# Test auto-deploy
python -m modules.auto_deploy

# Test rank report
python -m modules.rank_report
```

## Tool Choices

- **Groq over OpenAI**: Free tier available, faster inference, competitive quality
- **SerpAPI over manual scraping**: Structured data, Terms of Service compliant, reliable
- **GitHub API over FTP**: Real version control, free hosting via GitHub Pages, CI/CD ready
- **BeautifulSoup over Selenium**: Lightweight, no browser needed, faster for simple audits

## What I'd Improve

1. **Paid SerpAPI** - Free tier has 100 searches/month limit; paid plans offer more for production use

2. **Ahrefs/Semrush API** - Replace SerpAPI with dedicated keyword difficulty scores and volume data

3. **WordPress REST API** - Deploy to WordPress CMS instead of static HTML for easier content management

4. **DataForSEO** - Better for competitor rank tracking and SERP feature analysis

5. **Slack Webhooks** - Real-time alerts when rankings drop significantly

6. **A/B Testing** - Generate multiple content variants and track which ranks faster
