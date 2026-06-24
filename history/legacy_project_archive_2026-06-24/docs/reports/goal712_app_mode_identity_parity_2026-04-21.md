# Goal 712: App Mode Identity And Embree Parity Cleanup

Date: 2026-04-21

Status: ACCEPT

## Purpose

Goal 711 closed the public Embree app coverage gate, but Claude noted two
non-blocking cleanup items:

- `segment_polygon_hitcount` and `segment_polygon_anyhit_rows` emitted
  `payload_app: null` in the harness because their JSON did not include an
  `app` field.
- The gate checked only compact modes for `segment_polygon_anyhit_rows` and
  `robot_collision_screening`.

Goal 712 resolves those cleanup items without changing the public app model.

## Changes

- `examples/rtdl_segment_polygon_hitcount.py` now emits
  `"app": "segment_polygon_hitcount"`.
- `examples/rtdl_segment_polygon_anyhit_rows.py` now emits
  `"app": "segment_polygon_anyhit_rows"`.
- `tests/goal712_app_mode_parity_test.py` verifies:
  - segment/polygon hit-count app identity;
  - segment/polygon any-hit `rows`, `segment_flags`, and `segment_counts`
    modes match between CPU/Python oracle and Embree;
  - robot collision `full`, `pose_flags`, and `hit_count` modes match between
    CPU/Python oracle and Embree.

## Verification

Command:

```sh
PYTHONPATH=src:. python3 -m unittest -v tests.goal712_app_mode_parity_test
```

Result:

- 3 tests OK.
- All checked subtests pass.

## Boundary

This is a correctness and polish cleanup. It is not a performance claim and
does not expand engine support. It strengthens the existing Embree app surface
by removing ambiguous app identity and explicitly checking non-compact output
modes that Goal 711 did not cover.

## Consensus

- Codex: ACCEPT
- Gemini Flash: ACCEPT
- Claude: ACCEPT

The consensus closure is recorded in
`/Users/rl2025/rtdl_python_only/docs/reports/goal712_codex_consensus_closure_2026-04-21.md`.

## Verdict

Goal 712 is accepted as a small app identity and mode-parity cleanup.
