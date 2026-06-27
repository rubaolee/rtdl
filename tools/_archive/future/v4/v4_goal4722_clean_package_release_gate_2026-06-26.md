# V4 Goal4722 Clean Package Release Gate

Date: 2026-06-26

Status: `passed_with_review_debt`

Decision: `v4_release_candidate_local_package_gate_passed_no_final_tag`

## Purpose

Goal4722 validates that the current V4 Python eDSL/operator-pushdown release
candidate can be exercised from public no-CUDA examples, scanned for stale
current-user wording, and packaged as a Python wheel.

## Inputs

- Goal4720 machine convergence:
  `future/v4/v4_goal4720_release_candidate_guardrail_convergence_2026-06-26.md`
- Current public examples under `examples/v4/`
- Current public docs under `README.md`, `docs/`, `tutorials/current/`,
  `examples/`, `future/v4/README.md`, `future/v4/tier2_operator_catalog.md`,
  and `future/v4/v4_0_scope_gate.md`

## Commands And Results

### Public No-CUDA Examples

Command:

```powershell
py -3 examples\v4\v4_frontdoor_quickstart.py
py -3 examples\v4\operator_callback_planning.py --case tier2
py -3 examples\v4\operator_callback_planning.py --case scalar-callback
py -3 examples\v4\operator_callback_planning.py --case complex-callback
py -3 examples\v4\custom_predicate_early_exit_planning.py
```

Result: passed. The quickstart reports:

- `measured_surface_count: 10`
- `candidate_surface_count: 0`
- `catalog_operator_count: 10`
- `formal_release_authorized: false`
- `whole_app_speedup_claim_authorized: false`
- custom predicate planning reports
  `v4_ray_triangle_custom_predicate_early_exit_3d_numba` and
  `4.632757911153888x` serious-scale V4/V3.0.2 geomean.

### Current Public Wording Scan

Command:

```powershell
rg -n "bounded operator surface|bounded V4 operator|measured Tier-2 surfaces: `9`|measured Tier-2 surfaces: `8`|candidate Tier-2 surfaces: `1`|current V4 measured operator surface count is `9`|formal app-level high-performance V4 release yet|Goal4654/Goal4655|9 documented|nine measured|8 generic RT-core operators|near-OptiX performance from Python|Representative operator geomean" README.md docs/README.md docs/current_v4_status.md docs/app_level_benchmark_summary.md docs/public_documentation_map.md docs/learn/performance_wording.md tutorials/current examples/README.md examples/v4/README.md future/v4/README.md future/v4/tier2_operator_catalog.md future/v4/v4_0_scope_gate.md -g "*.md"
```

Result: no matches in the current public user path.

Note: a broad scan over all `future/v4` still finds old 8-surface wording inside
historical goal/review/design artifacts. Those are history/evidence records, not
current public front-door docs. They should not be edited retroactively because
that would corrupt the historical audit trail.

### Packaging

Initial command:

```powershell
py -m build --sdist --wheel --outdir dist/goal4722_v4_release_candidate
```

Result: local tool blocker. The current Python had no usable `build.__main__`,
`pip`, `setuptools`, or `wheel`.

Repair:

```powershell
py -m ensurepip --upgrade
```

Result: installed `pip 24.0` and `setuptools 65.5.0` for the local Python
environment.

Wheel command:

```powershell
py -m pip wheel . --no-deps -w dist/goal4722_v4_release_candidate
```

Result: passed.

Produced artifact:

- `dist/goal4722_v4_release_candidate/rtdl_source_tree-4.0.0-py3-none-any.whl`
- size: `1490853` bytes
- sha256 from pip output:
  `705b21f74a792b85bf41ca7591ecb560834b1875cc0daec7a3ec9ee4fa2c2891`

Cleanup:

- `ensurepip` temporarily wrote `scripts/pip3.exe`, `scripts/pip3.11.exe`, and
  `Lib/site-packages` into the workspace because the active Python prefix was
  the repository root.
- Those local toolchain artifacts were removed after the wheel build.
- The release artifact retained from this gate is only the wheel under
  `dist/goal4722_v4_release_candidate/`.

## Prior Validation Carried Forward

- Full V4 local suite:
  `py -m unittest discover -s tests -p "v4*_test.py"`
  - result: `435 tests OK`
- Catalog dry-run evidence:
  `future/v4/evidence/v4_goal4720_catalog_regression_gate_dry_run_2026-06-26.json`
  - result: `passed`

## Release Reading

Goal4722 supports the current V4 release-candidate state:

- package build works as a wheel;
- public no-CUDA examples are runnable;
- current public docs do not contain stale 8/9-surface release wording;
- the machine state remains release-candidate, not final public tag.

## Remaining Blocker

Final public tag is still blocked by external 3-AI review debt:

- `future/v4/reviews/v4_goal4720_release_candidate_guardrail_convergence_review_debt_2026-06-26.md`

## Non-Authorization

Goal4722 does not authorize broad V4 speedup wording, whole-application
speedups, all-benchmark speedups, public true-zero-copy claims, arbitrary
callbacks, raw OptiX callbacks, blanket CuPy performance claims, C ABI,
embedding, non-Python host bindings, app-specific native kernels, or final tag
without external review debt closure.

## Goal-Level Decision Audit

1. Was I being stupid?
   No. The action moved a concrete release blocker: packaging and public
   no-CUDA example validation.

2. If yes, what action made the decision stupid?
   Not applicable. The risky mistake would have been treating missing local
   packaging tools as a package failure or ignoring the packaging gate.

3. Is there another path that avoids getting stuck on a bad premise?
   Yes. Use `ensurepip` to repair the local Python toolchain, then build the
   wheel through `pip wheel` instead of pretending `py -m build` worked.

4. Can I now try the different path that actually solves the problem?
   Yes. The wheel exists and the next real blocker is review debt/final tag
   decision, not local packaging.
