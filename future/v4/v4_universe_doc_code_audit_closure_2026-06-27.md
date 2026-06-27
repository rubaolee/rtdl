# V4 Universe Documentation And Code Closure

Date: 2026-06-27

Status: `public_surface_clean__tracked_v4_code_gates_pass__strict_release_gate_passes`

## Scope

This pass treats V4.0.0 as the current user-facing release. The release tree is
partitioned as:

- `public_current`: root README, `docs/`, `tutorials/current/`, `examples/v4/`,
  and the benchmark-harness README;
- `current_code_or_gate`: `src/rtdsl/`, V4 scripts, tests, and benchmark-app
  source;
- `maintainer_provenance`: `future/`;
- `history_archive`: `history/`;
- local untracked debris: build output, raw evidence, local external checkout,
  and maintainer working records.

After this cleanup pass, old V3/Phoenix helpers, old local tests, external
checkouts, paper-reproduction patches, and local helper scripts were moved out
of the current tree into `history/local_workspace_debris_2026-06-27/payload/`.
The payload is ignored by Git; the tracked README documents why it exists and
why it is not part of the V4 user path.

The first sweep also revealed a real clean-checkout issue: the V4 verification
suite depended on review/evidence/package artifacts that had only existed as
untracked local files. Those artifacts were restored to their original
  `future/v4/` and `dist/` locations and staged as release provenance so a clean
checkout can run the same gates without relying on local-only files.

## Files And Gates Added

- `scripts/v4_universe_audit.py`
- `tests/v4_universe_audit_test.py`
- `future/v4/v4_universe_audit_snapshot_2026-06-27.md`

The gate scans the current public surface for internal process leakage, old
current-version wording, reviewer/audit wording, and misleading user-path
language. It also records the
tracked file buckets, classifies untracked workspace debris, and now supports a
strict release mode:

```powershell
py -3 scripts\v4_universe_audit.py --format json --strict-release
```

Strict mode fails if any local untracked debris remains. This prevents a future
agent from saying "public clean" when the intended operation is actually
"release from a clean tree." It now passes on this workspace after the local
debris archive sweep.

## Findings

Public surface:

- public current files scanned: `33`;
- public findings: `0`;
- tracked files still under `docs/reviews/`: `0`;
- missing required public files: `0`;
- missing required history directories: `0`.

Tracked repository:

- tracked files: `28344`;
- history archive files: `22046`;
- maintainer provenance files: `1839`;
- current code/gate files: `4355`;
- public current files: `33`.

Local workspace debris:

- untracked files: `0`;
- unknown untracked files: `0`;
- all Git-visible local debris has either been staged as release
  provenance or moved to ignored history payload storage.

This means the tracked V4 public release surface is clean, and strict release
mode also passes because no untracked local debris remains in the Git-visible
workspace. The ignored history payload remains available locally for forensic
recovery, but it is outside the release commit surface; test-contract
  evidence/package artifacts required by tests remain visible and staged as
  provenance.

## Verification Commands

Universe/public-surface gate:

```powershell
$env:PYTHONPATH='src;.;scripts'
py -3 -m unittest tests.v4_universe_audit_test
```

Result:

```text
Ran 2 tests in 3.076s
OK
```

Strict release debris gate:

```powershell
py -3 scripts\v4_universe_audit.py --format json --strict-release
```

Result:

```text
status: pass
untracked files: 0
unknown untracked files: 0
```

Public-current stale/process leakage scan:

```powershell
rg -n "Goal[0-9]+|goal[0-9]+|v4_goal|review debt|Claude|Gemini|Antigravity|release candidate|parity/control|docs/reviews|future/v4/reviews|external review|bounded framing|choose V2|choose V3|current V3|V4/V3/V2|\baudit\b|\breviewer\b|release-review" README.md docs tutorials examples\v4 future\v4\README.md future\v4\tier2_operator_catalog.md future\v4\examples\v4_frontdoor_quickstart.py future\v4\examples\operator_callback_planning.py
```

Result: no matches.

Focused public cleanup gate:

```powershell
$env:PYTHONPATH='src;.'
py -3 -m unittest tests.v4_universe_audit_test tests.v4_goal4640_public_docs_cleanup_test tests.v4_frontdoor_test tests.v4_goal4775_release_staging_manifest_test
```

Result:

```text
Ran 19 tests in 12.500s
OK
```

This gate now executes every public `examples/v4` command in dry-run or
planner mode, including the 10-app benchmark recipe planner, fixed-radius,
closest-hit grouped argmin, ray/triangle any-hit flags, primitive grouped-i64
reduction, point-group nearest witness, ray/triangle weighted sum, AABB
all-ops count, callback planning, and the custom predicate early-exit planner.
It also executes every Python snippet in `tutorials/current/` as a standalone
copy-paste block and verifies that the benchmark-app tutorial plus recipe
planner cover all 10 promoted apps.

The complete benchmark-app harness under `examples/current/research_benchmarks/`
is now presented as a maintainer matrix harness, not the first teaching surface.
The clean user learning path is `examples/v4/benchmark_app_recipes.py` plus the
current tutorial. The harness README is scanned as public current documentation;
the large harness source files remain compatibility and measurement backends.

The `rtdsl.v4` star-import surface is now constrained by
`PUBLIC_API_SYMBOLS_V4`. Maintainer goal/protocol symbols remain reachable by
direct name for existing internal gates, but they are no longer exported through
`rtdsl.v4.__all__` or shown by `dir(rtdsl.v4)`. The public cleanup gate rejects
any future `goal####`/audit/review symbol that re-enters the public star-import
or interactive API.

Full V4 discovery gate:

```powershell
$env:PYTHONPATH='src;.'
py -3 -m unittest discover -s tests -p "v4*_test.py"
```

Result:

```text
Ran 653 tests in 120.864s
OK (skipped=1)
```

Python syntax audit for current V4 scope:

```powershell
$env:PYTHONPATH='src;.;scripts'
py -3 -m compileall -q src examples\v4 scripts tests\v4_universe_audit_test.py tests\v4_goal4640_public_docs_cleanup_test.py tests\v4_frontdoor_test.py tests\v4_operator_catalog_test.py
```

Result: exit code `0`.

Benchmark-app source syntax audit:

```powershell
$env:PYTHONPATH='src;.'
py -3 -m compileall -q examples\current\research_benchmarks
```

Result: exit code `0`.

## Remaining Work

The remaining issue is release discipline, not local workspace hygiene:

- ignored history payload must stay out of V4 release commits;
- future evidence, review records, and package artifacts that tests or release
  ledgers require must be tracked as provenance, not left as local ghosts;
- future raw evidence, build outputs, external checkouts, and working review
  records that are not part of any test/release contract should be moved to
  payload or intentionally summarized into compact tracked provenance before
  final tagging;
- user-facing V4 docs and examples must continue to pass the public-surface
  leakage scan.

## Goal-Level Decision Audit

1. Was I foolish?
   - The earlier foolish path would be to claim "everything is clean" while
     ignoring hundreds of untracked local files. That path is now closed by
     strict release mode.

2. What action would make this foolish?
   - Staging raw evidence, external checkouts, V3/Phoenix local debris, review
     working files, or ignored history payload into the V4 user-facing release.

3. Is there another path?
   - Yes: classify current public files, audit/history files, current code
     gates, and local debris separately; then gate the public surface and
     document the remaining local debris honestly.

4. Can I now take the path that solves the problem?
   - Yes. The tracked V4 public surface is clean and gated. Strict release mode
     now also passes, so future work must preserve this boundary rather than
     reintroducing local debris into the current user path.
