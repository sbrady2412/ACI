#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
List bridge-domain subnets (fvSubnet): IP/mask, scope, preferred flag, and
tenant / BD from the distinguished name. Read-only.
"""

from __future__ import print_function

import argparse
import sys

import aci_common


def main():
    p = argparse.ArgumentParser(description="ACI BD subnet (fvSubnet) report.")
    aci_common.add_apic_arguments(p)
    p.add_argument(
        "--tenant",
        help="Only subnets in this tenant",
    )
    args = p.parse_args()
    md = aci_common.connect_md(args)

    subnets = aci_common.query_class(md, "fvSubnet")
    if not subnets:
        print("No fvSubnet objects returned.", file=sys.stderr)
        sys.exit(1)

    rows = []
    for mo in subnets:
        dn = getattr(mo, "dn", "") or ""
        tn, bd = aci_common.parse_bd_dn(dn)
        if not bd:
            tn = aci_common.tenant_name_from_dn(dn) or ""
            bd = ""
        if args.tenant and tn != args.tenant:
            continue
        ip = getattr(mo, "ip", "") or ""
        scope = getattr(mo, "scope", "") or ""
        pref = getattr(mo, "preferred", "") or ""
        ctrl = getattr(mo, "ctrl", "") or ""
        rows.append((tn, bd, ip, scope, pref, ctrl))

    rows.sort(key=lambda r: (r[0], r[1], r[2]))
    fmt = "{:<16}  {:<20}  {:<20}  {:<10}  {:<6}  {}"
    print(fmt.format("TENANT", "BRIDGE DOMAIN", "SUBNET", "SCOPE", "PREF", "CTRL"))
    print(fmt.format("-" * 16, "-" * 20, "-" * 20, "-" * 10, "-" * 6, "-" * 8))
    for r in rows:
        print(fmt.format(r[0][:16], r[1][:20], r[2][:20], r[3][:10], r[4][:6], r[5][:32]))


if __name__ == "__main__":
    main()
