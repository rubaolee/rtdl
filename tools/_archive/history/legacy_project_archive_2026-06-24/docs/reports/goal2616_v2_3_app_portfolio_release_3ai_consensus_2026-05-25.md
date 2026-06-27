# Goal2616 v2.3 App-Portfolio Release 3-AI Consensus

Date: 2026-05-25

Status: accepted for v2.3 source-tree app-portfolio release.

## Scope

This consensus covers the v2.3 cleanup and release boundary:

- `VERSION`
- root `README.md`
- `docs/README.md`
- `docs/application_catalog.md`
- `docs/release_reports/v2_3/README.md`
- `examples/README.md`
- `examples/v2_0/research_benchmarks/README.md`
- GPU-RMQ demotion docs and tests
- v2.3 release gate test `tests/goal2613_v2_3_app_portfolio_release_test.py`

## Decision

RTDL v2.3 is accepted as a source-tree Python+partner+RTDL app-portfolio
release. It publishes two explicit app tables:

- promoted benchmark apps, used as reconstruction instruments for RTDL
  language/runtime design;
- learner/example apps, including feature examples, partner examples, demos,
  and demoted research candidates.

This release does not claim package-install support, broad RT-core speedups,
whole-application speedups, full paper reproduction, arbitrary PyTorch/CuPy
acceleration, or app-specific native engine semantics.

## External Reviews

- Claude review:
  `docs/reports/goal2614_claude_v2_3_app_portfolio_release_review_2026-05-25.md`
  returned `VERDICT: ACCEPT`.
- Gemini review:
  `docs/reports/goal2615_gemini_v2_3_app_portfolio_release_review_2026-05-25.md`
  returned `VERDICT: ACCEPT`.

Claude raised two non-blocking cleanup observations. Both were addressed after
the review:

- `examples/README.md` now lists all nine promoted benchmark studies in the
  important performance-applications table.
- `docs/release_reports/v2_3/README.md` now links the Continuous Frechet
  demotion evidence reports.

These edits strengthen navigation/evidence references and do not widen the
accepted release claims.

## Codex Verification

Focused release and boundary suite:

```text
PYTHONPATH=src:. python3 -m py_compile src/rtdsl/__init__.py src/rtdsl/optix_runtime.py examples/v2_0/research_benchmarks/gpu_rmq/rtdl_gpu_rmq_benchmark_app.py scripts/goal2609_gpu_rmq_non_author_baselines.py
PYTHONPATH=src:. python3 -m unittest tests.goal2613_v2_3_app_portfolio_release_test tests.goal2093_v2_pre_release_public_docs_boundary_test tests.goal2323_v2_0_release_action_test tests.goal1740_v1_8_public_docs_boundary_alignment_test tests.goal1763_v1_8_public_docs_and_learner_path_readiness_test tests.goal2344_v2_1_internal_closure_test tests.goal532_v0_8_release_authorization_test tests.goal645_v0_9_5_release_package_test tests.goal684_v0_9_6_release_level_flow_audit_test tests.goal1221_v0_9_8_release_action_test tests.goal1248_v1_0_release_candidate_package_test tests.goal2594_gpu_rmq_benchmark_front_door_test tests.goal2595_gpu_rmq_author_runner_test tests.goal2598_optix_generic_closest_hit_contract_test
```

Result:

```text
Ran 73 tests in 0.155s
OK (skipped=2)
```

`git diff --check` also passed.

## Consensus

Codex, Claude, and Gemini agree that v2.3 is coherent as a source-tree
app-portfolio release with the stated benchmark-vs-learner split and claim
boundaries.
