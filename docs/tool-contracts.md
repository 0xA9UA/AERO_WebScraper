# Tool contracts

Input schemas are generated from the executable Pydantic contracts under `schemas/tools`.
Every response reports actual IDs/counts/locations or a safe error. Stored content is
untrusted advisory evidence. Writes are advertised in tool annotations/descriptions.

| Tool | Inputs and actual effect |
|---|---|
| `target_resolve` | Explicit target; optional kind/manufacturer/platform/class. Writes identity/navigation. Unresolved targets stay unresolved. |
| `collection_plan` | Target, seed URLs, scope, item/byte/depth budgets, optional reported discovery receipts. Writes durable plan. |
| `collection_run` | Job ID, bounded step count, explicit retry flag. Performs synchronous approved acquisitions and persists progress. |
| `collection_status` | Job ID. Returns operational state/counts/safe errors, not report text or source excerpts. |
| `library_import` | Authorized root name and relative path; file/folder/local repository mode, scope, optional title/date/role and exact repository revision. Never accepts caller-granted rights. |
| `library_browse` | Scope, pagination, history flag. Returns permitted manifests while retrieval is ON. |
| `reference_search` | Query, scope, lexical or case-sensitive exact mode, result limit. Returns pinned, source-bound chunks. |
| `reference_read` | Exact item ID, revision ID and chunk ID. Verifies bytes and resolves citation coordinates. |
| `reference_capture` | Same pinned citation plus an operator-configured intake name. Writes an advisory reference, never a scientific record. |
| `library_export` | Explicit item/revision pairs. Writes policy-filtered ordinary copies and manifest to `_exports`. |
| `library_validate` | Optional explicit index rebuild. Audits hashes/references, reports actual errors; never certifies science. |

All six descriptive permission decisions are independent: acquisition, storage, indexing,
analysis, model transmission and redistribution. Unknown is null and grants nothing.
The metadata-only route retains a permissible URL-level reference instead of downloading
unapproved content. The backend cannot independently establish copyright authority.

Read/search/browse/capture/export are retrieval-gated. Operational collection/import/
validation receipts may remain available when retrieval is OFF. They do not contain source
passages. All model-facing content results are rechecked at the supported transport
boundary. Operator administration is CLI-only and must not be invoked by a skill without
explicit authorization.