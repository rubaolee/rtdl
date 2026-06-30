# Goal4817 — RayJoin User-Mode Correctness Smoke Execution

Date: 2026-06-30

Status: `goal4817_smoke_executed_pending_external_review`

This goal executes the Goal4816-D smoke plan as an **RTDL user/application
author**, not as an RTDL runtime developer.

## Standing Boundary

No RTDL runtime/native/release-surface files were edited. The execution used a
fresh source checkout on the POD:

- repo: `/workspace/rtdl_goal4817_user_smoke_20260630_102224`
- HEAD: `293883ce12e4663ed80c2a07c166a5b22286f7ef`
- VERSION: `v2.14`
- `git status --short`: empty before and after the smoke runs

The user install/build step built `build/librtdl_optix.so` from the clean
checkout with the available OptiX SDK headers. This changed build artifacts only
and did not dirty the source tree.

## Artifact Index

Copied POD artifacts:

- `history/internal_docs/goal4817_artifacts_2026-06-30/environment.json`
- `history/internal_docs/goal4817_artifacts_2026-06-30/input_manifest.json`
- `history/internal_docs/goal4817_artifacts_2026-06-30/build_preflight_after_optix.json`
- `history/internal_docs/goal4817_artifacts_2026-06-30/tiny_fixture_route_smoke_summary.json`
- `history/internal_docs/goal4817_artifacts_2026-06-30/generic_numba_gap_probe_summary.json`
- `history/internal_docs/goal4817_artifacts_2026-06-30/author_sample_bundled_helper_correctness_summary.json`
- `history/internal_docs/goal4817_artifacts_2026-06-30/author_sample_bundled_helper_diff_head.txt`
- `history/internal_docs/goal4817_artifacts_2026-06-30/author_sample_equal_ties_correctness_summary.json`
- `history/internal_docs/goal4817_artifacts_2026-06-30/author_sample_author_binary_health_summary.json`

Remote raw artifacts remain under:

`/workspace/rtdl_goal4817_user_smoke_artifacts_20260630`

## Environment Preflight

Clean RTDL user environment:

- `import rtdsl`: OK, from the clean checkout.
- OptiX public primitive imports: OK.
- bundled RayJoin helper import: OK.
- GPU: NVIDIA RTX 4000 Ada Generation, driver 550.127.05.
- `import numba`: failed in the clean system Python
  (`ModuleNotFoundError: No module named 'numba'`).

Input availability:

- old exact root `/workspace/rayjoin_section57_data/cdb_topology`: missing.
- same-source County x Zipcode CDBs: present.
- same-source Block x Water CDBs: present.
- author public sample inputs and answer: present in `/workspace/RayJoin_fresh/test/dataset`.

Author source/binary:

- author repo HEAD: `02bf6220d6d20b04af77ee20364eced75cc029c9`.
- author worktree is dirty, so semantic source reading must use `git show HEAD:<file>`.
- author `release/bin/polyover_exec` exists and was used only for a public-sample
  health check.

## Smoke 1 — Tiny RTDL Fixture Route Smoke

Route label:

`bundled_helper_bounded_available_input_reproduction_not_generic`

Scope:

`tiny_fixture_route_smoke_not_section57_not_performance`

Input:

- `tests/fixtures/rayjoin/br_county_subset.cdb`
- `tests/fixtures/rayjoin/br_soil_subset.cdb`

Result:

- command completed.
- output file existed.
- output was empty because this tiny fixture produced zero overlay chains.
- clean checkout remained clean.

Interpretation:

This proves the released bundled helper can be imported, can load the fixture
CDBs, can use the built OptiX library, and can finish an overlay route. It is
**not** Section 5.7 evidence, not a paper reproduction, not a performance run,
and not generic RTDL+Numba evidence.

## Smoke 2 — Generic Primitive + Numba Public API Probe

Route label:

`generic_primitive_numba_attempt`

Scope:

`public_api_capability_probe_no_private_helpers_no_performance`

Result:

- Numba was not installed in the clean system Python.
- public OptiX primitives were visible:
  - `prepare_segment_pair_intersection_optix`
  - `prepare_segment_pair_left_set_optix`
  - `prepare_directed_segment_point_location_2d_optix`
- public `load_cdb` returned only high-level CDB fields (`chains`, `face_ids`,
  `name`).
- the probe did not identify a public overlay assembly API equivalent to the
  bundled `rayjoin_overlay` helper.
- no private helper was used.

Interpretation:

The generic-primitive + Numba route remains blocked or unproven in this clean
environment. The immediate causes are:

1. Numba was unavailable in the clean user Python.
2. The exposed public pieces do not yet form a complete Section 5.7 overlay
   app without bundled RayJoin helper code.

This is a user-mode capability finding, not a reason to patch RTDL inside this
goal.

## Smoke 3 — Author Public Sample, RTDL Bundled Helper

Route label:

`bundled_helper_bounded_available_input_reproduction_not_generic`

Scope:

`author_public_sample_correctness_smoke_not_section57_not_performance`

Input:

- author left: `/workspace/RayJoin_fresh/test/dataset/br_county_clean_25_odyssey_final.txt`
- author right: `/workspace/RayJoin_fresh/test/dataset/br_soil_ascii_odyssey_final.txt`
- author answer: `/workspace/RayJoin_fresh/test/dataset/br_countyXbr_soil_answer.txt`

Result:

