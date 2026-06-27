# Claude V3 Performance Rescue Handoff

Superseded current entrypoint:

`docs/handoff/PHOENIX_V3_CURRENT_HANDOFF_2026-06-22.md`

Use the superseding handoff first. This file is preserved for historical
performance-rescue context.

Date: 2026-06-20

Status: urgent handoff requested by the user after loss of trust in Codex.

Update from Repair Pass 1: this file is historical context for why the rescue
was necessary. For the latest executable state, read
`docs/handoff/CLAUDE_V3_REBUILD_TAKEOVER_HANDOFF_2026-06-20.md` first. The
current V3 tree now has clean current-side pod evidence for `goal2626`
22/22, `goal2636` 28/28, `goal3828` 10/10, and the GPU Python environment
gate. V3 is still not release-authorized because public docs/tutorials/setup
have not been rebuilt from those artifacts.

## Read This First

The user does not want more defensive wording, broad release language, or
discussion of later external-host/embedding strategy. Treat this as a V3-only
rescue.

The current user mandate is:

```text
V3 must be the highest-performance independent-language RTDL release.
V3 must solve real user performance problems.
If current V3 cannot prove that, fix it or recommend a rewrite.
Do not hide behind docs, route closure, or later roadmap language.
```

## Direct Answers The User Asked For

### 1. What problem must V3 solve?

V3 must solve this user problem:

```text
Python users have serious RT-shaped workloads but do not want to hand-build a
new C++/CUDA/OptiX engine for every app. They need an independent RTDL language
surface that lets them express the kernel, choose an RT/backend path, keep app
policy in Python or explicit partners, and get measured high performance on
real benchmark-shaped workloads.
```

Concretely, V3 must make these workloads practical and teachable:

- spatial joins and point/shape predicates;
- fixed-radius, nearest-neighbor, and ranked-summary queries;
- DBSCAN-style core/candidate discovery with explicit continuation;
- broadphase collision/contact queries;
- RayDB-style grouped count/sum reductions;
- RTNN-style ranked neighbor summaries;
- triangle-counting / RT-Graph-shaped summaries;
- Barnes-Hut-style RT-shaped node coverage or clearly scoped aggregate routes;
- LibRTS-style AABB spatial-index queries;
- Hausdorff/X-HD threshold and witness-oriented routes where evidence exists.

V3 should be judged by current, same-contract, artifact-backed performance
evidence, not by prose.

### 2. Why is the user dissatisfied with V3 and the subsequent work?

The user is dissatisfied for valid reasons:

- V3 was originally discussed as a major performance/architecture step, but the
  final V3.0.2 story was narrowed into source-tree route closure and docs
  cleanup.
- The system contains strong internal performance history, but current release
  docs still refuse broad public performance claims.
- A fresh comparison report on 2026-06-20 said V2.14 remains the stronger
  released public performance baseline, while V3.0.2 is stronger mainly as a
  cleaned current user surface.
- This makes V3 feel like a downgrade or retreat from the user's intended
  "major version" promise.
- V3 docs are internally mixed: some current app/catalog pages show strong
  OptiX-vs-Embree speedups, while the release packet says performance claims
  remain row-scoped, blocked, or not public.
- Some V3 scale rows are route-health rows, not claim-grade rows. Examples from
  the 2026-06-20 pod packet include skipped or partial validation signals for
  RT-DBSCAN, Robot, Barnes-Hut, and LibRTS scale rows.
- Codex repeatedly polluted the V3 conversation with later external-host scope
  and failed to stay focused on the user's V3-only question.
- The user wanted "Does V3 actually solve user problems better than V2.x?" and
  got too much boundary explanation before enough direct evidence.

The core trust problem:

```text
V3 was called done, but the evidence does not yet prove it is the
highest-performance independent-language release. That gap must be closed by
testing and repair, not by wording.
```

## Current Repo State From Codex Work

Codex added these files:

