#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
List fabric nodes (spine, leaf, APIC, etc.) with ID, model, serial, and
in-band/OOB management address when present. Read-only.
"""

from __future__ import print_function

import argparse
import sys

import aci_common


def _addr(mo):
    for attr in ("address", "oobAddr", "addr", "extAddr"):
        v = getattr(mo, attr, None)
        if v:
            return v
    return ""


def main():
    p = argparse.ArgumentParser(description="ACI fabric node inventory.")
    aci_common.add_apic_arguments(p)
    p.add_argument(
        "--role",
        help="Only show nodes whose role contains this substring (e.g. leaf)",
    )
    args = p.parse_args()
    md = aci_common.connect_md(args)

    nodes = aci_common.query_class(md, "fabricNode")
    if not nodes:
        print("No fabricNode objects returned.", file=sys.stderr)
        sys.exit(1)

    rows = []
    for mo in nodes:
        role = (getattr(mo, "role", "") or "").strip()
        if args.role and args.role.lower() not in role.lower():
            continue
        nid = getattr(mo, "id", "") or getattr(mo, "nodeId", "") or ""
        rows.append(
            (
                str(nid).zfill(3),
                role,
                (getattr(mo, "name", "") or "")[:28],
                (getattr(mo, "model", "") or "")[:18],
                (getattr(mo, "serial", "") or "")[:14],
                _addr(mo)[:40],
            )
        )

    rows.sort(key=lambda r: r[0])
    fmt = "{:>4}  {:12}  {:28}  {:18}  {:14}  {}"
    print(fmt.format("ID", "ROLE", "NAME", "MODEL", "SERIAL", "MGMT ADDR"))
    print(fmt.format("-" * 4, "-" * 12, "-" * 28, "-" * 18, "-" * 14, "-" * 10))
    for r in rows:
        print(fmt.format(*r))


if __name__ == "__main__":
    main()
