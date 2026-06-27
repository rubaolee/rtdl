# Claude Review: Phoenix V3 M4 Binding Venv Amendment

Date: 2026-06-20

Scope: external review of the execution amendment to use the rebuild venv
instead of pod system `python3`.

## Context

During pod preflight, system `python3` failed the GPU partner gate because CuPy
and Numba were missing. The existing rebuild venv at
`/root/rtdl_v3_rebuild_20260620/.venv/bin/python` passed the same gate with:

- `cupy-cuda12x==14.1.1`
- `numba==0.65.1`
- `torch==2.6.0+cu124`

Codex amended the M4 packet so all focused tests and measurements use the venv
interpreter explicitly.

## Verdict

VERDICT: ACCEPT_WITH_REQUIRED_AMENDMENTS

## Required Amendments

- Record the exact interpreter path and package versions directly in the M4
  packet as the binding execution environment.
- Reverify GPU partner, source identity, and claim-boundary checks against this
  exact venv path on the pod before running measurements.
- Add a note that system `python3` failed because CuPy/Numba were missing, which
  is an environment/packaging gap rather than a V3 M4 code-path failure.
- Confirm no other gate or test in the packet implicitly invokes plain
  `python3`/`python`.

## Risk Notes

- A pre-existing venv can drift if recreated or modified, so the packet must
  treat it as a versioned binding environment and re-record versions.
- If the user-facing standard path depends on system Python, the missing
  CuPy/Numba state remains a packaging gap to fix later, not something this M4
  rerun closes.

## Codex Follow-Up

Codex applied the required amendments to:

- `docs/rebuild/v3/phoenix_v3_m4_grouped_continuation_rerun_packet_2026-06-20.json`
- `docs/rebuild/v3/phoenix_v3_m4_grouped_continuation_rerun_packet_2026-06-20.md`
- `tests/v3_phoenix_m4_grouped_continuation_packet_test.py`

The packet now records the binding venv path, package versions, the system
`python3` failure reason, and the rule that focused tests and measurements must
use the venv. A local search found no plain `python3` in the M4 focused test or
measurement commands; the relevant Python subprocess paths use `sys.executable`.

