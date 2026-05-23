# Goal2566: Benchmark-App Evidence Manifest

Date: 2026-05-23

## Scope

Goal2551 requested a single machine-readable evidence manifest for the finished
benchmark-app wave. Goal2566 adds that manifest at:

`docs/reports/goal2566_benchmark_app_evidence_manifest_2026-05-23.json`

## Contents

The manifest records the four current benchmark apps:

- RT-DBSCAN
- Robot collision screening
- RayDB-style columnar aggregate
- Barnes-Hut / RT-BarnesHut-style

For each app it records the example path, closeout report, primitive contracts,
backend status, correctness oracle, performance artifact paths, language/runtime
contributions, and explicit claim boundaries.

The manifest also records shared substrate contracts added after the app
closeouts:

- `DeviceColumnDescriptor`
- `rtdl.grouped_reduction.v1`

## Boundary

The manifest is review infrastructure only. It does not authorize public
release wording, public speedup claims, authors-code reproduction claims,
SQL/DBMS claims, robot-solver claims, or native app-specific ABI claims.

## Validation

Added `tests/goal2566_benchmark_app_evidence_manifest_test.py` to validate:

- JSON schema marker and snapshot label;
- exactly four benchmark app entries;
- closeout reports and example paths exist;
- listed performance artifacts exist;
- all public speedup and native app-specific ABI flags remain false;
- the consensus and claim-boundary text is present.
- shared substrate contract reports exist.

No pod was used.
