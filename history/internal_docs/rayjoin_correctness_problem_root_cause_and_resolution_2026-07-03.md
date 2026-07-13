# RayJoin Correctness Problems: Root Cause, Debugging Cost, And Resolution

Date: 2026-07-03

Status: prepared for Claude review.

## Purpose

This document explains why the RayJoin reproduction work took several days,
what correctness problems were actually exposed, what the root causes were, how
they were fixed or bounded, and why the final Section 5.2 / 5.3 / 5.7 result is
now credible.

The short version:

```text
The hard part was not "running RayJoin." The hard part was discovering that
several apparently small geometric degeneracy contracts were different across
the old author behavior, the author's intended behavior, and released RTDL.
Those contracts sit exactly where RT hardware traversal, exact planar-map
topology, and application output-chain assembly meet.
```

## Final Outcome

After the corrections and bounded evidence:

- Section 5.2 LSI count reproduction is valid for the available tested pairs.
- Section 5.3 PIP / point-location is exact for the two serious recovered US
  workloads and count-consistent for the Australia representative pair.
- Section 5.7 overlay is reproduced in a bounded form: two available
  paper-style full-stream pairs plus two current-source Lakes/Parks
  representative pairs.

This does **not** claim:

- full hidden-input all-eight reproduction;
- broad speedup over the author implementation;
- Numba as correctness-critical;
- Embree results;
- that current-source representative OSM data equals the old hidden paper data.

## Why Correctness Took Days

The delay had three structural causes.

### 1. The visible failure was downstream, but the cause was not obviously downstream

The first visible symptom was a full overlay output mismatch. That output is a
long stream of chains, points, and faces. A missing 2-point chain near the
beginning can shift many later chain ids and make the diff look catastrophic.

Goal4818 showed that the first public-sample mismatch was not just formatting:

- author output chains: `64,459`
- RTDL output chains: `64,453`
- RTDL had no extra coordinate records;
- RTDL was missing six 2-point output chains;
- the omissions cascaded into many later chain/face differences.

At that stage, a full-output diff did not say whether the defect was in:

- LSI intersection discovery;
- LSI row materialization;
- PIP / point-location;
- midpoint construction;
- face-id assignment;
- duplicate half-edge selection;
- output-chain assembly.

Those are separate contracts. Treating them as one "RayJoin output differs"
bug would have led to blind patch-and-run work.

### 2. Scalar success did not imply row/output success

Section 5.2 count-only LSI could be correct while Section 5.7 still failed.
Later Goal4859 exposed the clearest form of this:

```text
minimal witness:
  scalar LSI count = 2
  LSI rows emitted = 0
```

That proved a key point:

```text
count correctness != row-materialization correctness
```

Section 5.7 needs actual intersection rows and coordinates, not just a scalar
count. Therefore the project had to add a row-surface gate before overlay work
could be trusted.

### 3. The author source itself exposed intended-vs-actual ambiguity

The author reply and source made clear that point-location determinism depends
on a Simulation-of-Simplicity rule:

```text
query map 0: prefer larger slope
query map 1: prefer smaller slope
```

and the priority must be encoded into reported hit distance (`t_reported`) so
RT traversal pruning does not discard the intended candidate before shader-side
tie-breaking can run.

Released RTDL did not implement that intended contract:

- its equal-height slope preference was opposite;
- its equal-ties knob only used `nextafterf(report_t, +inf)`;
- it did not encode the slope-dependent priority into `t_reported`.

The original author binary could also be nondeterministic on equal-height /
duplicate-half-edge cases. Therefore "match one old output file" was not always
the right correctness target. The project had to define:

```text
AuthorOfficial = Author+RTDLContractPatch
```

and compare against a deterministic contract rather than chasing a
hardware/order-dependent old run.

That comparator has two different kinds of content:

- **Author-derived content**: the directed point-location / PIP SoS rule. The
  author clarification and source indicate that query map 0 prefers larger
  slope, query map 1 prefers smaller slope, and that this priority must be
  reflected in reported hit distance so traversal pruning cannot discard the
  intended candidate.
- **RTDL-defined deterministic content**: duplicate-half-edge canonicalization.
  This rule was added to make identical or opposite half-edge witnesses
  deterministic. It is a defensible planar-map contract, but it is not
  independent evidence of original unpatched author behavior because the same
  rule is applied to the author comparator and to RTDL.

Therefore later equality against `AuthorOfficial` means deterministic-contract
agreement. It must not be shortened to "raw author output reproduction" when
the duplicate-half-edge rule is involved.

## Correctness Problems Found

