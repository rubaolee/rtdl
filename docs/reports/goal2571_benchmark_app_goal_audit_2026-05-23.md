# Goal2571 Benchmark-App Goal Audit

Date: 2026-05-23

## Purpose

This audit checks the benchmark-app development sequence from the RT-DBSCAN
campaign start through the current shared-substrate cleanup. The audit question
is:

```text
Are there remaining review or consensus debts from the benchmark-app wave, and
if so, are they blockers for the current internal benchmark-app snapshot?
```

This is not a release note, public speedup packet, or new performance claim.
It is an internal audit of goal closure, claim boundaries, and external-review
coverage.

## Scope

The audited sequence starts at Goal2392, the RT-DBSCAN benchmark campaign, and
runs through Goal2570, the shared-substrate manifest refresh.

| Range | App or cleanup lane | Closeout or control report |
| --- | --- | --- |
| Goals2392-2478 | RT-DBSCAN / fixed-radius graph continuation | `docs/reports/goal2478_rt_dbscan_project_completion_2026-05-21.md` |
| Goals2479-2491 | Robot collision / grouped finite segment any-hit screening | `docs/reports/goal2491_robot_collision_benchmark_app_closeout_2026-05-22.md` |
| Goals2492-2528 | RayDB-style / partner-resident columnar grouped aggregates | `docs/reports/goal2528_raydb_style_benchmark_app_closeout_2026-05-23.md` |
| Goal2529 | 3-AI consensus for finished benchmark apps so far | `docs/reports/goal2529_3ai_consensus_finished_benchmark_apps_2026-05-23.md` |
| Goals2530-2550 | Barnes-Hut / aggregate-frontier and vector/scalar accumulation pressure | `docs/reports/goal2550_barnes_hut_final_performance_and_closeout_2026-05-23.md` |
| Goal2551 | 3-AI rethinking of the benchmark-app wave through Barnes-Hut | `docs/reports/goal2551_codex_gemini_claude_consensus_benchmark_app_wave_2026-05-23.md` |
| Goals2552-2570 | Engine-purity, compatibility, shared substrate, and manifest cleanup | `docs/reports/goal2570_manifest_shared_substrate_refresh_2026-05-23.md` |

Earlier Hausdorff and RayJoin benchmark apps are referenced by Goal2529 because
they are part of the broader finished benchmark-app program, but the direct
audit focus here is the sequence that began with RT-DBSCAN.

## Evidence Reviewed

Primary closeouts:

- `docs/reports/goal2478_rt_dbscan_project_completion_2026-05-21.md`
- `docs/reports/goal2491_robot_collision_benchmark_app_closeout_2026-05-22.md`
- `docs/reports/goal2528_raydb_style_benchmark_app_closeout_2026-05-23.md`
- `docs/reports/goal2550_barnes_hut_final_performance_and_closeout_2026-05-23.md`

Primary consensus artifacts:

- `docs/reports/goal2529_finished_benchmark_apps_consensus_packet_2026-05-23.md`
- `docs/reports/goal2529_claude_review_finished_benchmark_apps_2026-05-23.md`
- `docs/reports/goal2529_gemini_review_finished_benchmark_apps_2026-05-23.md`
- `docs/reports/goal2529_3ai_consensus_finished_benchmark_apps_2026-05-23.md`
- `docs/reports/goal2551_codex_rethinking_benchmark_app_wave_2026-05-23.md`
- `docs/reports/goal2551_claude_rethinking_benchmark_app_wave_2026-05-23.md`
- `docs/reports/goal2551_gemini_rethinking_benchmark_app_wave_2026-05-23.md`
- `docs/reports/goal2551_codex_gemini_claude_consensus_benchmark_app_wave_2026-05-23.md`

Cleanup and substrate artifacts:

