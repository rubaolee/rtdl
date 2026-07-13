# Goal4822 - RayJoin Section 5.7 Exact Input/Answer Availability Audit

Date: 2026-06-30

Status: `goal4822_exact_input_answer_audit_complete_pending_review`

## Purpose

Goal4821 proved a narrow, correctness-gated public-sample result:

- author clean-compat binary and repaired RTDL OptiX helper both produced the
  public County x Soil answer byte-for-byte on 3/3 runs;
- median wall time was `7.702967159450054s` for the author clean-compat binary
  and `4.510876469314098s` for repaired RTDL;
- bounded public-sample ratio was `1.7076431181058986x`;
- the claim was explicitly limited to that public sample.

Goal4822 answers the next gate:

> Are exact Section 5.7 inputs and ground-truth answer files available for
> additional RayJoin polygon-overlay pairs, such that further performance runs
> would be correctness-verifiable?

This goal does not run more performance. It prevents the foolish path of timing
unverifiable outputs.

## Sources Checked

### Author repository on POD

POD:

`root@157.157.221.29 -p 23132`

Author repository:

`/workspace/RayJoin_fresh`

Author `HEAD`:

`02bf6220d6d20b04af77ee20364eced75cc029c9`

Files inspected from author `HEAD`:

- `expr/env.sh`
- `expr/run_overlay.sh`

Author in-repo test dataset scan:

- `/workspace/RayJoin_fresh/test/dataset/br_county_clean_25_odyssey_final.txt`
- `/workspace/RayJoin_fresh/test/dataset/br_soil_ascii_odyssey_final.txt`
- `/workspace/RayJoin_fresh/test/dataset/br_countyXbr_soil_answer.txt`

No other in-repo CDB or answer files were found under `test/dataset`.

### Expected author data root

`expr/env.sh` defines:

`DATASET_ROOT="/local/storage/liang/Downloads/Datasets"`

This path is missing on the current POD.

### Historical RTDL Section 5.7 data roots

Checked:

- `/workspace/rayjoin_section57_data`
- `/workspace/rayjoin_section57_same_source_cdb`

Result:

- `/workspace/rayjoin_section57_data` is missing.
- `/workspace/rayjoin_section57_same_source_cdb` exists but contains only:
  - `point_cdb/dtl_cnty/dtl_cnty_Point.cdb`
  - `point_cdb/USAZIPCodeArea/USAZIPCodeArea_Point.cdb`
  - related RTDL cache files.
- No answer file was found in that same-source root.

### Historical docs

Read:

- `history/internal_docs/goal4816_A_rayjoin_section57_paper_source_contract_extraction_2026-06-30.md`
- `history/internal_docs/goal4816_B_rayjoin_v2_14_asset_capability_map_2026-06-30.md`
- `history/internal_docs/docs_reports/goal4380_v2_14_pod_benchmark_execution_2026-06-14.md`
- `history/internal_docs/goal4821_rayjoin_public_sample_controlled_performance_2026-06-30.md`
- `history/internal_docs/goal4820_artifacts_2026-06-30/goal4821_perf_clean_compat_summary.json`

Goal4380 is valid historical evidence for 2/8 available-input Section 5.7
process-level rows, but it did not provide byte-for-byte answer-file validation
for all eight paper pairs.

## Author Section 5.7 Pair Contract

From `expr/env.sh` and `expr/run_overlay.sh`, the author overlay script expects
the following eight pairs:

| Pair | Author input path pattern |
| --- | --- |
| County x Zipcode | `point_cdb/dtl_cnty/dtl_cnty_Point.cdb` x `point_cdb/USAZIPCodeArea/USAZIPCodeArea_Point.cdb` |
| Block x Water | `point_cdb/USACensusBlockGroupBoundaries/USACensusBlockGroupBoundaries_Point.cdb` x `point_cdb/USADetailedWaterBodies/USADetailedWaterBodies_Point.cdb` |
| LKAF x PKAF | `point_cdb/lakes/Africa/lakes_Africa_Point.cdb` x `point_cdb/parks/Africa/parks_Africa_Point.cdb` |
| LKAS x PKAS | `point_cdb/lakes/Asia/lakes_Asia_Point.cdb` x `point_cdb/parks/Asia/parks_Asia_Point.cdb` |
| LKAU x PKAU | `point_cdb/lakes/Australia/lakes_Australia_Point.cdb` x `point_cdb/parks/Australia/parks_Australia_Point.cdb` |
| LKEU x PKEU | `point_cdb/lakes/Europe/lakes_Europe_Point.cdb` x `point_cdb/parks/Europe/parks_Europe_Point.cdb` |
| LKNA x PKNA | `point_cdb/lakes/North_America/lakes_North_America_Point.cdb` x `point_cdb/parks/North_America/parks_North_America_Point.cdb` |
| LKSA x PKSA | `point_cdb/lakes/South_America/lakes_South_America_Point.cdb` x `point_cdb/parks/South_America/parks_South_America_Point.cdb` |

