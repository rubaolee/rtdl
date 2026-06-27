# Goal1205 Repaired RTX Pod Intake Local Prep

Date: 2026-05-01

Verdict: `LOCAL_PREP_READY`

## Scope

Goal1205 adds the local intake tool for the future Goal1204 repaired RTX pod artifact. This is pre-cloud preparation only.

## Files

- `scripts/goal1205_repaired_rtx_pod_intake.py`
- `tests/goal1205_repaired_rtx_pod_intake_test.py`

## Validation

```bash
PYTHONPATH=src:. python3 -m unittest tests/goal1205_repaired_rtx_pod_intake_test.py tests/goal1204_repaired_rtx_pod_packet_test.py
```

Result: `Ran 7 tests ... OK`

Dry run against the default copy-back path:

```bash
PYTHONPATH=src:. python3 scripts/goal1205_repaired_rtx_pod_intake.py
```

Result: `valid=false`, because no Goal1204 pod artifact has been copied back yet. This is expected and must not be interpreted as a benchmark result.

## Boundary

Goal1205 does not run cloud, authorize public docs, release, or public RTX speedup wording. It only prepares the parser/classifier that will be used after a future Goal1204 pod run is copied back.
