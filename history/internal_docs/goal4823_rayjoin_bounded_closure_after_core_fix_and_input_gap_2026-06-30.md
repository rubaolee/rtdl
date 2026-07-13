# Goal4823 - RayJoin Bounded Closure After Core Fix And Input Gap

Date: 2026-06-30

Status: `goal4823_bounded_closure_complete_pending_review`

## Purpose

This closure packet records the honest end state of the current RayJoin line
after Goals 4820-4822.

It separates three things that must not be conflated:

1. real RTDL product/core fixes exposed by RayJoin;
2. one correctness-gated public-sample reproduction and performance smoke;
3. the still-blocked full Section 5.7 eight-pair paper reproduction claim.

## Final Closure Label

`complete_bounded_public_sample_reproduction_and_core_fix__section57_full_blocked_by_missing_exact_inputs_answers`

## What Is Now Done

### 1. Core directed-segment point-location SoS repair

Goal4820 implemented the author-clarified Simulation-of-Simplicity tie-break as
an RTDL directed-segment point-location contract repair, not as a RayJoin-only
shortcut.

The repair encodes the slope-dependent tie-break into the reported OptiX hit
distance, so equal-height boundary candidates are ordered before OptiX traversal
pruning can hide them.

Modified product file:

- `src/native/optix/rtdl_optix_core.cpp`

Reason to keep:

- deterministic equal-depth directed segment point-location is a general RTDL
  semantic issue;
- the author reply exposed the correct behavior, but the contract is not
  application-specific.

### 2. Per-map midpoint face data-model repair

Goal4820 also fixed a real overlay continuation data-model bug.

The same intersection object can be visited from both map-sorted lists. A single
`mid_point_polygon_id` field allowed the second map's assignment to overwrite
the first map's midpoint face. The fix stores midpoint faces per map.

Modified product file:

- `src/rtdsl/rayjoin_overlay.py`

Reason to keep:

- any directed overlay continuation that reuses intersection objects across
  both maps needs per-map midpoint face state;
- this is not a hidden RayJoin performance shortcut.

### 3. Focused regression coverage

Goal4820 added or updated focused regression coverage:

- `tests/goal4373_rayjoin_cdb_point_location_route_test.py`
- `tests/goal4374_rayjoin_exact_paper_suite_test.py`

The tests cover:

- source-level presence of the directed-segment SoS reported-distance contract;
- per-map midpoint face storage;
- output-chain writer behavior.

### 4. Public County x Soil sample correctness

After the core/product repairs, repaired RTDL reproduced the author public
County x Soil answer byte-for-byte.

Answer:

- `/workspace/RayJoin_fresh/test/dataset/br_countyXbr_soil_answer.txt`
- SHA256:
  `464f87a59cc2428f63cbfe5068965d7bc7adb8eee51e9c1e3a5960ae8b76019e`

RTDL repaired output:

- byte-equal: `true`
- bytes: `16631243`
- SHA256:
  `464f87a59cc2428f63cbfe5068965d7bc7adb8eee51e9c1e3a5960ae8b76019e`

### 5. Bounded public-sample performance smoke

Goal4821 measured only the public County x Soil sample, with correctness checked
on every run.

Author clean-compat binary:

- source HEAD: `02bf6220d6d20b04af77ee20364eced75cc029c9`
- clean-compat binary SHA256:
  `cc7bccbb2409a0c7fe8f8cf2ad4090ece63cf1e3c44c7852fd2d470de1dbc0bc`
- compatibility patch only fixed modern CUDA/GCC build issues:
  - NVTX marker header conflict;
  - `double2` hash/equality support.
- no author LSI/PIP/RT traversal/overlay algorithm logic was changed.

Median wall-clock:

| Route | Median wall seconds | Correctness |
| --- | ---: | --- |
| Author clean-compat binary | `7.702967159450054` | 3/3 byte-equal |
| Repaired RTDL OptiX helper | `4.510876469314098` | 3/3 byte-equal |

Bounded public-sample ratio:

`1.7076431181058986x`

This is a real result, but only for this public sample and this timing boundary.

## What Is Not Done

### 1. Full Section 5.7 eight-pair reproduction

Goal4822 found that the current POD does not contain exact inputs and author
answer files for the full Section 5.7 eight-pair matrix.

Current availability:

- Public County x Soil sample: exact inputs and author answer available.
- Section 5.7 County x Zipcode: same-source CDB inputs available, no author
  answer found.
- Remaining Section 5.7 pairs: exact CDB inputs and answers missing on current
  POD.

Therefore the following claim is still blocked:

> RTDL reproduced and benchmarked the full RayJoin Section 5.7 eight-pair
> polygon overlay workload.

### 2. Generic RTDL+Numba Section 5.7 language reproduction

Earlier Goal4816/Goal4807 evidence showed that complete Section 5.7 overlay
still depends on bundled RayJoin helper/application logic for:

- LSI row reconstruction;
- PIP face-array conversion;
- midpoint projection and midpoint PIP;
- output-chain assembly and author-format writing.

