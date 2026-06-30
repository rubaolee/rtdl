# Goal1658 Python+RTDL v2.5 Product Checkpoint

## Verdict

`productization_checkpoint_open`

The project should keep the accepted OptiX collect-k fastest solution and stop
new optimization studies until v2.5. The next product goal is to make RTDL
really usable as Python+RTDL: app logic must be implemented in Python, and
engines must expose generic RTDL primitives rather than app-specific native
continuations.

Current main is not yet fully product-ready under this stricter definition.
The repo contains usable Python+RTDL surfaces, but it also still contains
legacy/proof native exports whose names or semantics encode applications.

## Product Rule

For the Python+RTDL product target:

- app logic must be implemented in Python;
- engines must expose generic RTDL primitives;
- app-shaped native continuations are legacy/proof machinery until migrated;
- public examples must not require hidden app-specific engine behavior;
- `COLLECT_K_BOUNDED` remains experimental until a separate promotion gate;
- No new OptiX collect-k optimization candidates before v2.5.

The implementation checkpoint is now machine-readable in:

`src/rtdsl/python_rtdl_app_purity.py`

The regression gate is:

`tests/goal1658_python_rtdl_product_checkpoint_test.py`

## Current Classification

Pure Python+RTDL-ready apps are the apps whose current classification maps to
generic or scalar primitive surfaces. These are acceptable product targets when
their public examples use Python orchestration over primitive-shaped RTDL calls.

Legacy or blocked apps remain outside the product-ready claim until migrated:

| Status | Meaning | Examples |
| --- | --- | --- |
| `pure_python_rtdl_ready` | app can be expressed as Python orchestration over generic primitive surfaces | `event_hotspot_screening`, `dbscan_clustering` |
| `legacy_engine_customized` | app depends on wrapper-backed or app-shaped native continuation behavior | `database_analytics`, `road_hazard_screening`, `segment_polygon_hitcount` |
| `experimental_primitive_blocked` | app depends on experimental `COLLECT_K_BOUNDED` promotion boundary | `polygon_set_jaccard`, `segment_polygon_anyhit_rows` |
| `frozen_or_demo_only` | app is outside active Embree+OptiX product target | Apple RT and HIPRT demos |

Native engine audit currently finds app-shaped exports such as:

- `rtdl_optix_run_pip`
- `rtdl_optix_run_shape_pair_relation_flags`
- `rtdl_optix_db_dataset_compact_summary_batch`
- `rtdl_embree_run_segment_polygon_hitcount`

These are allowed to remain as compatibility/proof code, but they block any
claim that the engine tree is fully app-agnostic today.

## Next Work

The v2.5 work is migration and product hardening, not additional collect-k
optimization:

1. Keep `RTDL_OPTIX_COLLECT_K_FASTEST_CANDIDATE=1` as the fastest accepted
   collect-k implementation.
2. Rewrite or re-route public app examples so app behavior lives in Python and
   native calls are primitive-shaped.
3. Keep legacy app-shaped native exports available only as compatibility/proof
   surfaces until each app has a pure Python+RTDL route.
4. Add fail-closed tests for every app that is promoted to
   `pure_python_rtdl_ready`.
5. Update front page, tutorials, docs, and examples only after the promoted
   pure routes are runnable from the source tree.

## Claim Boundary

This checkpoint does not authorize v2.5 release action, stable
`COLLECT_K_BOUNDED` promotion, public speedup wording, whole-app speedup
wording, broad RTX/GPU acceleration wording, or true zero-copy wording.

It records the boundary for the next product step: make RTDL a real Python
eDSL front end over app-generic Embree and OptiX primitive engines.
