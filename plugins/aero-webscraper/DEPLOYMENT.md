# Deployment and connection

## What has and has not been connected

The release includes a real local stdio MCP server and its tested tool definitions.
There is no hosted server URL to enter into ChatGPT web/mobile. Account plugin creation
is a packaging/account action, not server hosting. The available environment did not
provide the Sites hosting skill/backend, and outbound package/download attempts failed.
A cloud connection therefore remains unperformed. Do not invent an endpoint or replace
storage with a Drive folder while claiming the transactional contract is unchanged.

## Local persistent setup

Use a local disk directory outside the package and any active AERO workspace. From the
source root:

```bash
python -m pip install ".[pdf]"
python -m aero_webscraper --root /absolute/path/AERO_LIBRARY init
python -m aero_webscraper --root /absolute/path/AERO_LIBRARY tools
```

Windows example: replace `/absolute/path/AERO_LIBRARY` with
`D:/AERO_DATA/AERO_LIBRARY`. Windows filesystem races and Windows deployment are not
live-tested; Linux/Python 3.13.5 is the validated environment.

For the extracted plugin package, install `runtime` into the Python interpreter that
will launch its `runtime/launch.py`:

```bash
python -m pip install "/absolute/path/aero-webscraper/runtime[pdf]"
```

The portable `mcp.json` uses `python` from the host PATH and anchors source with
`${PLUGIN_ROOT}` and data with `${PLUGIN_DATA}`. A compatible local client must expand
those variables. If using a virtual environment, configure the MCP command to its Python
interpreter or launch the client with that environment on PATH. The server initializes
its client-managed data root, with retrieval OFF and no acquisition rights. Inspect the
root through `library_validate` or the client's MCP launch configuration before making
operator policy changes. Saving this package in ChatGPT does not make local stdio
available to web/mobile.

For a generic local MCP client that does not install portable plugins, set its command to
the installed Python interpreter and arguments to:

```text
-m aero_webscraper --root /absolute/path/AERO_LIBRARY serve
```

Use that client's documented MCP setup; no client-specific installation was performed
on the user's computer during this build.

## Approve only sources you are authorized to collect

The following grants are operator actions, **not tool calls the model can make**. The
first example is appropriate for owned/permitted test inputs, not arbitrary downloads:

```bash
python -m aero_webscraper --root /absolute/path/AERO_LIBRARY grant import:inbox --rights acquisition,storage,indexing,analysis,model_transmission,redistribution --license CC0-1.0
python -m aero_webscraper --root /absolute/path/AERO_LIBRARY retrieval on
```

Do not label real material CC0 without authority. Omit redistribution or model
transmission when those rights are absent. Licensing is separate from technical access.
A public URL or an allowlist entry is not evidence of permission.

For an authorized website, both a host allowlist entry and a source rights grant are
required. Replace `approved.example` with an actual approved domain:

```bash
python -m aero_webscraper --root /absolute/path/AERO_LIBRARY allow-host approved.example
python -m aero_webscraper --root /absolute/path/AERO_LIBRARY grant host:approved.example --rights acquisition,storage,indexing,analysis,model_transmission
```

Each redirect destination must independently pass host, network and rights checks.
Robots denial/unavailability is fail-closed; no search-engine API is used. The backend
crawls supplied seeds and bounded same-origin HTML links; it does not render JavaScript,
solve access challenges, log in, or provide broad internet search. A coordinator may
use its host's existing authorized search tool to find seeds and pass reported search
receipts into `collection_plan`.

## Operator retrieval OFF

```bash
python -m aero_webscraper --root /absolute/path/AERO_LIBRARY retrieval off
```

This disables new library-content delivery, including queued results checked at egress.
It does not erase earlier model context or delete collected files. Separately approved
collection may continue. Turning ON again does not make pre-OFF cached Delivery tickets
valid. Revoking one item's model permission is also available:

```bash
python -m aero_webscraper --root /absolute/path/AERO_LIBRARY revoke item-REAL_ID --right model_transmission
```

## Explicit AERO intake

Create a dedicated reference-intake folder in the intended workspace, not its scientific
record directory. Register that exact folder as an operator and call `reference_capture`
with a real item/revision/chunk citation. Capture writes only an advisory reference file.
No AERO repository, scientific record or real workspace was modified in this build.

## Before any remote exposure

A separately designed authenticated HTTP transport, identity/access model, filesystem
isolation, outbound firewall, parser sandbox, job worker/recovery audit and live provider
checks are required. Do not forward this stdio process directly to the public internet.
This release does not include or claim production-ready hosted authentication.