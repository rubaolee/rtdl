# Goal4806 Section 5.7 Overlay Raw Output Digest Gate

Date: 2026-06-28

## Purpose

Goal4806 requires a serious RayJoin Section 5.7 Polygon Overlay reproduction path. Timing alone is insufficient: the local author code path, the RTDL/V2-compatible OptiX path, and the RTDL Embree control must also leave auditable output evidence when output assembly is requested.

This change adds a raw overlay-output digest gate to the Section 5.7 matrix runner.

## What Changed

- `scripts/rayjoin_section57_overlay_matrix.py` now passes `--overlay-output` to the author-code wrapper when `--assemble-overlay-output` is requested.
- Repeated author runs now write per-iteration overlay files instead of overwriting one shared file.
- Matrix summaries now record SHA-256 digests for:
  - author raw overlay output,
  - RTDL OptiX raw overlay output,
  - RTDL Embree raw overlay output.
- Matrix summaries now report:
  - `rtdl_optix_author_raw_output_digest_match`,
  - `rtdl_embree_author_raw_output_digest_match`,
  - `rtdl_optix_embree_raw_output_digest_match`.
- Markdown summaries now expose the same raw-output match fields.

## Claim Boundary

This is a raw file digest check, not a geometry/topology equivalence proof. A digest match is strong byte-level evidence. A digest mismatch can be a real correctness issue or a formatting/order difference and must be investigated before any correctness or performance claim is made.

The V4+Numba candidate route still remains a measured candidate route until POD evidence proves:

- correctness against the Section 5.7 contract,
- device-column execution,
- no host materialization in the hot path,
- performance against the author and RTDL/V2-compatible baselines.

## Local Validation

Commands run on Windows:

```powershell
py -3 -m unittest tests.v4_goal4806_rayjoin_section57_overlay_matrix_digest_test tests.v4_goal4806_rayjoin_numba_candidate_probe_test tests.v4_goal4806_rayjoin_section57_pod_setup_test tests.v4_goal4806_rayjoin_section57_pod_runbook_test tests.v4_rayjoin_section57_public_entry_test tests.v4_goal4806_rayjoin_numba_auto_planner_test
```

Result:

```text
Ran 21 tests in 33.859s
OK
```

Additional dry-run check:

- `author_rt`: command includes `--overlay-output`
- `rtdl_optix`: command includes `--overlay-output`
- `rtdl_embree`: command includes `--overlay-output`
- summary markdown includes the raw-output correctness caveat

## Next Required Evidence

This gate prepares the matrix for POD execution, but it does not provide the final Section 5.7 result by itself. The next required step is an RTX POD run with exact Section 5.7 inputs and author binaries available.
