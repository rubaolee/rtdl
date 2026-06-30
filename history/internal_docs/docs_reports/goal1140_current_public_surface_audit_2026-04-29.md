# Goal1140 Current Public Surface Audit

Date: 2026-04-29

## Scope

Audit the current public-facing RTDL surface after the Goal1135-Goal1139 RTX
artifact, status-sync, GEOS-preflight, and consensus-audit work.

This audit checks docs and commands only. It does not run cloud, tag a release,
authorize public RTX speedup claims, or broaden any whole-app acceleration
claim.

## Checks Run

| Check | Result | Notes |
| --- | --- | --- |
| Goal1020 public docs RTX boundary audit | `valid: true` | 7/7 release-facing docs contain required RTX claim-boundary wording. |
| Goal1024 final public surface audit | `valid: true` | Historical Goal1024 audit still passes; its recorded full-suite count is historical, not a new current full-suite run. |
| Goal497 public entry smoke check | `valid: true` | Public docs link/phrase checks passed and smoke commands executed successfully. |
| Goal515 public command truth audit | `valid: true` | 296 public commands across 15 docs are classified and mechanically covered. |
| Focused public docs unittest suite | `OK` | 12 focused tests passed. |

## Focused Test Command

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal512_public_doc_smoke_audit_test \
  tests.goal1010_public_rtx_readme_wording_test \
  tests.goal1020_public_docs_rtx_boundary_audit_test \
  tests.goal1024_final_public_surface_audit_test \
  tests.goal515_public_command_truth_audit_test -v
```

Result:

```text
Ran 12 tests in 0.201s

OK
```

## Current Findings

- The public docs preserve the RT-core claim boundary: `--backend optix` is not
  an automatic NVIDIA RT-core speedup claim.
- The v1.0 RTX status page and app-engine support matrix now include the newer
  Goal1135/Goal1136 changed-path RTX A5000 evidence.
- The command-truth audit sees 296 public commands across 15 public docs and
  reports `valid: true`.
- No public docs audit in this pass authorized release, new public speedup
  wording, or broad whole-app acceleration claims.

## Boundary

Goal1140 is a local public-surface audit. It does not replace cloud validation,
release-level full-test execution, or public speedup wording review.

## Codex Verdict

`ACCEPT`.

The current public surface is internally consistent for the audited docs and
commands, and the latest RTX evidence is visible without weakening claim
boundaries.
