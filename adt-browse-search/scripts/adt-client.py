#!/usr/bin/env python3
"""
SAP ADT REST API client — fills capability gaps not covered by adt-mcp-server.
Supports: search, list objects/packages, read/write source, transports,
          ATC checks, delete, where-used, change history, active/inactive diff.
"""

import argparse
import difflib
import json
import re
import sys
import time
import urllib.parse

import requests
import urllib3
from requests.auth import HTTPBasicAuth

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# ── Type path map (module-level, shared by all commands) ─────────────────────

TYPE_PATH_MAP = {
    "PROG/P": "programs/programs",
    "CLAS/OC": "oo/classes",
    "INTF/OI": "oo/interfaces",
    "FUGR/FF": "functions/groups",
}


# ── Session ──────────────────────────────────────────────────────────────────

def make_session(url: str, user: str, pwd: str, client: str, lang: str) -> requests.Session:
    """Build authenticated session with CSRF token."""
    s = requests.Session()
    s.auth = HTTPBasicAuth(user, pwd)
    s.verify = False
    s.headers.update({"sap-client": client, "sap-language": lang})
    resp = s.get(f"{url}/sap/bc/adt/discovery", headers={"X-CSRF-Token": "Fetch"})
    csrf = resp.headers.get("x-csrf-token", "")
    if csrf:
        s.headers["X-CSRF-Token"] = csrf
    return s


# ── XML parser ────────────────────────────────────────────────────────────────

def parse_xml_refs(xml: str) -> list[dict]:
    """Extract objectReference entries from ADT search XML response."""
    pattern = (
        r'adtcore:uri="([^"]*)"[^>]*adtcore:type="([^"]*)"'
        r'[^>]*adtcore:name="([^"]*)"'
        r'(?:[^>]*adtcore:packageName="([^"]*)")?'
        r'(?:[^>]*adtcore:description="([^"]*)")?'
    )
    return [
        {
            "uri": m.group(1),
            "type": m.group(2),
            "name": m.group(3),
            "package": m.group(4) or "",
            "description": m.group(5) or "",
        }
        for m in re.finditer(pattern, xml)
    ]


# ── Lock / Unlock helpers (used by write-source and delete) ──────────────────

def _lock(s: requests.Session, base_url: str) -> str | None:
    """Lock an ADT object for modification. Returns lock handle or None."""
    resp = s.post(
        f"{base_url}?_action=LOCK&accessMode=MODIFY",
        headers={"X-CSRF-Token": s.headers.get("X-CSRF-Token", "")},
    )
    m = re.search(r'adtcore:lockHandle="([^"]*)"', resp.text)
    if not m:
        # Some releases use a different attribute name
        m = re.search(r'lockHandle["\s:=]+([A-Za-z0-9+/=]{10,})', resp.text)
    return m.group(1) if m else None


def _unlock(s: requests.Session, base_url: str, handle: str) -> None:
    """Release an ADT object lock."""
    s.post(f"{base_url}?_action=UNLOCK&lockHandle={urllib.parse.quote(handle)}")


# ── ATC XML builder ───────────────────────────────────────────────────────────

def _build_atc_xml(objects: list[dict]) -> str:
    """Build ATC run request XML for a list of {name, type, uri} objects."""
    refs = "\n".join(
        f'        <adtcore:objectReference adtcore:uri="{o["uri"]}" '
        f'adtcore:type="{o["type"]}" adtcore:name="{o["name"]}"/>'
        for o in objects
    )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<atcrun:run maximumVerdicts="100"
  xmlns:atcrun="http://www.sap.com/adt/atc/run"
  xmlns:adtcore="http://www.sap.com/adt/core">
  <objectSets>
    <objectSet kind="inclusive">
      <adtcore:objectReferences>
{refs}
      </adtcore:objectReferences>
    </objectSet>
  </objectSets>
