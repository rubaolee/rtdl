# Goal4962 Larger Representative Input Run Blocked

Date: 2026-07-04

## Exit Label

`blocked_by_representative_input_availability__no_unverified_large_run`

## Purpose

Goal4962 was intended to run the fresh writer-free binary overlay route on a
larger representative input after the public County x Soil sample.

Goal4961 established that the current POD does not contain the required larger
representative inputs. Goal4962 therefore closes as a documented no-run rather
than fabricating, substituting, or silently regenerating data.

## Dependency

Goal4961 audited input availability across the active POD and found only the
public sample:

```text
Paper-reproduction-apps/rayjoin-paper/_data/public_sample/br_county_clean_25_odyssey_final.txt
Paper-reproduction-apps/rayjoin-paper/_data/public_sample/br_soil_ascii_odyssey_final.txt
Paper-reproduction-apps/rayjoin-paper/_data/public_sample/br_countyXbr_soil_answer.txt
data/public_sample_manifest.json
```

Historical larger-input paths checked by Goal4961 were missing, including:

```text
/workspace/goal4881_section57_south_america/...
/workspace/rayjoin_section57_same_source_cdb/...
/workspace/rtdl_goal4806_fast_min/...
/workspace/goal4848_rep/...
/workspace/rayjoin_section57_data/...
```

A bounded scan of `/root`, `/workspace`, `/tmp`, and `/dev/shm` found no larger
representative CDB pair available for a valid run.

## Decision

Do not run Goal4962 on invented or weakly substituted data.

The correct status is:

```text
blocked_by_representative_input_availability
```

This is a cleaner result than a fake large-input benchmark.

## What Would Unlock This Goal

At least one of the following must be restored:

1. the Goal4881 South America bounded representative pair,
2. the previous same-source County x Zipcode CDB pair,
3. the previous Block x Water CDB pair,
4. the Australia representative pair,
5. another documented representative pair with a manifest explaining source,
   preprocessing, size, and whether it is exact-paper or representative data.

Minimum required manifest:

```text
left_path
right_path
source_dataset
preprocessing_steps
exact_paper_input_or_representative
expected semantic fingerprint if known
author/comparator availability if known
```

## Not Authorized

- No larger representative performance claim.
- No "all Section 5.7" claim.
- No hidden substitution of public sample results as larger-data results.
- No regenerated-data result without manifest labeling it as representative.
- No performance ratio without stating the comparator and data boundary.

## Carry-Forward

Goal4966 should preserve this status as:

```text
Goal4962: blocked by input availability, no run performed.
```
