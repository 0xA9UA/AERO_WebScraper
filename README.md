# AERO-WebScraper Suite 0.1.0

A private, local-first plugin package with eight specialist skills and an executable
reference-library backend. It collects **approved sources**, preserves original bytes
and provenance, and supplies advisory references without changing AERO scientific records.

**Delivery status:** local backend implemented and fixture-tested; local stdio MCP process
tested. No public endpoint, cloud deployment, live website crawl, or ChatGPT web/mobile
backend connection is represented as completed. Saving the plugin to an account does not
host its Python process. This release is a testable first implementation, not a claim that
every production-hardening requirement is closed.

## Start locally

Python 3.11 or later is required. Python 3.13.5/Linux is the tested environment.
From this source directory, install the backend using the same Python interpreter that
will run the MCP server:

```bash
python -m pip install ".[pdf]"
python -m aero_webscraper --root /absolute/path/AERO_LIBRARY init
python -m aero_webscraper --root /absolute/path/AERO_LIBRARY tools
```

On Windows, use an absolute Windows path such as `D:/AERO_DATA/AERO_LIBRARY`.
See `docs/deployment.md` for local plugin installation, source approvals and persistent
storage. No search-engine API key is required for seed crawling; that is not the same as
providing an independent web search engine.

## Run the demonstration and tests

```bash
python -m pip install ".[pdf,test]"
python scripts/demo.py --output /absolute/path/new-demo-directory
python -m pytest -q
```

The demonstration uses synthetic documents, a locally created Git repository, and an
inert binary blob, organized under the Wii platform tree. They are **not Wii specifications,
Wii firmware, or recovered Nintendo code**. It reads a cited passage, exports ordinary
files, writes only to an explicitly configured reference intake, disables retrieval, and
verifies the disabled state. The output directory must not already exist.

## Included

The canonical source is `src/aero_webscraper/`. `plugins/aero-webscraper/` is a generated,
self-contained package containing skills, the portable manifest, local MCP configuration,
and a source-only runtime copy. Never hand-edit its runtime copy instead of canonical
source. `scripts/package.py` regenerates and checks it. There is no collected corpus in
plugin assets.

Read `MMA_SKILL_INDEX.md` first when changing code. Detailed contracts, test results and
known boundaries are in `docs/`. Input and record schemas are in `schemas/`.

## Non-negotiable distinctions

Stored is not indexed; indexed is not verified; a source claim is not an AERO finding.
A server archive pinned to a Git commit is a source snapshot, not a tested build.
Retrieval OFF blocks new library delivery through the supported CLI/stdio boundaries,
including a queued result, but cannot erase already supplied context or revoke files
that were previously exported. Acquisition and retrieval permissions are separate.