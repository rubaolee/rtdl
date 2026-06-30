# Goal4816-D RayJoin Correctness Preflight And Smoke Plan

Date: 2026-06-30

Status: `goal4816_D_correctness_preflight_plan_complete_pending_review`

Authorized by:

- `history/internal_docs/antigravity_goal4816_C_app_only_design_review_2026-06-30.md`
- Verdict: `approve_goal4816_C_app_only_design_authorize_4816_D`

This is a plan for correctness preflight and smoke validation. It does not
authorize performance benchmarking, optimization, or RTDL runtime/native edits.

## Role Constraint

The executor is an RTDL user/application author, not an RTDL developer.

Allowed:

- use released RTDL v2.14 package behavior;
- use existing examples and documented package modules;
- use explicit Numba partner continuation as application code;
- write user-side reproduction scripts or notebooks outside `src/rtdsl/**` and
  `src/native/**`.

Forbidden:

- patch RTDL runtime/native code;
- add or expose a new RayJoin primitive;
- call private underscored helper functions and label that as generic user API;
- change Section 5.7 semantics to make the app easier.

## Goal4816-D Purpose

Goal4816-D decides whether the environment and available inputs are ready for a
small correctness smoke run, and defines exactly what would count as a
correctness pass.

It deliberately does not measure performance.

## Preflight Inputs

### Required Environment Facts

The smoke executor must record:

- OS and hostname;
- Python executable and version;
- installed/imported RTDL path;
- git commit of the local RTDL source tree if using a source checkout;
- `git status --short`;
- CUDA availability, if the OptiX route is selected;
- Numba availability, if the generic+Numba route is selected.

Path handling must use `pathlib.Path` and/or environment variables because local
development is Windows while POD execution is Linux.

Recommended environment variables:

- `RTDL_RAYJOIN_AUTHOR_ROOT`;
- `RTDL_RAYJOIN_CDB_ROOT`;
- `RTDL_RAYJOIN_OUTPUT_ROOT`;
- `RTDL_RAYJOIN_ROUTE`, one of `bundled_helper` or `generic_primitive_numba`.

### Required Source Facts

Author source:

- root: `${RTDL_RAYJOIN_AUTHOR_ROOT}`;
- expected commit: `02bf6220d6d20b04af77ee20364eced75cc029c9`;
- read semantics with `git show HEAD:<file>` if worktree is dirty.

RTDL:

- no modified tracked files under `src/rtdsl/**` or `src/native/**`;
- if any such modification exists, stop and report
  `blocked_by_dirty_runtime_tree`.

### Required Input Facts

For each candidate pair, record:

- pair id;
- left CDB path;
- right CDB path;
- provenance:
  - `paper_preprocessed_cdb`;
  - `historical_exact_cdb`;
  - `same_source_regenerated_cdb`;
  - `missing_input`;
- file existence and byte size;
- whether the pair can support full author-output comparison.

Current known state from Goal4816-B:

- old exact root `/workspace/rayjoin_section57_data/cdb_topology` was not present
  on the current POD check;
- same-source County x Zipcode files were present under
  `/workspace/rayjoin_section57_same_source_cdb`;
- therefore the first smoke candidate is County x Zipcode only, labeled
  `same_source_regenerated_cdb` unless exact provenance is re-established.

## Smoke Route Selection

Goal4816-D defines two smoke routes, but only one should be executed first.

### First Smoke: Bundled Helper Correctness

Recommended first smoke route:

`bundled_helper_bounded_available_input_reproduction_not_generic`

Reason:

- It is the known feasible path.
- It checks whether current environment/input still supports a RayJoin overlay
  reproduction using released RTDL's shipped helper.
- It does not pretend to be generic user-language reproduction.

Allowed call shape:

```python
from pathlib import Path

from rtdsl.rayjoin_overlay import run_rayjoin_overlay_rtdl_from_cdb_paths

result = run_rayjoin_overlay_rtdl_from_cdb_paths(
    Path(left_cdb),
    Path(right_cdb),
    backend="optix",
    assemble_output=True,
    output_path=Path(output_path),
)
```

Correctness checks:

1. Author command completes on the same input provenance, or the author row is
   recorded as unavailable with reason.
2. RTDL bundled-helper command completes.
3. If both author and RTDL output files exist:
   - byte equality is strongest;
   - otherwise compute topology hash/count diagnostics and classify as bounded
     diagnostic, not full reproduction.
4. If only RTDL output exists:
   - report `author_baseline_missing_for_input`;
   - do not claim reproduction versus author.

No timing interpretation is allowed except "command completed" and optional
raw wall time for debugging. Do not report speedup.

### Second Smoke: Generic Primitive + Numba Gap Probe

Route label:

`generic_primitive_numba_attempt`

Purpose:

Check how far a user can get without private helpers.

Allowed checks:

- import and construct CDB-derived segment/topology columns;
- import direct prepared primitives from `rtdsl.optix_runtime`;
- run scalar/count or dry-run primitives only if needed to prove capability
  presence;
- invoke Numba continuation on toy user-owned columns only as an availability
  check.

Forbidden checks:

- private `_run_lsi_rows`;
- private `_assemble_output_chains`;
- private pair-dump environment variables;
- performance measurement;
- claiming scalar count as overlay.

Expected honest result:

- likely `generic_route_blocked_by_public_lsi_row_coordinate_gap` until a clean
  public pair-row/exact-coordinate surface is identified;
- possibly `unresolved_pip_tie_break_contract` if the generic PIP route cannot
  prove author-reply `t_reported` semantics.

## Author Baseline Command Shape

When author code is run in a future execution goal, use this shape:

```bash
polyover_exec \
  -poly1 <left.cdb> \
  -poly2 <right.cdb> \
  -serialize=<serialized_topology_prefix> \
  -grid_size=15000 \
  -mode=rt \
  -v=1 \
  -fau \
  -xsect_factor 0.1 \
  -enlarge=3.5 \
  -check=false
```

If output comparison is required, the execution goal must include the correct
author output flag/procedure discovered from source or prior Goal4806 artifacts.

## Required Smoke Artifacts

A future execution goal must write:

- `environment.json`;
- `input_manifest.json`;
- `author_command.txt`;
- `rtdl_command_or_script.py`;
- `correctness_summary.json`;
- `correctness_summary.md`;
- output files or hashes;
- raw logs.

Every artifact must state:

- route label;
- input provenance;
- whether author output exists;
- whether byte equality was checked;
- whether topology/hash diagnostics were checked;
- whether PIP determinism was checked or remains unresolved.

## Exit Labels For Future Smoke Execution

Use one:

- `bundled_helper_correctness_smoke_pass_not_generic`;
- `bundled_helper_correctness_smoke_inconclusive_missing_author_output`;
- `generic_primitive_numba_smoke_blocked_by_public_lsi_row_coordinate_gap`;
- `generic_primitive_numba_smoke_blocked_by_pip_tie_break_gap`;
- `blocked_by_missing_input`;
- `blocked_by_dirty_runtime_tree`;
- `blocked_by_environment_gap`.

## Self-Audit

1. **Am I being foolish?**
   Not if I keep this as a correctness plan and stay in user mode.

2. **What would make this foolish?**
   Running performance now, modifying RTDL, or calling the bundled helper a
   generic language solution.

3. **Is there another path?**
   Yes: first prove the bundled helper still works on available inputs, then
   separately probe the generic+Numba route as a language-capability exam.

4. **Can I try a better path now?**
   Yes. After review, execute the smallest correctness smoke with route labels
   and no speedup claims.

## Exit Label

`goal4816_D_correctness_preflight_plan_complete_pending_review`
