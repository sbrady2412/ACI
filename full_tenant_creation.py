#!/usr/bin/env python

# list of packages that should be imported for this code to work
import cobra.mit.access
import cobra.mit.request
import cobra.mit.session
import cobra.model.draw
import cobra.model.fv
import cobra.model.pol
import cobra.model.vz
from cobra.internal.codec.xmlcodec import toXMLStr

# log into an APIC and create a directory object
ls = cobra.mit.session.LoginSession('http://172.31.216.24', 'admin', 'scotch123')
md = cobra.mit.access.MoDirectory(ls)
md.login()

# the top level object on which operations will be made
polUni = cobra.model.pol.Uni('')


ftenant_name = raw_input('Name of Tenant: ')
ap_name = raw_input('Application Profile name: ')
VRF_name = raw_input('VRF name: ')
epg_name1 = raw_input('EPG 1 name: ')
epg_name2 = raw_input('EPG 2 name: ')
BD1_name = raw_input('BD1 name: ')
BD1_ip = raw_input('BD1 IP/Mask: ')
BD2_name = raw_input('BD2 name: ')
BD2_ip = raw_input('BD2 IP/Mask: ')
contract_name = raw_input('Contract name: ')

# build the request using cobra syntax
fvTenant = cobra.model.fv.Tenant(polUni, ownerKey=u'', name=ftenant_name, descr=u'', ownerTag=u'') 
drawCont = cobra.model.draw.Cont(fvTenant)
drawInst = cobra.model.draw.Inst(drawCont, info=u"{'epg-epg_name1':{'x':175,'y':20},'epg-epg_name2':{'x':-25,'y':20}}", oDn=u'uni/tn-ftenant_name/ap-ap_name')
fvCtx = cobra.model.fv.Ctx(fvTenant, ownerKey=u'', name=VRF_name, descr=u'', knwMcastAct=u'permit', ownerTag=u'', pcEnfPref=u'enforced')
fvRsCtxToExtRouteTagPol = cobra.model.fv.RsCtxToExtRouteTagPol(fvCtx, tnL3extRouteTagPolName=u'')
fvRsBgpCtxPol = cobra.model.fv.RsBgpCtxPol(fvCtx, tnBgpCtxPolName=u'')
vzAny = cobra.model.vz.Any(fvCtx, matchT=u'AtleastOne', name=u'', descr=u'')
fvRsOspfCtxPol = cobra.model.fv.RsOspfCtxPol(fvCtx, tnOspfCtxPolName=u'')
fvRsCtxToEpRet = cobra.model.fv.RsCtxToEpRet(fvCtx, tnFvEpRetPolName=u'')
fvBD = cobra.model.fv.BD(fvTenant, ownerKey=u'', name=BD1_name, descr=u'', unkMacUcastAct=u'proxy', arpFlood=u'no', limitIpLearnToSubnets=u'no', llAddr=u'::', mac=u'00:22:BD:F8:19:FF', epMoveDetectMode=u'', unicastRoute=u'yes', ownerTag=u'', multiDstPktAct=u'bd-flood', unkMcastAct=u'flood')
fvRsBDToNdP = cobra.model.fv.RsBDToNdP(fvBD, tnNdIfPolName=u'')
fvRsCtx = cobra.model.fv.RsCtx(fvBD, tnFvCtxName=VRF_name)
fvRsIgmpsn = cobra.model.fv.RsIgmpsn(fvBD, tnIgmpSnoopPolName=u'')
fvSubnet = cobra.model.fv.Subnet(fvBD, name=u'', descr=u'', ctrl=u'', ip=BD2_ip, preferred=u'no')
fvRsBdToEpRet = cobra.model.fv.RsBdToEpRet(fvBD, resolveAct=u'resolve', tnFvEpRetPolName=u'')
fvBD2 = cobra.model.fv.BD(fvTenant, ownerKey=u'', name=BD2_name, descr=u'', unkMacUcastAct=u'proxy', arpFlood=u'no', limitIpLearnToSubnets=u'no', llAddr=u'::', mac=u'00:22:BD:F8:19:FF', epMoveDetectMode=u'', unicastRoute=u'yes', ownerTag=u'', multiDstPktAct=u'bd-flood', unkMcastAct=u'flood')
fvRsBDToNdP2 = cobra.model.fv.RsBDToNdP(fvBD2, tnNdIfPolName=u'')
fvRsCtx2 = cobra.model.fv.RsCtx(fvBD2, tnFvCtxName=VRF_name)
fvRsIgmpsn2 = cobra.model.fv.RsIgmpsn(fvBD2, tnIgmpSnoopPolName=u'')
fvSubnet2 = cobra.model.fv.Subnet(fvBD2, name=u'', descr=u'', ctrl=u'', ip=BD1_ip, preferred=u'no')
fvRsBdToEpRet2 = cobra.model.fv.RsBdToEpRet(fvBD2, resolveAct=u'resolve', tnFvEpRetPolName=u'')
#vzFilter = cobra.model.vz.Filter(fvTenant, ownerKey=u'', name=u'SSH', descr=u'', ownerTag=u'')
#vzEntry = cobra.model.vz.Entry(vzFilter, tcpRules=u'', arpOpc=u'unspecified', applyToFrag=u'no', dToPort=u'22', descr=u'', prot=u'tcp', icmpv4T=u'unspecified', sFromPort=u'unspecified', stateful=u'no', icmpv6T=u'unspecified', sToPort=u'unspecified', etherT=u'ip', dFromPort=u'22', name=u'TCP-SSH')
fvRsTenantMonPol = cobra.model.fv.RsTenantMonPol(fvTenant, tnMonEPGPolName=u'')
fvAp = cobra.model.fv.Ap(fvTenant, ownerKey=u'', prio=u'unspecified', name=ap_name, descr=u'', ownerTag=u'')
fvAEPg = cobra.model.fv.AEPg(fvAp, prio=u'unspecified', matchT=u'AtleastOne', name=epg_name1, descr=u'')
fvRsCustQosPol = cobra.model.fv.RsCustQosPol(fvAEPg, tnQosCustomPolName=u'')
fvRsBd = cobra.model.fv.RsBd(fvAEPg, tnFvBDName=BD1_name)
fvRsProv = cobra.model.fv.RsProv(fvAEPg, tnVzBrCPName=contract_name, matchT=u'AtleastOne', prio=u'unspecified')
fvAEPg2 = cobra.model.fv.AEPg(fvAp, prio=u'unspecified', matchT=u'AtleastOne', name=epg_name2, descr=u'')
fvRsCons = cobra.model.fv.RsCons(fvAEPg2, tnVzBrCPName=contract_name, prio=u'unspecified')
fvRsCustQosPol2 = cobra.model.fv.RsCustQosPol(fvAEPg2, tnQosCustomPolName=u'')
fvRsBd2 = cobra.model.fv.RsBd(fvAEPg2, tnFvBDName=BD2_name)


# commit the generated code to APIC
print toXMLStr(polUni)
c = cobra.mit.request.ConfigRequest()
c.addMo(polUni)
md.commit(c)