- `docs/reports/goal2552_grouped_capacity_overflow_contract_2026-05-23.md`
- `docs/reports/goal2553_native_app_term_purity_gate_2026-05-23.md`
- `docs/reports/goal2554_native_columnar_type_boundary_2026-05-23.md`
- `docs/reports/goal2555_native_columnar_helper_boundary_2026-05-23.md`
- `docs/reports/goal2556_python_columnar_public_api_boundary_2026-05-23.md`
- `docs/reports/goal2557_python_columnar_internal_routing_2026-05-23.md`
- `docs/reports/goal2558_columnar_ctypes_alias_boundary_2026-05-23.md`
- `docs/reports/goal2559_python_wrapper_columnar_ctypes_usage_2026-05-23.md`
- `docs/reports/goal2560_optix_compact_summary_columnar_alias_2026-05-23.md`
- `docs/reports/goal2561_columnar_partner_wording_boundary_2026-05-23.md`
- `docs/reports/goal2562_robot_collision_app_adapter_boundary_2026-05-23.md`
- `docs/reports/goal2563_barnes_hut_app_adapter_boundary_2026-05-23.md`
- `docs/reports/goal2564_active_engine_app_independence_boundary_2026-05-23.md`
- `docs/reports/goal2565_device_column_descriptor_contract_2026-05-23.md`
- `docs/reports/goal2566_benchmark_app_evidence_manifest_2026-05-23.md`
- `docs/reports/goal2567_grouped_reduction_substrate_contract_2026-05-23.md`
- `docs/reports/goal2568_partner_resident_dispatcher_grouped_contract_2026-05-23.md`
- `docs/reports/goal2569_robot_collision_group_any_contract_metadata_2026-05-23.md`
- `docs/reports/goal2570_manifest_shared_substrate_refresh_2026-05-23.md`

Regression tests reviewed include the Goal2529 and Goal2551 consensus tests,
the Goal2552-2570 cleanup tests, and the Goal2566 evidence-manifest test.

## App Closure Audit

### RT-DBSCAN

Status: closed for the current benchmark-app scope.

Goal2478 records a complete scoped RTDL implementation of:

```text
3-D fixed-radius neighbor search -> core-point threshold -> radius-graph components
```

The closeout explicitly blocks paper reproduction, paper-level speedup wording,
broad DBSCAN acceleration, and native DBSCAN semantics. Goal2529 later covered
RT-DBSCAN in 3-AI consensus and classified it as a finished generic
fixed-radius graph/component benchmark app.

Debt status: no open review or consensus debt for internal snapshot closure.

Remaining non-debt deferrals:

- paper/authors-code comparison;
- broad public DBSCAN speedup wording;
- a v3-scale new native algorithm replacing grouped continuation;
- inactive backend work outside Embree and OptiX.

### Robot Collision

Status: closed for the current benchmark-app scope.

Goal2491 records a sampled discrete feasibility-screening benchmark over
prepared static triangle scenes and grouped finite 3D segment probes. The
closeout itself says Goal2491 requires at least 2-AI consensus before final
project closure.

That requirement was later satisfied by Goal2529 3-AI consensus, which
classified robot collision as a finished sampled static-scene
feasibility-screening benchmark app and adopted claim boundaries that block
general robot-collision, continuous/swept collision, exact solid contact,
authors-code comparison, and public speedup wording.

Debt status: the explicit Goal2491 consensus debt is closed by Goal2529.

Remaining non-debt deferrals:

- continuous/swept collision;
- exact solid-contact collision;
- paper/authors-code comparison;
- public robot-solver or speedup wording.

### RayDB-Style Columnar Aggregate

Status: closed for the current benchmark-app scope.

Goal2528 closes the app as a deterministic columnar grouped-aggregate
reconstruction benchmark. The final scope covers CPU correctness, PostgreSQL
correctness/indexed timing, DuckDB timing, cuDF timing, RTDL OptiX
partner-resident timing, and final fused grouped stats for the same contract.

The closeout blocks RayDB paper reproduction, authors-code comparison, SQL
engine/DBMS claims, SSB reproduction, Crystal/GPU-DBMS reproduction, and public
speedup wording. Goal2529 covered the RayDB-style app in 3-AI consensus and
classified it as a finished deterministic columnar grouped-aggregate
benchmark.

Debt status: no open review or consensus debt for internal snapshot closure.

Remaining non-debt deferrals:

- RayDB authors-code or SSB reproduction;
- SQL/query-optimizer/storage semantics;
- GPU database baseline beyond the scoped cuDF candidate;
- public DB speedup wording.

### Barnes-Hut / RT-BarnesHut-Style

Status: closed for the current benchmark-app scope.

Goal2530 promoted Barnes-Hut into the benchmark lane, Goal2549 rejected an
app-specific inverse-square native OptiX primitive, and Goal2550 closed the
phase with a final partner-resident diagnostic result and strict claim
boundary. The final closeout blocks same-contract authors-code speedup claims,
paper reproduction, native inverse-square force primitives, and public speedup
wording.

Barnes-Hut was not covered by Goal2529 because it started after that
consensus. It is covered by Goal2551 3-AI benchmark-wave rethinking. Claude,
Gemini, and Codex all agreed that Goal2549 correctly rejected native
app-specific inverse-square force math and that future Barnes-Hut work must be
math-agnostic native frontier production or a reviewed partner/operator
mechanism.

Debt status: no open review or consensus debt for internal snapshot closure.

Remaining non-debt deferrals:

