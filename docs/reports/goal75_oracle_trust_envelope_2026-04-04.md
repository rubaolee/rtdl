# Goal 75 Oracle Trust Envelope

Date: 2026-04-04

Status:
- complete
- published

## Objective

Build a trustable internal-oracle package for quick verification and demos by auditing:

- the Python reference oracle on deterministic mini cases
- the native C oracle on deterministic small cases

with PostGIS as the external truth source.

## Scope

Audited workloads:

- `lsi`
- `pip` full-matrix semantics
- `pip` positive-hit semantics
- overlay-seed semantics

Input envelopes:

- Python mini envelope:
  - 15 deterministic `lsi` cases
  - 15 deterministic `pip` cases
  - 15 deterministic overlay cases
- native small envelope:
  - 12 deterministic `lsi` cases
  - 12 deterministic `pip` cases
  - 12 deterministic overlay cases

Case construction:

- fixed handcrafted edge cases
- plus seeded deterministic random cases
- seeds:
  - mini: `7501`
  - small: `7511`

## Implementation

New harness:

- [goal75_oracle_trust_audit.py](/Users/rl2025/rtdl_python_only/scripts/goal75_oracle_trust_audit.py)

New tests:

- [goal75_oracle_trust_audit_test.py](/Users/rl2025/rtdl_python_only/tests/goal75_oracle_trust_audit_test.py)

Supporting Linux artifacts:

- [goal75_summary.json](/Users/rl2025/rtdl_python_only/docs/reports/goal75_oracle_trust_audit_artifacts_2026-04-04/goal75_summary.json)
- [goal75_summary.md](/Users/rl2025/rtdl_python_only/docs/reports/goal75_oracle_trust_audit_artifacts_2026-04-04/goal75_summary.md)
- [goal75_run.log](/Users/rl2025/rtdl_python_only/docs/reports/goal75_oracle_trust_audit_artifacts_2026-04-04/goal75_run.log)

## Validation

Local:

- `python3 -m py_compile scripts/goal75_oracle_trust_audit.py tests/goal75_oracle_trust_audit_test.py`
- `PYTHONPATH=src:. python3 -m unittest tests.goal75_oracle_trust_audit_test tests.goal50_postgis_ground_truth_test`
- result: `11` tests, `OK`

Linux `192.168.1.20`:

- `PYTHONPATH=src:. python3 tests/goal75_oracle_trust_audit_test.py`
- `PYTHONPATH=src:. python3 -m unittest tests.goal40_native_oracle_test tests.goal50_postgis_ground_truth_test`
- `PYTHONPATH=src:. python3 scripts/goal75_oracle_trust_audit.py --output-dir build/goal75_oracle_trust --host-label lx1 --db-name rtdl_postgis`

Linux targeted test result:

- `14` tests
- `OK`

## Results

Python reference oracle, mini envelope:

- `lsi`: `15 / 15` cases matched PostGIS
- `pip` full-matrix: `15 / 15` cases matched PostGIS
- `pip` positive-hit: `15 / 15` cases matched PostGIS
- overlay-seed: `15 / 15` cases matched PostGIS

Native C oracle, small envelope:

- `lsi`: `12 / 12` cases matched PostGIS
- `pip` full-matrix: `12 / 12` cases matched PostGIS
- `pip` positive-hit: `12 / 12` cases matched PostGIS
- overlay-seed: `12 / 12` cases matched PostGIS

## Trusted envelope

Accepted trust boundary after Goal 75:

- the Python reference oracle is trusted for deterministic mini `lsi`, `pip`, and overlay-seed verification
- the native C oracle is trusted for deterministic small `lsi`, `pip`, and overlay-seed verification
- the script also observed native-oracle agreement on the mini sweep, but that is retained only as supporting evidence rather than the accepted trust boundary
- both remain suitable as quick verification and demo oracles
- neither is claimed here as a large-package performance path

## Notes

- the decisive PostGIS-backed closure was run on Linux, where the full PostGIS and native-oracle toolchain is available
- this goal is about correctness and trust, not speed
