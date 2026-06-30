# Goal 642: v0.9.5 Pre-Release Documentation Refresh

Date: 2026-04-19

## Scope

Pre-release documentation gate for v0.9.5 bounded any-hit / visibility rows /
emitted-row reductions.

Checked public-facing docs and examples for:

- correctness of the new `rt.ray_triangle_any_hit(exact=False)` surface;
- correctness of `rt.visibility_rows_cpu(...)` and
  `rt.visibility_rows(..., backend=...)`;
- consistency of backend claims after Goals 637-640;
- correctness and honesty of `rt.reduce_rows(...)` after Goal644;
- absence of stale wording that says visibility is CPU-only or that HIPRT is
  still only a compatibility path for any-hit;
- runnable example coverage.

## Files Checked / Updated

Checked:

- `/Users/rl2025/rtdl_python_only/README.md`
- `/Users/rl2025/rtdl_python_only/docs/README.md`
- `/Users/rl2025/rtdl_python_only/docs/quick_tutorial.md`
- `/Users/rl2025/rtdl_python_only/docs/current_architecture.md`
- `/Users/rl2025/rtdl_python_only/docs/capability_boundaries.md`
- `/Users/rl2025/rtdl_python_only/docs/rtdl_feature_guide.md`
- `/Users/rl2025/rtdl_python_only/docs/release_facing_examples.md`
- `/Users/rl2025/rtdl_python_only/docs/backend_maturity.md`
- `/Users/rl2025/rtdl_python_only/docs/tutorials/README.md`
- `/Users/rl2025/rtdl_python_only/docs/features/README.md`
- `/Users/rl2025/rtdl_python_only/docs/features/ray_tri_anyhit/README.md`
- `/Users/rl2025/rtdl_python_only/docs/features/visibility_rows/README.md`
- `/Users/rl2025/rtdl_python_only/docs/features/reduce_rows/README.md`
- `/Users/rl2025/rtdl_python_only/docs/rtdl/dsl_reference.md`
- `/Users/rl2025/rtdl_python_only/docs/rtdl/workload_cookbook.md`
- `/Users/rl2025/rtdl_python_only/docs/tutorials/feature_quickstart_cookbook.md`
- `/Users/rl2025/rtdl_python_only/examples/README.md`
- `/Users/rl2025/rtdl_python_only/examples/rtdl_ray_triangle_any_hit.py`
- `/Users/rl2025/rtdl_python_only/examples/rtdl_visibility_rows.py`
- `/Users/rl2025/rtdl_python_only/examples/rtdl_reduce_rows.py`
- `/Users/rl2025/rtdl_python_only/examples/rtdl_feature_quickstart_cookbook.py`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/visibility_runtime.py`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/reduction_runtime.py`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9_5/README.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9_5/release_statement.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9_5/support_matrix.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9_5/audit_report.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9_5/tag_preparation.md`

Updated:

- `/Users/rl2025/rtdl_python_only/docs/tutorials/feature_quickstart_cookbook.md`
- `/Users/rl2025/rtdl_python_only/README.md`
- `/Users/rl2025/rtdl_python_only/docs/README.md`
- `/Users/rl2025/rtdl_python_only/docs/current_architecture.md`
- `/Users/rl2025/rtdl_python_only/docs/capability_boundaries.md`
- `/Users/rl2025/rtdl_python_only/docs/rtdl_feature_guide.md`
- `/Users/rl2025/rtdl_python_only/docs/release_facing_examples.md`
- `/Users/rl2025/rtdl_python_only/docs/backend_maturity.md`
- `/Users/rl2025/rtdl_python_only/docs/tutorials/README.md`
- `/Users/rl2025/rtdl_python_only/docs/features/README.md`
- `/Users/rl2025/rtdl_python_only/examples/README.md`

The update replaced stale wording that described visibility rows as CPU-only
with the current backend-dispatch boundary:

- CPU oracle: `rt.visibility_rows_cpu(...)`
- backend dispatch: `rt.visibility_rows(..., backend="embree" | "optix" |
  "vulkan" | "hiprt" | "apple_rt")`
- native early-exit: OptiX, Embree, HIPRT
- compatibility dispatch: Vulkan, Apple RT

Goal644 added and documented `rt.reduce_rows(...)` as a Python
standard-library helper over already-emitted rows. It supports `any`, `count`,
`sum`, `min`, and `max`, and the docs explicitly state that it is not a native
RT backend reduction or speedup path.

## Public Claim Boundary

Current public docs now consistently state:

- `v0.9.5` is the current public release-prepared surface.
- `v0.9.5` adds bounded any-hit and visibility rows.
- `v0.9.5` also adds `reduce_rows` for deterministic Python-side reductions
  over emitted rows.
- OptiX, Embree, and HIPRT have native any-hit implementations.
- Vulkan and Apple RT support the row contract through compatibility dispatch.
- Compatibility dispatch is real backend execution but not native early-exit
  performance evidence.
- HIPRT validation is on the Linux NVIDIA/Orochi path, not AMD GPU hardware.
- `reduce_rows` is not OptiX, Embree, Vulkan, HIPRT, or Apple RT acceleration.

## Stale-Phrase Check

Command:

```text
rg -n 'native backend-specific visibility helpers|CPU helper in `v0\.9\.5`|HIPRT, Vulkan|other backends may project' \
  README.md docs/features docs/rtdl docs/tutorials examples src/rtdsl/visibility_runtime.py
