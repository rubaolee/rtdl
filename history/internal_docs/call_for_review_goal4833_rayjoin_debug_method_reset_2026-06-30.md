# Call For Review: Goal4833 RayJoin Debugging Method Reset

Date: 2026-06-30

Requested reviewer: Claude first if available; Antigravity acceptable as review debt if Claude is unavailable.

Requested verdict labels:

- `approve_method_reset_and_authorize_contract_first_debugging`
- `approve_with_required_amendments`
- `block_until_paper_and_author_contract_are_extracted`
- `block_current_line_as_not_scientifically_controlled`

## 0. Why This Review Exists

The current RayJoin reproduction/debugging line has become too inefficient.

The user explicitly stopped the current run and asked for a reset:

> read the paper, study the author code, design experiments, synthesize data, test and compare; current efficiency is too low.

This review asks whether the next work should stop broad/full runs and move to a contract-first debugging plan:

1. Read and extract the exact paper/author-code contract.
2. Build tiny synthetic tests for each contract.
3. Only then return to public sample and County x Zipcode same-source validation.

## 1. Current Boundary

We are not doing V3/V4 work.

Current product context:

- Public project surface has been restored to v2.14.
- V3/V4 work is isolated in `exp-project-1/`.
- This line is RTDL v2.14-era RayJoin paper reproduction/product repair.

Allowed:

- Fix RTDL core semantics if they are generally wrong, especially directed-segment point-location / Simulation-of-Simplicity / numeric robustness.
- Use Python + Numba + RTDL as an application author where applicable.
- Use the author C++/CUDA/OptiX program as the reference.

Forbidden:

- No hidden RayJoin-only kernel disguised as a language feature.
- No changing public docs/tutorial/release surface in this correctness-debugging line.
- No Embree for this line.
- No performance claim until correctness passes.
- No treating old V4/dirty artifacts as evidence.

## 2. Data Sets and Evidence State

### Public sample: County x Soil

Exact author public sample:

- Author input:
  - `/workspace/RayJoin_goal4828_author_deterministic/test/dataset/br_county_clean_25_odyssey_final.txt`
  - `/workspace/RayJoin_goal4828_author_deterministic/test/dataset/br_soil_ascii_odyssey_final.txt`
- Author answer:
  - `/workspace/RayJoin_goal4828_author_deterministic/test/dataset/br_countyXbr_soil_answer.txt`

Current RTDL result:

- Byte-equal: yes.
- Bytes: `16631243`.
- SHA256: `464f87a59cc2428f63cbfe5068965d7bc7adb8eee51e9c1e3a5960ae8b76019e`.

This establishes that the repaired RTDL route can reproduce the smallest decisive public answer.

### County x Zipcode same-source regenerated CDB

This is not exact paper input/answer. It is same-source regenerated CDB from old Goal4806 artifacts:

- Left:
  - `/workspace/rayjoin_section57_same_source_cdb/point_cdb/dtl_cnty/dtl_cnty_Point.cdb`
- Right:
  - `/workspace/rayjoin_section57_same_source_cdb/point_cdb/USAZIPCodeArea/USAZIPCodeArea_Point.cdb`
- Deterministic author baseline generated in Goal4828:
  - `/workspace/rtdl_goal4820_sos_fix/artifacts/goal4828_county_zipcode_author_deterministic/author_deterministic_county_zipcode_overlay.txt`
  - bytes: `2390767769`
  - SHA256: `e8fed3e7e4691c028ee6c8e8a16a74eb06de5a0ffb20cc2b132ce8646b797b2a`

Previous streaming compare after the closer comparator path failed at:

```json
{
  "line": 90411,
  "author": "30138 1 31059 31059 63 110",
  "rtdl": "30138 1 31059 31059 106 107"
}
```

After a direct slope-direction flip experiment, public sample still passed but County x Zipcode became worse:

```json
{
  "line": 25,
  "author": "9 2 8 9 1 2",
  "rtdl": "9 2 8 9 5 6"
}
```

That direct flip was reverted. It should not be treated as product progress.

## 3. Current Code Changes Under Review Context

Relevant modified tracked files:

- `src/native/optix/rtdl_optix_core.cpp`
  - Core directed-segment point-location SoS `t_reported` repair.
  - Comparator direction currently restored to the closer path after the failed flip experiment.
- `src/rtdsl/rayjoin_overlay.py`
  - Per-map midpoint face storage.
  - Output-chain/midpoint logic and a currently unproven intersection sort tie attempt.
- `tests/goal4373_rayjoin_cdb_point_location_route_test.py`
  - Contract assertions for OptiX point-location route.

Important: the simple sort tie attempt did not fix the County x Zipcode first diff. It must not be promoted as solved evidence.

## 4. What Has Been Learned

### 4.1 Public sample correctness is real

The public County x Soil sample is byte-equal after the current core/data-model repairs.

### 4.2 County x Zipcode mismatch is structural, not formatting

The first known mismatch is a face-id difference in an output chain, not a formatting-only mismatch.

### 4.3 Chain 30138 is a boundary/degenerate case

Diagnostics around chain `30138` show a one-point output chain around duplicated/equal intersection coordinates:

- Author expects face pair `63 110`.
- Earlier RTDL streaming path produced `106 107`.
- Local chain events showed adjacent intersections with identical displayed/scaled coordinates.

### 4.4 Single-point point-location probe complicates the diagnosis

After restoring the closer comparator and rebuilding, a direct one-point query at the chain-30138 coordinate:

```text
(-87.97307499999893, 30.859138999999388)
```

returned:

```json
{
  "face_id": 11375,
  "segment_id": 8965020
}
```

