# V3 GitHub Release-Surface Audit — 2026-08-10

## Verdict

The scoped GitHub release surface passed its publication audit. It contains the V3
compiler/runtime changes, nine application adapters, required examples, a
compact self-contained test surface, reference documentation, a runnable
tutorial, and the release audit command.  It does not include private cache
state, prebuilt native binaries, or the historical experiment archive.

After this audit, the source version and public documentation were promoted to
RTDL 3.0.0. The release remains a scoped research compiler/runtime release, not
a universal performance claim.

## Cleanup

- Work was isolated in `rtdl_v3_functional_rc_release`; the dirty research
  workspace was not staged or modified by release cleanup.
- The exact Goal5747 base source archive was used as the implementation source.
- The public branch was rebuilt directly on `origin/main`; the private research
  checkpoint was removed from the branch ancestry rather than merely hidden by
  a later cleanup commit.
- The final diff contains 147 implementation, application, fixture, test,
  documentation, tutorial, and build files.  It adds or modifies zero paths
  under `history/`, `memory/`, or `research/`, and zero paper-result files.
- Two small frozen RTNN coordinate fixtures are retained because the selected
  non-Arkade second-consumer test reads those exact inputs.
- Line-ending-only Windows changes were discarded rather than committed.
- Historical tests that require omitted internal evidence were not presented as
  portable product tests.

## Documentation and tutorial

Added:

- V3 overview and claim boundary;
- statement-to-provider architecture;
- correctness and extension model;
- nine-application support matrix;
- V3 release installation and frozen identities;
- a runnable canonical-lowering tutorial and example.

The tutorial example resolves the L-infinity metric-kNN statement to the
source-bound OptiX provider without executing it.  It explicitly shows that
cost input was not used and that a behavioral traversal receipt is still
required.

## Mechanical audit

`PYTHONPATH=src:. python scripts/audit_v3_release_surface.py` passed with:

```text
semantic statements:       22
canonical bindings:        40
standalone providers:      10
canonical pair duplicates: 0
documentation links:       all resolved
nine app directories:      all present
tutorial example:          passed
```

The following self-contained unit-test selection passed 57/57 after the
version-consistency release gate was added:

```text
tests.v3_release_surface_test
tests.goal5731_common_action_production_frontdoor_test
tests.goal5738_fork_clean_action_target_probe_test
tests.goal5740_fast_fork_clean_optix_target_probe_test
tests.goal5745_generic_metric_knn_test
tests.goal5745_rtnn_second_consumer_test
tests.goal5019_native_lexsort_bridge_test
tests.goal5033_descriptor_consumer_native_lexsort_test
tests.goal5045_public_device_order_by_contract_test
tests.goal5066_aggregate_hierarchy_contract_test
```

Additional checks:

- `compileall` passed for `src/rtdsl`, Arkade, Triangle Counting, the tutorial
  example, and the audit script;
- `git diff --cached --check` passed;
- staged secret scan found no private-key, GitHub-token, or OpenAI-key pattern;
- no `.codex`, `.claude`, `__pycache__`, `.pyc`, or `.pyo` path is staged;
- the largest changed file is about 1.48 MB; no GitHub large-file limit risk was
  found.

## Preserved qualification evidence

This branch does not rewrite the frozen functional qualification.  The
authoritative portable artifact remains
`a570367ebdc3b2ac3544d3e36046017acb6e9a854a2b25b10145461978fa28db`.
The clean Home-Linux result remains nine applications, eleven fresh processes,
fourteen canonical regions, exact outputs, complete required behavioral OptiX
receipts, and zero registered performance timings.

## Known boundaries

- The repository project metadata is explicitly promoted to `3.0.0`; preserved
  v2.14 material remains historical comparison evidence.
- Large paper datasets and internal historical evidence are not bundled into
  the GitHub source branch.
- Target-native builds are target-specific and not claimed byte-reproducible.
- No universal no-slower, author-performance, RT-silicon-utilization, or
  managed-binary-service claim follows from this audit.

## Publication status

The reviewed branch was published as
[pull request #2](https://github.com/rubaolee/rtdl/pull/2), then promoted to the
RTDL 3.0.0 source release after version, front-page, documentation, link, test,
and release-surface checks. This publication does not assert universal
performance superiority.
