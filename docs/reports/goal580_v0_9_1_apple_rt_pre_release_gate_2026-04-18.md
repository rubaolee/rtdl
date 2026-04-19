# Goal580: v0.9.1 Apple RT Pre-Release Test, Doc, And Flow Gate

Status: implemented, external AI reviewed, accepted

Date: 2026-04-18 local EDT

## Scope

This gate checked whether the v0.9.1 Apple RT candidate was internally coherent enough to proceed toward a release action when authorized.

It covers:

- code correctness
- public docs/tutorials/examples consistency
- release-flow honesty

It does not tag, push, or publish a release.

## Goals Covered

- Goal578: Apple RT backend bring-up
- Goal579: Apple RT public doc/example integration
- Goal580: this pre-release gate

## Changed Files In Candidate

- `/Users/rl2025/rtdl_python_only/Makefile`
- `/Users/rl2025/rtdl_python_only/README.md`
- `/Users/rl2025/rtdl_python_only/docs/README.md`
- `/Users/rl2025/rtdl_python_only/docs/capability_boundaries.md`
- `/Users/rl2025/rtdl_python_only/docs/current_architecture.md`
- `/Users/rl2025/rtdl_python_only/docs/quick_tutorial.md`
- `/Users/rl2025/rtdl_python_only/docs/release_facing_examples.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9/README.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9/support_matrix.md`
- `/Users/rl2025/rtdl_python_only/docs/rtdl_feature_guide.md`
- `/Users/rl2025/rtdl_python_only/docs/tutorials/README.md`
- `/Users/rl2025/rtdl_python_only/examples/README.md`
- `/Users/rl2025/rtdl_python_only/examples/rtdl_apple_rt_closest_hit.py`
- `/Users/rl2025/rtdl_python_only/src/native/rtdl_apple_rt.mm`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/__init__.py`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/apple_rt_runtime.py`
- `/Users/rl2025/rtdl_python_only/tests/goal578_apple_rt_backend_test.py`

## Code Test Evidence

Native Apple RT build:

```bash
cd /Users/rl2025/rtdl_python_only
make build-apple-rt
```

Result: pass.

Apple RT example:

```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 examples/rtdl_apple_rt_closest_hit.py
```

Result summary:

```json
{
  "apple_rt_available": true,
  "apple_rt_probe": "Apple M4",
  "parity": true
}
```

Focused Apple RT unit test:

```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 -m unittest tests.goal578_apple_rt_backend_test -v
```

Result:

```text
Ran 4 tests in 0.017s
OK
```

Full local unit suite:

```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 -m unittest discover -s tests
```

Result:

```text
Ran 239 tests in 60.547s
OK
```

Compile check:

```bash
cd /Users/rl2025/rtdl_python_only
python3 -m compileall -q src/rtdsl examples/rtdl_apple_rt_closest_hit.py tests/goal578_apple_rt_backend_test.py
```

Result: pass.

Whitespace/diff check:

```bash
cd /Users/rl2025/rtdl_python_only
git diff --check
```

Result: pass.

## Doc Consistency Evidence

At pre-release gate time, the public-doc status intentionally said:

- current released tag: `v0.9.0`
- active candidate: `v0.9.1` Apple RT
- Apple RT platform: Apple Silicon macOS
- Apple RT backend mechanism: Apple Metal/MPS `MPSRayIntersector`
- Apple RT workload: 3D `ray_triangle_closest_hit`
- non-claims: no full Apple backend parity, no prepared Apple RT reuse, no speedup claim

Doc search:

```bash
cd /Users/rl2025/rtdl_python_only
rg -n "v0\\.9\\.1|Apple RT|run_apple_rt|rtdl_apple_rt" README.md docs/README.md docs/current_architecture.md docs/capability_boundaries.md docs/quick_tutorial.md docs/release_facing_examples.md docs/rtdl_feature_guide.md docs/tutorials/README.md docs/release_reports/v0_9/README.md docs/release_reports/v0_9/support_matrix.md examples/README.md examples/rtdl_apple_rt_closest_hit.py | wc -l
```

Result: `94` matching documentation/example references across the intended public files.

## Review Evidence

Goal578:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal578_gemini_flash_review_2026-04-18.md`: ACCEPT
- `/Users/rl2025/rtdl_python_only/docs/reports/goal578_claude_review_2026-04-18.md`: ACCEPT

Goal579:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal579_gemini_flash_review_2026-04-18.md`: ACCEPT
- `/Users/rl2025/rtdl_python_only/docs/reports/goal579_claude_review_2026-04-18.md`: ACCEPT

Claude found one non-blocking numbering issue in `/Users/rl2025/rtdl_python_only/docs/README.md`; it has been fixed.

Goal580:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal580_gemini_flash_review_2026-04-18.md`: ACCEPT
- `/Users/rl2025/rtdl_python_only/docs/reports/goal580_claude_review_2026-04-18.md`: ACCEPT

Claude recorded one informational naming note: `rtdl_apple_rt_context_probe`
uses its success buffer to return the Apple device name. The Python wrapper and
tests treat that behavior consistently, so this is not a release blocker.

## Code Error Assessment

No known code errors block the v0.9.1 release gate.

Residual code limitations:

- Apple RT currently supports only 3D `ray_triangle_closest_hit`.
- The backend creates device/queue and rebuilds MPS acceleration data per call.
- The current MPS API is deprecated by Apple in favor of newer Metal ray tracing APIs, but it is present and functional on this local SDK/host.

These are documented limitations, not release blockers for the stated v0.9.1 slice.

## Doc Error Assessment

No known public-doc error blocks the v0.9.1 release gate after the Goal579 numbering nit fix.

Residual doc boundary at pre-release time:

- Docs intentionally call Apple RT a candidate until release action.
- Docs intentionally keep `v0.9.0` as the current released tag.

After release transition, public docs are expected to identify `v0.9.1` as the
current released version and the Apple RT path as a bounded released slice.

## Flow Error Assessment

No flow error is known at this gate.

Release-flow status:

- no tag created at the time this gate was written
- no push performed at the time this gate was written
- external reviews recorded for Goal578, Goal579, and Goal580
- release action may proceed after the final release-action review and
  mechanical checks remain clean

## Current Verdict

Codex local verdict: ACCEPT for v0.9.1 Apple RT pre-release gate.

External AI consensus: ACCEPT from Gemini Flash and Claude.
