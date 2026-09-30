# Taxonomy

The complete templates are preserved verbatim in `user-specification.md` and in the
machine-readable `catalog/taxonomy.json`. No category list was silently replaced.
Variable IDs and version labels are instantiated as needed; empty placeholders are not
literal directory names. New category paths are accepted only after containment checks.

Use console categories for console-local evidence. Shared software belongs to the
software-project entity tree, games to game/release records, and services to service
entities. Link related entity IDs rather than copying an upstream project into every
console folder. Collection assigns reported scope; it does not prove compatibility.

Stable IDs are deterministic namespaced UUIDs. Human-readable slugs are safe labels,
not identities. Release keys use a safe original version label plus stable release ID;
unknown releases use `unknown--<release_id>`. Scope carries the original version string.

HardwareDocs handles hardware/identity/peripheral/repair categories. Firmware handles
firmware/releases/components and recovery formats. DevLibraries handles shared projects,
SDKs, APIs and toolchains. CodeResearch handles published reverse-engineering material.
GamesHomebrew handles global game/release entities and console homebrew references.
NetworkServices handles protocol and service entities with dated observations.
AERO-Library owns objects, records, indexing, exports and retrieval policy.