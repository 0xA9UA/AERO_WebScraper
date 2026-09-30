# Validation — AERO-WebScraper 0.2.0

Release checks are recorded in the accompanying validation report. Structural checks
cover manifest identity/version, preservation of defaultPrompt, eight matching skill
frontmatters, relative reference links, valid JSON templates, and no executable/runtime
or external-service configuration in the clean package.

The account migration additionally checks empty portable/legacy MCP maps and comment-only
legacy Python markers. Those checks establish package structure, not host instruction
compliance or server-enforced permissions.

A live native-tool smoke collection in the authoring conversation inspects official
OpenAI documentation and creates source notes, a catalog, and a checkpoint. It is not a
Wii corpus, binary-download test, or autonomous post-installation plugin test. No original
source files are claimed saved by that smoke collection.

Not tested: automatic skill activation in a new user conversation, complete website
mirroring, arbitrary original-file download, persistent storage/resumption across user
sessions, every specialist domain, or inaccessible-source handling in a separate host.
The former 77 backend tests do not apply to this skills-only release.
