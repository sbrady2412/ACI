#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
List vzBrCP (standard contracts) per tenant from the distinguished name.
Read-only.
"""

from __future__ import print_function

import argparse
import sys
from collections import defaultdict

import aci_common


def main():
    p = argparse.ArgumentParser(description="ACI contract (vzBrCP) list.")
    aci_common.add_apic_arguments(p)
    p.add_argument(
        "--tenant",
        help="Only contracts in this tenant",
    )
    args = p.parse_args()
    md = aci_common.connect_md(args)

    contracts = aci_common.query_class(md, "vzBrCP")
    if not contracts:
        print("No vzBrCP objects returned.", file=sys.stderr)
        sys.exit(1)

    by_tn = defaultdict(list)
    for mo in contracts:
        dn = getattr(mo, "dn", "") or ""
        tn = aci_common.tenant_name_from_dn(dn)
        if not tn:
            continue
        if args.tenant and tn != args.tenant:
            continue
        name = getattr(mo, "name", "") or ""
        descr = (getattr(mo, "descr", "") or "").replace("\n", " ")[:40]
        by_tn[tn].append((name, descr))

    for tn in sorted(by_tn.keys()):
        print("{0}:".format(tn))
        for name, descr in sorted(by_tn[tn], key=lambda x: x[0]):
            line = "  {0}".format(name)
            if descr:
                line += "  -  {0}".format(descr)
            print(line)


if __name__ == "__main__":
    main()
