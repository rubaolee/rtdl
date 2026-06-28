# Goal4795 V4 tutorial/API boundary honesty pass

Date: 2026-06-28

## Purpose

Goal4795 fixes a subtle but important user-facing boundary:

```text
In the V4 tutorial path != has a V4 operator/runtime surface.
```

The immediate trigger was the sorting tutorial. `sorting_rows.py` is a valid
RTDL kernel/relation lesson, but it does not have a V4 `sort` operator, a V4
segment-intersection operator, or a V4 prepared runtime surface. The public
materials now say this explicitly and tests enforce it.

## Files changed

| File | Action | Purpose |
| --- | --- | --- |
| `examples/tutorial_programs/sorting_rows.py` | Added explicit output fields: `lesson_layer`, `v4_operator_surface`, and `v4_runtime_claim`. | The script now machine-states that sorting is an RTDL kernel/relation lesson with no V4 operator surface. |
| `tutorials/current/03_sorting_rows.md` | Added a boundary paragraph and learning bullet. | The tutorial now says it has no V4 sorting operator surface and no V4 segment-intersection runtime surface. |
| `tutorials/current/README.md` | Added a language-layer vs V4 runtime-surface explanation. | Prevents readers from assuming every tutorial page has a V4 runtime surface. |
| `examples/tutorial_programs/README.md` | Added a language-layer vs runtime-surface explanation and updated sorting row. | Prevents the examples index from over-claiming V4 runtime support. |
| `examples/README.md` | Clarified that tutorial programs include both language-layer lessons and runtime-surface lessons. | Keeps the public examples front door honest. |
| `docs/current_v4_status.md` | Clarified that quick-check commands mix language-layer tutorials and runtime-surface checks. | Prevents status-page readers from interpreting sorting as a V4 operator claim. |
| `docs/public_documentation_map.md` | Clarified the same quick-check boundary. | Keeps first-time user navigation honest. |
| `README.md` | Added the same high-level boundary near Quick Start. | Makes the repository front page safer. |
| `tests/v4_goal4640_public_docs_cleanup_test.py` | Added `test_sorting_is_language_layer_not_v4_runtime_surface`. | Prevents regressions in public wording and script output. |

## Verified facts

Checked directly:

- `examples/tutorial_programs/sorting_rows.py` imports `rtdsl as rt`, not `rtdsl.v4`.
- It has no `--mode v4`.
- It supports RTDL backends such as `cpu_python_reference`, `cpu`, `embree`, `optix`, and `vulkan`.
- `rtdsl.v4.plan_operator_request_v4("sort", partner="rtdl_native")` reports `unsupported_no_fused_surface`.
- `rtdsl.v4.plan_operator_request_v4("segment_intersection", partner="rtdl_native")` reports `unsupported_no_fused_surface`.

The correct claim is:

```text
sorting_rows.py is a V4 tutorial-path RTDL language-layer lesson.
It is not a V4 operator/runtime-surface example.
```

## Validation

### Windows workspace

Commands:

```powershell
py -3 examples\tutorial_programs\sorting_rows.py
py -m unittest tests.v4_goal4640_public_docs_cleanup_test tests.v4_frontdoor_test tests.v4_goal4643_publication_decision_test
```

Result:

```text
Ran 22 tests in 82.827s
OK
```

The Windows Python process printed the known local prefix warning on subprocess
runs, but all commands exited successfully.

### Local Linux clean-copy simulation

Host: `192.168.1.20`

The workspace was copied to `/tmp/rtdl_goal4795_boundary_honesty` and run as a
clean user checkout with `PYTHONPATH=src:.`.

Commands:

```bash
PYTHONPATH=src:. python3 examples/tutorial_programs/sorting_rows.py >/tmp/rtdl_goal4795_sorting.json
python3 - <<'PY'
import json
p=json.load(open('/tmp/rtdl_goal4795_sorting.json'))
assert p['lesson_layer']=='rtdl_kernel_relation'
assert p['v4_operator_surface'] is None
assert 'no V4 sort' in p['v4_runtime_claim']
PY
PYTHONPATH=src:. python3 -m unittest tests.v4_goal4640_public_docs_cleanup_test tests.v4_frontdoor_test tests.v4_goal4643_publication_decision_test
```

Result:

```text
Ran 22 tests in 32.683s
OK
```

## Non-claims

This goal does not authorize:

- a V4 sorting operator claim,
- a V4 segment-intersection runtime-surface claim,
- broad V4 speedup wording,
- whole-app performance claims,
- a V4 public tag,
- Tier-3 arbitrary callback claims,
- raw OptiX callback claims,
- C ABI or embedding claims,
- paper-reproduction claims.

## Goal status

Implementation and Windows/Linux validation are complete. External review is
required before marking the goal complete.