Numba remains useful for selected continuation pieces, but this line did not
prove a complete generic RTDL primitive + Numba implementation of Section 5.7.

The current honest classification is:

- bounded public-sample helper reproduction: done;
- generic user-language Section 5.7 reproduction: not proven.

### 3. Broad RTDL performance claim

The `1.7076431181058986x` ratio is not a broad RTDL claim.

It is not:

- all Section 5.7;
- all RayJoin workloads;
- all benchmark apps;
- all input scales;
- a hot-kernel-only comparison;
- a pristine-author-source build comparison.

It is:

- a public County x Soil sample wall-clock smoke;
- author clean-compat binary vs repaired RTDL OptiX helper;
- byte-equal correctness checked on every run.

## External Review State

### Goal4820

Antigravity approved Goal4820:

`approve_goal4820_core_fix_and_author_public_sample_correctness_gate_passed`

Review file:

- `history/internal_docs/antigravity_goal4820_core_directed_segment_point_location_and_overlay_midpoint_fix_review_2026-06-30.md`

### Goal4821

Antigravity approved Goal4821:

`approve_goal4821_bounded_public_sample_performance_smoke`

Review file:

- `history/internal_docs/antigravity_goal4821_rayjoin_public_sample_controlled_performance_review_2026-06-30.md`

### Goal4822

Goal4822 Antigravity review was attempted through CLI but produced no review
artifact. Review debt is recorded:

- `history/internal_docs/antigravity_goal4822_cli_review_debt_2026-06-30.md`

This does not authorize overclaiming. It keeps the closure conservative.

## Required Artifacts To Reopen Full Section 5.7

To reopen the full paper-reproduction line, the project needs:

1. exact CDB inputs for all eight Section 5.7 pairs under the author script's
   expected contract;
2. author answer/output files for each pair, or a clearly documented procedure
   that regenerates authoritative answers from a verified author binary;
3. a clean author source/binary provenance record;
4. byte-equality checks for author output vs answer;
5. byte-equality checks for RTDL output vs answer;
6. only then, performance runs on the same machine and same inputs.

Without those artifacts, more performance runs would be busy but not useful.

## Recommended Next Work

### Product/code path

1. Keep the Goal4820 core/product fixes.
2. Run focused local tests and POD tests before commit.
3. Prepare a small product-fix commit with no public overclaim.

## Post-Packet Validation

After this closure packet was drafted, the focused validation was rerun.

Local Windows focused tests:

`py -m unittest tests.goal4373_rayjoin_cdb_point_location_route_test tests.goal4374_rayjoin_exact_paper_suite_test`

Result:

- `Ran 28 tests`
- `OK`

POD Linux focused tests:

`PYTHONPATH=src:. python3 -m unittest tests.goal4373_rayjoin_cdb_point_location_route_test tests.goal4374_rayjoin_exact_paper_suite_test`

Result:

- `Ran 28 tests`
- `OK`

POD native OptiX build:

`make build-optix OPTIX_PREFIX=/tmp/optix-sdk-probe CUDA_PREFIX=/usr/local/cuda-12.8 OPTIX_CUDA_ARCH=sm_89`

Result:

- built `/workspace/rtdl_goal4820_sos_fix/build/librtdl_optix.so`

POD public sample smoke using the freshly built library:

| Field | Value |
| --- | --- |
| Library | `/workspace/rtdl_goal4820_sos_fix/build/librtdl_optix.so` |
| Input | County x Soil public sample |
| LSI intersections | `20860` |
| Output bytes | `16631243` |
| Output SHA256 | `464f87a59cc2428f63cbfe5068965d7bc7adb8eee51e9c1e3a5960ae8b76019e` |
| Answer SHA256 | `464f87a59cc2428f63cbfe5068965d7bc7adb8eee51e9c1e3a5960ae8b76019e` |
| Byte equal | `true` |

### Evidence path

1. Close current RayJoin line at bounded public-sample evidence.
2. Keep Goal4822 external review as open debt until Antigravity or Claude
   reviews the availability audit.
3. Do not run additional Section 5.7 performance without exact answers.

### Future optional path

Open a separate data-acquisition goal for exact Section 5.7 inputs and answers.
That goal should be treated as data/provenance work, not runtime development.

## Goal-Level Decision Audit

1. **Am I being foolish?**
   No. This closure preserves real fixes and a real measured result, while
   refusing to inflate it into a full paper claim.

2. **What would make this foolish?**
   It would be foolish to hide the input/answer gap, to call bundled helper
   evidence generic RTDL+Numba language evidence, or to rerun performance where
   correctness cannot be checked.

3. **Is there another path that avoids being trapped in one bad idea?**
   Yes. Keep this line closed and reopen only when exact data and answers exist.

4. **Can I start a different path that actually solves the problem?**
   Yes. Commit the core fixes, keep the bounded sample evidence, and separately
   acquire/verify the missing Section 5.7 artifacts.

## Exit Label

`complete_bounded_public_sample_reproduction_and_core_fix__section57_full_blocked_by_missing_exact_inputs_answers`
