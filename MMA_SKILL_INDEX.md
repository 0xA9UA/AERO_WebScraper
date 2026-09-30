# MMA_SKILL_INDEX

## System purpose

Guide ChatGPT through native reference discovery, evidence extraction, organization,
retrieval, and resumable collection without a custom runtime. References remain advisory.

## Architecture

User request -> coordinator skill -> relevant subject skill -> native host tools ->
AERO-Library catalog/notes -> verified outputs and checkpoint.

## Module map

| Path | Responsibility |
|---|---|
| plugin.json | Portable identity, version, and listing; no server dependency |
| .codex-plugin/plugin.json | Synchronized legacy client discovery metadata |
| skills/aero-webscraper/SKILL.md | Scope, routing, budgets, collection loop, stopping |
| skills/aero-webscraper/references/native-operations.md | Native capability routing, evidence and safety boundaries |
| skills/aero-library/SKILL.md | Shared catalog, imports, retrieval preferences, export and persistence |
| skills/aero-library/references/ | Record semantics and logical taxonomy |
| skills/aero-library/templates/ | Declarative JSON record/checkpoint templates |
| Other skills/*/SKILL.md | Six narrowly scoped technical research procedures |
| DEPLOYMENT.md, LIMITATIONS.md | Setup-free use, migration, and honest limitations |
| TEST_RESULTS.md | Release-specific validation, not historical backend-test claims |

## Entry points and flows

Natural-language requests activate the coordinator or the matching specialist.
Resume loads actual checkpoint/catalog files before browsing pending sources.
Retrieval starts from scoped records and returns source-bound evidence, not model memory.
The native tool set is provided by the host; no executable entry point exists here.

## Invariants and navigation

No runtime, custom tools, network scripts, endpoints, secrets, or database dependencies.
Keep the exact defaultPrompt on listing edits. Keep eight skill names stable. Change
collection behavior in the coordinator; evidence format in AERO-Library references;
subject-specific judgment in the relevant specialist. All claims need actual evidence.
Update this map when those ownership boundaries change.
