# Catalog, checkpoint, and export contract — 0.2.0

This is an assistant-maintained interchange format, not a transactional database.
Schemas and templates describe expected output; no validation or enforcement runs
unless an actual host operation performs it.

## Source records

CATALOG.jsonl contains one complete JSON object per source observation. Use
[the template](../templates/source-record.json). Assign IDs such as R001-S001 within a
run. They must be unique in the loaded collection, stable on resume, and never described
as hashes or externally issued IDs. Increment observation_revision when changing an
existing record; preserve prior observations when their evidence/revision differs.

Required fields are schema_version, run_id, source_id, observation_revision, title,
source_type, requested_url, resolved_url, source_file_ref, observed_at, published_at,
source_revision, target, scope, category, inspection, capture, provenance, license,
notes, and relations. Unknown values remain null. Empty arrays mean no entries recorded,
not a proven absence from the source. source_type is web_page, document, repository,
source_file, binary, image, or other.

scope distinguishes hardware_model, hardware_revision, region, system_version,
component_version, game_build, and software_version. category is a slash-separated
logical classification, not proof that a directory was created.

inspection.state is discovered, snippet_only, inspected_partial, inspected, blocked,
failed, or deferred. inspection.locators are only pages/sections/lines actually inspected;
inspection.gaps names what was not read. inspected means the relevant requested content
was read, not an entire website or repository. Blocked/failed attempts retain a reason.

capture.state is not_saved, original_saved, derived_saved, unsupported, or blocked.
A generated note goes in notes and does not turn capture into original_saved. capture
refers to the source-file representation: original bytes versus an exported/rendered
representation. original_saved requires a verified file reference/path for acquired
original bytes, with byte count when actually measured. derived_saved requires a
representation description. A URL is not a saved-file reference. Computed sha256 stays
null until hashing actual bytes; publisher_checksum is a separate attributed claim.

provenance records discovery_query or parent_source_id, evidence_basis (primary_source,
community_report, user_provided, model_inference, or mixed), real session citations when
available, and uncertainty. License/attribution information is not an automated legal
clearance. relations contain actual referenced IDs; otherwise leave them empty.
notes list generated evidence notes with note_id, path_or_ref, kind, and source_locators.
A note ID is not a file path. Use kind=attributed_summary, not original_document.

## Output bundle

For a normal collection create REPORT.md, CATALOG.jsonl, CHECKPOINT.json, and
SOURCE_NOTES.md. Scale to notes/<source-id>.md and originals/<source-id>/<actual-name>
when useful and actually supported. A download manifest can list original links without
pretending those files are included. ZIP only real files, excluding credentials and
unrequested private inputs. Use safe relative names; do not write outside the chosen root.

REPORT.md must separate sources discovered, sources inspected, originals saved, generated
notes, blocked/failed/deferred items, and scope gaps. It must say whether outputs were
created, persisted, or only displayed inline. Do not use a single 'collected' count for
all of these. Validate references and JSON syntax using available operations; label
manual review separately from automated validation.

## Checkpoint and resumption

Use [the checkpoint template](../templates/checkpoint.json). Record the exact target,
run ID, catalog revision, scope restrictions, effective budgets, counters, visited URLs,
remaining queue, last completed action, output identities, persistence status, retrieval
preference, and next action. A checkpoint does not schedule anything or guarantee storage.

Before continuing, load the actual saved checkpoint and catalog, reconcile their IDs and
revisions, verify available files, and honor the user's newest restrictions. Resume only
pending/deferred work, not completed items. Preserve distinct version observations and
source occurrences; byte deduplication requires actual matching computed hashes.
If a recorded file is unavailable, mark it missing instead of assuming a path still works.
Across separate tasks use explicit export/import or verified storage; no implicit shared
state, background worker, vector database, lock manager, or atomic multi-agent merge.

## Retrieval preferences

Default to current-run evidence. User-requested retrieval=off applies to the designated
corpus, and is honored as a workflow instruction; it does not purge model context or
provide server-enforced revocation. New source collection must not circumvent that choice.
Preserve the preference in checkpoints but obey the user's latest instruction.
