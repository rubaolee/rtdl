# Goal4272 Current Examples Path Migration

Date: 2026-06-10

Status: complete locally with validation passing

## Purpose

The learner-facing examples tree still lived at `examples/v2_0/` even though
the current public surface is v2.10. That made the GitHub directory view look
old and implied that current examples were frozen at v2.0. This goal makes the
canonical examples tree version-neutral:

```text
examples/current/
```

Historical version evidence remains in reports, reviews, handoffs, history,
and release notes. It is no longer the first-run examples path.

## Operations

| Area | Finding | Operation | Result |
| --- | --- | --- | --- |
| Top-level examples tree | The real tracked learner tree was `examples/v2_0/`. | Renamed the tracked tree with `git mv examples/v2_0 examples/current`. | GitHub now shows `examples/current/` as the current learner path; no `examples/v2_0/` directory remains. |
| Examples index | `examples/README.md` told users to start in `v2_0/` and described it as a compatibility path. | Rewrote the index around `current/` and removed the compatibility-path framing. | New users see a current path, not an old version number. |
| Current examples README | The moved tree README still explained why `v2_0/` was retained. | Reframed it as the v2.10 current examples tree. | The first file inside the examples tree now matches the new directory name. |
| Current docs and tutorials | Current docs linked to `examples/v2_0/...`. | Mechanically updated current-facing docs to `examples/current/...`, excluding reports/reviews/handoffs/history/release reports. | Learner docs now point to the current path. |
| Python imports | Example modules, tests, scripts, and helper code imported `examples.v2_0.*`. | Mechanically updated current code references to `examples.current.*`. | Import paths match the moved package tree. |
| Executable runners | Two shell pod runners still invoked `examples/v2_0/...` scripts directly. | Updated those shell command paths to `examples/current/...`. | Current executable helpers no longer depend on the removed directory. |
| Benchmark registries | Current benchmark front doors and scale profiles used old example script paths. | Updated command paths to `examples/current/...`. | Registry commands resolve against the current examples tree. |
| Compatibility aliases | `examples/__init__.py` aliased old `examples.v2_0` modules. | Updated aliases to `examples.current.*`. | Legacy `from examples import ...` still works without teaching the old namespace. |
| Regression guard | The v2.10 doc cleanup test scanned `examples/v2_0`. | Updated it to scan `examples/current` and ban old example path tokens. | Existing doc guard now protects the current examples tree. |
| New guard | No focused test proved the version-named examples tree was gone. | Added `tests.goal4272_current_examples_canonical_path_test`. | The test fails if `examples/v2_0` returns, if current docs point to it, or if current benchmark command paths break. |

## Current Boundaries

- This goal is a repository hygiene and learner-surface cleanup.
- It does not change RTDL runtime semantics, native engine ABI, benchmark
  claims, release authorization, or partner support.
- Historical files under `docs/reports/`, `docs/reviews/`, `docs/handoff/`,
  `docs/history/`, and `docs/release_reports/` may still mention old paths as
  historical evidence.

## Validation

Validation run on Windows from the repository root:

| Command | Result |
| --- | --- |
| `rg -n "examples\\.v2_0\|examples/v2_0\|examples\\\\v2_0" README.md docs examples scripts tests src -g "*.md" -g "*.py" -g "*.json" -g "!docs/reports/**" -g "!docs/reviews/**" -g "!docs/handoff/**" -g "!docs/history/**" -g "!docs/release_reports/**"` | no matches |
| `$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal4271_v2_10_user_doc_cleanup_test tests.goal4272_current_examples_canonical_path_test` | 7 tests OK |
| `$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3056_v2_6_pre_release_public_doc_cleanup_audit_test tests.goal4248_current_public_docs_claim_boundary_scan_test tests.goal4271_v2_10_user_doc_cleanup_test tests.goal4272_current_examples_canonical_path_test` | 16 tests OK |
| `$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal513_public_example_smoke_test tests.goal514_tutorial_example_harness_refresh_test tests.goal1765_github_learner_readiness_double_check_test` | 9 tests OK |
| `$env:PYTHONPATH='src;.'; py -3 -m compileall -q examples/current` | OK |
| `$env:PYTHONPATH='src;.'; py -3 examples/current/getting_started/rtdl_hello_world.py` | printed `hello, world` |
