---
name: modular-memory-architecting
description: Use this skill when designing, creating, modifying, refactoring, reviewing, or extending source code. This skill should almost always be used by default for software coding tasks, especially in large, long-lived, or multi-file projects. Enforce agent-readable file memory summaries, cohesive modular architecture, and a project-local MMA_SKILL_INDEX.md that helps future agents locate responsibilities and dependencies across chat or context-window boundaries. Do not force compliance where comments or edits would break generated, vendored, lock, binary, or format-constrained files.
---

# Modular Memory Architecting (MMA)

**Version:** 1.2

## Purpose

Optimize codebases for long-term human and AI-agent maintainability.

MMA has three architectural invariants:

1. **Persistent file memory:** Every handwritten source file created or materially modified MUST contain a concise summary comment at the top of the file when the language and file format permit it.
2. **Useful modularity:** Code MUST be organized into cohesive, narrowly scoped modules with explicit boundaries so future changes can be made without loading, understanding, or rewriting unrelated parts of the system.
3. **Project-local repository memory:** Large, long-lived, or meaningfully multi-module code projects SHOULD maintain a root-level `MMA_SKILL_INDEX.md`, created and maintained by this skill inside the project itself. The index is not part of the installed skill package.

Optimize for:

- rapid comprehension after context loss;
- low change radius;
- explicit ownership of responsibilities;
- narrow, stable interfaces;
- testability and replaceability;
- minimal coupling between unrelated concerns;
- bounded per-file and per-module context requirements;
- fast repository navigation without loading the full codebase.

Correctness, security, platform constraints, and established language/framework requirements take precedence over MMA formatting conventions.

---

## 1. File Memory Headers

### 1.1 Requirement

For every handwritten source file that is created or materially modified, add or update an **MMA File Summary** comment.

The summary MUST be the first explanatory comment block in the file.

Place it:

1. after any syntax-required preamble that must legally come first, such as a shebang, encoding declaration, build tag, pragma, license header, or framework-required directive;
2. before imports, declarations, executable statements, or implementation code whenever the language permits.

Do not add comments to file formats that do not support comments.

Do not modify generated code, vendored dependencies, lockfiles, snapshots, compiled artifacts, or other machine-owned files solely to add an MMA header.

### 1.2 Canonical Header

Use the native comment syntax of the language.

The preferred logical structure is:

```text
MMA FILE SUMMARY
Purpose: <one-sentence reason this file exists>
Responsibilities: <the cohesive behaviors/data this file owns>
Public interface: <important exported functions, classes, types, commands, or "internal only">
Collaborators: <important adjacent modules/services and why they are used>
Invariants: <critical assumptions, constraints, side effects, or "none">
```

Keep the header concise. It is a memory index, not full documentation.

When a field would add no useful information, omit it rather than writing filler.

### 1.3 Examples

TypeScript / JavaScript:

```ts
// MMA FILE SUMMARY
// Purpose: Coordinates user-session authentication without owning persistence.
// Responsibilities: Validate credentials, issue sessions, and map auth failures.
// Public interface: authenticate(), revokeSession().
// Collaborators: userRepository for identity data; sessionStore for persistence.
// Invariants: Never stores plaintext credentials.
```

Python:

```python
# MMA FILE SUMMARY
# Purpose: Normalizes provider responses into the application's canonical model.
# Responsibilities: Parse payloads, validate required fields, map provider errors.
# Public interface: normalize_response().
# Collaborators: models.py for canonical types.
```

CSS:

```css
/*
 * MMA FILE SUMMARY
 * Purpose: Defines reusable layout primitives for application shells.
 * Responsibilities: Grid, stack, and container layout utilities.
 * Public interface: .layout-grid, .layout-stack, .layout-container.
 */
```

### 1.4 Header Quality Rules

A good header tells a future agent **why this file exists and what it owns** without reading the implementation.

MUST:

- describe the current implementation, not intended future behavior;
- identify responsibility boundaries rather than merely restating the filename;
- name important public interfaces when that materially reduces search time;
- mention critical side effects or invariants when relevant;
- remain short enough to scan quickly.

MUST NOT:

- duplicate the entire API;
- list every import;
- narrate implementation line by line;
- contain stale claims;
- become a changelog;
- include speculative future plans.

Whenever implementation behavior changes, verify the header before finishing the task. A stale summary is worse than no summary.

---

## 2. Useful Modularity

### 2.1 Core Rule

Structure code around **cohesive responsibilities and reasons to change**.

A module should own one coherent concept, capability, boundary, or layer. Code that changes for unrelated reasons should usually live in separate modules.