</atcrun:run>"""


# ── Commands ──────────────────────────────────────────────────────────────────

def cmd_search(s: requests.Session, url: str, args) -> list | dict:
    """Search ABAP objects by name, type, and/or package."""
    params = {"operation": "quickSearch", "query": args.query, "maxResults": args.max}
    if args.type:
        params["objectType"] = args.type
    if args.package:
        params["packageName"] = args.package
    if hasattr(args, "author") and args.author:
        params["author"] = args.author
    resp = s.get(
        f"{url}/sap/bc/adt/repository/informationsystem/search",
        params=params,
        headers={"Accept": "application/xml"},
    )
    return parse_xml_refs(resp.text)


def cmd_objects(s: requests.Session, url: str, args) -> list | dict:
    """List all objects assigned to a package."""
    params = {"operation": "quickSearch", "query": "*", "packageName": args.package, "maxResults": args.max}
    resp = s.get(
        f"{url}/sap/bc/adt/repository/informationsystem/search",
        params=params,
        headers={"Accept": "application/xml"},
    )
    return parse_xml_refs(resp.text)


def cmd_packages(s: requests.Session, url: str, args) -> dict:
    """List sub-packages inside a parent package via nodestructure."""
    resp = s.post(
        f"{url}/sap/bc/adt/repository/nodestructure",
        params={
            "parent_name": args.package,
            "parent_tech_name": args.package,
            "parent_type": "DEVC/K",
            "withShortDescriptions": "true",
        },
        headers={
            "Accept": "application/vnd.sap.as+xml;charset=utf-8;dataname=com.sap.adt.RepositoryObjectTreeContent"
        },
    )
    refs = re.findall(r'technicalName="([^"]*)"[^>]*description="([^"]*)"', resp.text)
    return {"parent": args.package, "subpackages": [{"name": n, "description": d} for n, d in refs]}


def cmd_packages_by_responsible(s: requests.Session, url: str, args) -> list:
    """List packages where adtcore:responsible matches the given user."""
    pattern = args.pattern or "Z*"
    params = {"operation": "quickSearch", "query": pattern, "objectType": "DEVC/K", "maxResults": args.max}
    resp = s.get(
        f"{url}/sap/bc/adt/repository/informationsystem/search",
        params=params,
        headers={"Accept": "application/xml"},
    )
    packages = parse_xml_refs(resp.text)

    result = []
    for pkg in packages:
        name = pkg["name"].lower().replace("/", "%2f")
        r = s.get(f"{url}/sap/bc/adt/packages/{name}")
        if r.status_code == 200:
            m = re.search(r'adtcore:responsible="([^"]*)"', r.text)
            responsible = m.group(1) if m else ""
            if responsible.upper() == args.responsible.upper():
                m_desc = re.search(r'adtcore:description="([^"]*)"', r.text)
                m_created = re.search(r'adtcore:createdBy="([^"]*)"', r.text)
                result.append({
                    "name": pkg["name"],
                    "responsible": responsible,
                    "created_by": m_created.group(1) if m_created else "",
                    "description": m_desc.group(1) if m_desc else "",
                })
    return result


def cmd_source(s: requests.Session, url: str, args) -> dict:
    """Fetch source code of a program, class, interface, or function module."""
    base = TYPE_PATH_MAP.get(args.type, "programs/programs")
    path = f"{base}/{args.name.lower()}/source/main"
    resp = s.get(f"{url}/sap/bc/adt/{path}", headers={"Accept": "text/plain"})
    return {"name": args.name, "type": args.type, "status": resp.status_code, "source": resp.text}


def cmd_write_source(s: requests.Session, url: str, args) -> dict:
    """Write/update source code: lock → PUT → unlock. Does not activate."""
    base_path = TYPE_PATH_MAP.get(args.type, "programs/programs")
    base = f"{url}/sap/bc/adt/{base_path}/{args.name.lower()}"

    handle = _lock(s, base)
    if not handle:
        return {"error": "Could not obtain lock — object may be locked by another user"}

    if args.text:
        source = args.text
    elif args.file:
        with open(args.file, encoding="utf-8") as f:
            source = f.read()
    else:
        return {"error": "Provide --file or --text"}

    put_resp = s.put(
        f"{base}/source/main",
        data=source.encode("utf-8"),
        headers={
            "Content-Type": "text/plain; charset=utf-8",
            "X-sap-adt-lockhandle": handle,
        },
    )
    _unlock(s, base, handle)

    ok = put_resp.status_code in (200, 204)
    return {
        "name": args.name,
        "type": args.type,
        "put_status": put_resp.status_code,
        "message": "OK — use abap_activate_objects MCP tool to activate" if ok else put_resp.text[:300],
    }


def cmd_atc_check(s: requests.Session, url: str, args) -> dict:
    """Run ATC static analysis on one or more ABAP objects."""
    objects = []
    for item in args.objects:
        if ":" not in item:
            return {"error": f"Invalid format '{item}' — use NAME:TYPE e.g. ZMY_PROG:PROG/P"}
        name, obj_type = item.rsplit(":", 1)
        base_path = TYPE_PATH_MAP.get(obj_type, "programs/programs")
        objects.append({
            "name": name.upper(),
            "type": obj_type,
            "uri": f"/sap/bc/adt/{base_path}/{name.lower()}",
        })

    run_resp = s.post(
        f"{url}/sap/bc/adt/atc/runs",
        data=_build_atc_xml(objects).encode("utf-8"),
        headers={"Content-Type": "application/xml", "Accept": "application/xml"},
    )
    if run_resp.status_code not in (200, 201):
        return {"error": "ATC run failed", "status": run_resp.status_code, "body": run_resp.text[:300]}

    results_url = run_resp.headers.get("Location", "")
    if not results_url:
        m = re.search(r'href="([^"]*results[^"]*)"', run_resp.text)
        results_url = m.group(1) if m else ""
    if results_url and not results_url.startswith("http"):
        results_url = f"{url}{results_url}"

    # Poll up to 3 times — ATC runs are async
    findings = []
    raw_xml = ""
    for _ in range(3):
        r = s.get(results_url, headers={"Accept": "application/xml"})
        raw_xml = r.text
        findings = re.findall(
            r'priority="(\d+)"[^>]*checkId="([^"]*)"[^>]*messageTitle="([^"]*)"',
            raw_xml,
        )
        if findings:
            break
        time.sleep(2)

    result = {
        "run_status": run_resp.status_code,
        "findings_count": len(findings),
        "findings": [{"priority": int(p), "check": c, "message": m} for p, c, m in findings],
    }
    if not findings and raw_xml:
        result["raw_xml_preview"] = raw_xml[:500]
    return result


def cmd_delete(s: requests.Session, url: str, args) -> dict:
    """Delete an ABAP object: lock → DELETE → done."""
    base_path = TYPE_PATH_MAP.get(args.type, "programs/programs")
    base = f"{url}/sap/bc/adt/{base_path}/{args.name.lower()}"

    handle = _lock(s, base)
    if not handle:
        return {"error": "Could not lock object — may be locked by another user"}

    params = {"lockHandle": handle}
    if args.transport:
        params["transportRequest"] = args.transport

    del_resp = s.delete(base, params=params, headers={"X-sap-adt-lockhandle": handle})

    if del_resp.status_code not in (200, 204):
        _unlock(s, base, handle)
        return {
            "error": "Delete failed",
            "status": del_resp.status_code,
            "body": del_resp.text[:300],
        }

    return {"name": args.name, "type": args.type, "delete_status": del_resp.status_code, "message": "Deleted"}


def cmd_where_used(s: requests.Session, url: str, args) -> dict:
    """Find all objects that reference a given ABAP object."""
    base_path = TYPE_PATH_MAP.get(args.type, "programs/programs")
    obj_uri = f"/sap/bc/adt/{base_path}/{args.name.lower()}"

    resp = s.get(
        f"{url}/sap/bc/adt/repository/informationsystem/usages",
        params={"uri": obj_uri, "maxResults": args.max},
        headers={"Accept": "application/xml"},
    )

    if resp.status_code == 404:
        # Fallback: search with usages operation
        resp = s.get(
            f"{url}/sap/bc/adt/repository/informationsystem/search",
            params={"operation": "usages", "uri": obj_uri, "maxResults": args.max},
            headers={"Accept": "application/xml"},
        )

    if resp.status_code not in (200, 201):
        return {
            "error": "where-used failed",
            "status": resp.status_code,
            "raw_xml_preview": resp.text[:300],
        }

    usages = parse_xml_refs(resp.text)
    return {
        "target": args.name,
        "target_type": args.type,
        "usages_count": len(usages),
        "usages": usages,
    }


def cmd_history(s: requests.Session, url: str, args) -> dict:
    """Show change history of an ABAP object."""
    base_path = TYPE_PATH_MAP.get(args.type, "programs/programs")
    base = f"{url}/sap/bc/adt/{base_path}/{args.name.lower()}"

    # Approach A: versions endpoint
    resp = s.get(f"{base}/source/versions", headers={"Accept": "application/xml"})
    if resp.status_code == 200:
        versions = re.findall(
            r'versionId="([^"]*)"[^>]*changedAt="([^"]*)"[^>]*changedBy="([^"]*)"',
            resp.text,
        )
        if versions:
            return {
                "name": args.name,
                "type": args.type,
                "source": "versions_endpoint",
                "versions": [
                    {"version": v, "changed_at": t, "changed_by": u}
                    for v, t, u in versions
                ],
            }

    # Approach B: object properties fallback (latest change only)
    resp2 = s.get(base)
    def _ex(pattern, text):
        m = re.search(pattern, text)
        return m.group(1) if m else ""

    return {
        "name": args.name,
        "type": args.type,
        "source": "object_properties_fallback",
        "note": "Full version history unavailable on this system - showing latest change only",
        "versions": [{
            "version": "active",
            "changed_at": _ex(r'adtcore:changedAt="([^"]*)"', resp2.text),
            "changed_by": _ex(r'adtcore:changedBy="([^"]*)"', resp2.text),
            "created_at": _ex(r'adtcore:createdAt="([^"]*)"', resp2.text),
            "created_by": _ex(r'adtcore:createdBy="([^"]*)"', resp2.text),
        }],
    }


def cmd_diff(s: requests.Session, url: str, args) -> dict:
    """Compare active vs inactive (unsaved) source version."""
    base_path = TYPE_PATH_MAP.get(args.type, "programs/programs")
    source_url = f"{url}/sap/bc/adt/{base_path}/{args.name.lower()}/source/main"

    active_resp = s.get(source_url, headers={"Accept": "text/plain"})
    inactive_resp = s.get(f"{source_url}?version=inactive", headers={"Accept": "text/plain"})

    active_src = active_resp.text if active_resp.status_code == 200 else ""
    inactive_src = inactive_resp.text if inactive_resp.status_code == 200 else ""

    if not inactive_src or inactive_src == active_src:
        return {"name": args.name, "type": args.type, "has_changes": False,
                "message": "No inactive version or no pending changes"}

    diff_lines = list(difflib.unified_diff(
        active_src.splitlines(keepends=True),
        inactive_src.splitlines(keepends=True),
        fromfile=f"{args.name} (active)",
        tofile=f"{args.name} (inactive)",
    ))
    diff_text = "".join(diff_lines)
    truncated = len(diff_text) > 10_000
    return {
        "name": args.name,
        "type": args.type,
        "has_changes": True,
        "diff_lines": len(diff_lines),
        "truncated": truncated,
        "diff": diff_text[:10_000] if truncated else diff_text,
    }


def cmd_transports(s: requests.Session, url: str, args) -> dict:
    """List open transport requests, optionally filtered by owner."""
    params = {}
    if args.owner:
        params["user"] = args.owner
    resp = s.get(
        f"{url}/sap/bc/adt/cts/workbench",
        params=params,
        headers={"Accept": "application/vnd.sap.adt.cts.workbench+xml"},
    )
    transports = re.findall(r'tm:number="([^"]*)"[^>]*tm:description="([^"]*)"', resp.text)
    return {
        "status": resp.status_code,
        "transports": [{"number": n, "description": d} for n, d in transports],
    }


# ── CLI ───────────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="SAP ADT REST API client — browse, search, and query ABAP repository",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  Search all programs starting with Z:
    adt-client.py --url https://host:44300 --user LEOS4 --pwd *** search "Z*" --type PROG/P

  Write source from file (activate separately via MCP):
    adt-client.py ... write-source ZMY_PROG --file source.abap --type PROG/P

  Run ATC static analysis:
    adt-client.py ... atc-check ZMY_PROG:PROG/P ZCL_X:CLAS/OC

  Delete object (non-interactive, requires transport):
    adt-client.py ... delete ZMY_PROG --transport UIK900123 --force

  Find where-used:
    adt-client.py ... where-used ZCL_MY_CLASS --type CLAS/OC

  Show change history:
    adt-client.py ... history ZMY_PROG --type PROG/P

  Diff active vs inactive version:
    adt-client.py ... diff ZMY_PROG --type PROG/P

  List open transports for user DEVUSER:
    adt-client.py ... transports --owner DEVUSER
        """,
    )
    p.add_argument("--url", required=True, help="SAP system base URL (e.g. https://host:44300)")
    p.add_argument("--user", required=True, help="SAP logon user")
    p.add_argument("--pwd", required=True, help="SAP password")
    p.add_argument("--client", default="100", help="SAP client (default: 100)")
    p.add_argument("--lang", default="EN", help="Logon language (default: EN)")

    sub = p.add_subparsers(dest="command", required=True, metavar="command")

    # search
    sp = sub.add_parser("search", help="Search ABAP objects by name/type/package")
    sp.add_argument("query", help='Search query — use * for all, e.g. "ZCL*"')
    sp.add_argument("--type", help="Object type, e.g. PROG/P  CLAS/OC  DEVC/K  TABL/DT")
    sp.add_argument("--package", help="Filter by package name")
    sp.add_argument("--author", help="Filter by author/responsible user")
    sp.add_argument("--max", type=int, default=100, metavar="N", help="Max results (default: 100)")

    # objects
    op = sub.add_parser("objects", help="List all objects assigned to a package")
    op.add_argument("package", help="Package name, e.g. \\$TMP or ZPACKAGE")
    op.add_argument("--max", type=int, default=999, metavar="N", help="Max results (default: 999)")

    # packages
    pp = sub.add_parser("packages", help="List sub-packages inside a parent package")
    pp.add_argument("package", help="Parent package name, e.g. \\$TMP")

    # source
    srcp = sub.add_parser("source", help="Read source code of an ABAP object")
    srcp.add_argument("name", help="Object name, e.g. ZCDS_VIEW")
    srcp.add_argument("--type", default="PROG/P", help="Object type (default: PROG/P)")

    # write-source
    wp = sub.add_parser("write-source", help="Write/update source code (lock->PUT->unlock; does not activate)")
    wp.add_argument("name", help="Object name, e.g. ZMY_PROG")
    wp.add_argument("--type", default="PROG/P", help="Object type (default: PROG/P)")
    wp.add_argument("--file", help="Path to .abap source file (UTF-8)")
    wp.add_argument("--text", help="Inline source text")

    # packages-by-responsible
    prp = sub.add_parser("packages-by-responsible", help="List packages by responsible user")
    prp.add_argument("responsible", help="Responsible user, e.g. LEOS4")
    prp.add_argument("--pattern", default="Z*", help="Package name pattern (default: Z*)")
    prp.add_argument("--max", type=int, default=500, metavar="N", help="Max packages to scan (default: 500)")

    # atc-check
    ap = sub.add_parser("atc-check", help="Run ATC static analysis on ABAP objects")
    ap.add_argument("objects", nargs="+", help="Objects as NAME:TYPE e.g. ZMY_PROG:PROG/P")

    # delete
    dp = sub.add_parser("delete", help="Delete an ABAP object (requires --transport for non-$TMP)")
    dp.add_argument("name", help="Object name, e.g. ZMY_PROG")
    dp.add_argument("--type", default="PROG/P", help="Object type (default: PROG/P)")
    dp.add_argument("--transport", help="Transport request number (required for non-$TMP objects)")
    dp.add_argument("--force", action="store_true", help="Skip confirmation prompt (for agent/non-interactive use)")

    # where-used
    up = sub.add_parser("where-used", help="Find all objects that reference a given object")
    up.add_argument("name", help="Object name, e.g. ZCL_MY_CLASS")
    up.add_argument("--type", default="CLAS/OC", help="Object type (default: CLAS/OC)")
    up.add_argument("--max", type=int, default=100, metavar="N", help="Max results (default: 100)")

    # history
    hp = sub.add_parser("history", help="Show change history of an ABAP object")
    hp.add_argument("name", help="Object name, e.g. ZMY_PROG")
    hp.add_argument("--type", default="PROG/P", help="Object type (default: PROG/P)")

    # diff
    dfp = sub.add_parser("diff", help="Compare active vs inactive (unsaved) source version")
    dfp.add_argument("name", help="Object name, e.g. ZMY_PROG")
    dfp.add_argument("--type", default="PROG/P", help="Object type (default: PROG/P)")

    # transports
    tp = sub.add_parser("transports", help="List open transport requests")
    tp.add_argument("--owner", metavar="USER", help="Filter by transport owner/user")

    return p


def main():
    parser = build_parser()
    args = parser.parse_args()

    # Confirmation guard for delete (safety net for interactive use)
    if args.command == "delete" and not getattr(args, "force", False):
        confirm = input(f"Delete {args.name} ({args.type})? [y/N] ").strip()
        if confirm.lower() != "y":
            print(json.dumps({"message": "Aborted"}))
            return

    session = make_session(args.url, args.user, args.pwd, args.client, args.lang)

    handlers = {
        "search": cmd_search,
        "objects": cmd_objects,
        "packages": cmd_packages,
        "packages-by-responsible": cmd_packages_by_responsible,
        "source": cmd_source,
        "write-source": cmd_write_source,
        "atc-check": cmd_atc_check,
        "delete": cmd_delete,
        "where-used": cmd_where_used,
        "history": cmd_history,
        "diff": cmd_diff,
        "transports": cmd_transports,
    }

    result = handlers[args.command](session, args.url, args)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
