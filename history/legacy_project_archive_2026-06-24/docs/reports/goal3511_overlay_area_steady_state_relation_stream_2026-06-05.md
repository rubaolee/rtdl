# Goal3511 Overlay Area Steady-State Relation Stream

Date: 2026-06-05

## Verdict

`accept-with-boundary`.

Goal3511 adds explicit steady-state timing evidence for the prepared
shape-pair active relation device-column stream used by the v2.8 public-CDB
overlay area route. The goal is not to claim a new full-app speedup. The goal is
to separate one-time setup/JIT/orchestration from the resident relation-stream
primitive that feeds the downstream overlay continuation.

## Why This Matters

After Goal3509, prepared-payload cache read is no longer the dominant stage.
The end-to-end runner still reports `relation_discovery` around `1.4s`, but
that monolithic timer includes setup and warm/cold behavior. Goal3447 had
already shown that the resident relation-column primitive can be millisecond
scale after preparation. Goal3511 makes the same distinction visible inside the
current overlay-area executor artifact.

## Pod Evidence

Artifacts:

- `docs/reports/goal3511_overlay_area_steady_state_relation_stream_cache_write_pod_2026-06-05.json`
- `docs/reports/goal3511_overlay_area_steady_state_relation_stream_pod_2026-06-05.json`

Pod hardware/software:

- GPU: NVIDIA RTX A5000
- CuPy: 14.1.1
- Shapely: 2.1.2
- RTDL commit: `b156242b00026d9e96ef0d6ba3da7c9c56cb0c68`

The measured read run uses:

```text
--payload-cache-mode read --payload-cache-format binary --payload-cache-evidence --relation-column-warmup-repeats 3 --relation-stream-steady-state-evidence
```

## Results

| Stage | Seconds |
| --- | ---: |
| Monolithic `relation_discovery` | 1.4564 |
| Active relation columns warmup 1 | 0.3716 |
| Active relation columns warmup 2 | 0.00746 |
| Active relation columns warmup 3 | 0.00716 |
| Final measured active relation columns | 0.00387 |
| Binary payload cache load | 0.1927 |
| Bounds-positive filter | 0.0494 |
| Device active-shape ordinals | 0.0303 |
| Device tile-task planner best repeat | 0.0517 |
| Tile-task executor best repeat | 0.0143 |
| Exact oracle, validation only | 0.2681 |

Correctness and workload shape remain stable:

- Relation rows: 4,543
- Candidate relation rows after bounds-positive filter: 2,274
- Supported relation rows: 2,149
- Exact positive rows: 1,086
- Observed positive rows: 1,086
- Planned triangle pairs: 4,070,240
- Total absolute area error: `9.227797193034348e-09`
- Max per-relation absolute error: `1.0414238360567651e-09`

## Interpretation

The final measured resident relation-column pass is `0.00387s` after warmup.
This is consistent with the earlier Goal3447 relation-column primitive evidence.
The slower monolithic `relation_discovery` timer should not be described as RT
traversal time. It contains setup, first-use runtime behavior, and surrounding
host orchestration.

This means the next serious performance target is not "make RT traversal
faster" for this row. The better target is a clearer prepared-execution API that
lets users keep right-side scenes, packed left-side columns, relation columns,
payload caches, and continuation inputs alive across repeated calls while
recording setup versus steady-state timing honestly.

## Boundary

Goal3511 does not authorize release, public speedup wording, broad RT-core
speedup wording, true zero-copy wording, RayJoin paper reproduction claims,
`rtdl beats RayJoin` wording, or full overlay claims.

The evidence is still scoped to this public-CDB overlay route on this RTX A5000
pod. It demonstrates that RTDL's generic resident relation-column stream is fast
after warmup, while one-time setup and validation remain separately visible.
