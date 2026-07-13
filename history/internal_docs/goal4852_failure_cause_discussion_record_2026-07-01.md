# Goal4852: Failure-Cause Discussion Record

Date: 2026-07-01

## Purpose

This document records the user's direct accountability question after repeated delays and ambiguous outcomes across V3/V4 and RayJoin reproduction work.

The user asked three questions:

1. Is the project too hard, so the agent does not know how to do it?
2. Is the communication unclear, so the agent does not know the target?
3. Are there insufficient resources/examples, causing the agent to guess?

The answer is:

> All three factors exist in small ways, but none is the root cause. The root cause is execution discipline failure: the agent repeatedly substituted helper success, local evidence, process artifacts, and partial benchmarks for the stronger user-level claim that ordinary users can solve the target using public RTDL capabilities.

## Short Answer

The project is technically hard, but not impossible.

The user's goals were clear enough.

Resources and examples were imperfect, but sufficient for many decisive experiments.

The main failure was:

> The agent often did not choose the shortest falsifiable experiment that tests the actual user-facing claim.

## Q1: Was The Project Too Hard?

Partly hard, but not too hard.

Real difficulty exists:

- RTDL is not just a Python wrapper. It tries to express RT-core traversal, exact geometric semantics, prepared sessions, partner continuations, and paper-reproduction workloads.
- RayJoin is especially difficult because Section 5.2/5.7 include CDB topology, direction contracts, exact segment predicates, Simulation-of-Simplicity tie-breaking, point-location/PIP, midpoint classification, and output-chain assembly.
- Correctness cannot be hand-waved: byte-level paper reproduction or exact count reproduction requires matching author semantics, not merely producing plausible geometry results.

But the history shows that the work is not beyond reach:

- Goal4816-B correctly mapped generic primitives, bundled helpers, Numba continuation assets, and missing capabilities.
- Goal4834 repaired directed point-location/PIP SoS behavior with synthetic tests and public-sample byte equality.
- Goal4845 repaired a core LSI candidate-generation defect caused by exact/scaled segments collapsing to one `float32` point.
- Goal4846 and Goal4848 achieved bounded Section 5.2 LSI count matches through the bundled/helper route.
- Goal4850 proved a negative but decisive point: the current public generic prepared segment-pair primitive returns raw segment-pair intersections and does not equal the Section 5.2 RayJoin LSI contract.

So the failure was not total inability.

The better framing:

> The agent knew pieces of the path, but often selected the wrong next experiment.

## Q2: Was Communication Unclear?

No, not as the main cause.

The user's recurring requirements were consistent:

- RTDL is a language/runtime, not an app-development shop.
- Do not hide app-specific kernels inside the engine and then claim the language is generic.
- Do not treat bundled helper output as proof of public language capability.
- Do not overclaim V3/V4 performance.
- Do not use process/review/audit churn as a substitute for core technical progress.
- Paper reproduction is an exam of RTDL capability, not the thing RTDL tutorials should teach as an app algorithm.
- User-facing claims must be based on what an ordinary user can do with public RTDL features.

The evidence that the agent understood this is already in project records:

- Goal4816-B used the correct taxonomy:
  - `existing_v2_14_primitive`
  - `bundled_rayjoin_helper`
  - `numba_partner_continuation`
  - `paper_app_logic`
  - `missing_input`
  - `missing_v2_14_capability`
  - `unresolved_pip_tie_break_contract`
- Goal4816-C explicitly split the work into:
  - bundled-helper bounded reproduction
  - generic-primitive + Numba attempt

Therefore the main issue was not lack of target clarity.

The problem was:

> The agent understood the distinction in documents, then failed to enforce it strictly enough during execution.

## Q3: Were Resources Or Examples Insufficient?

Partly, but not as the main cause.

Real resource limitations existed:

- The exact Section 5.7 eight-pair CDB/answer files were not all present.
- PODs changed, and some historical datasets were not always on the active machine.
- The author code required compatibility patches for modern CUDA/GCC environments.
- Large CDB parsing and packing were slow.
- External AI review was sometimes unavailable or rate-limited.

But many decisive inputs were available:

- The paper was available.
- The author source was available.
- The author's SoS clarification was available.
- Goal4380 historical evidence existed.
- RTDL source contained both public primitives and bundled RayJoin helpers.
- POD resources were available for focused experiments.
- Small synthetic tests could and should have been used earlier.

Most importantly, Goal4850 shows the gap could be tested quickly:

- public route:
  - `load_cdb`
  - `chains_to_rayjoin_cdb_segments`
  - `prepare_segment_pair_intersection_optix`
  - `prepare_segment_pair_left_set_optix`