- `docs/reports/v3_0_design_intent_reconstruction_and_performance_mandate_2026-06-20.md`
- `docs/reports/v3_0_performance_release_gate_plan_2026-06-20.md`
- `docs/reports/v2_14_vs_v3_0_2_pod_comparison_2026-06-20.md`
- `docs/reviews/call_for_review_v2_14_vs_v3_0_2_pod_comparison_2026-06-20.md`
- `docs/reports/v2_14_vs_v3_0_2_pod_comparison_2026-06-20_artifacts/`

Codex also modified:

- `docs/handoff/REFRESH_LOCAL_2026-04-13.md`
- `docs/handoff/NEXT_PRIMARY_AI_V3_CONTINUATION_HANDOFF_2026-06-18.md`

Important: review these changes critically. Do not assume they are right just
because they exist.

## Strong Existing Evidence To Read

### V3 Design Intent And Architecture

- `docs/reports/v3_0_custom_engine_extensions_concept.md`
- `docs/reviews/v3_0_custom_engine_extensions_critical_review_and_roadmap_after_v2_5_2026-05-29.md`
- `docs/reports/claude_v2_5_closeout_and_v3_0_residency_first_roadmap_2026-05-31.md`
- `docs/reports/goal4377_pre_v3_v2_13_v2_14_strategy_2026-06-14.md`
- `docs/reports/goal4392_v3_0_overall_plan_2026-06-15.md`
- `docs/reports/goal4393_v3_0_m1_execution_graph_ir_design_2026-06-15.md`
- `docs/reports/goal4414_v3_0_midterm_review_packet_2026-06-15.md`

### V3 Completion And Shrinkage

- `docs/reports/goal4536_v3_0_m138_v3_internal_completion_packet_2026-06-17.md`
- `docs/reports/goal4538_v3_0_m139_v3_completion_review_consensus_2026-06-17.md`
- `docs/reports/goal4614_v3_0_m215_current_scope_completion_gate_2026-06-18.md`
- `docs/release_reports/v3_0_2/final_closeout.md`
- `docs/release_reports/v3_0_2/release_statement.md`
- `docs/release_reports/v3_0_2/support_matrix.md`

### Performance Evidence

- `docs/reports/goal2636_current_benchmark_performance_report_2026-05-27.md`
- `docs/reports/goal2637_all_benchmark_perf_diffs_2026-05-27.md`
- `docs/reports/goal2655_benchmark_rt_core_speedup_summary_2026-05-27.md`
- `docs/history/release_reports/v2_14/public_rt_vs_embree_comparison.md`
- `docs/reports/v2_14_vs_v3_0_2_pod_comparison_2026-06-20.md`

## Critical Fact Pattern

There are two competing V3 stories:

### Story A: V3 As Performance Version

Older and midstream docs support this:

- execution graph / prepared graph;
- device-resident or reduced-materialization windows;
- compact outputs;
- grouped/ranked summaries;
- explicit CuPy/Numba/NumPy continuations;
- app-agnostic primitives;
- OptiX-vs-Embree performance rows;
- promoted benchmark suite.

Goal2636/Goal2637 show strong internal evidence:

- 10 promoted benchmark apps;
- 11 standard comparison rows;
- 13 strengthened rows;
- 16 stress rows;
- OptiX wins every recorded ratio row in those reports.

### Story B: V3.0.2 As Conservative Source-Tree Closure

Final release docs support this:

- ten current benchmark routes closed;
- user docs/source-tree surface cleaned;
- `v3_current` passes;
- source-tree doctor passes;
- public speedup and broad claims blocked;
- no claim that V3 beats V2.14 as performance release.

The user's current mandate chooses Story A as the target, but current evidence
still needs to be refreshed and repaired until Story A is true on the current
codebase.

## What Claude Should Do Next

### Step 1: Validate Or Reject Codex's Reconstruction

Read:

- `docs/reports/v3_0_design_intent_reconstruction_and_performance_mandate_2026-06-20.md`
- `docs/reports/v3_0_performance_release_gate_plan_2026-06-20.md`