MMA does **not** mean creating the maximum number of files.

Prefer the smallest set of modules that gives:

- strong internal cohesion;
- weak external coupling;
- explicit interfaces;
- predictable dependency direction;
- isolated change impact;
- manageable context size.

### 2.2 Boundary Tests

Before adding substantial logic to an existing file, evaluate these tests.

#### Responsibility test

Does the new logic belong to the same conceptual responsibility as the existing code?

If no, create or use another module.

#### Change-isolation test

Could this behavior plausibly change independently from the rest of the file?

If yes, consider separating it behind an interface.

#### Context test

Would a future agent need to read large amounts of unrelated code to understand or safely edit this behavior?

If yes, improve the boundary.

#### Dependency test

Does adding the code force a core/domain module to depend directly on UI, transport, filesystem, database, framework, or provider-specific details?

If yes, move environment-specific behavior toward an adapter or integration boundary where practical.

#### Reuse test

Is the behavior duplicated because there is no clear owner?

If yes, give the behavior one cohesive home and reuse it through an explicit interface.

#### Fragmentation test

Would splitting the code create tiny pass-through modules with no independent responsibility, no meaningful interface, and more navigation than isolation?

If yes, keep the code together.

### 2.3 Preferred Separation of Concerns

When applicable, separate:

- domain/business rules from infrastructure;
- pure computation from side effects;
- persistence from domain behavior;
- transport/API handling from application logic;
- UI/presentation from state and business rules;
- provider/framework-specific adapters from portable core logic;
- configuration from implementation;
- orchestration from reusable operations;
- public interfaces from private implementation details.

These are architectural guides, not mandatory directory names.

Follow the conventions of the existing language, framework, and repository when those conventions already provide clean boundaries.

### 2.4 Interface Rules

Prefer narrow interfaces.

A module SHOULD:

- expose only what callers need;
- keep implementation details private;
- communicate through explicit inputs and outputs;
- avoid hidden shared mutable state where practical;
- avoid circular dependencies;
- avoid requiring callers to know internal sequencing or storage details;
- make side effects visible at boundaries;
- support isolated testing when the cost is reasonable.

Do not create abstractions merely because an abstraction is possible. Create one when it reduces coupling, isolates volatility, enables testing/replacement, or materially reduces future context requirements.

---

## 3. Project-Local Repository Memory: `MMA_SKILL_INDEX.md`

### 3.1 Core Behavior

`MMA_SKILL_INDEX.md` is **not a file that ships with this skill**.

It is a project-local architectural memory file that this skill creates inside an active code project when the project is sufficiently large, long-lived, or modular for repository-level memory to be useful.

The installed skill contains the instructions for creating and maintaining the index. Each project gets its own index based on that project's actual architecture.

### 3.2 When to Create It

Create `MMA_SKILL_INDEX.md` at the project/repository root when one or more of these conditions are true:

- the project contains multiple meaningful modules or subsystems;
- the project is expected to continue across multiple tasks, chats, or context windows;
- understanding the project requires navigating several directories or architectural layers;
- multiple entry points, services, packages, adapters, or domains exist;
- the agent would otherwise need to repeatedly rediscover ownership and dependency relationships.

Do not create it for trivial scripts, throwaway prototypes, single-purpose snippets, generated repositories, vendored code, or projects where repository documentation changes are explicitly prohibited.

If the file already exists, read it before broad source exploration whenever practical.

### 3.3 What the Index Does

The index provides this navigation path:

```text
MMA_SKILL_INDEX.md
        ↓
relevant subsystem / module
        ↓
per-file MMA summaries
        ↓
exact implementation
```

Its purpose is to minimize repository-wide scanning after context loss.

It MUST remain architectural and concise. It is not:

- a duplicate README;
- an exhaustive file list;
- an API reference;
- a task log;
- a changelog;
- a substitute for tests or source documentation.

### 3.4 Required Contents

When creating or rebuilding a project index, include the sections that materially help navigation:

- **System Purpose:** what the repository/application does.
- **Architecture Snapshot:** major layers/subsystems and dependency direction.
- **Module Map:** important directories/modules, responsibility, public boundary, and key dependencies.
- **Entry Points:** where major runtime flows begin.
- **Key Flows:** concise paths for important control/data flows.
- **Global Invariants:** cross-module rules that must remain true.
- **Navigation Guide:** where to begin for common categories of change.

Use paths relative to the repository root whenever possible.

Do not include empty boilerplate sections if the project does not need them.

### 3.5 Canonical Index Template

