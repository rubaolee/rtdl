# Goal4834 Completion Report — RayJoin SoS Contract Repair and Synthetic Gate

Date: 2026-06-30

Status: `completed_correctness_repair__no_performance_win_claim`

## Purpose

Goal4834 was opened after Goal4818/Goal4819 showed that released RTDL could not
byte-reproduce the RayJoin public polygon-overlay sample because its directed
segment point-location contract did not fully match the RayJoin paper/source
Simulation-of-Simplicity behavior.

The goal was not to create a RayJoin-only hidden kernel.  The repair is scoped
as a product-level directed point-location/overlay correctness fix:

- follow the RayJoin author/source intended SoS contract for equal-height PIP
  boundary candidates;
- keep midpoint face state per directed map instead of overwriting a shared
  field;
- prove the contract on synthetic cases before using expensive OptiX runs;
- then verify the public County x Soil sample byte-for-byte against the author
  answer on NVIDIA OptiX.

Embree was intentionally out of scope.

## Inputs Read

- Paper: `C:/Users/Lestat/Downloads/ics24 (1).pdf`
- Author clarification: `C:/Users/Lestat/Downloads/rayjoin_pip_determinism_summary.md`
- Author source on POD: `/workspace/RayJoin_fresh`, HEAD
  `02bf6220d6d20b04af77ee20364eced75cc029c9`
- Public sample:
  - left: `/workspace/RayJoin_fresh/test/dataset/br_county_clean_25_odyssey_final.txt`
  - right: `/workspace/RayJoin_fresh/test/dataset/br_soil_ascii_odyssey_final.txt`
  - answer: `/workspace/RayJoin_fresh/test/dataset/br_countyXbr_soil_answer.txt`

## Implementation

Tracked files changed:

- `src/native/optix/rtdl_optix_core.cpp`
  - aligned equal-height directed point-location comparator with the author
    clarified SoS contract:
    - query map 0 prefers larger slope;
    - query map 1 prefers smaller slope.
- `src/rtdsl/rayjoin_overlay.py`
  - preserves midpoint face ids per directed map, so map0 and map1 overlay
    classification cannot overwrite each other.
- `tests/goal4373_rayjoin_cdb_point_location_route_test.py`
  - updated source guard for the corrected comparator.
- `tests/goal4374_rayjoin_exact_paper_suite_test.py`
  - retains midpoint-face/output-chain regression coverage.
- `tests/goal4834_rayjoin_sos_synthetic_contract_test.py`
  - new synthetic contract tests for the author clarified SoS behavior.

Internal artifacts:

- `history/internal_docs/goal4834_author_sos_t_reported.patch`
- `history/internal_docs/goal4834_author_patch_scope.md`
- `history/internal_docs/goal4834_contract_alignment_notes_2026-06-30.md`
- `history/internal_docs/goal4834_synthetic_cases.md`
- `history/internal_docs/goal4834_synthetic_gate_summary.json`
- `history/internal_docs/goal4834_author_patched_public_sample_summary.json`
- `history/internal_docs/goal4834_rtdl_rebuilt_public_sample_iter0_summary.json`
- `history/internal_docs/goal4834_public_sample_patched_author_vs_rtdl_perf_summary.json`

## Local Synthetic Gate

Command:

```bash
py -3 -m unittest \
  tests.goal4834_rayjoin_sos_synthetic_contract_test \
  tests.goal4373_rayjoin_cdb_point_location_route_test \
  tests.goal4374_rayjoin_exact_paper_suite_test.Goal4374RayjoinExactPaperSuiteTest.test_overlay_midpoint_faces_are_stored_per_map \
  tests.goal4374_rayjoin_exact_paper_suite_test.Goal4374RayjoinExactPaperSuiteTest.test_overlay_output_chain_writer_is_not_legacy_seed
```

Result:

- `Ran 12 tests`
- `OK`

POD rerun after syncing the same files:

- `Ran 12 tests in 6.595s`
- `OK`

## Patched Author Baseline

