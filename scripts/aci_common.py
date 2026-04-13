# -*- coding: utf-8 -*-
"""Shared APIC login and ClassQuery helpers for read-only ACI scripts."""

from __future__ import print_function

import argparse
import os
import re
import sys

import cobra.mit.access
import cobra.mit.request
import cobra.mit.session


def add_apic_arguments(parser):
    parser.add_argument(
        "--apic",
        default=os.environ.get("APIC_URL"),
        help="APIC URL (or APIC_URL)",
    )
    parser.add_argument(
        "--user",
        default=os.environ.get("APIC_USER", "admin"),
        help="APIC user (default admin, or APIC_USER)",
    )
    parser.add_argument(
        "--password",
        default=os.environ.get("APIC_PASSWORD"),
        help="APIC password (or APIC_PASSWORD)",
    )
    return parser


def apic_url_from_args(args):
    if not args.apic:
        print("error: set --apic or APIC_URL", file=sys.stderr)
        sys.exit(2)
    if not args.password:
        print("error: set --password or APIC_PASSWORD", file=sys.stderr)
        sys.exit(2)
    url = args.apic.rstrip("/")
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url


def connect_md(args):
    """Log in and return MoDirectory."""
    url = apic_url_from_args(args)
    ls = cobra.mit.session.LoginSession(url, args.user, args.password)
    md = cobra.mit.access.MoDirectory(ls)
    md.login()
    return md


def query_class(md, class_name, subtree=None, prop_filter=None):
    """Return list of MOs for a MIT class name."""
    q = cobra.mit.request.ClassQuery(class_name)
    if subtree:
        q.subtree = subtree
    if prop_filter:
        q.propFilter = prop_filter
    try:
        result = md.query(q)
    except AttributeError:
        result = md.lookup(q)
    if result is None:
        return []
    return list(result)


def tenant_name_from_dn(dn):
    """Return tenant name from a DN containing uni/tn-<name>/..."""
    if not dn:
        return None
    m = re.search(r"/tn-([^/]+)/", dn)
    return m.group(1) if m else None


def parse_epg_dn(dn):
    """Parse (tenant, ap, epg) from uni/tn-T/ap-A/epg-E/..."""
    m = re.match(r"uni/tn-([^/]+)/ap-([^/]+)/epg-([^/]+)", dn or "")
    if not m:
        return None, None, None
    return m.group(1), m.group(2), m.group(3)


def parse_bd_dn(dn):
    """Parse (tenant, bd) from uni/tn-T/BD-BDname/..."""
    m = re.match(r"uni/tn-([^/]+)/BD-([^/]+)", dn or "")
    if not m:
        return None, None
    return m.group(1), m.group(2)
