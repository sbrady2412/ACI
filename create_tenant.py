#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create a new ACI tenant on an APIC using the Cobra SDK.

Examples:
  python create_tenant.py --apic https://apic.example.com --user admin \\
      --password secret --tenant TN-PROD

  APIC_URL=https://10.1.1.1 APIC_USER=admin APIC_PASSWORD=secret \\
      python create_tenant.py --tenant TN-DEV --application-profile AP1
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
import cobra.model.vz
from cobra.internal.codec.xmlcodec import toXMLStr


def _parse_args():
    p = argparse.ArgumentParser(description="Create an fvTenant (and optional AP) on ACI APIC.")
    p.add_argument(
        "--apic",
        default=os.environ.get("APIC_URL"),
        help="APIC base URL, e.g. https://apic.example.com (or env APIC_URL)",
    )
    p.add_argument(
        "--user",
        default=os.environ.get("APIC_USER", "admin"),
        help="APIC username (default: admin, or env APIC_USER)",
    )
    p.add_argument(
        "--password",
        default=os.environ.get("APIC_PASSWORD"),
        help="APIC password (or env APIC_PASSWORD)",
    )
    p.add_argument("--tenant", required=True, help="New tenant name (fvTenant name)")
    p.add_argument("--descr", default="", help="Tenant description")
    p.add_argument(
        "--application-profile",
        metavar="NAME",
        help="If set, create an empty application profile under the tenant",
    )
    p.add_argument(
        "--vrf",
        metavar="NAME",
        help="If set, create a VRF (fvCtx) with this name under the tenant",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Print XML only; do not commit to APIC",
    )
    p.add_argument(
        "--verbose-xml",
        action="store_true",
        help="Print submitted XML before commit",
    )
    return p.parse_args()


def main():
    args = _parse_args()
    if not args.apic:
        print("error: --apic or APIC_URL is required", file=sys.stderr)
        sys.exit(2)
    if args.password is None:
        print("error: --password or APIC_PASSWORD is required", file=sys.stderr)
        sys.exit(2)

    apic_url = args.apic.rstrip("/")
    if not apic_url.startswith(("http://", "https://")):
        apic_url = "https://" + apic_url

    ls = cobra.mit.session.LoginSession(apic_url, args.user, args.password)
    md = cobra.mit.access.MoDirectory(ls)
    if not args.dry_run:
        md.login()

    pol_uni = cobra.model.pol.Uni("")
    fv_tenant = cobra.model.fv.Tenant(
        pol_uni,
        ownerKey=u"",
        name=args.tenant,
        descr=args.descr or u"",
        ownerTag=u"",
    )
    cobra.model.fv.RsTenantMonPol(fv_tenant, tnMonEPGPolName=u"")

    if args.application_profile:
        cobra.model.fv.Ap(
            fv_tenant,
            ownerKey=u"",
            prio=u"unspecified",
            name=args.application_profile,
            descr=u"",
            ownerTag=u"",
        )

    if args.vrf:
        fv_ctx = cobra.model.fv.Ctx(
            fv_tenant,
            ownerKey=u"",
            name=args.vrf,
            descr=u"",
            knwMcastAct=u"permit",
            ownerTag=u"",
            pcEnfPref=u"enforced",
        )
        cobra.model.fv.RsCtxToExtRouteTagPol(fv_ctx, tnL3extRouteTagPolName=u"")
        cobra.model.fv.RsBgpCtxPol(fv_ctx, tnBgpCtxPolName=u"")
        cobra.model.vz.Any(fv_ctx, matchT=u"AtleastOne", name=u"", descr=u"")
        cobra.model.fv.RsOspfCtxPol(fv_ctx, tnOspfCtxPolName=u"")
        cobra.model.fv.RsCtxToEpRet(fv_ctx, tnFvEpRetPolName=u"")

    if args.verbose_xml or args.dry_run:
        print(toXMLStr(fv_tenant))

    if args.dry_run:
        return

    c = cobra.mit.request.ConfigRequest()
    c.addMo(fv_tenant)
    md.commit(c)
    print("Committed tenant: uni/tn-{0}".format(args.tenant))


if __name__ == "__main__":
    main()
