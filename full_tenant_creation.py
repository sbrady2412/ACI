#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create a tenant with VRF, two bridge domains, an application profile, two EPGs,
and provider/consumer references to an existing contract (vzBrCP).

Requires Cobra SDK packages built for your APIC version. Credentials via
flags or APIC_URL, APIC_USER, APIC_PASSWORD.

The contract named by --contract must already exist under the tenant (or use
the APIC UI to create the vzBrCP first).
"""

from __future__ import print_function

import argparse
import os
import sys

import cobra.mit.access
import cobra.mit.request
import cobra.mit.session
import cobra.model.draw
import cobra.model.fv
import cobra.model.pol
import cobra.model.vz
from cobra.internal.codec.xmlcodec import toXMLStr


def _parse_args():
    p = argparse.ArgumentParser(description="Full tenant + VRF + 2x BD + 2x EPG (ACI Cobra).")
    p.add_argument("--apic", default=os.environ.get("APIC_URL"), help="APIC URL (or APIC_URL)")
    p.add_argument("--user", default=os.environ.get("APIC_USER", "admin"))
    p.add_argument("--password", default=os.environ.get("APIC_PASSWORD"))
    p.add_argument("--tenant", required=True, help="Tenant name")
    p.add_argument("--application-profile", required=True, dest="ap_name")
    p.add_argument("--vrf", required=True, dest="vrf_name")
    p.add_argument("--epg1", required=True)
    p.add_argument("--epg2", required=True)
    p.add_argument("--bd1", required=True)
    p.add_argument("--bd1-subnet", required=True, metavar="CIDR", help="e.g. 10.1.1.1/24")
    p.add_argument("--bd2", required=True)
    p.add_argument("--bd2-subnet", required=True, metavar="CIDR", help="e.g. 10.1.2.1/24")
    p.add_argument("--contract", required=True, help="Existing vzBrCP name under this tenant")
    p.add_argument("--dry-run", action="store_true", help="Print XML only, no commit")
    return p.parse_args()


def main():
    args = _parse_args()
    if not args.apic:
        print("error: set --apic or APIC_URL", file=sys.stderr)
        sys.exit(2)
    if not args.password:
        print("error: set --password or APIC_PASSWORD", file=sys.stderr)
        sys.exit(2)

    apic_url = args.apic.rstrip("/")
    if not apic_url.startswith(("http://", "https://")):
        apic_url = "https://" + apic_url

    ls = cobra.mit.session.LoginSession(apic_url, args.user, args.password)
    md = cobra.mit.access.MoDirectory(ls)
    if not args.dry_run:
        md.login()

    pol_uni = cobra.model.pol.Uni("")
    tn = args.tenant
    ap = args.ap_name
    vrf = args.vrf_name

    fv_tenant = cobra.model.fv.Tenant(pol_uni, ownerKey="", name=tn, descr="", ownerTag="")
    draw_cont = cobra.model.draw.Cont(fv_tenant)
    draw_info = (
        "{{'epg-{0}':{{'x':175,'y':20}},'epg-{1}':{{'x':-25,'y':20}}}}"
    ).format(args.epg1, args.epg2)
    cobra.model.draw.Inst(
        draw_cont,
        info=draw_info,
        oDn="uni/tn-{0}/ap-{1}".format(tn, ap),
    )

    fv_ctx = cobra.model.fv.Ctx(
        fv_tenant,
        ownerKey="",
        name=vrf,
        descr="",
        knwMcastAct="permit",
        ownerTag="",
        pcEnfPref="enforced",
    )
    cobra.model.fv.RsCtxToExtRouteTagPol(fv_ctx, tnL3extRouteTagPolName="")
    cobra.model.fv.RsBgpCtxPol(fv_ctx, tnBgpCtxPolName="")
    cobra.model.vz.Any(fv_ctx, matchT="AtleastOne", name="", descr="")
    cobra.model.fv.RsOspfCtxPol(fv_ctx, tnOspfCtxPolName="")
    cobra.model.fv.RsCtxToEpRet(fv_ctx, tnFvEpRetPolName="")

    fv_bd1 = cobra.model.fv.BD(
        fv_tenant,
        ownerKey="",
        name=args.bd1,
        descr="",
        unkMacUcastAct="proxy",
        arpFlood="no",
        limitIpLearnToSubnets="no",
        llAddr="::",
        mac="00:22:BD:F8:19:FF",
        epMoveDetectMode="",
        unicastRoute="yes",
        ownerTag="",
        multiDstPktAct="bd-flood",
        unkMcastAct="flood",
    )
    cobra.model.fv.RsBDToNdP(fv_bd1, tnNdIfPolName="")
    cobra.model.fv.RsCtx(fv_bd1, tnFvCtxName=vrf)
    cobra.model.fv.RsIgmpsn(fv_bd1, tnIgmpSnoopPolName="")
    cobra.model.fv.Subnet(
        fv_bd1, name="", descr="", ctrl="", ip=args.bd1_subnet, preferred="no"
    )
    cobra.model.fv.RsBdToEpRet(
        fv_bd1, resolveAct="resolve", tnFvEpRetPolName=""
    )

    fv_bd2 = cobra.model.fv.BD(
        fv_tenant,
        ownerKey="",
        name=args.bd2,
        descr="",
        unkMacUcastAct="proxy",
        arpFlood="no",
        limitIpLearnToSubnets="no",
        llAddr="::",
        mac="00:22:BD:F8:19:FF",
        epMoveDetectMode="",
        unicastRoute="yes",
        ownerTag="",
        multiDstPktAct="bd-flood",
        unkMcastAct="flood",
    )
    cobra.model.fv.RsBDToNdP(fv_bd2, tnNdIfPolName="")
    cobra.model.fv.RsCtx(fv_bd2, tnFvCtxName=vrf)
    cobra.model.fv.RsIgmpsn(fv_bd2, tnIgmpSnoopPolName="")
    cobra.model.fv.Subnet(
        fv_bd2, name="", descr="", ctrl="", ip=args.bd2_subnet, preferred="no"
    )
    cobra.model.fv.RsBdToEpRet(
        fv_bd2, resolveAct="resolve", tnFvEpRetPolName=""
    )

    cobra.model.fv.RsTenantMonPol(fv_tenant, tnMonEPGPolName="")
    fv_ap = cobra.model.fv.Ap(
        fv_tenant, ownerKey="", prio="unspecified", name=ap, descr="", ownerTag=""
    )

    fv_aepg1 = cobra.model.fv.AEPg(
        fv_ap, prio="unspecified", matchT="AtleastOne", name=args.epg1, descr=""
    )
    cobra.model.fv.RsCustQosPol(fv_aepg1, tnQosCustomPolName="")
    cobra.model.fv.RsBd(fv_aepg1, tnFvBDName=args.bd1)
    cobra.model.fv.RsProv(
        fv_aepg1,
        tnVzBrCPName=args.contract,
        matchT="AtleastOne",
        prio="unspecified",
    )

    fv_aepg2 = cobra.model.fv.AEPg(
        fv_ap, prio="unspecified", matchT="AtleastOne", name=args.epg2, descr=""
    )
    cobra.model.fv.RsCons(fv_aepg2, tnVzBrCPName=args.contract, prio="unspecified")
    cobra.model.fv.RsCustQosPol(fv_aepg2, tnQosCustomPolName="")
    cobra.model.fv.RsBd(fv_aepg2, tnFvBDName=args.bd2)

    print(toXMLStr(fv_tenant))

    if args.dry_run:
        return

    c = cobra.mit.request.ConfigRequest()
    c.addMo(fv_tenant)
    md.commit(c)
    print("Committed uni/tn-{0}".format(tn), file=sys.stderr)


if __name__ == "__main__":
    main()
