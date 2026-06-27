# Phoenix V3 High-Performance Candidate Matrix

Status: active Phoenix planning packet, 2026-06-20.

This packet is not release authorization. It is the V3-only decision matrix for
turning the useful M0-M149 work into a serious high-performance V3 language
release.

Phoenix means:

```text
Rebuild V3 from evidence after the failed release posture.
Keep only the parts that solve the V2.x user problem.
Prove every performance statement with current artifacts.
```

## Boundary

The V3 boundary is hard:

```text
M0-M149 can be mined for V3.
M150-M214 are out of V3.
```

The following cannot define Phoenix V3, teach Phoenix V3, or justify Phoenix V3
performance:

- C ABI work;
- embedding work;
- ctypes or language-binding packaging;
- external runtime ownership;
- stable SDK claims;
- true zero-copy product claims;
- DLPack-like bridge claims.

The useful V3 center is:

```text
execution graph discipline
prepared/reused routes
same-stream and no-hidden-copy measurement
device-resident continuation where measured
fused continuations where route-specific evidence wins
serious benchmark-app closure
```

Goal4392 remains the control plane for Phoenix. Benchmark tuning is not the V3
architecture by itself. A P0 route belongs in Phoenix only when it maps to a
generic V3 capability such as graph values, prepared graph plans, stream values,
generic fused continuations, partner nodes, phase accounting, or backend-neutral
contracts.

The alignment audit is:

```text
docs/rebuild/v3/phoenix_v3_goal4392_alignment_audit_2026-06-20.md
```

## Current Evidence Baseline

Current all-app OptiX-vs-Embree evidence:

```text
docs/rebuild/v3/v3_claim_grade_all_benchmark_results_2026-06-20.md
docs/rebuild/v3/evidence/v3_claim_grade_all_benchmarks_calibrated_20260620
40 rows / 40 ok / 0 failed
10 promoted benchmark apps covered
release_authorized: false
public_speedup_claim_authorized: false
```

Current V2.14-vs-current-V3 paired evidence:

```text
docs/rebuild/v3/v2_14_vs_v3_same_rt_hardware_paired_benchmark_2026-06-20.md
docs/rebuild/v3/evidence/v2_14_vs_v3_same_rt_hardware_paired_20260620_140120
Compared rows: 46
V3 faster by >5%: 10
Within +/-5%: 32
V3 slower by >5%: 4
Geomean V3 speedup vs V2.14: 1.012x
broad_v3_faster_than_v2_claim_authorized: false
```

Current evidence says Phoenix V3 has strong route-scoped acceleration candidates
and stronger route health than V2.14. It does not yet prove a broad same-row V3
speedup over V2.14.

## Phoenix Candidate Matrix

| Priority | Candidate route family | M0-M149 source | Current evidence | Why it belongs in Phoenix | Required next action | Claim boundary |
| --- | --- | --- | --- | --- | --- | --- |
| P0 | RayDB-style prepared grouped reductions | M28, M117 | OptiX-vs-Embree rows: grouped count 383.321x, grouped sum 367.516x. V2.14 paired row has 1.155x for one OptiX sum row. | It is one of the clearest examples of prepared grouped work solving an app-author aggregation problem. | Re-run same-hardware V2.14-vs-V3 with the calibrated large row and preserve Torch CUDA partner gate output. | Partner-gated grouped reduction, not universal database acceleration. |
| P0 internal | RTDBSCAN compact signature / direct-status point-column route | M88-M100, M114, M123-M124, M132; Phoenix same-contract rerun | The old clustered all-app ratio is superseded for public interpretation. Fresh same-contract rows pass at 65,536 / 262,144 / 524,288 points but show only 1.150x / 1.079x / 1.071x OptiX-over-Embree, with continuation costs dominating at larger scales. | It is still valuable as a continuation lesson: fixed-radius RT results can feed cluster-relevant status columns, but the current route is not a public M7 speed row. | Keep internal unless a new generic component route removes the continuation bottleneck, preserves the same contract, and passes external review. | Internal partner-gated cluster-signature route only; not full paper reproduction, not full DBSCAN replacement, and not a public RTDBSCAN speedup claim. |
| P0 | Triangle RT-Graph 2A1 / prepared segment replay / payload merge | M65-M86, M96-M98, M115, M125, M133-M141 | OptiX-vs-Embree synthetic clique rows: 116.060x and 347.232x. V2.14 had launch failures in triangle rows that V3 fixed. | It is the strongest proof that prepared graph discipline can rescue a previously failing route family. | Convert accepted Triangle subpath into one reproducible Phoenix tutorial-grade benchmark row with explicit synthetic-workload boundary. | Synthetic K4/clique ladder and RT-Graph 2A1 subpath only, not graph database or paper-dataset reproduction. |
| P0 | RTNN prepared ranked-summary / chunked partner runtime | M47, M63-M64, M102-M113, M120 | OptiX-vs-Embree rows: clustered 3.333x, shell 1.182x, uniform 1.084x. V2.14 app geomean is 1.019x. | It directly exercises prepared graph chunks, distribution sensitivity, and partner continuation. | Keep clustered row as performance candidate; classify shell/uniform as modest or boundary rows unless tuned. | Distribution-specific nearest-neighbor summary, not universal RTNN acceleration. |
| P0 | Barnes-Hut fused continuation path | M43-M54, M62, M87, M101, M116, M121-M122, M129-M131, M142; Phoenix M6 rerun | OptiX-vs-Embree node-coverage rows: 1.870x to 1.898x. Phoenix M6 route-parity rerun at 32,768 / 65,536 / 131,072 bodies passed checksum parity; fused Numba CUDA was fastest and prepared OptiX+Numba was 7.328x, 5.120x, and 13.912x slower than fastest. | It is the key lesson that V3 needs fused continuations when generic RT primitive output is not enough. | Regression is now explained: prepared OptiX frontier row emission is the wrong hot-path shape for Barnes-Hut force summary. Keep as internal fused-partner evidence unless M7 explicitly classifies it. | Fused-partner route only, not Barnes-Hut RT-core speedup or full force aggregation claim. |
| P0 | Spatial RayJoin authored tiled routes | M33, M55, M118 | OptiX-vs-Embree rows: overlay x2048 30489.613x, LSI x2048 516.792x, PIP x2048 10.703x. V2.14 paired geomean is 1.000x and Embree rows include losses. | It fixes the earlier misleading tiny-fixture story and gives strong hot-route evidence. | Preserve x2048 authored workload; tune/explain Embree regression rows; keep paper-reproduction boundary visible. | Authored tiled hot routes, not full paper reproduction or polygon overlay materialization. |
| P1 | LibRTS-style generic prepared AABB index | M30, M117 | OptiX-vs-Embree large AABB row: 814.339x. V2.14 app geomean is 1.163x. | It replaces the bad-looking toy row with a serious same-contract AABB workload. | Keep as primitive-route benchmark row; avoid LibRTS authors-code wording. | Generic AABB count-only route, not LibRTS paper-equivalent timing. |
| P1 | Hausdorff prepared threshold route | M22, M28-M34, M117 | OptiX-vs-Embree threshold rows: 1.595x to 2.000x. V2.14 app geomean is 1.062x. | It is a stable prepared decision route with understandable semantics. | Keep threshold decision tutorial row if validation and scale metadata are clear. | Threshold decision only, not full exact Hausdorff witness materialization. |
| P1 | Robot collision prepared any-hit route | M31, M50, M117 | OptiX-vs-Embree prepared collision flags row: 5.166x. V2.14 app geomean is 1.016x. | It demonstrates practical collision flags without overbuilding a planner. | Keep calibrated 8192 poses / 1024 obstacles row; document why larger CPU baseline is not the suite blocker. | Collision flags only, not full robot planning. |
| P1 | Contact manifold broadphase collect-k | M29, M117 | OptiX-vs-Embree broadphase row: 1.235x. V2.14 app geomean is 0.996x. | It covers broadphase candidate generation, a real app-author need. | Keep as moderate route-health evidence unless further tuned. | Broadphase collect-k only, not full physics/contact solver. |

