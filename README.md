# AERO-WebScraper 0.2.0 — skills-only

AERO-WebScraper is now an instruction-based research and collection plugin. ChatGPT
performs the browsing, source inspection, extraction, classification, and reporting with
its available native tools. There is no custom scraper, Python application, MCP server,
API key, database service, local installation, or externally hosted backend to run.

## Use it

Select AERO-WebScraper in ChatGPT and ask, for example:

> Collect Nintendo Wii hardware and networking documentation. Prioritize primary
> references. Inspect up to 20 relevant sources, extract technical notes, organize a
> source catalog, and create a checkpoint. Clearly separate saved originals from links.

> Resume this collection using the attached CHECKPOINT.json and CATALOG.jsonl.
> Focus on gaps in replacement-service protocol documentation.

The existing default prompt remains a planning request. Ask explicitly to collect or
research to execute a collection instead of only drafting a plan.

## Eight skills

AERO-WebScraper coordinates. HardwareDocs, Firmware, DevLibraries, CodeResearch,
GamesHomebrew, and NetworkServices provide specialist research procedures. AERO-Library
maintains the shared catalog, notes, provenance, exports, and checkpoints. These are
instructions used by one assistant, not eight running processes.

## Outputs

A collection normally produces REPORT.md, CATALOG.jsonl, CHECKPOINT.json, and
SOURCE_NOTES.md. With native file support, it may include actual original files and a ZIP.
Without file creation it returns the same content inline and reports that no file was
created. Unsupported binary downloads remain source links, not fake saved files.

## Boundaries

Tool availability, source accessibility, copyright limits, quotas, and host permissions
still apply. Skills cannot guarantee complete website mirrors, continuous background
crawling, immutable storage, or arbitrary downloads. Catalog IDs and retrieval preferences
are instruction-level bookkeeping, not backend enforcement. Persistence is reported only
for confirmed saves; temporary working files are not a cross-session database.

The active repository contains only instructions, references, templates, and manifests.
The 0.1.0 Python implementation remains in Git history, not in the active plugin.
See [deployment](DEPLOYMENT.md), [limitations](LIMITATIONS.md),
[validation](TEST_RESULTS.md), and [migration](CHANGELOG.md).
