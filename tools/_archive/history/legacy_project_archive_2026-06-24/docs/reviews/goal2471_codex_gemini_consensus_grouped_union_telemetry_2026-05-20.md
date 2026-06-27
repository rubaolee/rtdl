# Goal2471 Codex/Gemini Consensus - Grouped-Union Atomic Telemetry

Date: 2026-05-20

## Inputs

- Implementation/report: `docs/reports/goal2471_grouped_union_atomic_telemetry_2026-05-20.md`
- Gemini review: `docs/reviews/goal2471_gemini_review_grouped_union_telemetry_2026-05-20.md`
- Focused local tests: 42 tests passed across Goal2457-2471 grouped-stream and grouped-union coverage.
- Syntax/diff hygiene: `py_compile` for changed Python entry points and `git diff --check` passed.

## Consensus

Codex and Gemini agree that the local Goal2471 slice is acceptable as a
telemetry implementation boundary pending pod validation.

The accepted boundary is narrow:

- The added ABI is generic fixed-radius grouped-union telemetry, not DBSCAN
  native semantics.
- The default non-telemetry grouped-union runtime path remains the default and
  should not pay telemetry device-atomic overhead.
- The caller must explicitly provide a contiguous CUDA `uint64[4]` telemetry
  column.
- This work does not authorize a performance claim.

## Remaining Gate

Goal2471 is not closed as runtime evidence until a CUDA/OptiX pod validates:

- the telemetry symbol builds and loads with the deployed OptiX headers;
- all-items self-query produces positive parent atomic attempts/successes;
- fallback counters stay zero in all-items mode;
- predicate/fallback mode produces sane fallback counters on a small fixture;
- telemetry-on versus telemetry-off overhead is characterized separately.

The prepared pod command is:

```text
PYTHONPATH=src:. python scripts/goal2471_grouped_union_telemetry_pod_smoke.py \
  --output docs/reports/goal2471_grouped_union_telemetry_pod_smoke.json
```

The attempted pod endpoint `root@213.173.110.198:21453` was unreachable with
`Connection refused`, so no pod validation is included in this consensus.
