# Goal581: v0.9.1 Apple RT Release Action

Status: final external AI reviewed, accepted for commit/tag/push

Date: 2026-04-18 local EDT

## Scope

This goal records the final release action for `v0.9.1`.

The release action is allowed only if:

- Goal578 Apple RT backend bring-up is accepted.
- Goal579 public docs/examples integration is accepted.
- Goal580 pre-release test/doc/flow gate is accepted.
- final mechanical checks are clean.
- final external release-action review accepts commit/tag/push.

## Release Content

`v0.9.1` releases the first bounded Apple RT backend slice:

- `run_apple_rt`
- 3D `ray_triangle_closest_hit`
- macOS Apple Silicon only
- Apple Metal/MPS `MPSRayIntersector`
- direct helper and `run_apple_rt` parity against CPU Python reference

The release explicitly does not claim:

- full Apple backend parity
- non-macOS support
- prepared Apple RT reuse
- Apple hardware speedup
- Apple RT support for the broader `v0.9.0` HIPRT workload matrix

## Accepted Internal Goals

- `/Users/rl2025/rtdl_python_only/docs/reports/goal578_v0_9_1_apple_rt_backend_bringup_2026-04-18.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal579_v0_9_1_apple_rt_public_doc_example_integration_2026-04-18.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal580_v0_9_1_apple_rt_pre_release_gate_2026-04-18.md`

## External Review Evidence Before Release Action

Goal578:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal578_gemini_flash_review_2026-04-18.md`: ACCEPT
- `/Users/rl2025/rtdl_python_only/docs/reports/goal578_claude_review_2026-04-18.md`: ACCEPT

Goal579:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal579_gemini_flash_review_2026-04-18.md`: ACCEPT
- `/Users/rl2025/rtdl_python_only/docs/reports/goal579_claude_review_2026-04-18.md`: ACCEPT

Goal580:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal580_gemini_flash_review_2026-04-18.md`: ACCEPT
- `/Users/rl2025/rtdl_python_only/docs/reports/goal580_claude_review_2026-04-18.md`: ACCEPT

Goal581 final release-action reviews:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal581_gemini_flash_review_2026-04-18.md`: ACCEPT
- `/Users/rl2025/rtdl_python_only/docs/reports/goal581_claude_review_2026-04-18.md`: ACCEPT

## Final Mechanical Checks

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
  "parity": true,
  "scope": "v0.9.1 released Apple Metal/MPS closest-hit example for Ray3D/Triangle3D"
}
```

Focused Apple RT unit test:

```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 -m unittest tests.goal578_apple_rt_backend_test -v
```

Result:

```text
Ran 4 tests in 0.021s
OK
```

Full local unit suite:

```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 -m unittest discover -s tests
```

Result:

```text
Ran 239 tests in 61.236s
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

Public-doc Apple RT candidate wording scan:

```bash
cd /Users/rl2025/rtdl_python_only
rg -n 'candidate Apple|Apple RT candidate|v0\.9\.1 candidate|candidate.*Apple|active .*candidate|in-progress Apple' README.md docs/README.md docs/current_architecture.md docs/capability_boundaries.md docs/quick_tutorial.md docs/release_facing_examples.md docs/rtdl_feature_guide.md docs/tutorials/README.md docs/release_reports/v0_9/README.md docs/release_reports/v0_9/support_matrix.md docs/release_reports/v0_9_1 examples/README.md examples/rtdl_apple_rt_closest_hit.py
```

Result: no matches.

## Release Action Fields

Commit: pending execution

Tag: pending execution

Push: pending execution

## Current Verdict

Codex local verdict: ACCEPT to commit, tag, and push `v0.9.1`.

External release-action consensus: ACCEPT from Gemini Flash and Claude.
