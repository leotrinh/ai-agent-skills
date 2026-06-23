---
name: adt-browse-search
description: "Browse, search, read/write source, run ATC checks, delete objects, find where-used, view history and diffs in SAP ABAP via ADT REST API. Fills gaps in adt-mcp-server. Use when MCP ADT tools don't support the needed query."
category: sap-abap
keywords: [SAP, ABAP, ADT, packages, search, transport, source, ATC, where-used, history, diff]
argument-hint: "[command] [options]"
metadata:
  author: Leo
  version: "2.0.0"
---

# ADT Browse & Search

Bridges capability gaps in `adt-mcp-server` by querying the SAP ADT REST API directly.

## Script / Binary

```
~/.claude/skills/adt-browse-search/scripts/adt-client.py   # edit here
~/.claude/skills/adt-browse-search/bin/adt-client.exe      # prebuilt binary
```

Run with Python: `~\.claude\skills\.venv\Scripts\python.exe ~/.claude/skills/adt-browse-search/scripts/adt-client.py`

Or use the prebuilt binary (no Python needed): `~/.claude/skills/adt-browse-search/bin/adt-client.exe`

> After editing `adt-client.py`, rebuild the binary with PyInstaller — see bottom of this file.

## Connection Params (required for all commands)

| Param | Description | Example |
|-------|-------------|---------|
| `--url` | SAP system base URL | `https://host:44300` |
| `--user` | SAP logon user | `LEOS4` |
| `--pwd` | SAP password | `***` |
| `--client` | SAP client (default: `100`) | `100` |
| `--lang` | Logon language (default: `EN`) | `EN` |

## Commands

### `search` — Search objects by name / type / package
```bash
adt-client ... search "Z*" --type PROG/P --package ZPACKAGE --max 50
adt-client ... search "ZCL_*" --type CLAS/OC --author LEOS4
```
| Arg | Description |
|-----|-------------|
| `query` | Name pattern: `Z*`, `ZCL_*`, `*` |
| `--type` | `PROG/P` `CLAS/OC` `INTF/OI` `DEVC/K` `TABL/DT` `FUGR/FF` |
| `--package` | Filter by package |
| `--author` | Filter by author/responsible user |
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
adt-client ... packages-by-responsible LEOS4
adt-client ... packages-by-responsible LEOS4 --pattern "Z*" --max 500
```
Fetches each matching package's properties and filters by `adtcore:responsible`.

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
Workflow: lock → PUT source → unlock. **Does not activate** — use `abap_activate_objects` MCP tool after.

| Arg | Description |
|-----|-------------|
| `--file` | Path to `.abap` source file (must be UTF-8) |
| `--text` | Inline source text (for small snippets) |

### `atc-check` — Run ATC static analysis
```bash
adt-client ... atc-check ZMY_PROG:PROG/P
adt-client ... atc-check ZMY_PROG:PROG/P ZCL_X:CLAS/OC ZIF_Y:INTF/OI
```
Input format: `NAME:TYPE`. Returns findings with priority (1=error, 2=warning, 3=info), check ID, and message.

### `delete` — Delete an ABAP object
```bash
adt-client ... delete ZMY_PROG --transport UIK900123 --force
```
| Arg | Description |
|-----|-------------|
| `--transport` | Transport request number — **required** for non-`$TMP` objects |
| `--force` | Skip confirmation prompt (required for agent/non-interactive use) |

> **Warning:** Deletion is irreversible. Without `--force`, an interactive `[y/N]` prompt is shown.

### `where-used` — Find all objects referencing a given object
```bash
adt-client ... where-used ZCL_MY_CLASS --type CLAS/OC
adt-client ... where-used ZMY_PROG --type PROG/P --max 200
```
Returns list of objects that reference the target. Uses primary usages endpoint with fallback to search-usages.

### `history` — Show change history
```bash
adt-client ... history ZMY_PROG --type PROG/P
```
Returns versions with `changed_at`, `changed_by`. Response includes `"source"` field:
- `"versions_endpoint"` — full history from `/source/versions`
- `"object_properties_fallback"` — latest change only (versions endpoint unavailable on this system)

### `diff` — Compare active vs inactive (unsaved) version
```bash
adt-client ... diff ZMY_PROG --type PROG/P
```
Returns unified diff between active and inactive source. `has_changes: false` when no pending changes exist. Diff truncated at 10 000 chars (`"truncated": true` flag added).

### `transports` — List open transport requests
```bash
adt-client ... transports
adt-client ... transports --owner DEVUSER
```

## Output

All commands return **JSON**.

```json
{ "findings_count": 2, "findings": [
    { "priority": 1, "check": "SLIN_USAGE", "message": "Usage of obsolete statement" }
]}
```

## Usage in Workflow

When a user asks to browse, search, or modify the SAP repository and `adt-mcp-server` tools don't cover it:

1. Get connection details from the project's `.claude/settings.json` or ask the user
2. Run the appropriate command via the venv Python interpreter or the prebuilt binary
3. Parse the JSON output and present results

## Covered Gaps

| Capability | MCP | This skill |
|------------|-----|------------|
| Search objects by name/type | ❌ | ✅ `search` |
| Search by package | ❌ | ✅ `search --package` |
| List all objects in a package | ❌ | ✅ `objects` |
| Browse sub-packages | ❌ | ✅ `packages` |
| List packages by responsible user | ❌ | ✅ `packages-by-responsible` |
| Read source code | ❌ | ✅ `source` |
| **Write/update source code** | ❌ | ✅ `write-source` |
| List transport requests | ❌ | ✅ `transports` |
| **Run ATC static analysis** | ❌ | ✅ `atc-check` |
| **Delete object** | ❌ | ✅ `delete` |
| **Find where-used** | ❌ | ✅ `where-used` |
| **Change history** | ❌ | ✅ `history` |
| **Compare active/inactive** | ❌ | ✅ `diff` |
| Debug/breakpoints | ❌ | ❌ Not feasible via REST API |

## Rebuilding the Binary

After editing `adt-client.py`:

```powershell
& "$env:USERPROFILE\.claude\skills\.venv\Scripts\python.exe" -m PyInstaller `
    --onefile --console --name "adt-client" `
    --distpath "$env:USERPROFILE\.claude\skills\adt-browse-search\bin" `
    --workpath "$env:TEMP\pyinstaller-adt-client\build" `
    --specpath "$env:TEMP\pyinstaller-adt-client" `
    "$env:USERPROFILE\.claude\skills\adt-browse-search\scripts\adt-client.py"
```
