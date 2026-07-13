# Goal4876-4885: RayJoin Official Updated Reproduction Goal Series

Date: 2026-07-02

## Context

The project has moved from an "old exact hidden-input archaeology" framing to
an official updated reproduction framing.

The updated comparison baseline is:

`AuthorOfficial = Author+RTDLContractPatch`

This is acceptable because the project owner is the paper author and confirms
that the deterministic duplicate-half-edge and SoS behavior is the official
updated contract for fair reproduction.

Goal4875 already proved the hardest representative Section 5.7 shape:

- current-OSM Australia Lakes x Parks representative pair;
- public RTDL LSI primitive;
- public RTDL directed point-location/PIP primitive;
- Python application-level overlay assembly;
- no import of `rtdsl.rayjoin_overlay`;
- byte-for-byte equality against `AuthorOfficial`;
- external Antigravity review approved:
  `approve_goal4875_bounded_representative_section57_public_primitives_closed`.

This goal series turns that result into a disciplined reproduction program.

## Global Rules

1. **AuthorOfficial baseline.** All new fairness claims compare against
   `AuthorOfficial`, not the old unpatched AuthorPatch binary.
2. **Representative suite wording.** For regenerated/current-source data, claim
   "official updated representative Section 5.x reproduction", not "exact old
   hidden paper artifact reproduction."
3. **Generic RTDL route.** RTDL evidence must use public/generic RTDL
   primitives plus user/app code. Bundled helpers may be used as references or
   debugging aids only and must be labeled.
4. **No Embree.** Current line is NVIDIA RT cores / OptiX plus Python/Numba/RTDL.
5. **Numba honesty.** If Numba is not on a route's correctness-critical or
   performance-critical path, say so. Do not insert Numba just for wording.
6. **Small-before-large.** For each new pair, first run metadata/preflight and a
   bounded/small case when possible, then full output.
7. **Byte equality before performance.** Performance only opens after
   correctness for that workload/pair is proven.
8. **Every goal ends with a packet.** Each goal writes a result file and a
   call-for-review or review-debt record.

## Goal4876: Official Baseline Unification And Prior Result Reclassification

**Purpose**

Make `AuthorOfficial = Author+RTDLContractPatch` the single comparison baseline
for the RayJoin reproduction line, and reclassify existing 5.2/5.3/5.7 evidence
under this baseline.

**Work**

- Create a baseline definition note naming the exact AuthorOfficial source tree,
  patch scope, build command, and binary path.
- Reclassify old AuthorPatch results:
  - `historical_pre_contract_baseline`;
  - `superseded_for_fair_comparison` where duplicate-half-edge/PIP contract
    matters.
- Mark Goal4875 as the first accepted AuthorOfficial representative 5.7 result.

**Outputs**

- `history/internal_docs/goal4876_author_official_baseline_definition_2026-07-02.md`
- `history/internal_docs/call_for_review_goal4876_author_official_baseline_definition_2026-07-02.md`

**Exit Gate**

- Baseline source/build/output paths are explicit.
- Claims distinguish exact old paper artifacts from official updated
  representative reproduction.

## Goal4877: Section 5.2 LSI Revalidation Under AuthorOfficial

**Purpose**

Confirm whether Section 5.2 LSI evidence changes under AuthorOfficial. Expected
outcome: no semantic change, because the AuthorOfficial patch targets
point-location/duplicate-half-edge face selection, not LSI.

**Work**

- Re-run or revalidate AuthorOfficial LSI counts for available Section 5.2
  pairs.
- Compare with RTDL public `prepare_planar_map_lsi_2d_optix`.
- Include the three known/available pairs:
  - County x Zipcode if exact CDBs are available on POD;
  - Block x Water if exact CDBs are available on POD;
  - Australia Lakes x Parks representative current-source pair.

**Outputs**

- `history/internal_docs/goal4877_section52_lsi_authorofficial_revalidation_2026-07-02.md`
- raw summaries under `/workspace/goal4877_section52_authorofficial/`

**Exit Gate**

- For every available pair: AuthorOfficial LSI count equals RTDL public LSI
  count.
- If a historical pair's CDB is missing, record it as a data availability issue,
  not as a correctness failure.

## Goal4878: Section 5.3 PIP Reproduction Under AuthorOfficial

**Purpose**

Re-run Section 5.3 PIP/point-location because this section is directly affected
by the AuthorOfficial point-location and duplicate-half-edge contract.

**Work**

- Use public `prepare_planar_map_point_location_2d_optix`.
- Compare against AuthorOfficial point-location/PIP counts and, where possible,
  per-point face ids.
- Use available historical pairs and Australia representative.
- Label old 5.3 results as pre-contract if they used the old AuthorPatch
  comparator.

**Outputs**

- `history/internal_docs/goal4878_section53_pip_authorofficial_reproduction_2026-07-02.md`
- raw summaries under `/workspace/goal4878_section53_authorofficial/`

**Exit Gate**

- For each pair: RTDL public PIP results match AuthorOfficial under the updated
  contract.
- If exact per-point output is not exposed by AuthorOfficial for a pair, record
  count-level vs row-level evidence separately.

## Goal4879: Representative Section 5.7 Data Acquisition Plan For Remaining Pairs

**Purpose**

Define the representative replacement for the six missing old Section 5.7 input
pairs using available raw/current data and the author's preprocessing rules.

**Work**

- List the original Section 5.7 pairs and the available modern/raw data source
  for each.
