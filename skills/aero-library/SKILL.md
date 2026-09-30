---
name: aero-library
description: Use for every AERO source catalog, evidence note, import, reference lookup, export, or checkpoint. Organize native ChatGPT results without a database service, custom MCP tools, or a mandatory external storage connection.
---

# AERO-Library — shared catalog and evidence

## Inputs and shared rules

Receive target/scope, run ID, observed sources, actual file references, user restrictions,
and the desired output. Read [record format](references/record-format.md) and
[taxonomy](references/taxonomy.md). Reuse the coordinator's catalog; do not create
competing specialist databases. Native browsing and file tools do the work.
There is no custom backend, executable entry point, or dependency to install.

## Record evidence honestly

Assign stable run-local source IDs and revisions; preserve existing IDs on resume.
Separate requested/resolved URLs, source identity, scope, inspection coverage, generated
notes, and original-file capture. Unknown dates, versions, authors, licenses, hashes,
and applicability remain null or explicitly unknown. A URL identifies a source, not
proof of its contents. A file saved successfully is not proof of technical correctness.

Use the source-record template. Track source states independently from file states.
Do not claim immutable storage, atomic commits, parser isolation, permission enforcement,
semantic indexing, complete archives, or byte deduplication merely because instructions
request them. Hash equality is available only when actual bytes were computed; record
a publisher checksum separately from a locally computed checksum.

## Imports and retrieval

Use native file search/read for attachments or an existing Library source. For a named
prior file, search the actual permitted file surface before asking for another upload.
Use the live connector for connector-native data and honor its supported URL forms.
Do not use a similarly named document as a substitute for the requested version.

Default retrieval to the current task's sources. Search unrelated personal files only
when the user asks for that corpus. On 'retrieval off', stop intentionally searching,
reading, or quoting the named catalog/corpus until the user enables it. This is an
instruction-level preference, not a security ACL, context eraser, or guaranteed cache
revocation. Off does not authorize bypass through copies or cached excerpts. New
collection can remain link/metadata-only where compatible with the user's restriction.

Retrieve by literal symbol, title, category, scope, or source ID using actual file/search
tools. Open the relevant source or saved note before answering. Confirm exact model,
region, firmware component, software release, and repository revision. Native citation
IDs may be session-bound: exported evidence must also carry a source URL or file identity
and a human-readable locator. Do not fabricate a new live citation from an old label.

## Output and persistence

For a collection, produce REPORT.md, CATALOG.jsonl, CHECKPOINT.json, and SOURCE_NOTES.md;
individual notes and category folders are useful for larger collections. Use templates
and the taxonomy. Create ordinary files only through available native file-generation
or managed artifact tools. Managed computation may format, hash, validate, copy, or ZIP
already available bytes; it must not implement a network scraper or install a runtime.

A filesystem path is not a download link until the file exists and is exposed by the
host. A generated bundle is not an original-source archive. Verify paths, record counts,
file identities, valid JSON, and references using actual operations when supported;
otherwise call the checks manual or unverified. With no file-creation capability,
return inline catalog/checkpoint content and say no file was created.

Default outputs stay in the conversation. For a user-requested persistent destination,
use supported native Library or connected-storage actions, with the exact destination
and required permission checks. Preserve existing files; append a version or reconcile
before overwrite. Do not silently create folders in the user's persistent Library.
Report a save only after success, retaining returned file/version IDs. Do not promise
that a temporary working directory or old sandbox link will persist across sessions.

Never modify AERO scientific records. Explicit AERO intake creates a clearly labeled
advisory reference note containing source IDs, locators, provenance, and uncertainties.
Stop on missing authority or tool support, preserve the result obtained, and report gaps.
