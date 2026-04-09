# Goal 178 Claude 4K Windows Review

## Verdict

The Windows two-star 4K failures are almost certainly caused by Python's
`multiprocessing` `spawn` behavior on Windows interacting poorly with the
current launch method, not by a bug in the core render or shading logic. The
partial-frame evidence (`85` to `88` PPM files, no `summary.json`, no live
Python process afterward) points to a clean worker crash or silent early exit,
not a hang, memory OOM, or code-level shading defect.

## Findings

- `render_orbiting_star_ball_frames(...)` uses `ProcessPoolExecutor` with
  `initializer=_init_orbit_worker` and a large `worker_state` dict containing:
  - triangle mesh
  - pending hit records
  - background image
- on Windows, `spawn` serializes that state for each worker via pickle
- at `3840 x 2160`, `320` frames, and `96 x 192` mesh density, the state is
  large enough that `jobs=8` likely multiplies peak RSS sharply
- observed directory outcomes are consistent with worker failure:
  - `jobs8`: `0` PPM
  - `jobs8_clean`: `85` PPM
  - `jobs8_foreground`: `88` PPM
  - all with no `summary.json`
- no remaining Python process afterward suggests clean worker death or early
  process exit, not a hung pool
- the earlier single-star 4K run likely survived because it carried lower
  effective shading/shadow pressure than the later two-star line
- the Windows HD follow-up, where `--jobs 12` still showed only one visible
  Python process, reinforces that the worker-spawn path is not trustworthy yet

## Summary

The safest next fix before trusting another long Windows two-star run is:

1. verify the Windows spawn path and launch method carefully
2. prove end-to-end completion with a single-process Windows HD run first
3. only then scale `jobs` up incrementally

Important note:

- Claude also referenced the old stale NumPy/scalar parity test mismatch
- that specific stale test issue has already been fixed locally in:
  - [goal166_orbiting_star_ball_demo_test.py](/Users/rl2025/rtdl_python_only/tests/goal166_orbiting_star_ball_demo_test.py)
