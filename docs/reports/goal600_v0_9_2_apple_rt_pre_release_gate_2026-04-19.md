# Goal600: v0.9.2 Apple RT Pre-Release Gate

Date: 2026-04-19

Status: pre-release gate passed locally; external AI reviews ACCEPT; pending explicit user release action

## Scope

Goal600 validates the v0.9.2 Apple RT performance line after Goals594-599:

- Goal594 planned the Apple RT performance work.
- Goal595 added the repeatable Apple RT performance harness.
- Goal596 added prepared Apple RT closest-hit reuse.
- Goal597 designed and implemented masked Apple RT hit-count traversal.
- Goal598 analyzed and implemented masked Apple RT segment-intersection traversal.
- Goal599 refreshed public docs for the v0.9.2 candidate boundary.

This gate also fixes stale tests that still encoded older v0.8/v0.9 assumptions:

- `tests/goal506_public_entry_v08_alignment_test.py`
- `tests/goal511_feature_guide_v08_refresh_test.py`
- `tests/goal532_v0_8_release_authorization_test.py`
- `tests/goal543_hiprt_dispatch_test.py`
- `tests/goal546_hiprt_api_parity_skeleton_test.py`
- `scripts/goal515_public_command_truth_audit.py`

Those updates do not change runtime product behavior. They align release/documentation tests with the current released `v0.9.1` state, the current `v0.9.2` candidate Apple RT state, and the already-expanded HIPRT capability surface.

## Test Evidence

Broad public-pattern suite:

```text
PYTHONPATH=src:. python3 -m unittest discover -s tests -p '*test.py' -v
Ran 1118 tests in 108.847s
OK (skipped=171)
```

Targeted stale-test cleanup suite:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal506_public_entry_v08_alignment_test \
  tests.goal511_feature_guide_v08_refresh_test \
  tests.goal515_public_command_truth_audit_test \
  tests.goal532_v0_8_release_authorization_test \
  tests.goal543_hiprt_dispatch_test \
  tests.goal546_hiprt_api_parity_skeleton_test -v
Ran 20 tests in 0.013s
OK (skipped=2)
```

Apple RT focused suite after `make build-apple-rt`:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal578_apple_rt_backend_test \
  tests.goal582_apple_rt_full_surface_dispatch_test \
  tests.goal595_apple_rt_perf_harness_test \
  tests.goal596_apple_rt_prepared_closest_hit_test \
  tests.goal597_apple_rt_masked_hitcount_test \
  tests.goal598_apple_rt_masked_segment_intersection_test -v
Ran 19 tests in 0.046s
OK
```

Public command truth audit:

```text
PYTHONPATH=src:. python3 scripts/goal515_public_command_truth_audit.py
valid: true
public docs scanned: 14
public commands found: 244
```

Public example smoke:

```text
PYTHONPATH=src:. python3 examples/rtdl_hello_world.py
PYTHONPATH=src:. python3 examples/rtdl_apple_rt_closest_hit.py
PYTHONPATH=src:. python3 examples/rtdl_hiprt_ray_triangle_hitcount.py
```

Result:

- hello-world prints `hello, world`.
- Apple RT closest-hit reports `apple_rt_available: true` and `parity: true`.
- HIPRT example exits successfully on macOS with `hiprt_available: false` and an explicit missing-library message, which is the intended bounded behavior on this host.

Mechanical checks:

```text
python3 -m py_compile scripts/goal515_public_command_truth_audit.py scripts/goal595_apple_rt_perf_harness.py
git diff --check
```

Both passed.

## Performance Evidence

Fresh Goal600 artifact paths:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal600_v0_9_2_pre_release_apple_rt_perf_macos_2026-04-19.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal600_v0_9_2_pre_release_apple_rt_perf_macos_2026-04-19.md`

Host/backend versions:

- Host: macOS arm64, Apple M4
- Apple RT backend version: `0.9.2`
- Embree version: `4.4.0`
- Warmups: `5`
- Repeats: `20`
- Stability threshold: coefficient of variation <= `0.15`

Measured medians:

| Workload | Input sizes | Embree median | Apple RT median | Apple/Embree | Parity | Stability |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `ray_triangle_closest_hit_3d` | 256 rays, 256 triangles | 0.002579126 s | 0.001410938 s | 0.547x | true | true |
| `ray_triangle_hit_count_3d` | 128 rays, 512 triangles | 0.002449166 s | 0.115251041 s | 47.057x | true | false |
| `segment_intersection_2d` | 128 left, 128 right | 0.007471208 s | 0.030149874 s | 4.035x | true | true |

Interpretation:

- Closest-hit is the only stable local cell where Apple RT is faster than Embree in this fixture.
- Hit-count is correct but unstable and much slower than Embree in this fixture; it must not be used for public speedup wording.
- Segment-intersection is correct and stable, and the masked implementation is improved relative to the earlier per-right-segment loop, but it is still slower than Embree in this fixture.
- Therefore the correct public claim is: v0.9.2 makes Apple RT easier and more serious for Apple developers by adding prepared reuse, native hit-count and segment-intersection slices, and masked traversal overhead reductions, but it is not yet a broad Apple RT speedup release.

## Documentation Audit

Stale phrase audit over the public front-door docs produced no matches for obsolete Apple RT or v0.8-current-release wording:

```text
rg -n 'post-`v0\.9\.1`|post-v0\.9\.1|native_mps_rt_3d_else_cpu_reference_compat|currently unoptimized|no prepared Apple RT reuse|current released version: `v0\.8\.0`|current released version is `v0\.8\.0`' \
  README.md docs/README.md docs/release_facing_examples.md docs/tutorials/README.md \
  docs/rtdl_feature_guide.md docs/backend_maturity.md docs/quick_tutorial.md \
  examples/README.md docs/current_architecture.md docs/capability_boundaries.md \
  docs/release_reports/v0_9/support_matrix.md
```

Public docs now keep three states separate:

- current released version: `v0.9.1`
- current v0.9.2 candidate: Apple RT performance work on `main`
- honesty boundary: Apple RT is real and improving, but Embree remains the mature performance baseline

## Verdict

Codex verdict: ACCEPT for local v0.9.2 pre-release gate.

External review consensus:

- Gemini-style external review: ACCEPT in `/Users/rl2025/rtdl_python_only/docs/reports/goal600_external_pre_release_review_2026-04-19.md`
- Claude external review: ACCEPT in `/Users/rl2025/rtdl_python_only/docs/reports/goal600_claude_pre_release_review_2026-04-19.md`

No code, doc, or flow blocker is known from this local gate. Release should still wait for the user's explicit release action.
