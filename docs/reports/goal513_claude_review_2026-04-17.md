# Goal 513 External Review — Claude Sonnet 4.6

Date: 2026-04-17

Reviewer: Claude Sonnet 4.6 (external AI review)

## Verdict: PASS

Goal513 correctly adds a public example smoke gate without changing released public example output contracts.

## Evidence

**Scope is correct.** The test covers all 13 examples listed in the scope section and runs them as subprocesses with `PYTHONPATH=src:.`, matching the documented local usage pattern.

**Output contracts are preserved.** The check `"app" in payload or "rows" in payload` deliberately accepts both v0.7-style (`rows`) and v0.8-style (`app`) output, explicitly avoiding the contract change of forcing older examples to add an `app` field. This is the right design.

**v0.8-specific checks are appropriate.** `hausdorff["matches_oracle"]`, `robot["matches_oracle"]`, `barnes["boundary"]`, and `"candidate_row_count" in barnes` are all gating on fields that these examples already emit; the test observes them, it does not introduce them.

**Feature cookbook check is sound.** `feature_count >= 19` is a floor (not an exact match), so adding future recipes does not break the gate.

**SubTest isolation is correct.** Using `self.subTest(example=args[0])` inside the loop means one failing example does not suppress failures from the others.

## One Technical Concern (non-blocking)

`run_example` sets `env={"PYTHONPATH": "src:."}`, which **replaces** the entire OS environment rather than augmenting it. If any example or transitive import depends on `PATH`, `HOME`, `TMPDIR`, or other ambient variables, the subprocess will fail on some platforms. The safer pattern is `env={**os.environ, "PYTHONPATH": "src:."}`. Since the examples are pure-Python and use `sys.executable` (absolute path) this is unlikely to trigger in the current suite, but it is a latent fragility.

This does not affect the contract-preservation question, so it is not a blocking concern for Goal513's stated goal.

## Summary

The gate design is correct: it catches stale commands and broken output formats without tightening any existing JSON contract. The validation evidence (6 tests, OK) is consistent with the implementation. Goal513 is ready to be called closed subject to the team's acceptance of the non-blocking env-replacement note.
