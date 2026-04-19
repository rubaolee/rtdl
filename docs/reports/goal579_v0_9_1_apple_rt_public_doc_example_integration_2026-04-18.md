# Goal579: v0.9.1 Apple RT Public Doc And Example Integration

Status: implemented, external AI reviewed, accepted

Date: 2026-04-18 local EDT

## Purpose

Goal579 integrates the Goal578 Apple RT backend slice into the public-facing user surface without overclaiming release scope. The intended public message is:

- `v0.9.0` remains the latest released tag until final release action.
- `v0.9.1` is now an active Apple RT candidate on `main`.
- Apple RT currently means Apple Metal/MPS `MPSRayIntersector` on Apple Silicon macOS.
- `run_apple_rt` currently supports only 3D `ray_triangle_closest_hit`.
- There is no full Apple backend parity claim and no speedup claim yet.

## Files Changed For Public Integration

- `/Users/rl2025/rtdl_python_only/README.md`
- `/Users/rl2025/rtdl_python_only/docs/README.md`
- `/Users/rl2025/rtdl_python_only/docs/current_architecture.md`
- `/Users/rl2025/rtdl_python_only/docs/capability_boundaries.md`
- `/Users/rl2025/rtdl_python_only/docs/quick_tutorial.md`
- `/Users/rl2025/rtdl_python_only/docs/release_facing_examples.md`
- `/Users/rl2025/rtdl_python_only/docs/rtdl_feature_guide.md`
- `/Users/rl2025/rtdl_python_only/docs/tutorials/README.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9/README.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9/support_matrix.md`
- `/Users/rl2025/rtdl_python_only/examples/README.md`
- `/Users/rl2025/rtdl_python_only/examples/rtdl_apple_rt_closest_hit.py`

## Example Added

New example:

- `/Users/rl2025/rtdl_python_only/examples/rtdl_apple_rt_closest_hit.py`

It:

- defines a 3D closest-hit RTDL kernel
- computes CPU Python reference rows first
- attempts `rt.run_apple_rt`
- reports `apple_rt_available: false` cleanly when the backend is unavailable
- reports approximate parity when Apple RT is available

Local Apple M4 run:

```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 examples/rtdl_apple_rt_closest_hit.py
```

Observed result:

```json
{
  "apple_rt_available": true,
  "apple_rt_probe": "Apple M4",
  "parity": true
}
```

## Test Evidence

Focused Apple RT test:

```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 -m unittest tests.goal578_apple_rt_backend_test -v
```

Result:

```text
Ran 4 tests in 0.012s
OK
```

Full local test suite:

```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 -m unittest discover -s tests
```

Result:

```text
Ran 239 tests in 60.547s
OK
```

Whitespace audit:

```bash
cd /Users/rl2025/rtdl_python_only
git diff --check
```

Result: pass.

## Public-Doc Checks Performed

Searched public docs for Apple RT and v0.9.1 mentions:

```bash
rg -n "v0\\.9\\.1|Apple RT|rtdl_apple_rt" README.md docs examples/README.md
```

The search confirms that Apple RT is documented in:

- front page
- docs index
- quick tutorial
- release-facing examples
- examples index
- current architecture
- capability boundaries
- feature guide
- tutorials index
- v0.9 support matrix and release package

## Honesty Boundary

The public integration keeps these constraints explicit:

- Apple RT is candidate status until a v0.9.1 release action.
- `v0.9.0` remains the current released tag.
- Apple RT currently supports only 3D closest-hit ray/triangle traversal.
- No full workload parity claim.
- No Apple hardware speedup claim.
- No prepared Apple RT reuse claim.

## External Reviews

- Gemini review: `/Users/rl2025/rtdl_python_only/docs/reports/goal579_gemini_flash_review_2026-04-18.md`
- Claude review: `/Users/rl2025/rtdl_python_only/docs/reports/goal579_claude_review_2026-04-18.md`

Both external reviews returned ACCEPT with no blockers. Claude noted a
non-blocking duplicate-numbering issue in `/Users/rl2025/rtdl_python_only/docs/README.md`;
that issue was fixed after review.

## Current Verdict

Codex local verdict: ACCEPT for Goal579 public doc/example integration.
