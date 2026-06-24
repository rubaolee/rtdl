# Goal2247: RayJoin PIP Closed-Shape Prepack Pod 2-AI Consensus

Status: accepted with boundary.

## Evidence

- Codex pod-evidence report:
  `docs/reports/goal2245_rayjoin_pip_closed_shape_prepack_pod_evidence_2026-05-17.md`
- Pod artifact:
  `docs/reports/goal2245_rayjoin_pip_closed_shape_prepack_same_query_pod_2026-05-17.json`
- Gemini review:
  `docs/reviews/goal2246_gemini_review_goal2245_pip_closed_shape_prepack_pod_evidence_2026-05-17.md`
- Test:
  `tests/goal2245_rayjoin_pip_closed_shape_prepack_pod_evidence_test.py`

## Consensus

Codex and Gemini agree that the pushed-commit pod artifact supports this narrow
conclusion:

```text
On the 100,000-query RayJoin-exported PIP same-query stream, the generic
closed-shape membership path with once-per-run prepacked inputs returns exact
rows and runs in the fast class: 0.08343074284493923 seconds median across
9 repeats.
```

The artifact records:

- `implementation_path: closed_shape_membership_2d_optix`
- `input_preparation_path: prepacked_points_and_shapes_once_per_run_stream`
- `all_parity_vs_reference: true`
- `row_count_consistent: true`
- `row_counts: 8686` for every repeat

## Boundary

This consensus does not authorize:

- full RayJoin reproduction,
- a claim that RTDL beats RayJoin,
- paper-scale speedup claims,
- v2.0 release readiness,
- or broad PIP acceleration claims beyond this exact same-query pod evidence.