### Problem A: PIP / point-location SoS tie policy mismatch

Symptom:

- RTDL missed output chains and failed byte equality on the public County x Soil
  sample before repair.
- Existing `RTDL_RAYJOIN_CDB_ALLOW_EQUAL_TIES=1` did not change the output.

Root cause:

- RTDL's equal-height directed point-location comparator did not match the
  author's intended map-dependent slope preference.
- The priority was not encoded into `t_reported`, so OptiX traversal depth
  pruning could make shader-level tie-breaking too late.

Fix:

- Align RTDL OptiX directed point-location with the intended SoS contract:
  map 0 prefers larger slope, map 1 prefers smaller slope.
- Encode the priority into reported hit distance.
- Add synthetic contract tests before relying on full POD runs.

Evidence:

- Goal4834 synthetic gate: `12` tests passed locally and on POD.
- Rebuilt RTDL public County x Soil sample became byte-equal:
  SHA256 `464f87a59cc2428f63cbfe5068965d7bc7adb8eee51e9c1e3a5960ae8b76019e`.

### Problem B: Midpoint face state overwrite

Symptom:

- The public sample had missing chains / face differences even when LSI count
  matched.

Root cause:

- Overlay midpoint face state was stored in one shared field. Map 1 assignment
  could overwrite map 0 assignment on the same intersection object.

Fix:

- Store midpoint face ids separately per directed map:
  `mid_point_polygon_id_map0` and `mid_point_polygon_id_map1`.

Why this is generic:

- Directed overlay continuation needs distinct per-map midpoint classifications.
  This is not a RayJoin-only shortcut; a single shared field is wrong for any
  directed overlay path that reuses the same intersection object across both
  maps.

Evidence:

- Goal4820 review approved this as a product/data-model repair.
- Tests included `test_overlay_midpoint_faces_are_stored_per_map`.

### Problem C: Nonfinite midpoint / query coordinates

Symptom:

- County x Zipcode current-line revalidation could crash when midpoint points
  contained `nan`, `inf`, or `-inf`.

Root cause:

- Some LSI rows produced nonfinite coordinates. Passing those into native
  point-location violates a general product invariant: native point-location
  query points must be finite.

Fix:

- Filter/drop nonfinite midpoint rows with telemetry.
- Keep midpoint owners synchronized when rows are filtered.

Evidence:

- Goal4826 found:
  - `69` nonfinite LSI rows;
  - `26` map0 nonfinite midpoints;
  - `24` map1 nonfinite midpoints.
- Added tests:
  - `test_lsi_midpoint_projection_drops_nonfinite_points_with_telemetry`
  - `test_output_chain_midpoint_projection_drops_nonfinite_points_with_telemetry`

### Problem D: Rational midpoint vs displayed/rounded midpoint drift

Symptom:

- Direct probes using displayed float coordinates could suggest one face id,
  while overlay midpoint construction could produce another.

Root cause:

- The author uses exact/rational midpoint construction before truncating to
  internal coordinates. Averaging already-rounded/displayed coordinates can
  change midpoint classification.

Fix:

- Preserve rational scaled intersection coordinates where needed.
- Compute midpoints using exact/rational values before truncation.

Evidence:

- Goal4827 external review approved rational intersection preservation as
  aligned with the author `ExactPoint` midpoint construction.

### Problem E: Old author output was sometimes a moving target

Symptom:

- A mismatch could move from early output line to a much later output line.
- Some old baseline files were same-source regenerated clues, not deterministic
  ground truth.

Root cause:

- The old author behavior did not always encode the intended tie-break into
  traversal-reported distance. RT traversal order could choose among equal
  candidates differently.

Fix:

- Stop tuning to nondeterministic old output.
- Build and compare against `AuthorOfficial`, the author source plus
  deterministic contract patch.
- Keep the two patch categories separate: author-derived SoS behavior is
  reproduction of the clarified author contract; RTDL-defined duplicate
  half-edge canonicalization is deterministic-contract consistency.

Evidence:

- Goal4827 concluded the old same-source author-output file should be treated
  as a debug clue, not deterministic byte-equality truth.
- Later Section 5.2 / 5.3 / 5.7 evidence uses AuthorOfficial boundaries.

### Problem F: LSI scalar count vs LSI row materialization mismatch

Symptom:

- Section 5.2 count evidence could pass, but Section 5.7 could still lack the
  intersection rows needed for overlay reconstruction.

Root cause:

- The count path and row-finalization path were not always applying the same
  planar-map LSI contract under degenerate/endpoint cases.

Fix:

