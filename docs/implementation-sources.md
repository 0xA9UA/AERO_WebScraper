# Implementation sources

The attached user specification and MMA skill are the authoritative requested design.
Current external format checks were limited to primary specifications, consulted during
this build on 2026-09-30:

- Agent Plugins 1.0.0 manifest: https://agent-plugins.org/schemas/1.0.0/plugin.schema.json
- Agent Plugins 1.0.0 MCP configuration: https://agent-plugins.org/schemas/1.0.0/mcp.schema.json
- Portable packaging: https://agent-plugins.org/plugin-authors/mcp-servers
- MCP tool contract (implemented negotiated version): https://modelcontextprotocol.io/specification/2025-06-18/server/tools
- Official Python SDK status reviewed: https://github.com/modelcontextprotocol/python-sdk

The SDK was not installed or bundled; the shipped stdio adapter is a deliberately minimal
implementation of the documented tool protocol. No claims of current SDK conformance,
cloud-host availability or live crawling follow from reviewing these sources.