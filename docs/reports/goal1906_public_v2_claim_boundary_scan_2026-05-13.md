# Goal1906 - Public v2 Claim Boundary Scan

Status: active-local-gate

Date: 2026-05-13

## Scope

Goal1906 adds a local scanner for public documentation paths:

`scripts/goal1906_public_v2_claim_boundary_scan.py`

The scanner looks for claim-sensitive phrases around v2.0, package install,
arbitrary PyTorch/CuPy acceleration, whole-application acceleration, and broad
RT-core speedup. It allows those phrases only when the nearby text explicitly
blocks or narrows the claim.

## Public Paths

The scanner covers:

- `README.md`
- `docs/README.md`
- `docs/partner_acceleration_boundaries.md`
- `docs/tutorials/*.md`

## Command

```bash
PYTHONPATH=src:. python3 scripts/goal1906_public_v2_claim_boundary_scan.py
```

The generated JSON goes to:

`docs/reports/goal1906_public_v2_claim_boundary_scan.json`

## Boundary

Goal1906 is a wording hygiene gate. After the v2.0 release action, passing it
does not authorize package-install support, whole-app speedup claims, broad
RT-core speedup claims, or arbitrary partner-program acceleration claims.
