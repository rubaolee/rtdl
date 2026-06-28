# Goal4806 V4 + Numba RayJoin Auto-Primitive Planner - Implementation Status

Date: 2026-06-28

Status: implementation scaffold and public entrypoints complete; full high-performance paper-reproduction claim still blocked by missing real Section 5.7 inputs, missing RayJoin author baseline binaries, and missing RT-core POD execution in the current environment.

## What Is Implemented

1. **Semantic Python API**

   ```python
   from rtdsl import v4 as rtdl_v4

   payload = rtdl_v4.paper.rayjoin.section57_polygon_overlay(
       dataset_root="data/rayjoin_section57_cdb",
       partner="numba",
       select="fastest_valid",
   )
   ```

   The user names the workload and partner. The user does not provide primitive names.

2. **Public CLI**

   ```bash
   python examples/paper_reproduction/rayjoin.py \
     --section57-auto-numba \
     --dataset-root data/rayjoin_section57_cdb \
     --partner numba \
     --select fastest_valid
   ```

3. **Automatic Candidate Scoreboard**

   The planner emits candidate V4+Numba routes, including:

   - `v4_numba_post_traversal_mask_compact`
   - `v4_numba_post_traversal_segmented_counts`

   Each candidate records stages, skip reasons, measurement policy, correctness status, compile/JIT timing fields, and whether Numba JIT is required.

4. **Numba Boundary Enforcement**

   The implemented contract requires:

   - `numba.cuda.jit` for Numba partner kernels;
   - device-resident input columns;
   - no hidden hot-path host materialization;
   - no Numba/user callback injection inside the OptiX traversal loop;
   - post-traversal or refinement/continuation execution only.

5. **Author / V2.14 / V4 Columns**

   The evidence schema keeps these separate:

   - `author_code`
   - `v2_14_exact_suite`
   - `v4_numba_selected_plan`

   Missing author binaries are labeled `blocked_missing_author_baseline`, not omitted.

6. **Topology-Aware Correctness Gate**

   The planner records that row counts alone are insufficient. A complete run must validate topology/geometry through coordinates, chain structure, or stable structural hashes.

## Current Evidence

Generated evidence:

- `tools/_archive/future/v4/evidence/goal4806_rayjoin_numba_auto_planner_2026-06-28/evidence.json`
- `tools/_archive/future/v4/evidence/goal4806_rayjoin_numba_auto_planner_2026-06-28/evidence.md`

Current classification:

```text
blocked_missing_inputs
```

The evidence correctly reports:

- Section 5.7 CDB inputs missing in the current workspace.
- RayJoin author binaries missing in the current workspace.
- V4+Numba candidates are enumerated but skipped because real inputs are absent.
- No high-performance claim is authorized.
- No full paper-reproduction claim is authorized.

## Tests Passed

```bash
py -3 -m unittest \
  tests.v4_goal4806_rayjoin_numba_auto_planner_test \
  tests.v4_rayjoin_section57_public_entry_test \
  tests.v4_goal4803_public_markdown_link_integrity_test \
  tests.v4_goal4800_kernel_first_tutorial_classification_test \
  tests.v4_goal4640_public_docs_cleanup_test \
  tests.v4_goal4643_publication_decision_test \
  tests.v4_goal4774_release_packaging_audit_test
```

Result:

```text
Ran 40 tests in 97.142s
OK
```

## Environment Check

Windows workspace:

- `data/rayjoin_section57_cdb`: missing
- `C:\workspace\RayJoin_fresh\release\bin\query_exec`: missing
- `C:\workspace\RayJoin_fresh\release\bin\polyover_exec`: missing

Local Linux `192.168.1.20`:

- `/tmp/rtdl_v4_user_clone_main/data/rayjoin_section57_cdb`: missing
- `/workspace/RayJoin_fresh/release/bin/query_exec`: missing
- `/workspace/RayJoin_fresh/release/bin/polyover_exec`: missing
- `/data/rayjoin_section57_cdb`: missing
- `/home/lestat/rayjoin_section57_cdb`: missing
- GPU: NVIDIA GeForce GTX 1070, not an RT-core GPU

## What Remains To Finish The Full Goal

To complete the high-performance paper-reproduction version of Goal4806, run the implemented planner on an RT-core NVIDIA POD with:

1. exact or same-source regenerated RayJoin Section 5.7 CDB dataset root;
2. RayJoin author `query_exec` and `polyover_exec` binaries;
3. working RTDL OptiX route;
4. working Numba CUDA stack;
5. all eight Section 5.7 overlay pairs, or a predeclared measured subset for a bounded claim.

Required final evidence:

- author-code correctness and timing;
- V2.14 exact-suite correctness and timing;
- V4+Numba selected-plan correctness and timing;
- topology/geometry hashes or equivalent structural correctness proof;
- candidate scoreboard with measured and skipped routes;
- compile/JIT overhead separated from steady-state timing;
- phase timing showing any speedup source;
- classification as `high_performance`, `parity`, `regression`, `blocked_missing_inputs`, or `not_release_ready`.

## Verdict

The code path required to start Goal4806 is now implemented and tested. The full Goal4806 performance/paper-reproduction claim is not complete in the current environment because the authoritative data and author baseline are absent.
