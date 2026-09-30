# Persistent storage contract

`AERO_LIBRARY` must be outside plugin source and AERO workspaces. The entire supplied
hierarchy is retained in `src/aero_webscraper/catalog/taxonomy.json` and copied to
`_policies/taxonomy.yaml` when initialized. Fixed directories are materialized; variable
branches are populated when needed. The console example is
`devices/game_consoles/nintendo/wii/`. Classification is metadata, not a second duplicate
home/handheld folder hierarchy.

## Authority and projections

`_objects/sha256/<prefix>/<hash>` contains immutable, read-only original and derived
objects. `_records/items/<item_id>/<revision_id>.json` owns pinned item manifests.
Records are checksum envelopes: `{ "sha256": "...", "record": { ... } }`.
Schemas describe the payload, with a separate envelope schema.

`_records/source_occurrences` preserves source identity, requested/resolved URL,
acquisition date, repository revision and object hash. Publication date is null unless
explicitly supplied. `_records/relations` records reported applicability. Collection
plans and result snapshots are immutable under `_records/collections`. Operational
resume state remains in `_jobs/<job_id>/progress.json`.

`_derived/<item>/<run>/` contains an extraction manifest plus text/chunks object references.
Tables, page images and code-analysis references explicitly say NOT_PRODUCED when the
corresponding optional processor is absent. These are not fabricated outputs.

Device/game/project/service trees contain pinned `.ref.json` navigation. They do not
expose writable aliases to source bytes. `_exports/<id>` contains ordinary independently
writable copies with safe, collision-resistant filenames and a provenance manifest.
Exporting a local repository produces a source archive pinned to a commit; it does not
imply a build or running program. Export permissions are conservative: model transmission
and redistribution must both be authorized for model-facing exports.

## Ingestion and status

Import only from `_inbox` or explicitly configured import roots. Folder imports reject
symlinks, ignore `.git`, `.venv`, `node_modules` and `__pycache__`, and enforce bounds.
Use repository mode for a local Git commit archive. It intentionally does not clone
remote repositories, run Git hooks, checkout files, execute a build, or fetch LFS objects.
A Git snapshot can contain LFS pointer files or Git submodule references; it does not
hydrate those dependencies.

DISCOVERED means a queued/discovered reference, not downloaded content. METADATA_ONLY
means acquisition/storage rights are unresolved. STORED_ONLY means original bytes exist
without searchable text. PARTIAL means a bounded processor produced warnings or failed;
inspect its manifest. INDEXED means searchable text was produced and the local catalog
was made available. QUARANTINED means retrieval/export are blocked. FAILED means the
operation failed; a job receipt retains a safe error code.

The default original-file limit is 32 MiB; folder and archive expansion limits are
separately configured. A larger job budget does not override the per-file limit.
Metadata keeps original version labels alongside safe release keys. Shared bytes are not
duplicated across platform scopes; multiple pointers/relations can refer to them.

## Backups and recovery

Stop writers or take a consistent filesystem snapshot of objects, records, policies and
journal together. Include jobs to preserve crawl progress. Indexes are disposable.
After restoration run `library_validate` with `rebuild_index=true`. Do not put SQLite,
locks and a live redo journal on a synchronization folder and assume transactions remain
safe. Sync portable exports instead. No deletion/retention job is installed automatically.