from langchain.tools import tool
import requests
from dotenv import load_dotenv
from tavily import TavilyClient
from rich import print # to disply good print result
import os
from bs4 import BeautifulSoup
from readability import Document
import trafilatura
import re
load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

@tool
def web_search(query : str) -> str:
    """Search the web for recent and reliable information on a topic . Returns Titles , URLs and snippets."""
    results = tavily.search(query=query,max_results=5)

    # print(results)

    out = []

    for r in results['results']:
        out.append(
            f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['content'][:300]}\n"
        )
    
    return "\n----\n".join(out)

# (genai) PS D:\GenAI\21_Agentic_AI\03_langchain\multiagent_system> python main.py
# {
#     'query': 'Latest AI news',
#     'follow_up_questions': None,
#     'answer': None,
#     'images': [],
#     'results': [
#         {
#             'url': 'https://www.artificialintelligence-news.com',
#             'title': 'AI News | Latest News | Insights Powering AI-Driven Business Growth',
#             'content': 'October 30, 2025\n\n### Malaysia launches Ryt Bank, its first AI-powered 
# bank\n\nFinance AI\n\nAugust 26, 2025\n\n### Google’s Veo 3 AI video creation tools are now widely 
# available\n\nAI in Action\n\nJuly 29, 2025\n\n#### Computer Vision\n\n### Microsoft’s Majorana 2 quantum 
# chip is also a case study for agentic AI in R&D\n\nInside AI\n\nJune 3, 2026\n\n### US and Japan announce 
# sweeping AI and tech collaboration\n\nArtificial Intelligence\n\nApril 11, 2024\n\n### UK and Canada sign 
# AI compute agreement [...] August 18, 2026\n\n### Okta targets AI agent token costs with MCP 
# scoping\n\nData Engineering & MLOps\n\nAugust 13, 2026\n\n### Red Hat, NVIDIA, IBM back project turning AI 
# policy into code\n\nGovernance, Regulation & Policy\n\nAugust 4, 2026\n\n#### Industries\n\n### NVIDIA 
# Jetson Orin Nano 2 brings physical AI to drones and robots\n\nPhysical AI\n\nAugust 26, 2026\n\n### 
# HoneyBook bets on agentic AI to streamline small business operations with its new Claude connector\n\nWorld
# of Work\n\nAugust 6, 2026 [...] September 1, 2026\n\n# ChatGPT Ads passes $1B run rate in 200 
# days\n\nPhysical AI\n\nAugust 27, 2026\n\n# A quarter of Nvidia’s business next year comes from labs it is 
# financing\n\nAI in Action\n\nAugust 26, 2026\n\n# Gatik raises $200M to scale AI-powered autonomous 
# freight\n\nPhysical AI\n\nAugust 26, 2026\n\n# NVIDIA Jetson Orin Nano 2 brings physical AI to drones and 
# robots\n\nEnvironment & Sustainability\n\nAugust 25, 2026\n\n# MIT AI forecasts extreme weather without 
# historical data\n\nPhysical AI\n\nAugust 24, 2026',
#             'score': 0.8665964,
#             'raw_content': None,
#             'id': 'd20e3a-00'
#         },

# this result in  for r in results['results'] came from the output. 





@tool
def scrape_url(url: str) -> str:
    """
    Scrape and extract clean readable content from a URL.
    Uses multiple extraction strategies for better reliability.
    """

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/",
    }

    try:
        # ── Fetch page ─────────────────────────────────────
        response = requests.get(
            url,
            headers=headers,
            timeout=15
        )

        response.raise_for_status()

        html = response.text

        # ──────────────────────────────────────────────────
        # Strategy 1 → trafilatura (BEST for articles/blogs)
        # ──────────────────────────────────────────────────
        extracted = trafilatura.extract(
            html,
            include_comments=False,
            include_tables=False
        )

        if extracted and len(extracted.strip()) > 200:
            cleaned = re.sub(r'\s+', ' ', extracted)
            return cleaned[:5000]

        # ──────────────────────────────────────────────────
        # Strategy 2 → readability
        # ──────────────────────────────────────────────────
        doc = Document(html)
        clean_html = doc.summary()

        soup = BeautifulSoup(clean_html, "html.parser")

        for tag in soup([
            "script",
            "style",
            "nav",
            "footer",
            "header",
            "aside",
            "form"
        ]):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)

        if text and len(text.strip()) > 200:
            cleaned = re.sub(r'\s+', ' ', text)
            return cleaned[:5000]

        # ──────────────────────────────────────────────────
        # Strategy 3 → fallback full page extraction
        # ──────────────────────────────────────────────────
        soup = BeautifulSoup(html, "html.parser")

        for tag in soup([
            "script",
            "style",
            "nav",
            "footer",
            "header",
            "aside",
            "form"
        ]):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)

        cleaned = re.sub(r'\s+', ' ', text)

        if cleaned:
            return cleaned[:5000]

        return "Could not extract meaningful content from the page."

    except requests.exceptions.Timeout:
        return "Request timed out while scraping the URL."

    except requests.exceptions.HTTPError as e:
        return f"HTTP error occurred: {str(e)}"

    except Exception as e:
        return f"Could not scrape URL: {str(e)}"


# output of this tool: 
# (genai) PS D:\GenAI\21_Agentic_AI\03_langchain\multiagent_system> python main.py
# C-Suite Lessons From The AI Outage That Hit ChatGPT, Claude And Grok AI outage lessons for the C-suite after ChatGPT, Claude and Grok went down together, with four moves every C-Suite should make now. What should a CIO do? A single email doesn’t need the same firepower as a full market analysis — and Hollywood already learned that lesson The Even ‘Dune: Part Two’ Didn’t Trust One AI to Do Everything. Here’s How to Pick the Right ChatGPT Model for the Job first appeared on The Blast Meta is updating its AI glasses to stop recording if someone covers the capture LED and cracking down on covert filming and harassment. "The AI exposed the weakness during normal use."
# (genai) PS D:\GenAI\21_Agentic_AI\03_langchain\multiagent_system> 