#!/usr/bin/env python3
"""
SAP ADT REST API client — fills capability gaps not covered by adt-mcp-server.
Supports: search, list objects/packages, read source, list transports.
"""

import argparse
import json
import re
import sys
import urllib.parse

import requests
import urllib3
from requests.auth import HTTPBasicAuth

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# ── Session ──────────────────────────────────────────────────────────────────

def make_session(url: str, user: str, pwd: str, client: str, lang: str) -> requests.Session:
    """Build authenticated session with CSRF token."""
    s = requests.Session()
    s.auth = HTTPBasicAuth(user, pwd)
    s.verify = False
    s.headers.update({"sap-client": client, "sap-language": lang})
    # Fetch CSRF token (required for POST requests)
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


# ── Commands ──────────────────────────────────────────────────────────────────

def cmd_search(s: requests.Session, url: str, args) -> list | dict:
    """Search ABAP objects by name, type, and/or package."""
    params = {"operation": "quickSearch", "query": args.query, "maxResults": args.max}
    if args.type:
        params["objectType"] = args.type
    if args.package:
        params["packageName"] = args.package
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
    # Parse sub-packages from nodestructure XML
    refs = re.findall(r'technicalName="([^"]*)"[^>]*description="([^"]*)"', resp.text)
    return {"parent": args.package, "subpackages": [{"name": n, "description": d} for n, d in refs]}


def cmd_source(s: requests.Session, url: str, args) -> dict:
    """Fetch source code of a program, class, interface, or function module."""
    type_path_map = {
        "PROG/P": f"programs/programs/{args.name.lower()}/source/main",
        "CLAS/OC": f"oo/classes/{args.name.lower()}/source/main",
        "INTF/OI": f"oo/interfaces/{args.name.lower()}/source/main",
        "FUGR/FF": f"functions/groups/{args.name.split('/')[0].lower()}/fmfunctions/{args.name.lower()}/source/main",
    }
    path = type_path_map.get(args.type, f"programs/programs/{args.name.lower()}/source/main")
    resp = s.get(f"{url}/sap/bc/adt/{path}", headers={"Accept": "text/plain"})
    return {"name": args.name, "type": args.type, "status": resp.status_code, "source": resp.text}


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
    # Extract transport numbers and descriptions
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
    adt-client.py --url https://host:44300 --user E2908 --pwd *** search "Z*" --type PROG/P

  List all objects in $TMP:
    adt-client.py ... objects '$TMP'

  List sub-packages of $TMP:
    adt-client.py ... packages '$TMP'

  Read source of ZCDS_VIEW:
    adt-client.py ... source ZCDS_VIEW --type PROG/P

  List open transports for user P07084:
    adt-client.py ... transports --owner P07084
        """,
    )
    # Connection params (global)
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
    sp.add_argument("--max", type=int, default=100, metavar="N", help="Max results (default: 100)")

    # objects
    op = sub.add_parser("objects", help="List all objects assigned to a package")
    op.add_argument("package", help="Package name, e.g. \\$TMP or ZPACKAGE")
    op.add_argument("--max", type=int, default=999, metavar="N", help="Max results (default: 999)")

    # packages
    pp = sub.add_parser("packages", help="List sub-packages inside a parent package")
    pp.add_argument("package", help="Parent package name, e.g. \\$TMP")

    # source
    srcp = sub.add_parser("source", help="Get source code of an ABAP object")
    srcp.add_argument("name", help="Object name, e.g. ZCDS_VIEW")
    srcp.add_argument("--type", default="PROG/P", help="Object type (default: PROG/P)")

    # transports
    tp = sub.add_parser("transports", help="List open transport requests")
    tp.add_argument("--owner", metavar="USER", help="Filter by transport owner/user")

    return p


def main():
    parser = build_parser()
    args = parser.parse_args()

    session = make_session(args.url, args.user, args.pwd, args.client, args.lang)

    handlers = {
        "search": cmd_search,
        "objects": cmd_objects,
        "packages": cmd_packages,
        "source": cmd_source,
        "transports": cmd_transports,
    }

    result = handlers[args.command](session, args.url, args)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
