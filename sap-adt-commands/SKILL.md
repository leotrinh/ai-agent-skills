---
name: sap-adt-commands
description: "Full SAP ADT REST API command set: browse/search objects, list objects/reports by user, create objects (program/class/interface/function-module/function-group/CDS/package/transaction), read/write source code, manage message classes (create/read/add/update/delete individual messages), read/write text elements (selections/symbols/headings), activate, ATC/ABAP unit tests, transport management (create/release/move/delete/contents), object history/diff/where-used/unlock/delete. Use when MCP ADT tools don't cover the needed operation."
category: sap-abap
keywords: [SAP, ABAP, ADT, create, package, program, class, interface, function-module, function-group, CDS, text-elements, message-class, message, transport, source, activate, ATC, abap-unit, search, where-used, history, diff, delete, unlock, user, reports, objects-by-user]
argument-hint: "[command] [options]"
metadata:
  author: Leo
  version: "3.5.0"
---

# SAP ADT Commands

Bridges capability gaps in `adt-mcp-server` by querying the SAP ADT REST API directly.

## Script / Binary

```
~/.claude/skills/sap-adt-commands/scripts/adt-client.py   # edit here
~/.claude/skills/sap-adt-commands/bin/adt-client.exe      # prebuilt binary
```

Run with Python:
```powershell
& "$env:USERPROFILE\.claude\skills\.venv\Scripts\python.exe" `
    "$env:USERPROFILE\.claude\skills\sap-adt-commands\scripts\adt-client.py" `
    --dest DEV_100_LEO_EN [command] [options]
```

Or use the prebuilt binary (no Python needed):
```powershell
& "$env:USERPROFILE\.claude\skills\sap-adt-commands\bin\adt-client.exe" `
    --dest DEV_100_LEO_EN [command] [options]
```

> After editing `adt-client.py`, rebuild the binary — see **Rebuilding the Binary** at the bottom.

## Connection (required for all commands)

**Preferred: `--dest SID_CLIENT_USER_LANG`** (e.g. `DEV_100_LEO_EN`) — no
credential ever appears on the command line. Agents MUST use this form:
permission classifiers block any command carrying a plaintext `--pwd`.

`--dest DEV_100_LEO_EN` resolves to:

| Value | Source (first hit wins) |
|-------|------------------------|
| url | `--url` flag → `SAP_DEV_URL` env var |
| user | `--user` flag → `SAP_DEV_LEO_USER` env var → `LEO` (from the name) |
| pwd | `--pwd` flag → `SAP_DEV_LEO_PWD` env var (**required**) |
| client / lang | `--client`/`--lang` flags → `100` / `EN` (from the name) |

One-time setup per system — **the human runs this, never the agent** (an agent
typing the password is exactly what the classifier blocks):

```powershell
setx SAP_DEV_URL "https://host:44300"
setx SAP_DEV_LEO_PWD "<password>"
```

Env vars are read from the process environment first, then from
`HKCU\Environment` directly — so a fresh `setx` works without restarting the
agent session.

### If env vars are missing (first use of a destination)

The client exits with a JSON error naming exactly what to set, e.g.:

```json
{"error": "Missing connection values for --dest DEV_100_LEO_EN",
 "set_once_with": ["setx SAP_DEV_URL \"<value>\"", "setx SAP_DEV_LEO_PWD \"<value>\""]}
