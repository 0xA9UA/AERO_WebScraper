# AERO-WebScraper

This is one private plugin with eight skills and a local Python stdio MCP runtime.
Install the runtime dependencies into the Python interpreter used by the MCP host:
`python -m pip install "/absolute/path/aero-webscraper/runtime[pdf]"`.
The host must support local stdio and expand PLUGIN_ROOT/PLUGIN_DATA. Retrieval defaults
OFF. No source is approved automatically. See `DEPLOYMENT.md` before use.

A saved account plugin is not a hosted backend. On ChatGPT web/mobile, acquisition and
storage remain unavailable unless a separately hosted compatible service is connected.
There is no deployed endpoint in this package. All corpus data belongs outside the
plugin, in the host's persistent data directory. No real Wii reference corpus is bundled.