# Goal4275 Spatial RayJoin Tutorial Reference

Status: current v2.10 learner and benchmark-app documentation update.

## Purpose

Goal4275 adds Spatial RayJoin to the current tutorial track as benchmark-app
reference material and adds a detailed code walkthrough for two audiences:

- new learners who need to understand how RTDL expresses spatial join
  operations;
- RayJoin authors or spatial-system researchers who need to understand what is
  new in RTDL at the language, optimization, and performance levels.

## Files Updated

| File | Action |
| --- | --- |
| `docs/tutorials/current/08_spatial_join_rayjoin_reference.md` | Added a current tutorial reference chapter for Spatial RayJoin. |
| `examples/current/research_benchmarks/spatial_rayjoin/CODE_WALKTHROUGH.md` | Added the detailed learner and RayJoin-author code explanation. |
| `docs/tutorials/current/README.md` | Added Spatial Join as step 8 in the current tutorial track. |
| `docs/tutorials/README.md` | Added Spatial Join to the guided tutorial table. |
| `examples/current/research_benchmarks/spatial_rayjoin/README.md` | Linked the new walkthrough beside the app entry point. |
| `tests/goal4273_current_tutorial_ladder_test.py` | Extended the tutorial ladder guard to include the Spatial Join reference. |
| `tests/goal4275_spatial_rayjoin_tutorial_reference_test.py` | Added targeted checks for learner coverage, RayJoin-author coverage, README links, and CPU-reference smoke. |

## Explanation Boundary

The walkthrough deliberately separates:

- RTDL language/runtime contribution: generic primitives and explicit route
  metadata;
- optimization contribution: prepared handles, packed-left reuse, scalar count
  routes, compact grouped counts, active-count continuations, and partner
  baselines;
- performance reading: contract-specific evidence only.

It is not a full RayJoin paper reproduction claim and does not collapse
PIP, LSI, and overlay into one universal speedup number.

## Local Smoke

The current tutorial command was run locally:

```powershell
$env:PYTHONPATH='src;.'; py -3 examples\current\research_benchmarks\spatial_rayjoin\rtdl_rayjoin_v2_spatial_join_app.py --backend cpu_python_reference --no-rows
```

Result: CPU reference suite passed with `all_match_cpu_python_reference: true`.

## Validation

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal4273_current_tutorial_ladder_test tests.goal4275_spatial_rayjoin_tutorial_reference_test
```

The broader public-doc validation should continue to include Goal4273 and
Goal4274 guards.