```

Agent playbook for this error — do NOT treat it as a connection failure:

1. `SAP_<SID>_URL` is **not a secret** — the agent may run that `setx` itself
   if the base URL is known.
2. The `*_PWD` var **must be set by the human**: show them the `setx` command
   verbatim (with `<password>` placeholder) and wait. Never ask the user to
   paste the password into the chat, never run the password `setx` yourself.
3. After the user confirms, **retry the original command as-is** — the registry
   fallback picks the value up immediately; no restart, no re-login, nothing
   else to do.

Explicit flags (`--url`, `--user`, `--pwd`, `--client`, `--lang`) still work
without `--dest` (backward compatible) and override resolved values when
combined with it.

> `--user` is also used as `adtcore:responsible` in object creation XML — no separate `--responsible` needed.

## Commands

### `search` — Search objects by name / type / package
```bash
adt-client ... search "Z*" --type PROG/P --package ZPACKAGE --max 50
adt-client ... search "ZCL_*" --type CLAS/OC --author DEVUSER
```
| Arg | Description |
|-----|-------------|
| `query` | Name pattern: `Z*`, `ZCL_*`, `*` |
| `--type` | `PROG/P` `CLAS/OC` `INTF/OI` `DEVC/K` `TABL/DT` `FUGR/FF` |
| `--package` | Filter by package |
| `--author` | Passed to ADT API but **ignored by most systems** — use `objects-by-user` instead |
| `--max` | Max results (default: 100) |

### `objects` — List all objects in a package
```bash
adt-client ... objects '$TMP'
adt-client ... objects ZPACKAGE --max 500
```

### `packages` — List sub-packages of a parent package
```bash
adt-client ... packages '$TMP'
adt-client ... packages ZROOT_PACKAGE
```

### `packages-by-responsible` — List packages owned by a user
```bash
adt-client ... packages-by-responsible DEVUSER
adt-client ... packages-by-responsible DEVUSER --pattern "Z*" --max 500
```
Fetches each matching package's properties and filters by `adtcore:responsible`.

### `objects-by-user` — List all objects across a user's packages
```bash
adt-client ... objects-by-user DEVUSER
adt-client ... objects-by-user DEVUSER --type PROG/P
adt-client ... objects-by-user DEVUSER --type CLAS/OC --pattern "ZHABA*"
```
Combines `packages-by-responsible` + `objects` per package into one call. Returns `by_type` summary + flat `objects[]` list. ADT quickSearch does not support `author` filtering — package ownership is the correct proxy for custom-namespace work.

| Arg | Description |
|-----|-------------|
| `USER` | SAP user (positional) |
| `--type` | Filter by object type, e.g. `PROG/P`, `CLAS/OC` (omit for all types) |
| `--pattern` | Package name pattern (default: `Z*`) |

### `reports-by-user` — List programs/reports owned by a user
```bash
adt-client ... reports-by-user DEVUSER
adt-client ... reports-by-user DEVUSER --pattern "ZHABA*"
```
Convenience alias for `objects-by-user USER --type PROG/P`. Returns programs and executable reports only.

### `source` — Read source code
```bash
adt-client ... source ZMY_PROG --type PROG/P
adt-client ... source ZCL_MY_CLASS --type CLAS/OC
```
Supported types: `PROG/P` `CLAS/OC` `INTF/OI` `FUGR/FF`

### `write-source` — Write / update source code
```bash
adt-client ... write-source ZMY_PROG --file source.abap --type PROG/P
adt-client ... write-source ZMY_PROG --text "REPORT zmy_prog." --type PROG/P
```
Workflow: lock → PUT source → unlock. **Does not activate** — call `activate` or use the MCP tool after.

| Arg | Description |
|-----|-------------|
| `--file` | Path to `.abap` source file (must be UTF-8) |
| `--text` | Inline source text (for small snippets) |
| `--transport` | Lock into a specific transport (avoids auto-generated ones) |

### `create-package` — Create ABAP package (DEVC/K)
```bash
adt-client ... create-package ZTEST \
  --description "My package" --superpackage ZHOME \
  --transport DEVK900001 --sw-component HOME --transport-layer ZSD2
```
| Arg | Description |
|-----|-------------|
| `--superpackage` | Parent package (required) |
| `--sw-component` | Software component (default: `HOME`) |
| `--transport-layer` | Transport layer, e.g. `ZSD2` (leave empty for local) |

### `create-program` — Create ABAP report (PROG/P)
```bash
adt-client ... create-program ZMY_REPORT \
  --description "My report" --package ZPKG --transport DEVK900001
```
Creates an executable program shell using the correct `program:abapProgram` XML namespace.

### `create-class` — Create ABAP class (CLAS/OC)
```bash
adt-client ... create-class ZCL_HELPER \
  --description "Helper class" --package ZPKG --transport DEVK900001
```

### `create-interface` — Create ABAP interface (INTF/OI)
```bash
adt-client ... create-interface ZIF_CONTRACT \
  --description "My interface" --package ZPKG --transport DEVK900001
