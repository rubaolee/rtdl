# Goal2240: Closed-Shape Membership 2-AI Consensus

Status: accepted with boundary.

## Evidence

- Codex implementation/report: `docs/reports/goal2238_closed_shape_membership_primitive_2026-05-17.md`
- Gemini review: `docs/reviews/goal2239_gemini_review_goal2238_closed_shape_membership_2026-05-17.md`
- Test gate: `tests/goal2238_closed_shape_membership_primitive_test.py`

## Consensus

Codex and Gemini agree that Goal2238 is a valid app-agnostic primitive
improvement:

- `rtdl_optix_run_point_closed_shape_membership_2d` is exposed as a generic
  native OptiX ABI.
- `closed_shape_membership_2d_optix` is exposed as the Python helper.
- The public row vocabulary is `point_id`, `shape_id`, and `membership`.
- The future-version to-do list now captures deferred ideas without authorizing
  release work by itself.

## Performance Evidence

On the RTX pod, the 10,000-query RayJoin-style probe showed:

- row match: `true`
- row count: `879`
- generic closed-shape median: `0.03738784417510033`
- legacy optimized median: `0.03850874863564968`
- ratio: `0.9708922128019587`

The accepted narrow conclusion is that the generic closed-shape wrapper reaches
the same performance class as the existing optimized closed-boundary path on
this probe, while preserving the app-agnostic public surface.

## Pushed-Commit Rerun

After Goal2240 was committed and pushed, the pod was reset to `origin/main` at
`b6bbba120c86697454cbf876113fbbf965755282` and rebuilt from Git without local
patches:

```text
timeout 600 make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk CUDA_PREFIX=/usr/local/cuda-12.8
PYTHONPATH=src:. python3 -m unittest \
  tests.goal2238_closed_shape_membership_primitive_test \
  tests.goal2240_closed_shape_membership_2ai_consensus_test
Ran 9 tests: OK
```

The pushed-commit RayJoin-style timing rerun produced:

```json
{
  "closed_shape_median_sec": 0.03516587242484093,
  "closed_shape_over_legacy_ratio": 0.8500515311435861,
  "closed_shape_rows": 879,
  "legacy_median_sec": 0.041369106620550156,
  "legacy_rows": 879,
  "limit": 10000,
  "repeats": 5,
  "row_match": true
}
```

This confirms the online commit preserves the exact row contract and reaches the
same-or-better performance class than the legacy optimized closed-boundary path
on this bounded probe.

## Boundary

This does not authorize:

- v2.0 release,
- broad RayJoin speedup claims,
- broad PIP speedup claims,
- full RayJoin reproduction claims,
- or a claim that the old internal closed-boundary implementation has been fully
  rewritten.

The next RayJoin reproduction step remains a larger workload-level project with
its own evidence and consensus.
