# Repository maintenance

Read MMA_SKILL_INDEX.md before edits. This is a skills-only plugin, not an application.
Do not add a scraper, custom MCP endpoint, Python runtime, SDK dependency, daemon,
worker, or external service requirement without a new explicit architecture request.

Preserve the eight skill names, package identity, scope/audience, and exact defaultPrompt.
Bump the semantic version and synchronize the compatibility manifest for a release.
Keep shared rules in references and skill triggers/procedures in SKILL.md files.
Validate JSON/frontmatter, relative links, archive contents, and absence of executable
or service bindings. Label static checks separately from live host workflow tests.
Never claim a generated catalog is a server-enforced database or an original archive.