```

### `create-function-module` — Create function module inside a function group
```bash
adt-client ... create-function-module Z_MY_FM \
  --description "Calculate discount" --group ZFUGR_UTILS \
  --package ZPKG --transport DEVK900001
adt-client ... create-function-module Z_RFC_FUNC \
  --description "RFC-enabled" --group ZFUGR_RFC --processing-type remote-enabled \
  --package ZPKG --transport DEVK900001
```
| Arg | Description |
|-----|-------------|
| `--group` | Parent function group name (required) |
| `--processing-type` | Informational only — ADT creation API cannot set it; returns a note to set it in SE37 afterwards |

POSTs to `functions/groups/{group}/fmodules` (FMs are nested under their group).

### `create-function-group` — Create function group (FUGR/FF)
```bash
adt-client ... create-function-group ZFUGR_UTILS \
  --description "Utility function group" --package ZPKG --transport DEVK900001
```

### `create-message-class` — Create message class (MSAG/N)
```bash
adt-client ... create-message-class ZMSAG \
  --description "Messages" --package ZPKG --transport DEVK900001
```

### `create-transaction` — Create report transaction (TRAN/T)
```bash
adt-client ... create-transaction ZMY_TCODE \
  --description "My transaction" --program ZMY_REPORT \
  --package ZPKG --transport DEVK900001
