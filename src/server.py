# Copyright (c) 2025 Dedalus Labs, Inc. and its contributors
# SPDX-License-Identifier: MIT

from dedalus_mcp import MCPServer
from dedalus_mcp.server import TransportSecuritySettings

from brave import brave_tools


# --- Server ------------------------------------------------------------------

server = MCPServer(
    name="brave-search-mcp",
    http_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
    streamable_http_stateless=True,
)


async def main() -> None:
    server.collect(*brave_tools)
    await server.serve(port=8080)