When a qualifying project lacks an index, create a project-root file named exactly:

```text
MMA_SKILL_INDEX.md
```

Use this structure as the default:

```md
# MMA_SKILL_INDEX

> Project-level architectural memory for Modular Memory Architecting (MMA).
> Keep this file concise, architectural, and current.

## System Purpose

<1–3 sentences describing what this repository/application does.>

## Architecture Snapshot

<Describe the major layers or subsystems and intended dependency direction.>

```text
<optional compact dependency diagram>
```

## Module Map

| Path | Owns | Public boundary | Depends on |
|---|---|---|---|
| `<path>` | `<cohesive responsibility>` | `<exports / API / entry boundary>` | `<important dependencies>` |

## Entry Points

| Entry point | Purpose | First-owned module |
|---|---|---|
| `<path or command>` | `<what starts here>` | `<module>` |

## Key Flows

### <Flow name>

```text
<entry>
  → <module>
  → <module>
  → <side effect / output>
```

## Global Invariants

- <cross-module rule that must remain true>
- <dependency, state, security, consistency, or lifecycle invariant>

## Navigation Guide

| Change needed | Start here | Likely collaborators |
|---|---|---|
| `<category of change>` | `<module/path>` | `<related modules>` |
```

Adapt the template to the project rather than mechanically filling every field.

### 3.6 How to Build the Index

When creating `MMA_SKILL_INDEX.md` for an existing project:

1. inspect the repository tree;
2. identify runtime/build entry points;
3. inspect high-level configuration and package/module boundaries;
4. read existing README/architecture documentation when available;
5. use MMA file summaries first where present;
6. inspect implementation only as needed to verify ownership and dependency direction;
7. write the smallest accurate architecture map that meaningfully reduces future discovery work.

Never invent architecture merely to complete the template.

### 3.7 Maintenance Rule

Update `MMA_SKILL_INDEX.md` only when a task materially changes:

- module ownership;
- directory structure;
- public architectural boundaries;
- dependency direction;
- major entry points;
- key cross-module flows;
- global invariants.

Do NOT update it for implementation-only changes that leave the architecture unchanged.

After structural refactors, treat stale repository memory as a defect.

Before finishing, verify that paths, ownership statements, dependencies, and invariants still match the code.

### 3.8 Monorepos

For a monorepo, prefer one root `MMA_SKILL_INDEX.md`.

Create package- or application-level indexes only when a subproject is independently complex enough that doing so materially reduces context requirements.

If nested indexes exist, the root index SHOULD link to them and remain a map of the overall system.

Do not create nested indexes merely for symmetry.

---

## 4. Context-Window-Aware Architecture

Large projects MUST be structured so useful work can continue without loading the entire repository into context.

Design toward this property:

> A future agent should usually be able to locate a subsystem from `MMA_SKILL_INDEX.md`, then understand a file from its MMA header, public interface, tests, and a small number of directly related modules.

When this is not true, investigate whether:

- responsibilities are mixed;
- dependencies cross too many layers;
- global state is hiding relationships;
- a generic `utils`, `helpers`, `common`, or equivalent module has become a dumping ground;
- interfaces are too broad;
- orchestration and implementation are interleaved;
- one file has become the de facto owner of unrelated subsystems;
- the repository index is missing, stale, or too vague to guide navigation.

File length is a signal, not a rule. Do not split code solely to satisfy a line-count target.

---

## 5. Workflow for Coding Tasks

When this skill is active, use the following workflow.

### Step 1 — Inspect memory before implementation

Before editing:

1. if the active project contains `MMA_SKILL_INDEX.md`, read it first whenever practical;
2. inspect the relevant repository structure;
3. identify existing architectural conventions;
4. read MMA headers in relevant files before full implementations when practical;
5. identify the modules that own the requested behavior;
6. avoid loading unrelated implementation unless necessary.

If a qualifying project lacks `MMA_SKILL_INDEX.md`, create one when sufficient architecture can be determined accurately and doing so is within task scope.

### Step 2 — Model the change

Determine:

- which responsibility is changing;
- which module should own that responsibility;
- what interface callers need;
- what dependencies are required;
- whether the change introduces a new architectural boundary;
- whether `MMA_SKILL_INDEX.md` must be created or updated.

Prefer extending an existing cohesive owner over creating a parallel competing abstraction.

### Step 3 — Implement modularly

Write the smallest cohesive implementation that satisfies the requirement.

Split code when doing so improves responsibility ownership, change isolation, testing, replaceability, or context efficiency.

Do not perform unrelated repository-wide refactors unless explicitly requested or necessary for correctness.