```

### `read-message-class` — Read message class XML
```bash
adt-client ... read-message-class ZMSAG
```

### `write-messages` — Write messages to an existing message class
```bash
adt-client ... write-messages ZMSAG --file messages.xml
```
Workflow: lock → PUT → unlock. Activate separately.

### `add-message` / `update-message` — Add or update a single message (upsert)
```bash
adt-client ... add-message ZMSAG --id 001 --text "No data found"
adt-client ... add-message ZMSAG --id 015 --text "Export complete: &1 records" --transport DEVK900001
adt-client ... update-message ZMSAG --id 001 --text "Updated text"
```
Both commands are upsert: inserts if the ID doesn't exist, updates if it does. `--id` is zero-padded to 3 digits automatically. Workflow: read XML → patch in-memory → lock → PUT → unlock. Activate separately.

### `delete-message` — Delete a single message by ID
```bash
adt-client ... delete-message ZMSAG --id 015
adt-client ... delete-message ZMSAG --id 015 --transport DEVK900001
```
Removes the message element with the given ID from the class. Returns error if ID not found. Workflow: read XML → remove → lock → PUT → unlock. Activate separately.

### `activate` — Activate ABAP objects
```bash
adt-client ... activate ZMY_PROG:PROG/P
adt-client ... activate ZMY_PROG:PROG/P ZCL_X:CLAS/OC ZMSAG:MSAG/N
```
Input format: `NAME:TYPE`. Returns `success`, `inactive_remaining`, `errors`. Returns 403 if object is locked by an open SE38 session (close SE38 first).

### `atc-check` — Run ATC static analysis
```bash
adt-client ... atc-check ZMY_PROG:PROG/P
adt-client ... atc-check ZMY_PROG:PROG/P ZCL_X:CLAS/OC
```
2-step flow: POST worklists → POST runs → GET worklists/{id}. Returns `gate: PASS/FAIL/UNKNOWN_POLL_UNSUPPORTED`. Some systems return 406 for the worklist endpoint (system limitation — use SCI/SE38 instead).

### `abap-unit` — Run ABAP unit tests
```bash
adt-client ... abap-unit ZMY_PROG:PROG/P
adt-client ... abap-unit ZMY_PROG:PROG/P ZCL_X:CLAS/OC
```
Input format: `NAME:TYPE` (type optional, defaults to PROG/P). Returns `gate: PASS/FAIL`, `total`, `passed`, `failed`, method list and failure details.

### `object-properties` — Read full metadata of any object
```bash
adt-client ... object-properties ZMY_PROG --type PROG/P
adt-client ... object-properties ZHABA_MDM --type DEVC/K
```
Returns: `description`, `package`, `responsible`, `created_by/at`, `changed_by/at`, `master_lang`, `inactive`.

### `unlock` — Release a stuck lock on an object
```bash
adt-client ... unlock ZMY_PROG --type PROG/P
```
Tries to find and release the lock handle. If locked by another user, an admin must use SM12 — this command notes that.

### `inactive-objects` — List inactive (not-yet-activated) objects
```bash
adt-client ... inactive-objects
adt-client ... inactive-objects --user-filter DEVUSER
```
Uses `/sap/bc/adt/workarea/inactive` with fallback. Returns `inactive_objects[]`.

### `delete` — Delete an ABAP object
```bash
adt-client ... delete ZMY_PROG --transport DEVK900123 --force
```
| Arg | Description |
|-----|-------------|
| `--transport` | Transport request number — **required** for non-`$TMP` objects |
| `--force` | Skip confirmation prompt (required for agent/non-interactive use) |

> **Warning:** Deletion is irreversible.

### `delete-transport` — Delete an empty transport request
```bash
adt-client ... delete-transport DEVK900002 --force
adt-client ... delete-transport DEVK900003 DEVK900004 --force
```
Use after moving objects to another transport via SE10. The transport must be empty. Returns per-transport results.

### `where-used` — Find all objects referencing a given object
```bash
adt-client ... where-used ZCL_MY_CLASS --type CLAS/OC
adt-client ... where-used ZMY_PROG --type PROG/P --max 200
```

### `history` — Show change history
```bash
adt-client ... history ZMY_PROG --type PROG/P
```
Returns versions with `changed_at`, `changed_by`. Field `"source"`:
- `"versions_endpoint"` — full history from `/source/versions`
- `"revision_atom_feed"` — full history from the object's versions atom link
- `"object_properties_fallback"` — latest change only (when no versions source is available)

### `diff` — Compare active vs inactive (unsaved) version
```bash
adt-client ... diff ZMY_PROG --type PROG/P
```
Returns unified diff. `has_changes: false` when no pending changes. Diff truncated at 10 000 chars.

### `transports` — List open transport requests
```bash
adt-client ... transports
adt-client ... transports --owner DEVUSER
```

### `create-transport` — Create a new Workbench transport request
```bash
adt-client ... create-transport --description "TICKET-1234: My feature"
adt-client ... create-transport --description "TICKET-1234: My feature" --package ZPKG
```
| Arg | Description |
|-----|-------------|
| `--description` | Transport description (required) |
| `--package` | Package (DEVCLASS) — determines transport route (optional) |
| `--target` | Deprecated — target system follows the package's transport layer |
| `--type-tr` | `K` = Workbench (default). `W` (Customizing) is rejected — no ADT REST path; use SE01/SE09 |

POSTs the ABAP-serialized `CreateCorrectionRequest` structure to `/sap/bc/adt/cts/transports`. Returns `transport` number on success; SE01/SE09 note if CTS REST not enabled.

### `release-transport` — Release a transport request
```bash
adt-client ... release-transport DEVK900001
```
Two-step: releases all open tasks first, then the request — each via `POST /sap/bc/adt/cts/transportrequests/{nr}/newreleasejobs`. Returns `released: true/false` + per-task results.

### `move-object` — Record object into a target transport
```bash
adt-client ... move-object ZMY_PROG:PROG/P --transport DEVK900002
adt-client ... move-object ZMY_PROG:PROG/P --transport DEVK900002 --task DEVK900003
```
Re-locks the object with the target `corrNumber`, which records it in that transport task. SAP automatically de-registers it from the previous task. If `--task` is omitted, the first task of the transport is auto-detected. Falls back to direct task-objects PUT if lock approach fails.

### `transport-contents` — Show objects in a transport request
```bash
adt-client ... transport-contents DEVK900001
```
Parses CTS workbench XML. Returns `objects[]` with `pgmid`, `type`, `name`. Requires CTS REST enabled on the system.

### `discovery` — List available ADT endpoints
```bash
adt-client ... discovery
```
Returns `workspaces[]`, `collections[]` (href + title), and total href count. Useful for probing what a system supports.

### `create-cds` — Create CDS Data Definition (DDLS/DF)
```bash
adt-client ... create-cds ZCDS_MY_VIEW \
  --description "My CDS view" --package ZPKG --transport DEVK900001
adt-client ... create-cds ZCDS_MY_VIEW \
  --description "My CDS view" --package ZPKG --source-file my_view.ddls
