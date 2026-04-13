#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
List application EPGs with tenant, application profile, and associated
bridge domain (from fvRsBd). Read-only.
"""

from __future__ import print_function

import argparse
import sys

import aci_common


def main():
    p = argparse.ArgumentParser(description="ACI EPG list with bridge domain.")
    aci_common.add_apic_arguments(p)
    p.add_argument(
        "--tenant",
        help="Only EPGs in this tenant (name match)",
    )
    p.add_argument(
        "-o",
        "--output",
        choices=("table", "csv"),
        default="table",
        help="Output format (default: table)",
    )
    args = p.parse_args()
    md = aci_common.connect_md(args)

    rs_bds = {}
    for mo in aci_common.query_class(md, "fvRsBd"):
        dn = getattr(mo, "dn", "") or ""
        bd = getattr(mo, "tnFvBDName", "") or ""
        parent_epg_dn = dn.rsplit("/", 1)[0]
        rs_bds[parent_epg_dn] = bd

    epgs = aci_common.query_class(md, "fvAEPg")
    if not epgs:
        print("No fvAEPg objects returned.", file=sys.stderr)
        sys.exit(1)

    rows = []
    for mo in epgs:
        dn = getattr(mo, "dn", "") or ""
        tn, ap, epg = aci_common.parse_epg_dn(dn)
        if not epg:
            continue
        if args.tenant and tn != args.tenant:
            continue
        bd = rs_bds.get(dn, "")
        rows.append((tn or "", ap or "", epg, bd, dn))

    rows.sort(key=lambda r: (r[0], r[1], r[2]))
    if args.output == "csv":
        print("tenant,application_profile,epg,bridge_domain,dn")
        for r in rows:
            print(
                ",".join(
                    '"{0}"'.format(x.replace('"', '""'))
                    for x in (r[0], r[1], r[2], r[3], r[4])
                )
            )
        return

    fmt = "{:<18}  {:<22}  {:<22}  {:<18}"
    print(fmt.format("TENANT", "APPLICATION", "EPG", "BRIDGE DOMAIN"))
    print(fmt.format("-" * 18, "-" * 22, "-" * 22, "-" * 18))
    for tn, ap, epg, bd, _ in rows:
        print(fmt.format(tn[:18], ap[:22], epg[:22], bd[:18]))


if __name__ == "__main__":
    main()
