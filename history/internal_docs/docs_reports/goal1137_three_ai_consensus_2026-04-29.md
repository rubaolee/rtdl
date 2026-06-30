# Goal1137 Three-AI Consensus

Date: 2026-04-29

## Scope

Goal1137 fixes the recurring cloud-pod failure where strict reference paths
fail after OptiX bootstrap because the pod lacks GEOS C:

```text
cannot find -lgeos_c
```

Changed files:

- `scripts/goal763_rtx_cloud_bootstrap_check.py`
- `docs/rtx_cloud_single_session_runbook.md`
- `tests/goal763_rtx_cloud_bootstrap_check_test.py`
- `tests/goal829_rtx_cloud_single_session_runbook_test.py`
- `docs/reports/goal1137_cloud_geos_bootstrap_preflight_2026-04-29.md`

## Verdict

ACCEPT.

## Codex Review

The bootstrap now emits GEOS/pkg-config metadata and treats missing
`pkg-config`, missing GEOS pkg-config metadata, or missing `libgeos_c` as
non-dry-run preflight blockers. This moves a recurring paid-pod failure from
mid-workload execution into the bootstrap phase.

The runbook now requires:

```bash
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y libgeos-dev pkg-config
```

before `goal763_rtx_cloud_bootstrap_check.py`.

No benchmark, release, or public RTX speedup claim is introduced.

## Claude Review

Claude verdict: ACCEPT.

Saved report:

- `docs/reports/goal1137_claude_review_2026-04-29.md`

Claude found the implementation correctly checks `pkg-config`, `pkg-config
--libs geos/geos_c`, and `ctypes.util.find_library("geos_c")`; places the
runbook install step before bootstrap; and preserves the no-claim boundary.

## Gemini Review

Gemini verdict: ACCEPT.

Saved report:

- `docs/reports/goal1137_gemini_review_2026-04-29.md`

Gemini found the implementation correctly prevents the recurring missing-GEOS
pod failure, aligns documentation, and avoids benchmark/release overclaiming.

## Verification

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal763_rtx_cloud_bootstrap_check_test \
  tests.goal829_rtx_cloud_single_session_runbook_test -v
```

Result: 11 tests OK.

Additional dry-run:

```bash
PYTHONPATH=src:. python3 scripts/goal763_rtx_cloud_bootstrap_check.py \
  --dry-run --skip-build --skip-tests \
  --output-json /tmp/goal763_dry_run_geos.json
```

Result: status `ok`; GEOS preflight metadata emitted.

## Closure

Goal1137 is closed with 3-AI consensus: Codex, Claude, and Gemini. This closure
is limited to cloud bootstrap reliability and does not authorize public RTX
speedup wording or release.