```
Uses ADT endpoint `/sap/bc/adt/ddic/ddl/sources` (root `ddl:ddlSource`). Note: `ddic/ddla/sources` is a *different* object type (DDLA = annotation definitions) — do not use it for data definitions. After the object is created, optionally writes initial source from `--source` (inline) or `--source-file` (file path).

| Arg | Description |
|-----|-------------|
| `--source` | Inline initial DDLS source (optional) |
| `--source-file` | Path to `.ddls` file for initial source (optional) |

> Once created, use `source ZCDS_MY_VIEW --type DDLS/DF` to read source, and `write-source ZCDS_MY_VIEW --type DDLS/DF` to update it later.

### `read-text-elements` — Read text elements (selections / symbols / headings)
```bash
adt-client ... read-text-elements ZMY_PROG --type PROG/P
adt-client ... read-text-elements ZMY_PROG --type PROG/P --section selections
adt-client ... read-text-elements ZCL_MY_CLASS --type CLAS/OC
adt-client ... read-text-elements ZFUGR_UTILS --type FUGR/FF
```
Reads text elements from `/sap/bc/adt/textelements/{obj_class}/{name}/source/{section}`. Returns all three sections by default, or a single one with `--section`.

| Section | Content format |
|---------|----------------|
| `selections` | `FIELD_NAME  =Description text` — one per selection field |
| `symbols` | `@MaxLength:N\nCODE=Text` — each symbol with max-length annotation |
| `headings` | `key=value` — list/column headers |

Supported types: `PROG/P` (default), `CLAS/OC`, `FUGR/FF`.

### `write-text-elements` — Write a text element section
```bash
adt-client ... write-text-elements ZMY_PROG --section selections \
  --file sel.txt --transport DEVK900001
adt-client ... write-text-elements ZMY_PROG --section symbols \
  --text "@MaxLength:10\nTITLE=My Title" --transport DEVK900001
```
Workflow: lock → PUT section → unlock. **Does not activate** — call `activate` after.

Content must match the ADT plain-text format (same as what `read-text-elements` returns).

| Arg | Description |
|-----|-------------|
| `--section` | `selections` / `symbols` / `headings` (required) |
| `--file` | Path to text file (UTF-8) |
| `--text` | Inline section content |
| `--transport` | Transport request number |

## Output

All commands return **JSON**.

```json
{ "findings_count": 2, "findings": [
    { "priority": 1, "check": "SLIN_USAGE", "message": "Usage of obsolete statement" }
]}
```

## Usage in Workflow

**When to activate this skill:** any time the user asks to browse, search, inspect, create, or modify SAP ABAP objects and the `adt-mcp-server` MCP tools don't cover the operation. Use the Covered Gaps table below to confirm.

### 0. Get connection details
Read from `.claude/settings.json` → `sap.systems[].{url, user, client}`. If missing, ask the user. Never hardcode credentials.

```powershell
$b = @("--url","https://host:44300","--user","DEVUSER","--pwd","****","--client","100")
$exe = "$env:USERPROFILE\.claude\skills\sap-adt-commands\bin\adt-client.exe"
```

### 1. Browse & search the repository
```powershell
# Find objects by name pattern or type
& $exe @b search "ZMY_*" --type PROG/P
& $exe @b objects ZPACKAGE
& $exe @b packages ZROOT_PACKAGE

# Find everything a user owns (correct proxy — ADT quickSearch ignores --author)
& $exe @b packages-by-responsible DEVUSER
& $exe @b objects-by-user DEVUSER --type CLAS/OC
& $exe @b reports-by-user DEVUSER

# Inspect a single object
& $exe @b object-properties ZMY_PROG --type PROG/P
& $exe @b discovery   # probe which ADT services are active on the system
```

### 2. Read & write source code
```powershell
& $exe @b source ZMY_PROG --type PROG/P
& $exe @b write-source ZMY_PROG --file new_source.abap --type PROG/P --transport DEVK900001
& $exe @b diff ZMY_PROG --type PROG/P       # pending (unsaved) changes
& $exe @b history ZMY_PROG --type PROG/P    # change log
& $exe @b activate ZMY_PROG:PROG/P          # always activate after write
```

### 3. Create ABAP objects (full flow)
```powershell
# 1. Create package first if needed
& $exe @b create-package ZPKG --description "My pkg" --superpackage ZHOME --transport DEVK900001

