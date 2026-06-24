# Goal1201 External Review Request

Please review Goal1201, the local intake of the Goal1200 OptiX slower-app investigation pod artifacts.

Files to inspect:

- `scripts/goal1201_optix_slower_investigation_intake.py`
- `tests/goal1201_optix_slower_investigation_intake_test.py`
- `docs/reports/goal1201_optix_slower_investigation_intake_2026-05-01.json`
- `docs/reports/goal1201_optix_slower_investigation_intake_2026-05-01.md`
- Source artifact directory:
  `docs/reports/goal1200_live_pod_2026-04-30/extracted/docs/reports/goal1200_optix_slower_app_investigation/`

Review questions:

1. Does the intake faithfully represent the Goal1200 pod artifacts, including the 5 failed probes?
2. Is it correct that this batch authorizes no new public positive RTX speedup wording candidate?
3. Are the per-app decisions technically honest?
   - DB: blocked by candidate/row ceilings and no positive 30k speedup.
   - Graph: RT subpaths completed, but total time is pack/prepare dominated.
   - Polygon pair: stable RT path evidence, largest scale near parity, no positive public wording.
   - Jaccard: blocked by chunk-64 correctness/stability failure.
   - Road hazard: directionally positive but below the 0.1s timing floor.
   - Hausdorff: normalized repair evidence exists, but same-scale public ratio is still missing.
4. Are the tests sufficient for this intake, or is there a blocker that must be fixed before Goal1201 can be closed?

Required verdict format:

- `VERDICT: ACCEPT` or `VERDICT: BLOCK`
- Reasons
- Required fixes, if any

Boundary: this review does not authorize public docs, release, or public RTX speedup claims. It only reviews the local intake classification.
