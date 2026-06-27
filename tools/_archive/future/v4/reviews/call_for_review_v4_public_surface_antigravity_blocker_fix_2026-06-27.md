# Call For Review: V4 Public Surface Antigravity Blocker Fix

Date: 2026-06-27

Requested reviewer: Antigravity

Requested verdict labels:

- `approve_antigravity_public_surface_blockers_closed`
- `approve_with_required_fixes`
- `block_public_surface_until_fixed`

## Context

Please review the blocker-fix response to your prior review:

- prior request:
  `future/v4/reviews/call_for_review_v4_public_surface_api_docs_packaging_hardening_2026-06-27.md`
- your prior review:
  `future/v4/reviews/antigravity_v4_public_surface_hardening_review_2026-06-27.md`
- prior verdict: `block_public_surface_until_fixed`
- fix commit: `12a53df01055 Fix V4 public API and recipe review blockers`
- branch: `codex/v4-tier2-section8`

Your previous review named two blocking issues:

1. **P0 IDE/static-analysis pollution**: `src/rtdsl/v4.py` still imported many
   internal `v4_goal...` modules, so IDEs could expose maintainer/release-process
   symbols even if `__all__` and `dir()` looked clean.
2. **P1 fake tutorial**: `examples/v4/benchmark_app_recipes.py` was a JSON
   dumper, not idiomatic human-facing tutorial code.

This request asks only whether those blockers are now truly fixed. It does not
ask for broader V4 performance authorization.

## Fixes To Inspect

### 1. Public API module split

Files:

- `src/rtdsl/v4.py`
- `src/rtdsl/v4_maintainer.py`

Expected state:

- `src/rtdsl/v4.py` is now a public-only V4 API module.
- `src/rtdsl/v4.py` should contain no `from .v4_goal...` imports.
- `src/rtdsl/v4.py` should contain no `V4_GOAL`, `v4_goal`, numbered goal,
  review, audit, or maintainer-module markers.
- `src/rtdsl/v4.py` should not import `src/rtdsl/v4_maintainer.py`.
- `src/rtdsl/v4_maintainer.py` preserves the old internal compatibility exports
  for maintainer tests and evidence gates.
- Existing internal tests that need goal/protocol symbols now import
  `rtdsl.v4_maintainer as v4`.

The intended architecture is:

- users and IDEs inspect/import `rtdsl.v4`;
- maintainers who need old internal goal/protocol compatibility opt into
  `rtdsl.v4_maintainer`;
- runtime hiding tricks are no longer the safety mechanism.

### 2. Human-facing benchmark-app recipe

File:

- `examples/v4/benchmark_app_recipes.py`

Expected state:

- It no longer imports `json`.
- It no longer calls `json.dumps`.
- It defines small typed recipe objects and app-specific builder functions.
- It calls `rt.plan_operator_request_v4(...)` in code paths that resemble how a
  user chooses V4 operators.
- It prints human-readable steps for all 10 benchmark apps:
  RTDBSCAN, RTNN, Triangle counting, Robot collision, RayDB-style, LibRTS
  spatial index, Contact manifold, Spatial RayJoin, Barnes-Hut, and Hausdorff
  XHD.
- It is acceptable as a clean learning bridge, while the large benchmark harness
  remains maintainer machinery.

### 3. Non-public Tier-3 candidate example

File:

- `future/v4/examples/v4_specialized_tier3_scalar_callback_candidate_example.py`

Expected state:

- This is not a public V4 API example.
- It now imports its internal planner from `rtdsl.v4_maintainer`, not
  `rtdsl.v4`.

### 4. Regression gates

File:

- `tests/v4_goal4640_public_docs_cleanup_test.py`

Expected state:

- The public cleanup gate now reads `src/rtdsl/v4.py` source text directly and
  fails if `from .v4_goal`, `V4_GOAL`, `v4_goal`, or `Goal` reappears.
- The public cleanup gate executes `examples/v4/benchmark_app_recipes.py` as a
  human-readable planner example, not as JSON.
- The gate still executes public examples, tutorial snippets, link checks, and
  public API checks.

Closure record:

- `future/v4/v4_universe_doc_code_audit_closure_2026-06-27.md`

## Verification Already Run After The Fix

Full V4 discovery:

```powershell
$env:PYTHONPATH='src;.'
py -3 -m unittest discover -s tests -p "v4*_test.py"
```

Result:

```text
Ran 656 tests in 115.460s
OK (skipped=1)
```

Focused public/staging gate:

```powershell
$env:PYTHONPATH='src;.'
py -3 -m unittest tests.v4_universe_audit_test tests.v4_goal4640_public_docs_cleanup_test tests.v4_frontdoor_test tests.v4_goal4775_release_staging_manifest_test
```

Result:

```text
Ran 25 tests in 33.834s
OK
```

Strict release audit:

```powershell
$env:PYTHONPATH='src;.;scripts'
py -3 scripts\v4_universe_audit.py --format json --strict-release
```

Result:

```text
status: pass
public_findings: []
unknown_untracked_count: 0
untracked_file_count: 0
```

Syntax audit:

```powershell
$env:PYTHONPATH='src;.'
py -3 -m compileall -q src examples\v4 future\v4\examples scripts tests
```

Result: exit code `0`.

Diff hygiene:

```powershell
git diff --cached --check
```

Result: exit code `0` before commit.

## Required Questions

Please answer each question explicitly:

1. Does `src/rtdsl/v4.py` now pass the static-analysis/IDE cleanliness standard
   you required?
2. Is `src/rtdsl/v4_maintainer.py` an acceptable place for the internal
   maintainer compatibility surface?
3. Does the split avoid using `__all__`/`dir()` as the primary protection
   mechanism?
4. Is `examples/v4/benchmark_app_recipes.py` now a genuine human-facing
   learning bridge rather than a CI JSON payload?
5. Are the new/updated gates sufficient to prevent the same public API/tutorial
   regression?
6. Do you authorize closing your prior
   `block_public_surface_until_fixed` verdict for the two named blockers?
7. If not, list the exact remaining P0/P1 file-level fixes required.

## Non-Authorization

This review must not authorize:

- broad V4-over-V2.14 or V4-over-V3 speedup wording;
- whole-app high-performance wording across all benchmark apps;
- Tier-3 arbitrary callback support;
- raw OptiX callback support;
- C ABI, embedding, or non-Python host claims;
- true external zero-copy claims;
- Barnes-Hut paper-reproduction expanded claims;
- app-identity native kernels.

The only requested decision is whether the two Antigravity public-surface
blockers are now fixed and whether the V4.0 public docs/API/examples surface may
continue toward final release closure.

## Short Forwarding Message

Please review this blocker-fix packet:

`future/v4/reviews/call_for_review_v4_public_surface_antigravity_blocker_fix_2026-06-27.md`

It responds directly to your prior `block_public_surface_until_fixed` verdict.
Please check only the two named blockers: static/IDE pollution in `rtdsl.v4` and
the fake JSON tutorial issue in `benchmark_app_recipes.py`. The fix commit is
`12a53df01055`. Please return one of:
`approve_antigravity_public_surface_blockers_closed`,
`approve_with_required_fixes`, or `block_public_surface_until_fixed`.
