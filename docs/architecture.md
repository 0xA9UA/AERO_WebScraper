# Architecture and implemented boundaries

One plugin contains the coordinator and seven specialist/library skills. There is no
assumption that a host can launch independently packaged agents or delegate across
plugins. A skill is a workflow, not a running worker. All collectors call the same backend.

The backend is single-operator, local Python. The portable package declares an actual
stdio launcher. The wire adapter implements the tool-only subset of MCP protocol revision
2025-06-18: initialize, initialized notification, ping, tools/list, and tools/call. It was
tested with a real subprocess harness. It is not an official SDK/Inspector certification.
No HTTP/OAuth server, multi-tenant ACL layer, remote endpoint, UI app, or cloud worker was
implemented or deployed in this release.

The domain, acquisition, parsing, orchestration, storage, catalog, retrieval and adapter
boundaries are separate modules with MMA headers. Detailed policy is not hidden in prompts.
A caller cannot supply its own rights to an ingestion tool. Permissions live in
operator-controlled files. Model-facing operations are declared in one typed registry.

## Source and data authority

Original and derived byte objects are SHA-256 addressed. Item revisions and source
occurrences are distinct. An unchanged logical source/scope/bytes tuple is idempotent.
Changed bytes or relevant scope/source metadata create another pinned revision. Identical
bytes from different source URLs or import paths share the object but retain separate
item/source-occurrence records. A record envelope includes a checksum; this detects
accidental changes, not a malicious operating-system owner who can recompute checksums.

A redo journal is written and flushed before authoritative record application. Restart
finishes prepared commits. CAS objects written before a crash can be orphaned; no automatic
garbage collector deletes them. Indexes and navigation can be reconstructed. Local
same-filesystem operation is assumed; network-drive locking semantics are not validated.

## Scope and citation coordinates

Hardware model/revision, region, system version, component identity/version, game edition
and build are distinct fields. Source applicability remains reported, not verified.
PDF citation pages are physical, one-based page numbers; offsets within extracted page
text are Unicode text coordinates. Text sources have character offsets and line numbers.
Archive results retain member paths and SHA-256 hashes. Binary file offsets and virtual
addresses are not produced by this release; it never substitutes one for the other.

## Retrieval boundary

Retrieval defaults OFF. A Delivery carries a generation and policy epoch. OFF/ON changes
the generation; operator permission changes advance the epoch. Stdio/CLI recheck tickets
under the same interprocess lock used for policy changes, immediately before writing the
serialized response. An OFF acknowledgement therefore follows any output already admitted
under that lock. A not-yet-emitted stale result is rejected. This cannot recall bytes
already transmitted, client-managed caches, prior context, or previous export copies.
Direct use of internal Python return values bypasses the supported transport contract.

## Optional and deferred components

Lexical token/literal search is implemented; exact mode is case-sensitive. It is a small-
corpus baseline, not an FTS/vector performance benchmark. Semantic embeddings and RAG
providers, OCR, structured PDF table extraction, code decompilers, emulator execution,
automatic binary analysis, JavaScript browser rendering, search-engine providers,
Google Drive/S3 adapters, remote Git acquisition, and hosted authentication are not
implemented. Their absence does not change AERO research rules or block ordinary work.