# 2. Create the object
& $exe @b create-program   ZMY_PROG  --description "My report"  --package ZPKG --transport DEVK900001
& $exe @b create-class     ZCL_UTIL  --description "Util class"  --package ZPKG --transport DEVK900001
& $exe @b create-interface ZIF_IFACE --description "Interface"   --package ZPKG --transport DEVK900001
& $exe @b create-function-group ZFUGR_UTIL --description "FG"   --package ZPKG --transport DEVK900001
& $exe @b create-function-module Z_FM --group ZFUGR_UTIL --description "FM" --package ZPKG --transport DEVK900001
& $exe @b create-transaction ZTC --description "My TCode" --program ZMY_PROG --package ZPKG --transport DEVK900001
& $exe @b create-cds ZCDS_VIEW --description "CDS view" --package ZPKG --transport DEVK900001

# 3. Write initial source, then activate
& $exe @b write-source ZMY_PROG --text "REPORT zmy_prog." --type PROG/P --transport DEVK900001
& $exe @b activate ZMY_PROG:PROG/P
```

### 4. Message class operations
```powershell
# Create shell, add individual messages, activate
& $exe @b create-message-class ZMSAG --description "My messages" --package ZPKG --transport DEVK900001
& $exe @b add-message ZMSAG --id 001 --text "No data found" --transport DEVK900001
& $exe @b add-message ZMSAG --id 002 --text "Export complete: &1 records" --transport DEVK900001
& $exe @b update-message ZMSAG --id 001 --text "No data found for selection" --transport DEVK900001
& $exe @b delete-message ZMSAG --id 002 --transport DEVK900001
& $exe @b activate ZMSAG:MSAG/N