- RTDL bundled helper completed.
- RTDL output bytes: `16631122`.
- author answer bytes: `16631243`.
- RTDL output SHA256:
  `296ad11acb39cd6c54ca6d95aab16598a44d56bb14d960a370b629c9ea5289c7`
- author answer SHA256:
  `464f87a59cc2428f63cbfe5068965d7bc7adb8eee51e9c1e3a5960ae8b76019e`
- byte equality: **false**
- line counts:
  - author answer: `737830`
  - RTDL output: `737812`

Diff head shows face-id/topology ownership changes, for example:

```text
-250 2 2317 2318 0 71
+250 2 2317 2318 0 176
```

The first five lines match, but later output-chain headers diverge. This is not
a whitespace-only mismatch.

Interpretation:

The bundled helper can execute on the author public sample, but it does **not**
pass byte-equivalent correctness against the author answer. The difference shape
is consistent with a point-location/face-ownership/tie-break issue, but this
goal does not prove the exact cause.

## Smoke 4 — Existing Equal-Ties Environment Knob

Route label:

`bundled_helper_bounded_available_input_reproduction_not_generic`

Scope:

`author_public_sample_correctness_smoke_equal_ties_existing_env_not_section57_not_performance`

Execution set:

`RTDL_RAYJOIN_CDB_ALLOW_EQUAL_TIES=1`

Result:

- RTDL output hash was unchanged:
  `296ad11acb39cd6c54ca6d95aab16598a44d56bb14d960a370b629c9ea5289c7`
- byte equality with author answer remained false.

Interpretation:

The existing released equal-ties knob does not implement the author-reply
slope-dependent `t_reported` rule and does not repair this correctness mismatch.

## Smoke 5 — Author Binary Health Check

Scope:

`author_binary_health_on_public_sample_not_performance`

Command:

```bash
/workspace/RayJoin_fresh/release/bin/polyover_exec \
  -poly1 /workspace/RayJoin_fresh/test/dataset/br_county_clean_25_odyssey_final.txt \
  -poly2 /workspace/RayJoin_fresh/test/dataset/br_soil_ascii_odyssey_final.txt \
  -output /workspace/rtdl_goal4817_user_smoke_artifacts_20260630/author_sample_author_binary_health/author_polyover_rt_output.txt \
  -mode=rt \
  -check=false
```

Result:

- author binary return code: `0`
- output byte-equal to author answer: **true**
- output SHA256:
  `464f87a59cc2428f63cbfe5068965d7bc7adb8eee51e9c1e3a5960ae8b76019e`

Interpretation:

The author answer is valid for this public sample and the author binary can
reproduce it in the current POD environment. Therefore the RTDL bundled-helper
mismatch is a real RTDL-vs-author correctness gap on this sample, not a bad
answer file.

## Goal4817 Exit Assessment

Current exit labels:

- `bundled_helper_correctness_smoke_failed_author_sample_byte_equality_not_generic`
- `generic_primitive_numba_smoke_blocked_by_environment_gap`
- `generic_primitive_numba_smoke_blocked_or_unproven_by_public_overlay_api_gap`

These labels extend the Goal4816-D list because the actual evidence found a
more specific failure mode than "missing author output": author output exists,
the author binary matches it, and RTDL bundled-helper output does not match it.

## What This Means

Goal4817 does **not** authorize:

- performance benchmarking;
- Section 5.7 full reproduction claims;
- generic RTDL+Numba reproduction claims;
- runtime/native/source modifications;
- public release wording changes.

It does establish:

1. A clean RTDL v2.14 user checkout can build and load OptiX.
2. The bundled RayJoin helper executes on both tiny fixture data and the author
   public sample.
3. The author binary reproduces its public sample answer.
4. RTDL bundled-helper output does not match the author public sample answer.
5. The existing equal-ties knob does not fix the mismatch.
6. The generic+Numba route is not yet runnable as a complete user-language
   overlay app in this clean environment.

## Next Recommended Goal

Proceed only after external review.

Recommended next goal:

**Goal4818 — RayJoin public-sample correctness gap diagnosis in user mode.**

Allowed work:

- compare RTDL and author outputs structurally;
- use author source and paper notes to classify the mismatch;
- inspect RTDL public/bundled output semantics from the outside;
- optionally install Numba in a user virtual environment to probe partner
  availability.

Forbidden work:

- editing `src/rtdsl/**`, `src/native/**`, or release surface;
- implementing the slope-dependent author tie-break in RTDL;
- running Section 5.7 performance before correctness is resolved;
- reporting any current RTDL route as exact paper reproduction.

Likely outcomes:

- `blocked_by_pip_tie_break_gap`;
- `blocked_by_bundled_helper_author_sample_correctness_gap`;
- `generic_primitive_numba_blocked_by_public_overlay_api_gap`;
- or, if analysis shows only output-order/format differences, a new
  topology-equivalence check may be proposed for external review.

## Goal-Level Decision Audit

1. **Am I being foolish?**
   No, because the smoke stayed in user mode and produced a falsifiable
   correctness result before any performance run.

2. **What actions would make this foolish?**
   Calling the non-byte-equal RTDL sample a success, treating bundled-helper
   output as generic language reproduction, or patching RTDL to force a match.

3. **Is there another path that avoids being trapped?**
   Yes. Stop performance work and diagnose the correctness gap from the outside.
   If released RTDL lacks the exact author semantics, record a capability gap.

4. **Can I start a different path that truly solves the problem?**
   Yes. The next useful path is a narrow correctness-gap diagnosis using author
   source, author reply, and structural output comparison. The RTDL runtime must
   remain untouched.

