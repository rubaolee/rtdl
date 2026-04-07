# Codex Consensus: Goal 135 System Midterm Check

## Verdict

Keep.

## Findings

- The Goal 135 package answers the right midterm question: not whether the
  archived v0.1 package was good, but whether current `main` behaves like one
  coherent system.
- The audit found one real integration regression:
  `tests/baseline_integration_test.py` omitted
  `segment_polygon_anyhit_rows` from its representative kernel map. That issue
  was repaired and the clean Linux `full` matrix then passed.
- The Linux evidence is the most important result:
  - clean checkout at `68075bab222877b6f3dd3635e1bbe06015d67cae`
  - `v0_2_full`: `36 tests`, `OK`, `3 skipped`
  - `full`: `281 tests`, `OK`, `2 skipped`
- The macOS evidence is also useful and should remain explicit:
  - local compileall is clean
  - local `v0_2_local`, `integration`, and `system` groups are green
  - the broad `unit` group is not green because local `geos_c` linkage is
    missing
- The documentation consistency finding is correct. Before this goal,
  `README.md` and `docs/README.md` undersold the live branch state by staying
  too centered on the archived v0.1 story. The front-door updates are justified
  and appropriately modest.

## Review status

- Gemini review: completed and saved
- Claude review: handoff prepared, but no usable artifact was returned through
  the current non-interactive subprocess path

## Summary

Goal 135 is a valid whole-system midterm check. The most important result is
that current `main` is green as a whole system on the accepted Linux primary
platform after one real integration fix, while the local Mac remains an
explicitly limited support platform rather than a whole-system release target.