# Read / bulk-write
& $exe @b read-message-class ZMSAG                         # inspect raw XML
& $exe @b write-messages ZMSAG --file all_messages.xml     # replace all messages at once
```

### 5. Text elements (selections / symbols / headings)
```powershell
& $exe @b read-text-elements ZMY_PROG --type PROG/P
& $exe @b write-text-elements ZMY_PROG --section selections --file sel.txt --transport DEVK900001
& $exe @b write-text-elements ZMY_PROG --section symbols --text "@MaxLength:10\nTITLE=My title" --transport DEVK900001
& $exe @b activate ZMY_PROG:PROG/P
```

### 6. Transport management
```powershell
& $exe @b transports --owner DEVUSER         # list open transports
& $exe @b create-transport --description "TICKET-1234: Feature X" --package ZPKG
& $exe @b move-object ZMY_PROG:PROG/P --transport DEVK900002
& $exe @b transport-contents DEVK900001      # inspect objects inside
& $exe @b release-transport DEVK900001       # release tasks then request
& $exe @b delete-transport DEVK900002 --force
```

### 7. Quality gates
```powershell
& $exe @b atc-check ZMY_PROG:PROG/P          # static analysis (406 on some systems)
& $exe @b abap-unit ZMY_PROG:PROG/P          # unit tests (schema varies by SAP version)
& $exe @b inactive-objects                   # check for unactivated objects (404 on some systems)
```

### 8. Cleanup & diagnostics
```powershell
& $exe @b where-used ZCL_UTIL --type CLAS/OC   # find all references (500 on some systems)
& $exe @b unlock ZMY_PROG --type PROG/P         # release stuck lock (SM12 for other-user locks)
& $exe @b delete ZMY_PROG --transport DEVK900001 --force
```

## Covered Gaps

| Capability | MCP | This skill |
|------------|-----|------------|
| Search objects by name/type | ❌ | ✅ `search` |
| Search by package | ❌ | ✅ `search --package` |
| List all objects in a package | ❌ | ✅ `objects` |
| Browse sub-packages | ❌ | ✅ `packages` |
| List packages by responsible user | ❌ | ✅ `packages-by-responsible` |
| All objects across user's packages | ❌ | ✅ `objects-by-user` |
| Reports/programs by user | ❌ | ✅ `reports-by-user` |
| Read source code | ❌ | ✅ `source` |
| Write/update source code | ❌ | ✅ `write-source` |
| List transport requests | ❌ | ✅ `transports` |
| Run ATC static analysis | ❌ | ✅ `atc-check` |
| Run ABAP unit tests | ❌ | ✅ `abap-unit` |
| Delete object | ❌ | ✅ `delete` |
| Find where-used | ❌ | ✅ `where-used` |
| Change history | ❌ | ✅ `history` |
| Compare active/inactive source | ❌ | ✅ `diff` |
| Activate objects | ❌ | ✅ `activate` |
| Show transport object list | ❌ | ✅ `transport-contents` |
| Create transport request | ❌ | ✅ `create-transport` |
| Release transport request | ❌ | ✅ `release-transport` |
| Move/record object in transport | ❌ | ✅ `move-object` |
| Delete transport request | ❌ | ✅ `delete-transport` |
| Create package (full XML) | ❌ | ✅ `create-package` |
| Create program / class / interface | ❌ | ✅ `create-program/class/interface` |
| Create function group | ❌ | ✅ `create-function-group` |
| Create function module | ❌ | ✅ `create-function-module` |
| Read message class XML | ❌ | ✅ `read-message-class` |
| Create message class + write messages | ❌ | ✅ `create-message-class` + `write-messages` |
| Add / update single message (upsert) | ❌ | ✅ `add-message` / `update-message` |
| Delete single message by ID | ❌ | ✅ `delete-message` |
| Create transaction | ❌ | ✅ `create-transaction` |
| Object metadata / properties | ❌ | ✅ `object-properties` |
| Release stuck lock | ❌ | ✅ `unlock` |
| List inactive objects | ❌ | ✅ `inactive-objects` |
| Discover available ADT endpoints | ❌ | ✅ `discovery` |
| Create CDS Data Definition | ❌ | ✅ `create-cds` |
| Read text elements (sel/sym/hdg) | ❌ | ✅ `read-text-elements` |
| Write text elements | ❌ | ✅ `write-text-elements` |
| Debug/breakpoints | ❌ | ❌ Not feasible via REST API |

## System Compatibility Notes

| Feature | Note |
|---------|------|
| `atc-check` | Returns 406 on some S/4HANA Cloud systems — use SCI/SE38 instead |
| `abap-unit` | Schema varies by SAP release; returns 400 on some versions |
| `transports` / `transport-contents` | Requires CTS REST (`/sap/bc/adt/cts/workbench`) — returns 404 when not enabled |
| `inactive-objects` | `GET /sap/bc/adt/activation/inactiveobjects`; falls back to `workarea/inactive` on 404 |
| `where-used` | `POST /sap/bc/adt/repository/informationsystem/usageReferences?uri=…` with usageReferenceRequest body |
| `search --author` | ADT quickSearch ignores the `author` param — use `objects-by-user` as the correct proxy |
| `write-source` | Blocked on systems where `MODIFICATION_SUPPORT=false` (locked/delivery systems) |
| `activate` | Returns 403 when the object is locked by an open editor session — close it first |
| `read-message-class` | Path and accepted Content-Type vary by SAP release; skill auto-probes both variants |
| `add-message` / `update-message` / `delete-message` | Read XML → patch in-memory → PUT full XML back — activate separately |
| `create-cds` | Uses the DDL endpoint (`ddic/ddl/sources`, root `ddl:ddlSource`) — DDLA is annotation definitions, a different object type |
| `create-function-module` | Nested endpoint `functions/groups/{group}/fmodules` with `adtcore:containerRef` |
| creation transport param | Query param is `corrNr` on all creation POSTs and DELETE |
| `read-text-elements` | `Accept: */*` required — specific Content-Type returns 406 on some releases |
| `write-text-elements` | Locks the textelements object; falls back to the program object lock if that fails |

## Rebuilding the Binary

After editing `adt-client.py`:

```powershell
& "$env:USERPROFILE\.claude\skills\.venv\Scripts\python.exe" -m PyInstaller `
    --onefile --console --name "adt-client" `
    --distpath "$env:USERPROFILE\.claude\skills\sap-adt-commands\bin" `
    --workpath "$env:TEMP\pyinstaller-adt-client\build" `
    --specpath "$env:TEMP\pyinstaller-adt-client" `
    "$env:USERPROFILE\.claude\skills\sap-adt-commands\scripts\adt-client.py"
```