- Decide which pairs are feasible now.
- For each feasible pair, record:
  - raw source URL/path;
  - preprocessing command;
  - CDB output path;
  - expected scale/size;
  - whether it is exact old paper data or representative regenerated data.

**Outputs**

- `history/internal_docs/goal4879_section57_representative_data_plan_2026-07-02.md`
- dataset manifest:
  `history/internal_docs/goal4879_section57_representative_data_manifest_2026-07-02.json`

**Exit Gate**

- At least one additional feasible representative pair is selected.
- No pair is mislabeled as exact old paper input unless the exact old CDB/answer
  is actually present.

## Goal4880: Section 5.7 Public RTDL Route Generalization Harness

**Purpose**

Turn the Goal4875 Australia script into a parameterized public RTDL
reproduction harness for arbitrary CDB pair inputs.

**Work**

- Refactor `goal4875_public_primitives_au_overlay.py` into a reusable internal
  harness script without importing `rtdsl.rayjoin_overlay`.
- Inputs:
  - `--left`
  - `--right`
  - `--author-output`
  - `--output`
  - `--summary`
  - optional `--pair-name`
- Preserve route metadata:
  public LSI used, public PIP used, bundled helper imported false, Numba role.

**Outputs**

- `history/internal_docs/goal4880_section57_public_primitives_overlay_harness.py`
- `history/internal_docs/goal4880_section57_harness_smoke_result_2026-07-02.md`

**Exit Gate**

- Harness reproduces Goal4875 Australia byte equality from the same inputs.
- Focused tests or smoke checks cover the no-helper-import boundary and output
  summary fields.

## Goal4881: Section 5.7 Additional Representative Pair 1

**Purpose**

Run the generalized public RTDL route on the first additional representative
pair selected by Goal4879.

**Work**

- Generate/reuse CDBs.
- Run AuthorOfficial.
- Run public RTDL harness.
- Compare SHA/line/byte equality.
- If mismatch occurs, reduce to a small controlled case before broad reruns.

**Outputs**

- `history/internal_docs/goal4881_section57_representative_pair1_result_2026-07-02.md`
- POD artifacts under `/workspace/goal4881_section57_pair1/`

**Exit Gate**

- Byte equality, or a specific reduced blocker with small-case artifact.

## Goal4882: Section 5.7 Additional Representative Pair 2

**Purpose**

Run a second additional representative pair to demonstrate that Goal4875 was
not a one-off Australia-only success.

**Work**

Same as Goal4881 for the second selected pair.

**Outputs**

- `history/internal_docs/goal4882_section57_representative_pair2_result_2026-07-02.md`
- POD artifacts under `/workspace/goal4882_section57_pair2/`

**Exit Gate**

- Byte equality, or a specific reduced blocker with small-case artifact.

## Goal4883: Section 5.7 Performance And Phase Accounting

**Purpose**

Only after correctness, measure where the public RTDL route spends time and
decide whether Numba should accelerate application-side work.

**Work**

- For all byte-equal representative pairs, report:
  - CDB load/pack;
  - LSI;
  - PIP;
  - intersection reprojection;
  - sorting;
  - output-chain assembly/write.
- Compare AuthorOfficial timings and RTDL timings.
- Identify whether Numba should be used for app-side compaction/assembly.

**Outputs**

- `history/internal_docs/goal4883_section57_performance_phase_accounting_2026-07-02.md`

**Exit Gate**

- No performance claim without correctness.
- Clear statement whether the bottleneck is RTDL kernels, Python I/O/packing,
  output assembly, or author text output.

## Goal4884: Numba Partner Route Decision For RayJoin Reproduction

**Purpose**

Decide whether Numba has a real role in the RayJoin reproduction route beyond
historical partner support.

**Work**

- Identify app-layer stages suitable for Numba:
  - output-chain assembly;
  - point/chain compaction;
  - coordinate formatting prepass;
  - candidate filtering not already inside RTDL native primitives.
- Prototype only the most promising stage if the phase data justifies it.
- If Numba does not improve or is unnecessary, record that honestly.

**Outputs**

- `history/internal_docs/goal4884_rayjoin_numba_partner_decision_2026-07-02.md`

**Exit Gate**

- Numba is either:
  - promoted for a measured stage with correctness preserved; or
  - explicitly not used because public RTDL primitives and Python assembly are
    sufficient for the correctness goal.

## Goal4885: Official Updated RayJoin Reproduction Report

**Purpose**

Close the reproduction line with a coherent report.

**Work**

- Summarize 5.2, 5.3, and 5.7 under AuthorOfficial.
- Include exact-old vs representative-regenerated labeling.
- Include all pair-level correctness results.
- Include performance/phase accounting only where correctness passed.
- Include limitations:
  - missing old exact six Section 5.7 inputs;
  - representative regenerated suite scope;
  - Numba role if limited.

**Outputs**

- `history/internal_docs/goal4885_official_updated_rayjoin_reproduction_report_2026-07-02.md`
- `history/internal_docs/call_for_review_goal4885_official_updated_rayjoin_reproduction_report_2026-07-02.md`

**Exit Gate**

- External review requested.
- Report contains no hidden V3/V4 claims, no Embree claim, no broad speedup
  claim, and no mislabeled exact-paper-input claim.

## Execution Order

1. Goal4876
2. Goal4877
3. Goal4878
4. Goal4879
5. Goal4880
6. Goal4881
7. Goal4882
8. Goal4883
9. Goal4884
10. Goal4885

The first execution target is Goal4876.