The script also passes:

- `grid_size=15000`
- `mode=rt`
- `-fau`
- `xsect_factor=0.1`
- `enlarge=3.5`
- `check=true` for RT mode

## Current Availability Matrix

| Workload | Exact input currently on POD | Author answer currently on POD | Current classification | Action |
| --- | --- | --- | --- | --- |
| Public sample: County x Soil | Yes, under `/workspace/RayJoin_fresh/test/dataset` | Yes, `br_countyXbr_soil_answer.txt` | `exact_input_and_answer_available_public_sample` | Already measured by Goal4821; keep bounded claim. |
| Section 5.7 County x Zipcode | Partial: same-source CDB exists under `/workspace/rayjoin_section57_same_source_cdb` | No answer found | `input_without_answer` | Do not run further performance as paper-reproduction evidence. |
| Section 5.7 Block x Water | No current CDB found | No answer found | `missing_input_and_answer` | Blocked. |
| Section 5.7 LKAF x PKAF | No current CDB found | No answer found | `missing_input_and_answer` | Blocked. |
| Section 5.7 LKAS x PKAS | No current CDB found | No answer found | `missing_input_and_answer` | Blocked. |
| Section 5.7 LKAU x PKAU | No current CDB found | No answer found | `missing_input_and_answer` | Blocked. |
| Section 5.7 LKEU x PKEU | No current CDB found | No answer found | `missing_input_and_answer` | Blocked. |
| Section 5.7 LKNA x PKNA | No current CDB found | No answer found | `missing_input_and_answer` | Blocked. |
| Section 5.7 LKSA x PKSA | No current CDB found | No answer found | `missing_input_and_answer` | Blocked. |

## Relationship To Goal4380

Goal4380 remains important and valid, but it must be read narrowly:

- it reported two exact-ready Section 5.7 rows available at that time:
  - County x Zipcode;
  - Block x Water;
- it reported local author process wall and RTDL OptiX/Embree totals;
- it reported `Count Match=True` for those two rows;
- it explicitly stated that full Section 5.7 remained blocked by missing exact
  inputs.

Goal4380 does not, by itself, provide the stronger Goal4821-style criterion:

- exact answer file present;
- author binary byte-equal to answer;
- RTDL output byte-equal to answer on every run.

Therefore Goal4822 does not authorize reviving the 2/8 historical rows as
current exact output-chain reproduction claims unless the exact inputs and
author answers are restored and revalidated.

## Decision

Additional Section 5.7 performance runs are blocked in the current POD state.

The correct current claim is:

> RTDL now has one bounded, correctness-gated public-sample RayJoin overlay
> reproduction and performance smoke: County x Soil, byte-equal to the author
> public answer, with repaired RTDL measuring `1.7076431181058986x` faster than
> the clean-compat author binary on that sample.

The blocked claim is:

> RTDL has reproduced and benchmarked the full Section 5.7 eight-pair polygon
> overlay matrix.

That claim remains blocked by missing exact Section 5.7 inputs and answer files
in the current environment.

## Recommended Next Goal

Proceed to Goal4823 as a closure packet unless the exact Section 5.7 CDB inputs
and author answer files are restored.

Goal4823 should:

1. preserve the Goal4820 core/product fixes;
2. preserve the Goal4821 bounded public-sample performance result;
3. state that full eight-pair Section 5.7 reproduction is blocked by missing
   exact inputs/answers;
4. list what external data would be required to reopen the line;
5. avoid any broad RayJoin-paper or whole-system performance claim.

If exact Section 5.7 inputs and author answers become available later, the next
run goal should be opened with a fresh correctness gate before performance.

## Goal-Level Decision Audit

1. **Am I being foolish?**
   No. This goal refuses to run performance where correctness cannot be checked.

2. **What would make this foolish?**
   It would be foolish to use historical count-match evidence as byte-equal
   output-chain evidence, or to time same-source CDB inputs without answer files
   and call it paper reproduction.

3. **Is there another path that avoids being trapped in one bad idea?**
   Yes. Close the current line honestly at bounded public-sample reproduction,
   or reacquire exact inputs and author answers before expanding.

4. **Can I start a different path that actually solves the problem?**
   Yes. The useful product path is to keep the core SoS/data-model repair and
   add a future data-acquisition goal for the missing Section 5.7 artifacts.

## Exit Label

`goal4822_exact_input_answer_audit_complete_pending_review`