## Immediate Phoenix Work Queue

1. Freeze this matrix through 2-AI consensus after Goal4392 alignment.
2. Build a current M1-M7 compliance table from existing M0-M149 artifacts:
   - M1 execution graph IR;
   - M2 planner skeleton and validators;
   - M3 residency and phase instrumentation;
   - M4 generic fused continuation with cross-app reuse;
   - M5 RayJoin point-location/topology pilot;
   - M6 aggregate-tree/frontier pilot;
   - M7 release-grade benchmark harness.
3. For each P0 route, prove its named generic V3 capability before treating it as
   M7-qualified:
   - grouped reduction;
   - compact positives / component union;
   - ranked summary;
   - point-location / topology streams;
   - frontier / node summary / vector accumulation;
   - prepared graph chunking.
   Rows that do not instantiate a named generic V3 capability are removed from
   Phoenix release evidence rather than kept as supplementary performance rows.
4. Run focused pod reruns for P0 routes, starting with rows that can change the
   V2.14-vs-V3 answer and satisfy Goal4392 evidence rules:
   - Spatial RayJoin Embree regression rows;
   - RayDB calibrated grouped rows against V2.14;
   - RTDBSCAN validation and no-hidden-copy measurement;
   - Triangle synthetic row tutorial-grade rerun.
5. Promote only rows with clean artifacts into tutorials and public docs.
6. Keep all broad V3 speedup wording blocked until the paired benchmark changes
   materially. The current 1.012x same-hardware V3-over-V2.14 geomean is a
   release-blocking fact for broad timing superiority wording.

## Release Wording Allowed From This Matrix

Allowed:

```text
Phoenix V3 has identified route-scoped high-performance candidates across the
promoted benchmark apps, with exact artifact boundaries and a focused tuning
queue.
```

Not allowed:

```text
Do not claim V3 is released.
Do not claim V3 broadly beats V2.x.
Do not claim every benchmark app is solved end to end.
Do not treat the P0 matrix itself as release authorization.
```

## Goal-Level Decision Audit

Decision: use this Phoenix matrix as the next V3 control point before changing
code or rerunning expensive pods.

1. Was I foolish?

   The corrected decision is not foolish. It is bounded, evidence-based, and
   keeps release authorization false.

2. If yes, what actions made the earlier decision foolish?

   The earlier foolish action was treating V3 closure as a wording or scope
   exercise while the V2.14-vs-V3 timing evidence still showed parity and
   regressions.

3. Was there another path that avoided being stuck?

   Yes. Start from M0-M149, classify routes by current evidence, and only then
   choose the next pod and code work.

4. Can I now try a different path that truly solves the problem?

   Yes. Phoenix now has a concrete P0 work queue that targets the exact gap:
   make V3's high-performance story real, measured, and user-safe.

## 2-AI Consensus Status

Accepted as a planning baseline, not release authorization.

Codex consensus:

```text
docs/reviews/codex_phoenix_v3_goal4392_alignment_2ai_consensus_2026-06-20.md
```

External Claude compact review:

```text
docs/reviews/claude_phoenix_v3_goal4392_alignment_review_2026-06-20.md
VERDICT: ACCEPT_WITH_REQUIRED_AMENDMENTS
```
