# AERO-WebScraper 0.1.0 — validation report

Build date: 2026-09-30. Environment: Linux, Python 3.13.5.

## Result

**77 automated tests passed; zero failures, errors or skips in the final completed runs.**
The final source was tested in two invocations. Prior exploratory/incomplete runs are not
counted as release evidence. No live website was crawled in this build.

| Final run | Passed | Elapsed |
|---|---:|---:|
| Integration | 30 | 29.89 seconds |
| Unit and security | 47 (12 unit + 35 security) | 10.77 seconds |
| Total | 77 | 40.66 seconds |

Raw console logs and JUnit XML are in `docs/validation/`. These counts cover the backend;
packaging checks and the standalone demonstration are separate validations below.

## Covered behavior

Imports: unchanged idempotence, changed-content revisions, separate scope/version records,
SHA-256 deduplication with separate source occurrences, local Git commit pinning, inert
binary retention, folder imports, HTML visible-text extraction and physical PDF-page anchors.

Durability: interrupted record-commit replay, simultaneous thread/process imports,
immutable-record conflict rejection and index rebuilding from authoritative records.

Retrieval and export: exact case-sensitive symbols, lexical search, scope filtering,
pinned source-bound reads, permission-filtered ordinary file copies, explicit advisory
intake, OFF-gate checks and stale queued-result revocation after operator changes.

Security: private/mixed DNS responses, exact host allowlists, redirect rechecks,
robots failure/denial, bounded streamed reads, path traversal and symlinks, archive
traversal/symlink/expansion rejection, heuristic secret quarantine, original-byte tamper,
source/storage/model-transmission revocation and untrusted instruction treatment.

Orchestration: bounded synthetic seed crawling, resumable steps, accurate failures,
metadata-only handling without acquisition authority, item budgets and attributed
operator/agent discovery receipts. Network tests use synthetic adapters/mocked sockets,
not live external services.

## Actual packaged stdio check

The packaged `runtime/launch.py` was started as a real Python subprocess without relying
on the repository PYTHONPATH. It initialized a fresh isolated data directory, negotiated
MCP 2025-06-18, exposed **all eleven tools**, passed `library_validate`, and denied a
reference search because retrieval defaults to OFF. This is not a test in the user's
ChatGPT/Codex client or independent MCP SDK/Inspector conformance certification.

## Standalone synthetic platform workflow

The demonstrated platform identity is Nintendo Wii; **all document content and bytes
are synthetic test data, not Nintendo documentation, firmware or factual device evidence.**

| Step | Observed result |
|---|---|
| Markdown manual | Imported and indexed; model-generated provenance recorded |
| Local source repository | Imported as a snapshot pinned to `0520086afded2f26f54883a6ecf9ba553ff917e5` |
| Inert binary | Retained as STORED_ONLY; never executed |
| Two-page PDF | Imported; search resolved the physical page-2 marker |
| Cited passage | Returned a pinned item/revision/chunk citation and matching original hash |
| AERO intake | Wrote an advisory reference into a synthetic, explicitly registered intake |
| Ordinary export | Four independent, correctly suffixed files and a provenance manifest |
| Retrieval OFF | New search and queued result both rejected with RETRIEVAL_OFF |
| Integrity/rebuild | Valid, with zero reported integrity/citation/pointer errors |

Final library validation counted 4 item records,
11 immutable objects and
5 citation chunks. The demo ends with retrieval OFF.
`docs/validation/demo-report.json` contains actual generated IDs and paths. Paths under
`/mnt/data` identify the build environment, not an installed library on the user's machine.
The PDF was rendered and visually inspected. `scripts/demo.py --output NEW_DIRECTORY`
reproduces the workflow using installed test/PDF dependencies and Git.

## Package and source checks

Eight skills, eleven tool schemas, sixteen total JSON schemas, and forty handwritten
Python files passed local structural/schema/syntax/MMA checks. Tool schemas match the
current Pydantic input contracts. Plugin and source ZIPs have a single expected root,
pass ZIP integrity checks, and exclude corpus, dependency installations, credentials,
symlinks and bytecode caches. The runtime copy is regenerated from canonical source.
These checks do not substitute for the plugin account service's own package validation.

## Explicitly not validated or not implemented

The scraper is **not hosted or connected to ChatGPT web/mobile**. The runtime is local
stdio only. Remote authenticated HTTP, OAuth, UI, semantic embeddings, OCR, JavaScript
rendering, remote repository cloning, binary decompilation and cloud/Drive storage
adapters are not implemented. Internet discovery uses externally supplied seeds/receipts;
there is no built-in general search-engine service.

No live website crawling, Windows deployment, distributed/NFS durability, hostile-parser
sandbox certification, high-volume performance testing or user's-client installation
was performed. The parser subprocess is resource-bounded but is not an OS security
sandbox. Transfer/request budgeting has documented gaps around failed requests, robots
traffic, DNS deadlines and crashes; do not treat retained-byte budgets as strict billed
network-transfer limits. See `docs/security-and-limitations.md` before deployment.

## Installed dependency versions used for tests

| Package | Version |
|---|---|
| pydantic | 2.13.4 |
| filelock | 3.29.0 |
| PyYAML | 6.0.3 |
| pypdf | 5.9.0 |
| pytest | 9.0.2 |
| jsonschema | 4.26.0 |
| reportlab | 4.4.9 |

Runtime installation will require these compatible dependencies to be available. Network
dependency downloads failed in the build environment; installed packages were used.