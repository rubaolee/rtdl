# Goal4806 V4+Numba Candidate Probe Runbook Integration

Date: 2026-06-28

## Status

Local execution plumbing now advances one step beyond measurement import:
the RayJoin Section 5.7 POD runbook can generate the V4+Numba candidate
measurement file itself before importing it into the overlay matrix.

This is still not final performance evidence. The probe requires an RT-core POD
for real rows, and full paper-reproduction selection still requires independent
topology/geometry correctness confirmation.

## What Changed

- Added `scripts/rayjoin_section57_numba_candidate_probe.py`.
- The probe writes schema
  `rtdl.v4.rayjoin.section57_numba_measured_candidates.v1`.
- On a POD, the probe executes this candidate-stage chain:
  `RTDL OptiX segment-pair device columns -> Numba CUDA continuation`.
- It measures two candidate plans:
  - `v4_numba_post_traversal_segmented_counts`
  - `v4_numba_post_traversal_mask_compact`
- It refuses to emit performance rows on non-RT-core hardware by default.
- It does not treat stage-count correctness as full Section 5.7 correctness.
  Without explicit independent topology/geometry hash confirmation, rows remain
  selector-rejected by the existing fail-closed import gate.
- `scripts/rayjoin_section57_pod_runbook.py` now runs:
  `preflight -> plan -> candidate_probe -> run`.
- If a caller supplies an existing `--v4-numba-measurements` file, the runbook
  skips candidate probing and imports the supplied file instead.

## Verification

Windows local tests:

```text
py -3 -m unittest tests.v4_goal4806_rayjoin_numba_candidate_probe_test \
  tests.v4_goal4806_rayjoin_section57_pod_setup_test \
  tests.v4_goal4806_rayjoin_section57_pod_runbook_test \
  tests.v4_rayjoin_section57_public_entry_test \
  tests.v4_goal4806_rayjoin_numba_auto_planner_test \
  tests.goal4374_rayjoin_exact_paper_suite_test \
  tests.v4_goal4640_public_docs_cleanup_test

Ran 57 tests in 120.617s
OK
```

Public-surface leak scan:

```text
rg -n "Goal4806|goal4806|Antigravity|Claude|Gemini|review debt|parity/control" \
  README.md docs tutorials examples scripts/rayjoin_section57_pod_setup.py \
  scripts/rayjoin_section57_pod_runbook.py \
  scripts/rayjoin_section57_numba_candidate_probe.py -g "*.md" -g "*.py"
```

Result: no matches.

## Remaining POD Work

The next required evidence is a real RT-core POD run with:

- exact Section 5.7 inputs for all eight overlay pairs,
- RayJoin author binaries,
- current RTDL OptiX backend,
- Numba CUDA,
- candidate probe output,
- author/V2.14/V4 matrix summary,
- independent topology/geometry correctness confirmation before selector-pass
  V4+Numba rows can be accepted.