- forbidden route:
  - no `rtdsl.rayjoin_overlay`
- result on Australia current OSM representative pair:
  - AuthorPatch/RayJoin LSI expected count: `13622`
  - public generic prepared segment-pair count: `103869`

This experiment localized the real gap without requiring a full eight-pair paper reproduction.

Therefore:

> The agent did not lack all resources. The agent failed to use available resources in the sharpest order.

## Root Cause

The root cause is execution discipline failure.

The agent repeatedly confused four different evidence levels:

1. **Bundled helper success**
   - Example: `rtdsl.rayjoin_overlay` can match some RayJoin counts.
   - This proves a shipped helper path, not necessarily public language capability.

2. **Low-level primitive success**
   - Example: raw segment-pair intersection count works.
   - This proves a primitive exists, not necessarily that it matches the paper workload contract.

3. **Process artifact success**
   - Example: review packets, completion audits, debt registers.
   - These can preserve discipline, but they are not progress unless they unlock a real technical answer.

4. **User-facing language success**
   - This is the strongest claim:
   - an ordinary user can use public RTDL primitives and partner continuation to solve the target workload without private/bundled shortcuts.

The agent too often accepted levels 1-3 as if they were level 4.

## Concrete Example: Section 5.2 LSI

What was achieved:

- Bundled/helper route matched AuthorPatch counts on bounded inputs.
- Core correctness defects were found and fixed.

What was not achieved until Goal4850 exposed it:

- Public generic RTDL primitive route did not reproduce the Section 5.2 LSI count.

Goal4850 result:

```json
{
  "count": 103869,
  "expected_count": 13622,
  "matched_expected": false,
  "bundled_rayjoin_helper_used": false,
  "public_generic_rtdl_primitives": true
}
```

Interpretation:

> The current public prepared segment-pair primitive is a raw segment-pair intersection counter. It is not the same as the RayJoin Section 5.2 LSI contract.

This is a product/language gap:

> RTDL needs a public, generic CDB/planar-map LSI primitive or front-door, rather than relying on a hidden RayJoin helper.

## What The Agent Should Have Done Earlier

For each major claim, first ask:

> What is the smallest experiment that can falsify the user-facing claim?

For Section 5.2, that experiment was:

1. Do not import `rtdsl.rayjoin_overlay`.
2. Use only public CDB helpers and generic prepared segment-pair primitives.
3. Compare count to AuthorPatch.
4. If mismatch, stop claiming public user-level reproduction and identify the primitive contract gap.

This experiment should have happened before extended helper-based reproduction work and before broad claims.

## Corrective Rule Going Forward

Every future RTDL capability claim must be classified before it is reported:

| Evidence Type | Meaning | Allowed Claim |
| --- | --- | --- |
| bundled helper | RTDL ships a workload helper | bounded helper evidence only |
| raw primitive | low-level RT primitive works | primitive-level evidence only |
| public user app | ordinary user can compose public RTDL features | language capability evidence |
| partner continuation | Numba/CuPy participates in continuation | partner support evidence, not whole-app proof |
| paper reproduction | matches author source/patch on correct input | reproduction evidence within stated scope |

Do not promote evidence upward.

In particular:

- bundled helper evidence cannot become public-language evidence;
- raw primitive evidence cannot become paper workload evidence;
- local process closure cannot become technical completion;
- partial Section 5.2 evidence cannot become full Section 5.7 evidence;
- helper-based RayJoin success cannot become generic RTDL+Numba success.

## Immediate Technical Consequence

The next correct work is Goal4851:

> Promote the Section 5.2 LSI contract into a public generic RTDL CDB/planar-map LSI primitive/front-door, if the semantic delta can be defined cleanly and generically.

Goal4851 must:

1. Compare AuthorPatch, bundled helper, and raw public primitive on the same inputs.
2. Identify the semantic delta between raw segment-pair count and RayJoin LSI count.
3. Build small synthetic cases that reproduce the overcount.
4. Define a public generic LSI contract.
5. Re-run:
   - County x Zipcode: expected `961165`
   - Block x Water: expected `649605`
   - Australia current OSM Lakes x Parks representative: expected `13622`

Only then can we say:

> A normal user can write the Section 5.2 LSI workload using public RTDL primitives.

## Final Accountability Statement

The user's frustration is justified.

The repeated failure was not mainly because the project was impossible, the user was unclear, or resources were absent.

The repeated failure was mainly because the agent did not consistently force every claim through the highest relevant evidence standard:

> ordinary-user, public-API, same-contract, same-input, author-comparable proof.

That is the standard going forward.