- Treat this as a generic planar-map LSI row-surface repair.
- Require gates such as:

```text
planar_map_lsi_count == planar_map_lsi_rows.length
```

Evidence:

- Goal4859 minimal witness: `count=2`, `rows=0`.
- Goal4860 was authorized to repair this as generic LSI row behavior before
  Section 5.7 proceeded.

### Problem G: Duplicate half-edge deterministic face selection

Symptom:

- Overlay face ids could disagree even when geometry and point ids matched.

Root cause:

- Identical geometry can appear as duplicate or opposite half-edges with
  different face associations. Without a deterministic canonical edge/face
  rule, two correct-looking geometric witnesses can imply different faces.

Fix:

- Define a deterministic duplicate-half-edge canonicalization contract.
- Apply the same contract to the AuthorOfficial comparator and RTDL path.

Why this is acceptable:

- The rule is a general deterministic planar-map overlay contract. It is not a
  hidden "RayJoin kernel"; it says how a planar-map implementation resolves
  duplicate half-edge ambiguity.
- It is, however, RTDL-defined. It is not proven to be the original author's
  unpatched behavior. Results depending on this rule should be described as
  deterministic-contract consistency, not as independent raw-author
  reproduction.

Evidence:

- `history/internal_docs/goal4868_author_rtdl_contract_patch.diff`
- later full-stream and representative Section 5.7 byte-equality evidence.

Impact status:

- County x Zipcode retained the same checked full-stream output after duplicate
  contract revalidation: `0 / 87,758,114` output lines changed in that stream.
- Block x Water has targeted witness evidence that at least two probed
  duplicate-half-edge cases changed semantics under the canonicalization rule.
  The full old-comparator-vs-new-comparator impact count is not yet quantified.
- Australia/South America representative Section 5.7 equality is against the
  patched deterministic comparator, not raw old author output.

## What Changed In The Debugging Method

The early failure mode was broad, expensive full-output comparison without a
small enough contract witness. That made the work look busy while not always
reducing uncertainty.

The corrected method was:

1. **Read paper, author source, and author clarification.**
2. **Extract the exact contract for one layer.**
3. **Build a minimal synthetic reproducer for that contract.**
4. **Only then patch generic RTDL behavior if old behavior is proven wrong.**
5. **Run a small public sample.**
6. **Then scale to available/recovered or representative data.**
7. **Keep performance blocked until correctness passes.**

Claude's Goal4833 review made this explicit:

```text
contract -> minimal reproducer -> regression -> scale
```

and warned that:

```text
"It made RayJoin pass" is not a valid reason to change core behavior.
```

This became the rule for distinguishing generic RTDL correctness repairs from
RayJoin-specific patching.

## Why The Fixes Are Not RayJoin-Only Hidden Kernels

The fixes are legitimate only because they repair app-independent contracts:

| Fix | Generic contract repaired | Not allowed interpretation |
| --- | --- | --- |
| SoS `t_reported` priority | deterministic directed point-location under equal-depth candidates | hidden RayJoin point-location kernel |
| per-map midpoint face ids | directed overlay continuation state must keep both map classifications | RayJoin-specific output-chain shortcut |
| nonfinite midpoint filtering | native point-location query points must be finite | silently skipping RayJoin records |
| rational midpoint construction | exact planar-map midpoint before truncation | tuning to one output file |
| LSI count/row parity | scalar count and row materialization must share one planar-map LSI contract | app-layer coordinate recovery hack |
| duplicate half-edge canonicalization | RTDL-defined deterministic planar-map face selection for identical geometry | independent proof of raw unpatched author behavior |

One subtle boundary remains: the SoS rule is map-id dependent. That makes it
best described as a **directed two-map planar-overlay point-location contract**,
not as a universal standalone point-location rule for every possible geometry
API. It is appropriate for RTDL's planar-map overlay route, but public wording
should not imply that this exact map0/map1 policy is a general-purpose PIP
semantic outside the directed overlay setting.

The application layer remains responsible for:

- CDB loading and preprocessing;
- paper-compatible command parameters;
- output-chain formatting;
- exact-vs-representative labeling.

## Current Evidence After Resolution

### Section 5.2

| Pair | AuthorOfficial LSI count | RTDL public LSI count | Result |
| --- | ---: | ---: | --- |
| County x Zipcode | 961,165 | 961,165 | match |
| Block x Water | 649,605 | 649,605 | match |
| Australia Lakes x Parks representative | 13,622 | 13,622 | match |

### Section 5.3

