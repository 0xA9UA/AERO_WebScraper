# Security model and known limitations

This is a **single-operator, local first release**, not a multi-tenant production service.
The operating-system owner and policy files are trusted. MCP callers cannot change
permissions, grant a source, add import/intake roots or re-enable retrieval. Other tools
running as the same operating-system owner can still modify those files; isolate the
service account from agent shell access when a stronger boundary is required.

Implemented controls include source rights checks, exact domain allowlists, public-IP
validation for every resolved address, pinned socket destinations with TLS hostname
verification, redirect rechecks, disabled environment proxies/cookies, identity encoding,
robots checks, per-host rate reservations, bounded reads/parsers/archives, rejection of
archive traversal/symlinks/special files, and safe error codes. POSIX import reads pin
ancestor directory descriptors. Windows uses a weaker path-check/read fallback and
requires trusted, non-concurrently-mutated import roots until Windows-specific hardening.
Local Git repositories must also be trusted against concurrent filesystem mutation.

The parser child has wall-time/output constraints, reduced environment inheritance and
POSIX CPU/address-space/file-size limits. **A subprocess is not a security sandbox against
parser exploitation.** No seccomp/container/jail or network namespace was deployed.
Before hostile internet-scale parsing, isolate parser processes from the library,
credentials, host filesystem and network. Secret detection is heuristic, not exhaustive
DLP; encrypted archives/PDFs and opaque binaries are not evidence of safe contents.
Quarantine is an API/permissions boundary within an owner-protected library, not encryption.

Network code is fixture-tested, not live-tested here. DNS resolution can exceed the
intended socket deadline on some platforms. Crawl rate handling is conservative but has
not been tested against a real site's rate-limit policy. Acquisition byte budgets count
accepted file bodies, not every TLS/HTTP/robots byte. Failed/interrupted fetch attempts
can consume network transfer not represented by that retained-byte count. HTTP request
counts on failed attempts are approximate. This is a known gap for strict billed-egress
or adversarial retry budgets. No unattended infinite worker is installed.

Jobs run synchronously in bounded steps and persist progress. A crashed in-flight entry
can be retried; ingestion is idempotent. A crash between receipt append and progress
update can duplicate attempt receipts, which are audit attempts rather than unique source
occurrences. Cross-process source import and redo recovery are fixture-tested. There is
no distributed lease coordinator, remote queue, NFS/SMB certification, or adversarial
multi-host crash proof. Index operations serialize under the library lock. Large-corpus
latency and storage scalability have not been benchmarked.

The MCP adapter is a minimal tool-only stdio implementation, negotiated at 2025-06-18.
It does not implement HTTP transport, OAuth, task APIs, interactive views, resource
streaming or preemptive cancellation of an already executing synchronous operation.
Tests verify negotiation/tool discovery/calls with a subprocess harness, not independent
SDK/Inspector certification. Runtime dependency installation and local client installation
were not tested on the user's machine. Runtime network dependency downloads could not be
performed in this environment.

Optional semantic RAG, embeddings, OCR, PDF layout/table/image extraction, JavaScript
rendering, internet-search providers, arbitrary remote repository cloning, binary static
analysis/decompilation, executable/emulator tests, external storage adapters and cloud
hosting remain unimplemented. Opaque bytes are retained, not described as analyzed.
The first release is not an end-to-end autonomous reverse-engineering or server-restoration
system; it supplies the permitted reference-library layer without changing AERO's rules.