```

Result:

```text
no matches
```

Additional `reduce_rows` boundary check:

```text
rg -n 'reduce_rows.*native RT|native RT.*reduce_rows|backend reduction.*speedup' \
  README.md docs/features docs/rtdl docs/tutorials examples src/rtdsl/reduction_runtime.py
```

Result:

```text
README.md:32:engines. `reduce_rows` is a standard-library helper, not a native RT backend
examples/rtdl_reduce_rows.py:28:        "boundary": "reduce_rows is a Python standard-library helper over emitted rows; it is not a native RT backend reduction.",
```

Interpretation:

- the only matches are explicit boundary disclaimers;
- no doc claims `reduce_rows` is a native RT backend speedup path.

## Runnable Example Check

Commands:

```text
PYTHONPATH=src:. python3 examples/rtdl_ray_triangle_any_hit.py
PYTHONPATH=src:. python3 examples/rtdl_visibility_rows.py
PYTHONPATH=src:. python3 examples/rtdl_reduce_rows.py
```

Result:

- `rtdl_ray_triangle_any_hit.py` emitted matching CPU Python reference and CPU
  oracle rows with `parity: true`.
- `rtdl_visibility_rows.py` emitted the expected observer-target visibility
  rows.
- `rtdl_reduce_rows.py` emitted pose collision flags, neighbor counts, and a
  Hausdorff-style max-distance row while reporting the no-native-backend-
  reduction boundary.

Focused public-doc/example tests:

```text
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal511_feature_guide_v08_refresh_test \
  tests.goal532_v0_8_release_authorization_test \
  tests.goal645_v0_9_5_release_package_test \
  tests.goal513_public_example_smoke_test \
  tests.goal515_public_command_truth_audit_test

Ran 14 tests in 2.679s
OK
```

Public command truth audit after adding the v0.9.5 release-facing commands:

```text
PYTHONPATH=src:. python3 scripts/goal515_public_command_truth_audit.py
```

Result:

```text
valid: true
command_count: 248
public_doc_count: 14
```

Tutorial/example harness after adding `ray_triangle_any_hit` and
`visibility_rows`:

```text
PYTHONPATH=src:. python3 scripts/goal410_tutorial_example_check.py \
  --machine local-goal645 \
  --output docs/reports/goal645_tutorial_example_check_2026-04-19.json
```

Result:

```text
65 passed, 0 failed, 26 skipped, 91 total
```

## Verdict

Codex doc-refresh verdict: ACCEPT.

No public doc blocker remains for the v0.9.5 any-hit / visibility-row /
emitted-row reduction slice.

## External Review

Combined Goals 641-643 review:

- File: `/Users/rl2025/rtdl_python_only/docs/reports/goal641_643_external_review_2026-04-19.md`
- Verdict: ACCEPT.
- Original doc finding: stale visibility wording was corrected, stale-phrase grep was
  clean, runnable examples passed, and public-doc smoke tests passed.
- Superseded after Goal644 by this report's additional `reduce_rows`
  documentation, runnable example, and public-command coverage.
