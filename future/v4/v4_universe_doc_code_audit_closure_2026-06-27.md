# V4 Universe Documentation And Code Audit Closure

Date: 2026-06-27

Status: `public_surface_clean__tracked_v4_code_gates_pass__strict_release_blocked_by_local_debris`

## Scope

This audit treats V4.0.0 as the current user-facing release. The release tree is
partitioned as:

- `public_current`: root README, `docs/`, `tutorials/current/`, and
  `examples/v4/`;
- `current_code_or_gate`: `src/rtdsl/`, V4 scripts, tests, and benchmark-app
  source;
- `audit_provenance`: `future/`;
- `history_archive`: `history/`;
- local untracked debris: build output, raw evidence, local external checkout,
  and working review records.

After this cleanup pass, untracked V3/Phoenix helper scripts, old local tests,
paper-reproduction patches, and the local review helper were moved out of the
current `scripts/`, `tests/`, and `tools/` front door into
`history/local_workspace_debris_2026-06-27/payload/`. The payload is ignored by
Git; the tracked README documents why it exists and why it is not part of the
V4 user path.

## Files And Gates Added

- `scripts/v4_universe_audit.py`
- `tests/v4_universe_audit_test.py`
- `future/v4/v4_universe_audit_snapshot_2026-06-27.md`

The gate scans the current public surface for internal process leakage, old
current-version wording, and misleading user-path language. It also records the
tracked file buckets, classifies untracked workspace debris, and now supports a
strict release mode:

```powershell
py -3 scripts\v4_universe_audit.py --format json --strict-release
```

Strict mode fails if any local untracked debris remains. This prevents a future
agent from saying "public clean" when the intended operation is actually
"release from a clean tree."

## Findings

Public surface:

- public current files scanned: `31`;
- public findings: `0`;
- tracked files still under `docs/reviews/`: `0`;
- missing required public files: `0`;
- missing required history directories: `0`.

Tracked repository:

- tracked files: `27673`;
- history archive files: `22046`;
- audit provenance files: `1171`;
- current code/gate files: `4356`;
- public current files: `31`.

Local workspace debris:

- untracked files: `671`;
- unknown untracked files: `0`;
- all untracked files are classified as known local debris: raw V4 evidence,
  local V4 review working records, local build output, and an external
  author-code checkout.

This means the tracked V4 public release surface is clean, but the local
workspace is still intentionally not a clean-room checkout. Normal audit mode
passes for public-surface truth; strict release mode fails until these 671
remaining local files are removed, archived, or intentionally excluded by a
separate release-packaging decision.

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
status: fail_local_debris
untracked files: 671
unknown untracked files: 0
```

Public-current stale/process leakage scan:

```powershell
rg -n "Goal[0-9]+|goal[0-9]+|v4_goal|review debt|Claude|Gemini|Antigravity|release candidate|parity/control|docs/reviews|future/v4/reviews|external review|bounded framing|choose V2|choose V3|current V3|V4/V3/V2" README.md docs tutorials examples\v4 future\v4\README.md future\v4\tier2_operator_catalog.md future\v4\examples\v4_frontdoor_quickstart.py future\v4\examples\operator_callback_planning.py
```

Result: no matches.

Focused public cleanup gate:

```powershell
$env:PYTHONPATH='src;.;scripts'
py -3 -m unittest tests.v4_universe_audit_test tests.v4_goal4640_public_docs_cleanup_test
```

Result:

```text
Ran 9 tests in 9.401s
OK
```

Full V4 discovery gate:

```powershell
$env:PYTHONPATH='src;.'
py -3 -m unittest discover -s tests -p "v4*_test.py"
```

Result:

```text
Ran 649 tests in 95.481s
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

The remaining issue is local workspace hygiene, not tracked V4 public-surface
truth:

- raw evidence and local review records should stay out of the user path;
- V3/Phoenix local scripts/tests have been moved under
  `history/local_workspace_debris_2026-06-27/payload/`;
- `dist/` and `external/` should not be included in V4 release commits.

## Goal-Level Decision Audit

1. Was I foolish?
   - The earlier foolish path would be to claim "everything is clean" while
     ignoring hundreds of untracked local files.

2. What action would make this foolish?
   - Staging raw evidence, external checkouts, V3/Phoenix local debris, or
     review working files into the V4 user-facing release.

3. Is there another path?
   - Yes: classify current public files, audit/history files, current code
     gates, and local debris separately; then gate the public surface and
     document the remaining local debris honestly.

4. Can I now take the path that solves the problem?
   - Yes. The tracked V4 public surface is clean and gated. Strict release mode
     now blocks a final clean-tree release while local debris remains, so the
     next cleanup is a deliberate local-debris/archive decision, not a
     release-claim shortcut.
