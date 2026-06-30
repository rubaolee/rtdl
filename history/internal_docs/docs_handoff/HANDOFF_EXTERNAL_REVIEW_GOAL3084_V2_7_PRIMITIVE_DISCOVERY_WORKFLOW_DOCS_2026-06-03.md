# Handoff: External Review Of Goal3084 v2.7 Primitive Discovery Workflow Docs

Please review Goal3084 and write:

`docs/reviews/goal3085_<reviewer>_review_goal3084_v2_7_primitive_discovery_workflow_docs_2026-06-03.md`

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or
`reject`.

## Files To Inspect

- `examples/v2_0/getting_started/rtdl_primitive_discovery_workflow.py`
- `docs/learn/primitive_discovery_workflow.md`
- `docs/learn/README.md`
- `docs/tutorials/README.md`
- `docs/app_example_quickstart.md`
- `docs/application_catalog.md`
- `examples/README.md`
- `examples/v2_0/README.md`
- `examples/v2_0/getting_started/README.md`
- `examples/__init__.py`
- `tests/goal3084_v2_7_primitive_discovery_workflow_docs_test.py`
- `docs/reports/goal3084_v2_7_primitive_discovery_workflow_docs_example_2026-06-03.md`

## Review Questions

1. Does the example run as metadata-only discovery and avoid backend execution,
   partner dispatch, hidden routing, or selected partner behavior?
2. Do the learner docs explain `find_primitive(...)`, `find_recipe(...)`, and
   `plan_continuation(...)` clearly without making RTDL look like an app-shaped
   library or hidden dispatcher?
3. Do the public index links improve discoverability without frustrating normal
   learners with historical or release-report material?
4. Does wording avoid release readiness, package install, broad speedup,
   broad RT-core, true zero-copy, paper-reproduction, automatic Triton, and
   automatic partner-selection claims?
5. Are the tests sufficient for this small learner workflow slice?

## Boundary

This review must not authorize release, performance, broad RT-core, true
zero-copy, package-install, paper-reproduction, automatic partner-selection, or
app-specific native-engine claims.