The author source was patched only to encode the author clarified intended SoS
tie-break into reported distance.  Compatibility changes needed for modern
CUDA/GCC were kept separate from algorithm semantics.

Patch artifact:

- `history/internal_docs/goal4834_author_sos_t_reported.patch`

Build:

- worktree: `/workspace/RayJoin_goal4834_patched_author`
- binary: `/workspace/RayJoin_goal4834_patched_author/release/bin/polyover_exec`
- build completed successfully.

Public sample single-run result:

- return code: `0`
- byte-equal to answer: `true`
- output SHA256:
  `464f87a59cc2428f63cbfe5068965d7bc7adb8eee51e9c1e3a5960ae8b76019e`
- bytes: `16631243`
- LSI count in author log: `20860`

Artifact:

- `history/internal_docs/goal4834_author_patched_public_sample_summary.json`

## Rebuilt RTDL OptiX Gate

POD checkout:

- `/workspace/rtdl_goal4817_user_smoke_20260630_102224`

Build command:

```bash
make build-optix \
  OPTIX_PREFIX=/tmp/optix-sdk-probe \
  CUDA_PREFIX=/usr/local/cuda-12.8 \
  OPTIX_CUDA_ARCH=sm_89
```

Result:

- `build/librtdl_optix.so` rebuilt successfully.

Single public-sample correctness run:

- byte-equal to answer: `true`
- output SHA256:
  `464f87a59cc2428f63cbfe5068965d7bc7adb8eee51e9c1e3a5960ae8b76019e`
- bytes: `16631243`
- LSI intersections: `20860`
- midpoint positives:
  - map0 in map1: `934`
  - map1 in map0: `3189`
- vertex positives:
  - map0 in map1: `337691`
  - map1 in map0: `255272`

Artifact:

- `history/internal_docs/goal4834_rtdl_rebuilt_public_sample_iter0_summary.json`

## Bounded Performance Smoke

This smoke compares the patched-author intended-SoS binary against rebuilt RTDL
on the same public County x Soil sample.  It is correctness-gated and writes the
full output file on every run.

Artifact:

- `history/internal_docs/goal4834_public_sample_patched_author_vs_rtdl_perf_summary.json`

Results:

| Route | Runs byte-equal | Median wall seconds |
| --- | ---: | ---: |
| patched author binary | `3/3` | `3.722452186048031` |
| rebuilt RTDL OptiX helper | `3/3` | `6.272514246404171` |

Ratio:

- `author_median / rtdl_median = 0.5934545606145083x`

Interpretation:

- correctness is fixed for this public sample;
- RTDL does **not** beat the patched-author baseline in this run;
- no performance-win claim is authorized.

The previous Goal4821 ratio against a different clean-compat author baseline
must not be promoted over this patched-author comparison.

## Decision Audit

1. Was I stupid in closing this as a performance win?
   - No. I am not closing it as a performance win.
2. If there was a stupid failure mode, what was it?
   - The dangerous failure mode would have been reusing the old Goal4821
     `1.7x` result after changing the author baseline. I reran instead.
3. Was there another path that avoids being stuck on a bad idea?
   - Yes: separate correctness repair from performance optimization. Goal4834
     closes correctness; any performance work must be a new goal.
4. Can we start a different path that truly solves the problem?
   - Yes. Next work should either expand exact-input availability or optimize
     RTDL overlay assembly/write overhead, but only after preserving this
     correctness gate.

## Claim Boundary

Authorized:

- RTDL core directed point-location/overlay correctness repair;
- public County x Soil sample byte-equality after rebuilding OptiX;
- bounded patched-author-vs-RTDL performance smoke showing no RTDL speed win.

Not authorized:

- full Section 5.7 eight-pair reproduction claim;
- broad RayJoin performance claim;
- broad RTDL performance claim;
- claim that RTDL beats the patched author implementation on this sample;
- Embree claim.

## Exit Label

`completed_correctness_repair__public_sample_byte_equal__no_performance_win_claim`
