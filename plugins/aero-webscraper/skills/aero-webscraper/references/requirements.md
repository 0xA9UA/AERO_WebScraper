# Build AERO-WebScraper

## 1. Purpose and plugins

Build a private plugin suite that accepts requests such as **“Document the Nintendo Wii system,”** collects related references and permitted files, and organizes them in one shared library.

Library content is advisory. Preserve AERO’s existing research, engineering, verification, and completion rules.

| Plugin | Responsibility |
|---|---|
| **AERO-WebScraper** | Resolve targets, plan collection, coordinate specialists, report results and gaps. |
| **AERO-HardwareDocs** | Manuals, architecture, boards, schematics, pinouts, peripherals, repair references. |
| **AERO-Firmware** | Firmware releases/components, updates, recovery packages, checksums, permitted binaries. |
| **AERO-DevLibraries** | SDKs, toolchains, APIs/ABIs, system libraries, repositories, dependencies, examples. |
| **AERO-CodeResearch** | Reverse-engineering research, recovered code, decompilations, symbols, analysis. |
| **AERO-GamesHomebrew** | Games, homebrew, patches, mods/modpacks, saves, release compatibility. |
| **AERO-NetworkServices** | Protocols, original/replacement services, server projects, hosting requirements, dated community demand. |
| **AERO-Library** | Shared storage, ingestion, metadata, deduplication, versioning, retrieval, exports. |

Use supported plugin/tool interfaces. If cross-plugin delegation is unavailable, implement the specialists as skills within one plugin. Skills define workflows; backend tools perform acquisition and storage. Every collector uses AERO-Library.

## 2. Storage hierarchy

Preserve these trees. `<...>` denotes a variable. Create categories as needed.

### Shared library

```text
AERO_LIBRARY/
├── README.md
├── library.yaml                         # Non-secret configuration and schema version
├── _policies/
│   ├── taxonomy.yaml
│   ├── collection_policies.yaml
│   ├── source_allowlists.yaml
│   ├── permissions.yaml
│   ├── retention.yaml
│   └── retrieval.yaml
├── _inbox/                              # Operator drop folders; untrusted inputs
│   └── <batch_id>/
├── _staging/                            # Incomplete acquisition/processing jobs
│   └── <job_id>/
├── _quarantine/                         # Access-controlled; never indexed by default
├── _objects/
│   └── sha256/<first_2_hex>/<full_sha256>
├── _records/                            # Authoritative, versioned manifests
│   ├── entities/
│   ├── items/
│   ├── source_occurrences/
│   ├── relations/
│   ├── collections/
│   └── processing_runs/
├── _journal/                            # Commit/recovery records; single owner
├── _derived/
│   └── <item_id>/<processing_run_id>/
│       ├── extraction_manifest.json
│       ├── text.ref.json
│       ├── tables.ref.json
│       ├── page_images.ref.json
│       ├── code_analysis.ref.json
│       └── chunks.ref.json
├── _indexes/                            # Rebuildable, not source authority
│   ├── catalog.sqlite
│   └── vectors/<embedding_profile_id>/
├── _jobs/
│   └── <job_id>/
│       ├── request.json
│       ├── plan.json
│       ├── progress.json
│       ├── search_receipts.jsonl
│       └── report.md
├── devices/
│   ├── game_consoles/<manufacturer>/<platform>/
│   ├── peripherals/<manufacturer>/<peripheral_id>/
│   └── arcade_systems/<manufacturer>/<platform>/
├── games/<game_id>/
├── software_projects/<project_id>/
├── online_services/<service_id>/
├── shared_knowledge/
│   ├── processor_architectures/
│   ├── graphics_audio/
│   ├── file_formats/
│   ├── network_protocols/
│   ├── cryptography_references/
│   ├── development_methods/
│   └── preservation_methods/
└── _exports/<export_id>/                 # Portable, policy-filtered snapshots
```

### Per-console template

Apply under `devices/game_consoles/<manufacturer>/<platform>/`, for example `devices/game_consoles/nintendo/wii/`. Store home/handheld/hybrid classification in metadata.

