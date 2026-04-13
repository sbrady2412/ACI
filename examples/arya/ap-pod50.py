#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example: tenant + application profile (see ap-TestAP.json).
Prefer ../../scripts/create_tenant.py --tenant X --application-profile Y for new work.
"""

from __future__ import print_function

import argparse
import os
import sys

import cobra.mit.access
import cobra.mit.request
import cobra.mit.session
import cobra.model.fv
import cobra.model.pol
from cobra.internal.codec.xmlcodec import toXMLStr


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--apic", default=os.environ.get("APIC_URL"))
    p.add_argument("--user", default=os.environ.get("APIC_USER", "admin"))
    p.add_argument("--password", default=os.environ.get("APIC_PASSWORD"))
    p.add_argument("--tenant", default="Tenant_ARYA50")
    p.add_argument("--application-profile", default="TestAP", dest="ap")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    if not args.apic or not args.password:
        print("Need --apic / APIC_URL and --password / APIC_PASSWORD", file=sys.stderr)
        sys.exit(2)

    url = args.apic.rstrip("/")
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    ls = cobra.mit.session.LoginSession(url, args.user, args.password)
    md = cobra.mit.access.MoDirectory(ls)
    if not args.dry_run:
        md.login()

    pol_uni = cobra.model.pol.Uni("")
    fv_tenant = cobra.model.fv.Tenant(
        pol_uni, ownerKey="", name=args.tenant, descr="", ownerTag=""
    )
    cobra.model.fv.Ap(
        fv_tenant, ownerKey="", name=args.ap, prio="unspecified", ownerTag="", descr=""
    )
    cobra.model.fv.RsTenantMonPol(fv_tenant, tnMonEPGPolName="")

    print(toXMLStr(fv_tenant))
    if args.dry_run:
        return

    c = cobra.mit.request.ConfigRequest()
    c.addMo(fv_tenant)
    md.commit(c)
    print("Committed uni/tn-{0}".format(args.tenant), file=sys.stderr)


if __name__ == "__main__":
    main()
