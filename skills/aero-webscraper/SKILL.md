---
name: aero-webscraper
description: Use when the user asks AERO to research, scrape, collect, document, or organize sources for a device, console, game, software project, or service. Coordinate the eight skills using only tools actually available inside ChatGPT; no custom backend or local setup.
---

# AERO-WebScraper — native coordinator

## Execution boundary

You are the researcher and collector. These documents are instructions, not tools or
running agents. Use native web search, page opening/link following, document inspection,
and file tools exposed in this conversation. Never require or launch the old AERO
backend, install packages, write a network crawler, start a server, or request API keys.
Do not invent the retired eleven AERO tool functions. A missing optional tool reduces
that operation only; it must not block supported browsing and research.

Read [native operations](references/native-operations.md) and the
[AERO-Library skill](../aero-library/SKILL.md) before collection. These references own
shared evidence and output rules. Load a specialist only for its subject. Apply skill
loading through the host's documented resource mechanism; relative paths here identify
bundled resources, not invented remote endpoints. When a resource cannot be loaded,
report that narrow limitation and follow the shared rules already available.

## Start with execution, not a setup exercise

1. Extract target, requested result, source restrictions, and stopping condition from
   the user's request. Reuse supplied details. Resolve truly different possible targets
   only when necessary; otherwise state a narrow assumption and start.
2. Identify the actual available tools. Native browsing is enough for research;
   file creation adds exports. Connected storage is optional and never a prerequisite.
   Do not claim installation grants new capabilities or enables a disabled tool.
3. Choose the requested mode: research (cited findings), collect (catalog plus evidence
   and supported original files), catalog-only (links/metadata), retrieve, or resume.
   Default a broad device request to a first collection pass, not exhaustive mirroring.
4. Set visible scope and finite bounds. Unless the user specifies otherwise, use at
   most 8 search queries, 20 distinct opened source pages, 2 link hops beyond a seed,
   and 10 original-file attempts per pass. These are workflow limits, not measured
   bandwidth or platform quotas. A tool's smaller limits always win. Reading successive
   ranges of one document does not add distinct pages, but still consumes tool budget.
5. Create a run identifier unique within the loaded catalog and a small work queue.
   IDs assigned here are catalog labels, not backend-generated identifiers. Read the
   latest saved checkpoint before reusing an existing run. Never assume hidden memory.

## Discovery and bounded collection loop

Search primary publishers, official documentation, maintainers, upstream repositories,
and original research first. Use community sources when needed and label their role.
Form queries from target aliases, exact model/revision, category, symbols, and formats.
Avoid secrets or private identifiers in public searches. For a URL-scoped task, stay
inside that scope unless the user authorizes expansion.

For each relevant candidate: record how it was found; open the actual source; read the
relevant content; follow useful observed documentation/download links within budget;
extract source-supported facts; record precise applicability; and update one shared
catalog. Do not treat a search snippet as a fully inspected source. Follow pagination
and continuation only from actual tool outputs, not guessed page URLs or invented IDs.
Deduplicate discovered URLs before visiting; keep distinct versions, anchors, and source
occurrences where they carry different evidence.

Create an attributed note with concrete technical information, not just an annotated
bookmark, when a source was actually inspected. For large sources read the relevant
section and explicitly record partial coverage. Inspect visual evidence when a claim
depends on a diagram, chart, scan, or pinout. Never reconstruct missing evidence from
memory and call it extraction. Unsupported downloads become link-only catalog entries;
never save rendered text with a .pdf/.bin suffix or call a summary an original.

## Specialist routing

| Subject | Skill |
|---|---|
| Manuals, hardware, boards, pinouts, peripherals | [HardwareDocs](../aero-hardware-docs/SKILL.md) |
| Firmware releases, formats, components, updates | [Firmware](../aero-firmware/SKILL.md) |
| SDKs, libraries, APIs, toolchains, examples | [DevLibraries](../aero-dev-libraries/SKILL.md) |
| RE papers, decompilations, symbols, emulator research | [CodeResearch](../aero-code-research/SKILL.md) |
| Games, ports, homebrew, mods, saves | [GamesHomebrew](../aero-games-homebrew/SKILL.md) |
| Protocols, replacement services, deployment references | [NetworkServices](../aero-network-services/SKILL.md) |
| Cataloging, imports, retrieval, export, checkpoints | [Library](../aero-library/SKILL.md) |

These are role-specific procedures executed by the current assistant, not separate
processes. Do not claim parallel workers or cross-agent delegation without actual tools.

## Checkpoint and finish

After each small batch and before ending, record completed sources, failed attempts,
remaining URLs, coverage gaps, counters, source restrictions, and the next useful step.
End at the requested coverage, access barrier, tool/context limit, or declared budget;
return partial work now rather than promising future background completion.

Report inspected-source count, originals actually saved, notes generated, catalog-only
entries, failures, unresolved categories, and confirmed output locations separately.
Use real source citations. Give a resume instruction tied to the exported checkpoint.
Preserve AERO's existing scientific-record, verification, engineering, and completion
rules: collected references are advisory, not verified reverse-engineering conclusions.