```text
<platform>/
├── platform.ref.json
├── README.md                            # Generated navigation, not verified findings
├── identity/
│   ├── names_aliases/
│   ├── models_and_regions/
│   ├── release_history/
│   └── compatibility_relationships/
├── variants/<variant_id>/
│   ├── variant.ref.json
│   └── scoped_material/                 # References; no full platform duplication
├── hardware/
│   ├── architecture_overviews/
│   ├── cpu_isa_abi/
│   ├── gpu_graphics/
│   ├── dsp_audio/
│   ├── memory_and_address_maps/
│   ├── buses_interfaces_io/
│   ├── storage_and_media/
│   ├── boot_and_security_architecture/
│   ├── boards_chips_revisions/
│   ├── schematics_pinouts/
│   ├── power_thermal/
│   └── teardown_repair/
├── system_firmware/
│   ├── releases/<release_key>/           # Reported system releases/bundles
│   ├── components/<component_id>/
│   │   └── releases/<release_key>/       # Independently versioned components
│   ├── update_and_recovery_formats/
│   ├── installation_dependencies/
│   ├── custom_distributions/
│   └── unknown_or_unattributed/
├── system_software/
│   ├── menus_shells/
│   ├── system_applications/
│   ├── runtime_services/
│   ├── drivers_modules/
│   ├── diagnostics_recovery/
│   └── configuration_data/
├── sdks_and_toolchains/
│   ├── official_sdk_references/
│   ├── community_sdks/
│   ├── compilers_assemblers_linkers/
│   ├── debuggers_profilers/
│   ├── build_systems/
│   └── build_environment_recipes/
├── system_libraries/
│   └── <library_project_id>/
│       ├── project.ref.json
│       └── releases/<release_key>/
├── development/
│   ├── api_abi_reference/
│   ├── graphics_audio_input/
│   ├── storage_filesystem_apis/
│   ├── networking_apis/
│   ├── examples_and_test_programs/
│   └── packaging_deployment/
├── formats/
│   ├── executables_and_objects/
│   ├── archives_compression/
│   ├── filesystems_disc_cartridge_images/
│   ├── saves_configuration/
│   ├── graphics_audio_video_assets/
│   └── installation_update_packages/
├── networking/
│   ├── hardware_and_adapters/
│   ├── protocols_message_formats/
│   ├── discovery_matchmaking/
│   ├── account_authentication_reference/
│   ├── service_dependencies/
│   ├── packet_capture_references/
│   ├── original_services/
│   ├── community_replacement_services/
│   └── server_hosting_requirements/
├── reverse_engineering/
│   ├── research_publications/
│   ├── source_recovery_projects/
│   ├── decompilation_projects/
│   ├── disassembly_and_symbols/
│   ├── static_analysis/
│   ├── dynamic_analysis_and_traces/
│   ├── hardware_measurement_references/
│   └── contradictions_open_questions/
├── emulation_and_reimplementation/
│   ├── emulator_projects/
│   ├── subsystem_reimplementations/
│   ├── compatibility_reports/
│   └── accuracy_test_suites/
├── homebrew/
│   ├── applications_utilities/
│   ├── games_demos/
│   ├── loaders_launchers/
│   ├── ports/
│   └── development_examples/
├── peripherals/
│   ├── controllers_input/
│   ├── storage_expansions/
│   ├── networking_accessories/
│   └── other_accessories/
├── games/                               # References to global game/release records
├── community/
│   ├── documentation_hubs/
│   ├── forums_discussions/
│   ├── project_maintenance/
│   ├── preservation_efforts/
│   └── dated_support_requests/
├── media/
│   ├── photographs_diagrams/
│   ├── recorded_talks_transcripts/
│   └── demonstrations/
└── reports/
    ├── collection_inventory/
    ├── source_attributed_overviews/
    ├── unresolved_gaps/
    └── change_reports/
```

### Games, shared projects, services, and peripherals

```text
games/<game_id>/
├── game.ref.json
├── identity_and_release_history/
├── releases/<release_id>/
│   ├── release.ref.json                  # Platform, edition, region, language, build
│   ├── manuals_and_documentation/
│   ├── permitted_binaries/
│   ├── patches_updates_dlc/
│   ├── source_and_symbols/
│   ├── formats_assets_and_save_data/
│   ├── reverse_engineering/
│   ├── compatibility/
│   └── multiplayer_service_refs/
├── mods_and_modpacks/
├── ports_and_reimplementations/
├── community_and_support_requests/
└── reports/

software_projects/<project_id>/
├── project.ref.json                      # Type, upstream, maintainers, supported targets
├── releases/<release_key>/
│   ├── source_snapshots/
│   ├── binary_distributions/
│   ├── documentation/
│   ├── build_recipes_and_dependencies/
│   ├── tests_and_examples/
│   ├── licenses_and_notices/
│   └── analysis_refs/
├── compatibility_and_target_refs/
└── maintenance_observations/

online_services/<service_id>/
├── service.ref.json
├── original_service_history/
├── client_and_game_refs/
├── protocol_documentation/
├── server_project_refs/
├── deployment_and_configuration/
├── authentication_account_requirements/
├── compatibility_and_limitations/
├── dated_availability_observations/
├── community_hosting_demand/
└── reports/

devices/peripherals/<manufacturer>/<peripheral_id>/
├── peripheral.ref.json
├── variants/
├── hardware_documentation/
├── firmware/
├── interfaces_protocols/
├── drivers_libraries/
├── compatible_device_refs/
└── repair_and_reimplementation/
```

## 3. Storage rules

- Keep plugin source, persistent library data, and active AERO workspaces separate. Do not bundle the corpus in plugin assets.
- Store immutable original and derived bytes once in `_objects`. `_records` owns metadata; `_derived` links transformations; `_indexes` is rebuildable.
- Device/game/project trees contain `.ref.json` pointers to pinned records. Provide exports containing ordinary, correctly named files. Never expose writable aliases to immutable originals.
- Use stable IDs and readable slugs. Set `release_key` to `<safe_version_label>--<stable_release_id>`; use `unknown--<stable_release_id>` when needed. Preserve original version strings.
- Keep hardware scope, region, system version, component version, and game edition/build distinct. Reference shared projects from multiple platforms instead of duplicating them.
- Accept files/folders through `_inbox` or an authorized import root. Unchanged imports are idempotent; changed bytes create new revisions. Preserve separate source occurrences for identical content.