- true app-independent native aggregate-frontier primitive;
- reviewed operator/partner mechanism for fused app math;
- fixed authors-artifact same-input reload path;
- public RT-BarnesHut speedup or reproduction wording.

## Cross-App Review Debt Ledger

| Debt or review finding | Source | Current status | Evidence |
| --- | --- | --- | --- |
| Robot closeout needed at least 2-AI consensus | Goal2491 | Closed | Goal2529 3-AI consensus |
| Finished-app classification needed external review | Goal2529 packet | Closed | Claude `ACCEPT`, Gemini `ACCEPT-WITH-BOUNDARY`, final `ACCEPT-WITH-BOUNDARY` |
| Benchmark-wave architecture needed 3-AI rethinking | User request before Goal2551 | Closed | Goal2551 Codex, Claude, Gemini, and consensus reports |
| Grouped `_with_capacity` APIs lacked overflow signal | Goal2551 Claude review | Addressed | Goal2552 adds `overflowed_out` and fail-closed behavior |
| Native active engine carried DBSCAN/RayDB-shaped internal names | Goal2551 consensus | Addressed for active implementation names | Goal2553, Goal2554, Goal2555, Goal2564 |
| Shared partner module carried robot-specific adapter | Goal2551 consensus | Addressed | Goal2562 moves it to `rtdsl.app_adapters.robot_collision` |
| Shared partner module carried Barnes-Hut inverse-square adapter | Goal2549 / Goal2551 | Addressed | Goal2563 moves it to `rtdsl.app_adapters.barnes_hut` |
| Columnar partner wording was RayDB-shaped | Goal2551 consensus | Addressed | Goal2561 |
| Device column descriptors were fragmented | Goal2551 consensus | Partially addressed | Goal2565 adds `DeviceColumnDescriptor`; output descriptors remain future work |
| Grouped reductions were fragmented | Goal2551 consensus | Partially addressed | Goal2567-2569 add shared contract/metadata; full native migration remains future work |
| Evidence needed a single manifest | Goal2551 consensus | Addressed | Goal2566 plus Goal2570 |
| Post-cleanup audit itself needs independent review | Current Goal2571 | Pending in this report | Claude and Gemini reviews to be added as Goal2571 artifacts |

## Compatibility Debt Versus Review Debt

Some compatibility debt remains by design and is not the same as unclosed
review debt:

- `RtdlDb*` prelude aliases remain as compatibility aliases to generic
  columnar names.
- Python DB-shaped compatibility names and ctypes class definitions remain for
  older tests and wrappers.
- Top-level `rtdsl` exports preserve moved app adapters for compatibility, but
  the shared `partner_adapters.py` module no longer owns those app-specific
  implementations.
- Native compatibility C symbols have not been renamed.

These are acceptable only under the current internal snapshot boundary. They
do not authorize external ABI stability, public release wording, or claims that
all historical compatibility surfaces are app-name-free.

## Current Claim Boundary

Allowed after this audit, if external reviews agree:

- The RT-DBSCAN, robot-collision, RayDB-style, and Barnes-Hut benchmark apps are
  closed as internal RTDL reconstruction benchmark apps for their stated
  scopes.
- The post-benchmark cleanup addressed the P0/P1 review debts identified by
  Goal2551 enough for continued internal engineering and external code review.
- Active Embree/OptiX primitive implementation paths and shared partner/columnar
  modules now have guardrails against benchmark-app vocabulary.
- Shared substrate work exists for `DeviceColumnDescriptor` and
  `rtdl.grouped_reduction.v1`, but it is not yet a fully stabilized external
  ABI.

Blocked:

- public release wording;
- broad speedup or whole-app acceleration wording;
- authors-code parity claims;
- paper reproduction claims;
- SQL/DBMS, robot-solver, or RT-BarnesHut solver claims;
- external native ABI stability claims;
- true zero-copy claims.

## Codex Preliminary Verdict

Preliminary verdict: `ACCEPT-WITH-BOUNDARY`.

No unresolved review or consensus debt blocks the current internal
benchmark-app snapshot. The remaining items are documented future work or
compatibility debt, not evidence that any benchmark-app closeout lacks required
review coverage.

This preliminary verdict is not final until Claude and Gemini independently
review this audit and the final Goal2571 consensus report records their
verdicts.

## Post-Review Note

The external reviews are recorded in companion artifacts:

- `docs/reports/goal2571_claude_benchmark_app_goal_audit_review_2026-05-23.md`
- `docs/reports/goal2571_gemini_benchmark_app_goal_audit_review_2026-05-23.md`

The final 3-AI verdict is recorded separately in:

- `docs/reports/goal2571_3ai_consensus_benchmark_app_goal_audit_2026-05-23.md`