This is consistent with the author-side face expected for that local region.

Therefore the remaining issue may not be a simple raw point-location failure. It may be:

- mismatch between direct point query and midpoint generated by overlay path;
- rational-vs-float midpoint coordinate drift;
- intersection sorting/grouping mismatch;
- stale native/library artifact in an earlier run;
- output-chain face remapping / face-id creation order issue;
- or another author-contract mismatch not yet isolated.

The stopped run `goal4834_streaming_full_compare_after_direct_point_location_check` was intended to test this but was halted per user instruction. It has no result and must not be cited as evidence.

## 5. Main Error To Correct

The current debugging has relied too much on expensive full comparisons and reactive patching.

Correct method should be:

1. Paper contract first.
2. Author-code contract second.
3. Synthetic tests third.
4. Public sample regression fourth.
5. Same-source County x Zipcode full stream only after the smaller contracts pass.

This is not just a productivity preference. Without contract-first synthetic tests, the same bug can appear to move between line 25 and line 90411 without proving what changed.

## 6. Required Contract Extraction Before More Fixing

Goal4833 should produce a contract note before additional implementation changes.

It must read and summarize:

- Paper Section 3.2:
  - RT PIP / Simulation-of-Simplicity rule.
  - What is required for deterministic point-location.
- Paper Section 5.7:
  - Polygon overlay workload definition.
  - What is measured vs what is output.
- Author source:
  - `src/algo/rt_pip_custom.cu`
  - `src/algo/pip.h`
  - `src/app/map_overlay_rt.h`
  - `src/app/output_chain.h`
  - any CDB scaling / planar graph loading code needed to explain coordinates and face ids.
- Author response file:
  - `C:/Users/Lestat/Downloads/rayjoin_pip_determinism_summary.md`

The output must distinguish:

- exact paper/source contract;
- author compatibility patch contract;
- RTDL current implementation;
- known gap;
- unresolved hypothesis.

## 7. Required Synthetic Tests

Before another County x Zipcode full stream, build or document tiny synthetic tests for:

1. Equal-height PIP tie with two boundary edges.
   - query_map_id = 0.
   - query_map_id = 1.
   - expected segment choice from author code.
2. Vertex-hit / excluded-endpoint behavior.
   - left endpoint vs right endpoint.
   - query map direction effects.
3. Midpoint construction between adjacent intersections.
   - integer/rational midpoint.
   - float midpoint.
   - same displayed coordinate but different exact rational coordinate.
4. Output-chain flush behavior around:
   - first intersection;
   - duplicated intersections;
   - one-point chain after dedupe;
   - face-id remapping order.
5. Direct point-location vs overlay midpoint path.
   - same coordinate must return the same face when generated as direct query and when generated as midpoint.

Each synthetic test must state:

- author expected result;
- RTDL result;
- whether it is a core semantics test or RayJoin app compatibility test;
- exact file/function involved.

## 8. Proposed Next Goal Sequence

### Goal4833-A: Contract Extraction

Purpose:

- Stop guessing.
- Extract exact paper/source/author-response contract.

Exit:

- `contract_extracted_author_source_mapped`
- or `blocked_by_missing_author_contract`

### Goal4833-B: Synthetic Contract Tests

Purpose:

- Make small deterministic tests for PIP SoS, midpoint construction, and output-chain handling.

Exit:

- `synthetic_contract_tests_pass`
- or `core_semantics_gap_identified`

### Goal4833-C: Public Sample Regression

Purpose:

- Confirm public County x Soil remains byte-equal after any core repair.

Exit:

- `public_sample_byte_equal_preserved`
- or `public_sample_regression_block`

### Goal4833-D: County x Zipcode First-Diff Recheck

Purpose:

- Only after A/B/C, re-run streaming compare against the deterministic author baseline.

Exit:

- `county_zipcode_same_source_stream_match`
- or `county_zipcode_first_diff_localized`

### Goal4833-E: Review Packet

Purpose:

- Summarize whether the repaired RTDL core can fairly continue toward larger Section 5.7 reproduction, or whether this line is blocked by a remaining product gap.

Exit:

- `authorize_next_dataset_or_performance`
- or `close_as_remaining_correctness_gap`

## 9. Reviewer Questions

Please answer:

1. Is the stop/reset justified, given the observed inefficiency and patch-and-run behavior?
2. Is the evidence summary accurate, especially the distinction between public-sample success and County x Zipcode same-source mismatch?
3. Is it correct that no more broad/full County x Zipcode runs should happen before paper/source contract extraction and synthetic tests?
4. Are the proposed synthetic tests the right minimum set?
5. Is there a missing author-code file or contract that must be read before implementation continues?
6. Is the current direct point-location probe result (`face_id=11375`, `segment_id=8965020`) enough to shift suspicion from raw PIP to midpoint/overlay path, or is that premature?
7. Should the simple sort tie attempt in `rayjoin_overlay.py` be kept for now, amended to exact rational distance, or reverted until justified by author-code tests?
8. Does the proposed Goal4833-A through Goal4833-E sequence prevent the previous inefficient debugging pattern?
9. What exact evidence should be required before authorizing another full streaming compare?

## 10. Non-Authorization

This review request does not authorize:

- performance runs;
- full Section 5.7 claims;
- broad RTDL speedup claims;
- V3/V4 work;
- Embree work;
- public docs/tutorial/release surface edits;
- RayJoin-only hidden kernels;
- citing old V4/Goal4806 dirty artifacts as correctness evidence.

It asks only whether to reset the debugging method to paper/source contract extraction plus synthetic tests before further large runs.
