# MMA_SKILL_INDEX

## System Purpose

Collect permitted reference material into a versioned, content-addressed library and
provide source-bound, operator-gated retrieval for AERO. Library material is advisory.

## Architecture Snapshot

```text
plugin skills -> adapters/service -> orchestration -> acquisition / ingestion
                         |                |
                         +-> retrieval -> storage <- catalog projections
                                  |           |
                            operator policy  immutable objects + redo records
```

Domain contracts do not depend on adapters. Transport owns final delivery authorization.
The canonical source is `src/aero_webscraper`; the packaged runtime is generated.

## Module Map

| Path | Responsibility and public boundary | Important collaborators |
|---|---|---|
| `src/aero_webscraper/domain/` | Strict inputs/records, IDs, URL and error vocabulary | Standard library, Pydantic |
| `src/aero_webscraper/storage/` | Bounded files, immutable objects, redo commits, exports, validation | Domain; validation consumes catalog |
| `src/aero_webscraper/catalog/` | Supplied taxonomy, pointer navigation, rebuildable catalog and literal search | Store, Policy |
| `src/aero_webscraper/ingestion/` | Trusted parser worker over untrusted bytes | Domain, bounded subprocess runner |
| `src/aero_webscraper/acquisition/` | Public-IP-pinned HTTP(S), robots/rate checks, local Git snapshots | Operator Policy, standard network/Git interfaces |
| `src/aero_webscraper/orchestration/` | Import transactions, target identity, durable collection steps | All reusable library subsystems |
| `src/aero_webscraper/retrieval/` | Rights/generation gating, cited reads, explicit intake | Store, Index |
| `src/aero_webscraper/adapters/` | Eleven tool definitions, CLI administration, MCP stdio egress | Orchestration, retrieval, storage |
| `plugins/aero-webscraper/skills/` | Coordinator and specialist workflows | Eleven backend tools; no imaginary cross-plugin delegation |
| `scripts/` | Synthetic demonstration and reproducible packaging | Canonical source, schemas |

## Entry Points

`python -m aero_webscraper` / `aero-webscraper`: operator CLI.
`aero-webscraper serve`: synchronous MCP stdio process.
`adapters/service.py:SPECS`: authoritative tool registry.
`scripts/demo.py`: synthetic platform workflow. `scripts/package.py`: release packaging.

## Key Flows

Import -> authorized root -> bounded read -> staging -> SHA-256 object -> isolated parser
process -> immutable item/occurrence/processing manifests -> redo commit -> generated
pointers -> disposable index.

Search/read -> retrieval snapshot -> scope/permission filters -> verified objects and
pinned anchors -> Delivery ticket -> transport recheck -> serialized output under lock.

Collection -> persisted seeds/budget -> one bounded synchronous run -> approved fetch ->
shared Library.ingest -> receipts/progress -> immutable collection snapshot.

## Global Invariants

Unknown descriptive metadata remains null. Tool inputs cannot grant permissions.
All original/derived object bytes are immutable; records and journals, not indexes, own
provenance. Quarantine never enters ordinary retrieval. Never run imported programs.
AERO intake is explicit and cannot mutate scientific records. Library, plugin source,
and active workspaces are distinct roots. OFF/ON and policy changes invalidate queued
Deliveries. The operating-system owner remains trusted; see the threat model.

## Navigation Guide

Change permissions or delivery semantics in `retrieval/policy.py` and
`adapters/mcp_stdio.py` together. Change filesystem/commit semantics in `storage/` and
run durability/security tests. Add a format in `ingestion/parsers.py`, retain coordinate
semantics and worker bounds. Add acquisition providers behind `acquisition/`, never in
skills. Add tool inputs in `domain/models.py`, register them in `adapters/service.py`,
regenerate schemas/package, and update the relevant skill/tool references.