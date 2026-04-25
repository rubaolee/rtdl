# Goal 913 RTX A5000 Cloud Group F/H Follow-Up

Date: 2026-04-25

## Scope

This report records the follow-up to the RTX A5000 cloud artifacts copied into
`docs/reports/cloud_2026_04_25/`. The committed evidence keeps the group
summaries, Goal762 artifact reports, the failed graph/Jaccard gate artifacts,
and `rtdl_rtx_a5000_cloud_artifacts_2026-04-25.tgz`; several very large raw
per-app JSON files are preserved in that tarball rather than committed as
400k-line text diffs. The cloud pod was used only for grouped,
artifact-producing tests. The pod is not currently reachable from this machine,
so the fixes below are local pre-cloud work and require a targeted RTX rerun.

## Cloud Findings

| Group | Artifact | Result | Finding |
| --- | --- | --- | --- |
| F graph | `goal889_graph_visibility_optix_gate_rtx.json` | fail | `visibility_edges` produced 8,000,000 rows instead of the intended 80,000 because the app passed copied observers and copied targets to Cartesian `visibility_rows(...)`. |
| F graph | `goal889_graph_visibility_optix_gate_rtx.json` | fail | BFS and triangle-count summaries matched expected counts, but summary-mode parity still hashed non-empty row payloads because the gate called the apps in rows mode. |
| H polygon | `goal877_pair_overlap_phase_rtx.json` | pass | Pair-overlap summary/analytic parity passed at 20,000 copies. Candidate discovery and CPU exact refinement were phase-separated. |
| H polygon | `goal877_jaccard_phase_rtx.json` | fail | Jaccard summary/analytic parity failed: expected intersection area 100,000 but OptiX-assisted output reported 78,500. |

## Local Fixes

1. Added `rt.visibility_pair_rows(...)` as an explicit candidate-edge helper.
   `rt.visibility_rows(...)` remains a Cartesian observer-target matrix helper;
   graph candidate edges now use pair-preserving semantics.

2. Updated `examples/rtdl_graph_analytics_app.py` so `visibility_edges` builds
   explicit candidate edges and dispatches through `rt.visibility_pair_rows(...)`.
   Local CPU/oracle checks now produce exactly `4 * copies` rows, with
   `copies` visible edges and `3 * copies` blocked edges.

3. Updated `scripts/goal889_graph_visibility_optix_gate.py` so summary-mode
   OptiX and CPU records call graph apps with `output_mode="summary"`. This
   prevents row-digest mismatches caused by hashing rows that are intentionally
   omitted from summary-mode validation.

4. Updated `scripts/goal877_polygon_overlap_optix_phase_profiler.py` to emit
   `candidate_diagnostics` in addition to parity digests. The next Jaccard RTX
   artifact will show raw expected/actual candidate counts instead of hiding
   candidate count fields inside the canonical parity digest.

## Verification

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal633_visibility_rows_test \
  tests.goal889_graph_visibility_optix_gate_test -v
```

Result: 12 tests OK.

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal877_polygon_overlap_optix_phase_profiler_test \
  tests.goal759_rtx_cloud_benchmark_manifest_test -v
```

Result: 19 tests OK.

```bash
PYTHONPATH=src:. python3 -m py_compile \
  src/rtdsl/visibility_runtime.py \
  src/rtdsl/__init__.py \
  examples/rtdl_graph_analytics_app.py \
  scripts/goal889_graph_visibility_optix_gate.py \
  scripts/goal877_polygon_overlap_optix_phase_profiler.py
```

Result: passed.

## Required Targeted RTX Rerun

When the next pod is available, do not rerun the full suite first. Run only:

```bash
PYTHONPATH=src:. python3 scripts/goal889_graph_visibility_optix_gate.py \
  --copies 20000 \
  --output-mode summary \
  --validation-mode analytic_summary \
  --chunk-copies 100 \
  --strict \
  --output-json docs/reports/goal889_graph_visibility_optix_gate_rtx.json
```

Then run the Jaccard gate with the same production-scale shape:

```bash
PYTHONPATH=src:. python3 scripts/goal877_polygon_overlap_optix_phase_profiler.py \
  --app jaccard \
  --mode optix \
  --copies 20000 \
  --output-mode summary \
  --validation-mode analytic_summary \
  --chunk-copies 100 \
  --output-json docs/reports/goal877_jaccard_phase_rtx.json
```

If Jaccard still fails, use the new `candidate_diagnostics` field to decide the
next action:

| Diagnostic | Interpretation | Next action |
| --- | --- | --- |
| candidate count below expected | OptiX candidate discovery is dropping pairs. | Reduce chunk size and inspect native LSI/PIP output limits or precision behavior. |
| candidate count matches but parity fails | Candidate discovery is complete but exact Jaccard summary is wrong. | Inspect CPU refinement aggregation over chunked copied sets. |
| candidate count differs only by false-positive pairs and parity passes | Accept; false positives are allowed before exact CPU refinement. | Document candidate count separately from refined row count. |

## Claim Boundary

These fixes do not authorize a public RTX speedup claim. They make the next RTX
cloud run semantically valid and more diagnostic. Promotion still requires
passing cloud artifacts and independent review.
