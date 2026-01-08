# Copyright (c) 2025 Dedalus Labs, Inc. and its contributors
# SPDX-License-Identifier: MIT

"""Sample MCP client for testing the Brave Search MCP server."""

import asyncio

from dedalus_mcp import MCPClient


SERVER_URL = "http://localhost:3009/mcp"


async def main() -> None:
    client = await MCPClient.connect(SERVER_URL)

    # List tools
    result = await client.list_tools()
    print(f"\nAvailable tools ({len(result.tools)}):\n")
    for t in result.tools:
        print(f"  {t.name}")
        if t.description:
            print(f"    {t.description[:80]}...")
        print()

    # Test brave_web_search
    print("--- brave_web_search ---")
    web_results = await client.call_tool(
        "brave_web_search",
        {"query": "python programming", "count": 3},
    )
    print(web_results)
    print()

    # Test brave_local_search
    print("--- brave_local_search ---")
    local_results = await client.call_tool(
        "brave_local_search",
        {"query": "coffee shops near Times Square", "count": 3},
    )
    print(local_results)

    await client.close()


if __name__ == "__main__":
    asyncio.run(main())
