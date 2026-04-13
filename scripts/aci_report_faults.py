#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
List active fault instances (faultInst). Use --severity to narrow results.
Read-only.
"""

from __future__ import print_function

import argparse
import sys

import aci_common


def main():
    p = argparse.ArgumentParser(description="ACI fault instance report.")
    aci_common.add_apic_arguments(p)
    p.add_argument(
        "--severity",
        help="Filter by severity (e.g. critical, major, minor, warning, cleared)",
    )
    p.add_argument(
        "--max",
        type=int,
        default=100,
        metavar="N",
        help="Maximum faults to print (default: 100)",
    )
    args = p.parse_args()
    md = aci_common.connect_md(args)

    prop_filter = None
    if args.severity:
        prop_filter = 'eq(faultInst.severity,"{0}")'.format(args.severity)

    try:
        faults = aci_common.query_class(md, "faultInst", prop_filter=prop_filter)
    except Exception as exc:
        print(
            "faultInst query failed ({0}). Your SDK/APIC may use a different class.".format(
                exc
            ),
            file=sys.stderr,
        )
        sys.exit(1)

    if not faults:
        print("No matching faultInst objects.")
        return

    def sort_key(mo):
        return getattr(mo, "lastTransition", "") or getattr(mo, "created", "") or ""

    faults.sort(key=sort_key, reverse=True)

    fmt = "{:<10}  {:<8}  {:<14}  {}"
    print(fmt.format("SEVERITY", "CODE", "DOMAIN", "DESCR / DN"))
    print(fmt.format("-" * 10, "-" * 8, "-" * 14, "-" * 40))
    for i, mo in enumerate(faults):
        if i >= args.max:
            print("... ({0} more not shown)".format(len(faults) - args.max))
            break
        sev = (getattr(mo, "severity", "") or "")[:10]
        code = (getattr(mo, "code", "") or "")[:8]
        dom = (getattr(mo, "domain", "") or "")[:14]
        descr = (getattr(mo, "descr", "") or "").replace("\n", " ")[:64]
        if not descr:
            descr = (getattr(mo, "dn", "") or "")[:72]
        print(fmt.format(sev, code, dom, descr))


if __name__ == "__main__":
    main()