### Step 4 — Add or update MMA headers

For every handwritten source file created or materially modified:

- create the MMA File Summary if missing and legally possible;
- update it if responsibilities, public interfaces, collaborators, or important invariants changed;
- verify that it describes the resulting file accurately.

### Step 5 — Maintain project-level memory

If `MMA_SKILL_INDEX.md` should exist:

- create it if absent and the project qualifies;
- update it only when architecture materially changes;
- keep it concise;
- remove stale paths or claims;
- never turn it into a task log.

### Step 6 — Validate architecture

Before finishing, check:

- Did any file acquire multiple unrelated responsibilities?
- Did the change introduce circular or unnecessary dependencies?
- Is environment-specific code leaking into a portable/core module?
- Was reusable logic duplicated instead of given a clear owner?
- Did modularization create meaningless pass-through files?
- Can the changed subsystem be located quickly from the project index when one exists?
- Can it be understood without loading unrelated parts of the repository?

Correct meaningful violations before completion when doing so is within task scope.

### Step 7 — Validate behavior

Run the appropriate tests, type checks, linters, builds, or other project validation available in the environment.

Do not claim validation succeeded if it was not actually run.

---

## 6. Legacy Code

When modifying a legacy file that does not follow MMA:

1. add or update an MMA header if technically legal;
2. keep the requested change scoped;
3. improve modularity locally when this can be done safely;
4. create or update `MMA_SKILL_INDEX.md` only when the project qualifies and the architectural memory would be accurate and useful;
5. do not rewrite the entire surrounding subsystem solely to conform to MMA.

If the requested change exposes a severe architectural boundary problem that cannot be fixed safely within scope, preserve correctness and explicitly identify the boundary problem for future work.

---

## 7. Exceptions

Do not force MMA headers into:

- JSON or other formats that prohibit comments;
- generated source;
- vendored third-party code;
- dependency lockfiles;
- binary or compiled artifacts;
- files whose required syntax would be broken by the header.

When a mandatory directive or legal header must appear first, place the MMA summary immediately after that required preamble.

Do not sacrifice correctness, security, licensing requirements, build semantics, framework conventions, or tool compatibility to satisfy an MMA formatting preference.

Do not create or update `MMA_SKILL_INDEX.md` when the repository is machine-generated, immutable, vendored, trivial, or the task explicitly forbids documentation changes.

---

## 8. Anti-Patterns

Avoid:

- monolithic files that own unrelated subsystems;
- “god” classes or modules;
- generic utility dumping grounds with unrelated helpers;
- hidden cross-module mutation;
- circular dependency chains;
- broad interfaces that expose internal implementation;
- copy-pasted logic with no clear owner;
- abstraction layers that only forward calls without isolating anything;
- one-function-per-file fragmentation without architectural benefit;
- splitting tightly coupled logic merely to reduce line count;
- MMA headers that only paraphrase filenames;
- stale MMA headers;
- repository indexes that enumerate every file;
- repository indexes that become changelogs;
- architectural maps that claim dependencies not supported by the code;
- bundling a generic `MMA_SKILL_INDEX.md` with the skill and treating it as project architecture.

---

## 9. Definition of Done

A coding task using MMA is complete only when all applicable conditions are true:

- every handwritten source file created or materially modified has a current MMA File Summary when comments are technically legal;
- each changed file has a clear cohesive responsibility;
- new public interfaces are as narrow as practical;
- unrelated concerns have not been merged into the same module;
- no unnecessary circular dependency was introduced;
- modularization improved or preserved change isolation rather than merely increasing file count;
- the changed subsystem can be understood from a bounded set of related files;
- `MMA_SKILL_INDEX.md` has been created for a qualifying project when doing so is useful and within task scope;
- an existing `MMA_SKILL_INDEX.md` accurately reflects any material architectural changes;
- available relevant validation has been run, or the inability to run it is stated accurately.

---

## 10. Governing Principle

Optimize the codebase not only for execution today, but for **safe comprehension and modification after memory loss**.

A future agent should be able to answer, in order:

1. What does this repository do?
2. Which subsystem owns the behavior I need?
3. Why does this file exist?
4. What does this file own?
5. What can other modules call?
6. What does it depend on?
7. What must remain true?
8. Can I change this behavior without understanding unrelated parts of the system?

Use the project-local `MMA_SKILL_INDEX.md` to answer the first two questions and per-file MMA summaries to answer the rest.

If those answers are difficult to obtain, improve the architecture, project index, or file summary until they are clear, within the scope and constraints of the task.