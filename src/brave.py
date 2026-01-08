# Copyright (c) 2025 Dedalus Labs, Inc. and its contributors
# SPDX-License-Identifier: MIT

"""Brave Search operations for MCP server.

Required environment variables:
    BRAVE_API_KEY: Brave Search API subscription token

API Documentation:
    https://api.search.brave.com/app/documentation/web-search/get-started
"""

import os
from typing import Any
from urllib.parse import quote

import httpx
from dotenv import load_dotenv
from pydantic import BaseModel

from dedalus_mcp import tool


load_dotenv()

# Read API key from environment
BRAVE_API_KEY = os.getenv("BRAVE_API_KEY", "")
BRAVE_BASE_URL = "https://api.search.brave.com/res/v1"


# --- Response Models ---------------------------------------------------------


class BraveResult(BaseModel):
    """Generic Brave API result."""

    success: bool
    data: Any = None
    error: str | None = None


# --- Helper ------------------------------------------------------------------


async def _request(path: str) -> BraveResult:
    """Make a request to Brave Search API.

    Args:
        path: API path (e.g., "/web/search?q=...")

    Returns:
        BraveResult with success status and data or error.
    """
    if not BRAVE_API_KEY:
        return BraveResult(success=False, error="BRAVE_API_KEY environment variable not set")

    url = f"{BRAVE_BASE_URL}{path}"
    headers = {
        "X-Subscription-Token": BRAVE_API_KEY,
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return BraveResult(success=True, data=response.json())
    except Exception as e:
        return BraveResult(success=False, error=str(e))


def _format_address(address: dict[str, Any] | None) -> str:
    """Format address components into a single string."""
    if not address:
        return "N/A"

    parts = [
        address.get("streetAddress", ""),
        address.get("addressLocality", ""),
        address.get("addressRegion", ""),
        address.get("postalCode", ""),
    ]
    formatted = ", ".join(part for part in parts if part)
    return formatted or "N/A"


# --- Search Tools ------------------------------------------------------------


@tool(
    description=(
        "Performs a web search using the Brave Search API, ideal for general queries, "
        "news, articles, and online content. Use this for broad information gathering, "
        "recent events, or when you need diverse web sources. Supports pagination. "
        "Maximum 20 results per request."
    )
)
async def brave_web_search(
    query: str,
    count: int = 10,
    offset: int = 0,
) -> BraveResult:
    """Search the web using Brave Search API.

    Args:
        query: Search query (max 400 chars, 50 words).
        count: Number of results (1-20, default 10).
        offset: Pagination offset (max 9, default 0).

    Returns:
        BraveResult with search results.
    """
    count = max(1, min(count, 20))
    offset = max(0, min(offset, 9))

    encoded_query = quote(query, safe="")
    path = f"/web/search?q={encoded_query}&count={count}&offset={offset}"

    result = await _request(path)
    if result.success:
        web_results = result.data.get("web", {}).get("results", [])
        result.data = [
            {
                "title": r.get("title", ""),
                "description": r.get("description", ""),
                "url": r.get("url", ""),
            }
            for r in web_results
        ]
    return result


@tool(
    description=(
        "Searches for local businesses and places using Brave's Local Search API. "
        "Best for queries related to physical locations, businesses, restaurants, services, etc. "
        "Returns detailed information including business names, addresses, ratings, "
        "phone numbers, and opening hours. Use this when the query implies 'near me' "
        "or mentions specific locations. Automatically falls back to web search if no "
        "local results are found."
    )
)
async def brave_local_search(
    query: str,
    count: int = 5,
) -> BraveResult:
    """Search for local businesses and places.

    Args:
        query: Local search query (e.g., 'pizza near Central Park').
        count: Number of results (1-20, default 5).

    Returns:
        BraveResult with local search results.
    """
    count = max(1, min(count, 20))

    encoded_query = quote(query, safe="")
    path = f"/web/search?q={encoded_query}&search_lang=en&result_filter=locations&count={count}"

    result = await _request(path)
    if not result.success:
        return result

    locations = result.data.get("locations", {}).get("results", [])
    location_ids = [loc.get("id") for loc in locations if loc.get("id")]

    # If no local results, fall back to web search
    if not location_ids:
        web_result = await brave_web_search(query, count)
        if web_result.success:
            web_result.data = [
                {"name": r["title"], "address": "N/A", "description": r["description"]}
                for r in web_result.data
            ]
        return web_result

    # Get POI details
    ids_param = "&".join(f"ids={id_}" for id_ in location_ids if id_)
    pois_result = await _request(f"/local/pois?{ids_param}")

    if not pois_result.success:
        return pois_result

    # Get descriptions (optional)
    descriptions_map = {}
    desc_result = await _request(f"/local/descriptions?{ids_param}")
    if desc_result.success:
        descriptions_map = desc_result.data.get("descriptions", {})

    # Format results
    results = []
    for poi in pois_result.data.get("results", []):
        poi_id = poi.get("id", "")
        rating_info = poi.get("rating", {}) or {}

        results.append({
            "name": poi.get("name", "Unknown"),
            "address": _format_address(poi.get("address")),
            "phone": poi.get("phone"),
            "rating": rating_info.get("ratingValue"),
            "rating_count": rating_info.get("ratingCount", 0),
            "price_range": poi.get("priceRange"),
            "hours": ", ".join(poi.get("openingHours", [])) or None,
            "description": descriptions_map.get(poi_id),
        })

    return BraveResult(success=True, data=results)


# --- Export ------------------------------------------------------------------

brave_tools = [
    brave_web_search,
    brave_local_search,
]
