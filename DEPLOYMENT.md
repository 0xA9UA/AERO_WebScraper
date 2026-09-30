# Use inside ChatGPT — no backend deployment

Select the updated AERO-WebScraper plugin and send a research or collection request.
Use a conversation with native web browsing for public-source research. Native file
creation is optional for downloadable catalogs; native file reading enables imports and
retrieval. No terminal, dependency installation, model download, local computer access,
server URL, API key, or MCP connection is required by this release.

Capabilities come from the selected ChatGPT mode and account, not from these skill files.
When a needed operation is absent, the plugin must identify that operation and continue
with supported work. A fresh chat may be needed if an existing conversation retains old
instructions; verify the plugin version shown is 0.2.0 rather than assuming a UI refresh.

## Persistence and resumption

Keep the generated checkpoint and catalog together. Attach or select them in a later
conversation and request resumption. Native Library or an already connected storage app
may be used only when available and authorized. No external storage account is required.
A saved conversation and temporary file path are not proof of a durable shared filesystem.

## Existing account-plugin migration

The account updater overlays files and cannot delete old paths. The update therefore
empties both MCP server maps, removes legacy manifest launch bindings, replaces old
runtime source with inert comment-only migration markers, and supersedes backend-era
references. Historical filenames may remain in that account package, but they contain
no functioning crawler/server or required dependency installation.

The clean ZIP and current repository omit runtime paths altogether. Prior release
archives/history are unchanged. The update does not uninstall anything from a user's PC,
stop an independently running 0.1.0 process, move an existing library, or change sharing.
No such process is needed for 0.2.0.
