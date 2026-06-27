# Goal 713: Polygon Overlap Apps Expose Embree Native-Assisted Mode

Date: 2026-04-21

Status: ACCEPT

## Purpose

Before Goal 713, two public polygon-overlap apps were CPU-reference-only at
the app CLI level:

- `examples/rtdl_polygon_pair_overlap_area_rows.py`
- `examples/rtdl_polygon_set_jaccard.py`

Goal 713 adds honest Embree support for both apps without overclaiming a fully
native area-overlay kernel.

## Implementation

Both apps now accept:

```sh
--backend cpu_python_reference
--backend cpu
--backend embree
```

The Embree path is `embree_native_assisted`:

1. Embree executes the existing native `overlay_compose` polygon/polygon
   candidate-discovery path over polygon geometry.
2. The app keeps exact bounded grid-cell area/Jaccard refinement in Python/CPU.
3. The JSON payload exposes the boundary explicitly.

This is a real Embree RT/BVH candidate-discovery path, but it is not a fully
native Embree polygon area-overlay or Jaccard kernel.

## Files Changed

- `/Users/rl2025/rtdl_python_only/examples/rtdl_polygon_pair_overlap_area_rows.py`
- `/Users/rl2025/rtdl_python_only/examples/rtdl_polygon_set_jaccard.py`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/app_support_matrix.py`
- `/Users/rl2025/rtdl_python_only/docs/app_engine_support_matrix.md`
- `/Users/rl2025/rtdl_python_only/docs/application_catalog.md`
- `/Users/rl2025/rtdl_python_only/docs/release_facing_examples.md`
- `/Users/rl2025/rtdl_python_only/docs/tutorials/segment_polygon_workloads.md`
- `/Users/rl2025/rtdl_python_only/docs/v0_2_user_guide.md`
- `/Users/rl2025/rtdl_python_only/scripts/goal711_embree_app_coverage_gate.py`
- `/Users/rl2025/rtdl_python_only/tests/goal713_polygon_overlap_embree_app_test.py`

## Matrix Update

`docs/app_engine_support_matrix.md` and `rtdsl.app_engine_support_matrix()`
now mark:

- `polygon_pair_overlap_area_rows` Embree status:
  `direct_cli_native_assisted`
- `polygon_set_jaccard` Embree status:
  `direct_cli_native_assisted`

The note states that Embree performs candidate discovery and CPU/Python
performs exact area/Jaccard refinement.

## Verification

Focused test:

```sh
PYTHONPATH=src:. python3 -m unittest -v tests.goal713_polygon_overlap_embree_app_test
```

Result:

- 3 tests OK.
- Polygon-pair overlap CPU/Python vs Embree parity: OK.
- Polygon-set Jaccard CPU/Python vs Embree parity: OK.
- App matrix status for both apps: `direct_cli_native_assisted`.

Updated Embree app coverage gate:

```sh
PYTHONPATH=src:. python3 scripts/goal711_embree_app_coverage_gate.py \
  --goal 713 \
  --output docs/reports/goal713_embree_app_coverage_gate_macos_2026-04-21.json
```

Result:

- Apps checked: 16
- Runs checked: 32
- Commands valid: true
- Backend-normalized semantic payloads match: true
- Overall valid: true

The two newly included apps both pass:

- `polygon_pair_overlap_area_rows`: CPU OK, Embree OK, semantic match true
- `polygon_set_jaccard`: CPU OK, Embree OK, semantic match true

## Performance Boundary

The macOS app gate timings are smoke-level CLI timings around 0.10 seconds and
are not performance evidence. Goal 713 is an Embree coverage/correctness goal.
Performance claims require larger workloads and phase-split timing.

## AI Review

- Codex local implementation and verification verdict: ACCEPT.
- Gemini 2.5 Flash Lite review:
  `/Users/rl2025/rtdl_python_only/docs/reports/goal713_gemini_flash_lite_review_2026-04-21.md`,
  verdict ACCEPT.
- Claude review was attempted but unavailable due usage limit. Per user
  instruction, Gemini-only external review is sufficient when Claude is
  blocked.

## Verdict

Goal 713 is closed as ACCEPT with Codex + Gemini consensus.