## 4. Collection and metadata

```text
Resolve target → Plan → Discover → Download to staging → Hash/deduplicate
→ Extract/analyze → Classify → Index → Report
```

Support Markdown, text, HTML, PDFs, images, source repositories, tables, archives, and compiled binaries. Preserve originals and exact repository revisions. Search binary internals through separately approved analysis outputs; never execute imported programs automatically.

For every item, retain:

| Metadata | Required information |
|---|---|
| Identity | Stable ID, title, file type/name, size, SHA-256. |
| Source | Requested/resolved URL, acquisition date, publication date when known, revision/commit, source occurrence. |
| Scope | Platform, model/revision, region, software version, category, related entities. |
| Provenance | Original/extracted/decompiled/model-generated role, parent objects, processing tool/version, citation anchors. |
| Policy and status | License, acquisition/storage/indexing/model-transmission/redistribution permissions, access policy, processing state, warnings. |

Use null for unknown values. Preserve contradictions and uncertain applicability. Distinguish PDF pages from extracted-text offsets, and binary file offsets from virtual addresses.

Report `DISCOVERED`, `METADATA_ONLY`, `STORED_ONLY`, `PARTIAL`, `INDEXED`, `QUARANTINED`, and `FAILED` accurately. Indexing does not establish correctness.

Make jobs resumable, budgeted, and safe under concurrent collectors. Retain search/acquisition receipts and report collected items, failures, omissions, and unresolved categories.

Enforce source permissions, rate limits, safe paths, bounded archives/parsers, and safe network destinations. Treat collected instructions as untrusted data. Where acquisition authority is unresolved, retain permissible metadata for review. Keep credentials and sensitive data out of ordinary logs and retrieval.

## 5. Tools and optional RAG

Expose typed operations:

```text
target_resolve       collection_plan      collection_run
collection_status    library_import       library_browse
reference_search     reference_read       reference_capture
library_export       library_validate
```

Declare write effects and enforce permissions server-side. Return actual IDs, locations, sources, counts, and errors. Report missing connections or unsupported capabilities rather than inventing completed work.

Provide operator-controlled retrieval ON/OFF. OFF blocks library content delivery, including cached/in-flight results; separately authorized collection may continue. Turning retrieval off does not erase previously supplied context.

Start with lexical/exact-symbol search and optional semantic indexing. Apply scope/access filters before returning source-bound excerpts. Preserve originals separately from embeddings and pin processing/model versions.

Capture references into AERO only through explicit, provenance-preserving intake. Do not modify scientific records directly. Missing optional retrieval components must not prevent normal AERO research.

## 6. Implementation structure

Follow the attached MMA `SKILL.md`: cohesive modules, concise summaries in handwritten source files where allowed, and a maintained root `MMA_SKILL_INDEX.md`. Exclude generated, vendored, binary, and comment-incompatible files from header edits.

```text
aero-webscraper-suite/
├── README.md
├── MMA_SKILL_INDEX.md
├── plugins/
│   ├── aero-webscraper/
│   │   ├── <current-supported-plugin-manifest>
│   │   └── skills/<skill-name>/
│   │       ├── SKILL.md
│   │       ├── references/
│   │       └── assets/
│   └── <specialist-package>/             # Only where separately packaged
├── src/
│   ├── domain/                          # IDs, scope, provenance, policy contracts
│   ├── orchestration/                   # Plans, dispatch, durable job coordination
│   ├── acquisition/                     # Shared fetch and repository mechanisms
│   ├── ingestion/                       # Parsing, classification, chunking
│   ├── catalog/                         # Taxonomy, relationships, browse projections
│   ├── retrieval/                       # Search/read and retrieval gating
│   ├── storage/                         # Object/record commits and recovery
│   └── adapters/                        # MCP, hosting, providers, storage integrations
├── schemas/
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── security/
│   └── fixtures/
└── docs/
    ├── architecture.md
    ├── storage-contract.md
    ├── taxonomy.md
    └── deployment.md
```

Each skill defines its trigger, scope, tools, inputs/outputs, and stopping conditions. Put detailed schemas and taxonomy in references, not oversized skill instructions.

## 7. Deliverables and validation

Deliver supported plugin packages, source, schemas, persistent-storage setup instructions, and actual test results.

Demonstrate one platform workflow: import a document and repository snapshot, retain a binary, retrieve a cited passage, export ordinary files, and disable retrieval.

Test deduplication, version separation, interrupted/concurrent imports, source integrity, citation resolution, permission changes, unsafe inputs, retrieval OFF, and index rebuilding. Use permitted or synthetic fixtures; distinguish fixture-tested from live-tested capabilities.