| Pair | Count match | Closest-edge hash match | Classification |
| --- | --- | --- | --- |
| County x Zipcode | yes | yes | exact per-point closest-edge match |
| Block x Water | yes | yes | exact per-point closest-edge match |
| Australia Lakes x Parks representative | yes | no | count-consistent only |

### Section 5.7

| Pair | Result | Classification |
| --- | --- | --- |
| County x Zipcode | exact full-stream match | available paper-style pair; no observed output change from duplicate-half-edge contract revalidation |
| Block x Water | exact full-stream match | available paper-style pair; deterministic-contract consistency because duplicate-half-edge canonicalization is in the comparator |
| Australia Lakes x Parks | byte-equal | current-source representative against AuthorOfficial |
| South America Lakes x Parks | byte-equal | bounded current-source representative against AuthorOfficial |

Evidence-strength ordering:

1. Section 5.3 County x Zipcode and Block x Water raw `query_exec` per-point
   closest-edge hash matches are the strongest non-circular evidence.
2. Section 5.7 matches against `AuthorOfficial` are valid deterministic
   contract evidence, but any duplicate-half-edge-dependent row inherits the
   RTDL-defined-contract caveat.
3. Representative current-source rows are useful reproduction engineering
   evidence, not hidden old paper-input reproduction.

## Remaining Limits

The correctness work is substantial, but it does not remove all limits:

1. The remaining old hidden paper-preprocessed continent CDB inputs are not
   available in the current public workspace.
2. Representative current-source OSM data is not the same claim as exact old
   hidden paper input.
3. Current evidence is correctness-first; performance is not optimized.
4. Python CDB loading/packing and output-chain assembly remain performance debt.
5. Numba is not yet on the correctness-critical path; future Numba work should
   target app-layer acceleration only if it removes a real bottleneck.

## Lessons

1. **Do not equate count equality with row/output equality.**
   Section 5.2 scalar count success was necessary but insufficient for Section
   5.7 overlay.

2. **Do not tune to unstable old outputs, but name the comparator precisely.**
   The correct comparator is a deterministic author-contract comparator. Its
   author-derived and RTDL-defined pieces must stay separated in wording.

3. **Do not use full-stream diffs as the first debugger.**
   Full-stream diffs are excellent final gates, but poor first tools because a
   small omission causes massive downstream shifts.

4. **Core fixes require synthetic contract proof.**
   A core change must be justified by a generic contract and a minimal
   reproducer, not by "RayJoin passes now."

5. **Keep bundled helper, public primitive, and app logic separate.**
   The project only became clean once public LSI/PIP front doors replaced
   bundled helper evidence for the representative route.

## Files To Review

Primary diagnosis and repair:

- `history/internal_docs/goal4818_rayjoin_public_sample_correctness_gap_diagnosis_2026-06-30.md`
- `history/internal_docs/goal4819_rayjoin_user_mode_reproduction_closure_packet_2026-06-30.md`
- `history/internal_docs/goal4834_completion_report_2026-06-30.md`
- `history/internal_docs/claude_goal4833_method_reset_review_2026-06-30.md`
- `history/internal_docs/goal4868_author_rtdl_contract_patch.diff`

Reproduction summaries:

- `history/internal_docs/rayjoin_sections_52_53_57_reproduction_report_2026-07-03.md`
- `docs/release_reports/v2_14/rayjoin_section57_bounded_reproduction.md`

Selected reviews:

- `history/internal_docs/antigravity_goal4820_core_directed_segment_point_location_and_overlay_midpoint_fix_review_2026-06-30.md`
- `history/internal_docs/antigravity_goal4826_county_zipcode_current_revalidation_review_2026-06-30.md`
- `history/internal_docs/antigravity_goal4827_county_zipcode_same_source_status_review_2026-06-30.md`
- `history/internal_docs/antigravity_goal4859_lsi_row_surface_gap_review_2026-07-02.md`
- `history/internal_docs/antigravity_goal4883_section57_final_bounded_reproduction_packet_review_2026-07-03.md`

## Reviewer Questions For Claude

1. Does this document correctly identify the main correctness problems, or does
   it omit any decisive root cause?
2. Is the explanation for why this took several days technically fair?
3. Does the document distinguish generic RTDL core repairs from RayJoin-specific
   app logic strongly enough?
4. Does it correctly explain why LSI count success was not enough for Section
   5.7 overlay?
5. Does it correctly explain the AuthorOfficial comparator decision?
6. Does it avoid turning the bounded reproduction result into an all-eight or
   performance claim?
7. What amendments are required before this should be treated as the canonical
   correctness postmortem?