Give a blunt review:

- Is the V3 problem statement right?
- Is the performance gate complete?
- Which runner choices are wrong?
- Which rows are missing?
- Which docs overstate or understate V3?

### Step 2: Run A True V3 Performance Gate

Use the pod the user provided if available:

```text
ssh root@213.173.108.14 -p 11592 -i ~/.ssh/id_ed25519
```

Use the historical working key and do not waste time rediscovering SSH basics.

Candidate minimum command set:

```bash
set -euo pipefail
export PYTHONPATH=src:.

python3 scripts/rtdl_source_tree_doctor.py --json
python3 scripts/run_test_matrix.py --group v3_current

python3 scripts/goal2626_benchmark_embree_optix_baseline.py \
  --scale standard \
  --artifact-dir docs/reports/v3_0_performance_release_candidate_2026-06-20/goal2626_standard \
  --timeout-sec 1800 \
  --build-native

python3 scripts/goal2636_strengthen_benchmark_rows.py \
  --tier standard \
  --artifact-dir docs/reports/v3_0_performance_release_candidate_2026-06-20/goal2636_standard \
  --timeout-sec 2400 \
  --build-native

python3 scripts/rtdl_human_scale_rt_vs_embree_comparison.py \
  --output-dir docs/reports/v3_0_performance_release_candidate_2026-06-20/human_scale
```

Do not treat `goal3828_current_benchmark_scale_profile_runner.py` as sufficient
for performance release. It is route-health support only.

### Step 3: Classify Every Row

For each row, mark exactly one:

- `release_ready`;
- `needs_repair`;
- `internal_only`;
- `demote`.

A row is not `release_ready` unless it is:

- same-contract;
- correctness validated at performance scale;
- current-code;
- pod-run;
- phase-split;
- repeated or duration-calibrated;
- artifact-backed;
- clear about backend and partner.

### Step 4: Repair Before Polishing

Do not polish docs first. Repair failing rows first.

Likely risk rows:

- Barnes-Hut: current route closure is mixed-explicit; full force semantics are
  not proven as an RTDL-native performance row.
- Triangle Counting: graph/capture language was fail-closed; keep to
  same-contract prepared weighted any-hit summary unless stronger evidence
  exists.
- RT-DBSCAN: continuation dominates; separate RT threshold and partner
  continuation.
- Spatial RayJoin: keep PIP, LSI, and overlay-seed separate.
- Contact: choose scale where broadphase contract is meaningful and validated.

### Step 5: Rewrite V3 Docs Only After Evidence

Once performance evidence is current:

- create a new V3 performance release packet or replace the conservative
  v3.0.2 public story;
- reconcile `docs/application_catalog.md` with release docs;
- reconcile `docs/performance_model.md` with the final matrix;
- update tutorials only after the performance story is stable;
- preserve old docs in history and keep the current user path simple.

## What Not To Do

- Do not call V3 complete just because ten routes run.
- Do not call V3 a performance release without a current same-contract matrix.
- Do not use external-host/SDK/cross-language work to explain V3.
- Do not hide failed rows behind "claim boundary" prose.
- Do not ask the user for another decision until the evidence table is clear.
- Do not wait on AI review while doing nothing; if review is slow, run tests or
  inspect artifacts in parallel.

## Current Best Answer To The User

V3 is supposed to solve the problem of serious RT-shaped computation from a
Python-hosted independent RTDL language surface, with measured performance from
prepared RTDL primitives, compact outputs, backend dispatch, and explicit
partner continuations.

The user is dissatisfied because current V3 was presented as "done" while the
evidence only proves cleaned route health and internal performance history. It
does not yet prove, on current code and pod, that V3 is the strongest
independent-language performance release over V2.14.

Claude should therefore treat V3 as a rescue: verify the intended performance
matrix, run it, repair failed rows, then rewrite docs.
