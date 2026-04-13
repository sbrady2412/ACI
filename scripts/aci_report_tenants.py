#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
List tenants and counts of VRFs (fvCtx), application profiles (fvAp), and
bridge domains (fvBD). Read-only.
"""

from __future__ import print_function

import argparse
import sys
from collections import defaultdict

import aci_common


def main():
    p = argparse.ArgumentParser(description="ACI tenant summary (counts per tenant).")
    aci_common.add_apic_arguments(p)
    args = p.parse_args()
    md = aci_common.connect_md(args)

    tenants = {}
    for mo in aci_common.query_class(md, "fvTenant"):
        tenants[mo.name] = {"descr": getattr(mo, "descr", "") or ""}

    vrf_by_tn = defaultdict(int)
    for mo in aci_common.query_class(md, "fvCtx"):
        tn = aci_common.tenant_name_from_dn(getattr(mo, "dn", "") or "")
        if tn:
            vrf_by_tn[tn] += 1

    ap_by_tn = defaultdict(int)
    for mo in aci_common.query_class(md, "fvAp"):
        tn = aci_common.tenant_name_from_dn(getattr(mo, "dn", "") or "")
        if tn:
            ap_by_tn[tn] += 1

    bd_by_tn = defaultdict(int)
    for mo in aci_common.query_class(md, "fvBD"):
        tn = aci_common.tenant_name_from_dn(getattr(mo, "dn", "") or "")
        if tn:
            bd_by_tn[tn] += 1

    names = sorted(tenants.keys())
    if not names:
        print("No fvTenant objects returned.", file=sys.stderr)
        sys.exit(1)

    hdr = "{:<24} {:>5} {:>5} {:>5}  {}".format(
        "TENANT", "VRFs", "APs", "BDs", "DESCRIPTION"
    )
    print(hdr)
    print("-" * len(hdr))
    for name in names:
        d = tenants[name]["descr"].replace("\n", " ")[:48]
        print(
            "{:<24} {:>5} {:>5} {:>5}  {}".format(
                name[:24],
                vrf_by_tn[name],
                ap_by_tn[name],
                bd_by_tn[name],
                d,
            )
        )


if __name__ == "__main__":
    main()
