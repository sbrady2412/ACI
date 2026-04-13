# ACI

Small **Cisco ACI** utilities using the APIC **Cobra** Python SDK (read-only reports, tenant creation). Third-party trees are kept under `third_party/` unchanged.

## Layout

| Path | Purpose |
|------|---------|
| `scripts/` | Runnable tools: `create_tenant.py`, `full_tenant_creation.py`, `aci_common.py`, `aci_report_*.py` |
| `examples/arya/` | Sample APIC JSON exports and short example scripts |
| `third_party/arya-master/` | [Arya](https://github.com/datacenter/arya) — cobra code generation from config |
| `third_party/who-moved-my-cli-master/` | Legacy Nexus/CLI helpers (Python 2 era) |
| `requirements.txt` | How to install **acicobra** / **acimodel** for your APIC version |

## Setup

Install Cobra wheels that match your fabric (see `requirements.txt`), then run from the **repository root**:

```bash
export APIC_URL=https://your-apic APIC_PASSWORD='secret'

python3 scripts/aci_report_tenants.py
python3 scripts/create_tenant.py --tenant DEMO --dry-run
```

Reports and provisioning scripts expect `import aci_common` from the same `scripts/` directory (Python adds the script directory to `sys.path` automatically).
