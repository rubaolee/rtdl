# Goal4889: Traversal Work-Count Measurement Gate

Date: 2026-07-03

Status: `active_measurement_goal__no_engine_implementation`

## One-Line Goal

Measure or derive the traversal work counts needed to decide whether RTDL's
RayJoin hot-path gap is caused by **more candidates/tests** or by **slower work
per candidate/test**.

## Why This Goal Exists

Goal4888 established that the current RTDL+Numba Section 5.7 hot path is native
RT traversal dominated:

```text
RTDL+Numba v2 core query compute: 18.880 s
LSI public rows:                  5.667 s
vertex PIP traversal:            11.314 s
```

Claude accepted the measurement-first plan but added the required amendment:

```text
AM1: measure traversal WORK, not just traversal TIME.
```

This goal executes that amendment.

The critical distinction:

1. If RTDL traverses far more candidates than AuthorPatch, then the main
   missing feature is in-traversal pruning / operator pushdown / data-flow
   fusion.
2. If RTDL traverses roughly the same number of candidates but is much slower
   per test, then the main missing feature is native kernel optimization.

The next high-performance direction depends on this measurement.

## Scope

This goal is measurement and evidence only.

Allowed:

- inspect existing RTDL summaries, logs, and source;
- inspect AuthorPatch logs and source;
- derive work counts from existing artifacts if available;
- run read-only or external-harness measurements if necessary;
- add temporary scripts under `history/internal_docs/` or `tools/tmp/`;
- produce a phase/work-count ledger and decision report.

Forbidden:

- modify `src/rtdsl/**`;
- modify `src/native/**`;
- change the AuthorPatch comparator;
- add prepared sessions;
- add row-buffer ABI;
- add Numba partner API;
- add native kernel optimizations;
- add raw callback APIs;
- add RayJoin-specific fast paths;
- claim performance improvement.

## Measurement Questions

For RTDL and AuthorPatch, measure or derive:

1. LSI query segment count.
2. LSI candidate / intersection-test count.
3. LSI accepted hit count.
4. PIP query point count.
5. PIP ray / edge candidate count.
6. PIP accepted / closest-hit count.
7. rejected candidate count where available.
8. per-query candidate distribution if available:
   - min;
   - median;
   - mean;
   - p95;
   - max.
9. time per candidate/test where counts and timings are comparable.

## Primary Dataset

Use the same Australia representative Section 5.7 dataset used by Goal4886:

```text
left:  lakes_Australia_current_osm_Point.cdb
right: parks_Australia_current_osm_Point.cdb
comparator: AuthorOfficial / Author+RTDLContractPatch output
```

Primary RTDL artifact:

```text
history/internal_docs/goal4886_pod_numba_au_skip_v2_summary.json
```

## Work Plan

### Step 1: Existing Evidence Inventory

Search current artifacts for:

- explicit candidate/test counters;
- hit counters;
- LSI row counts;
- PIP query point counts;
- native timing subfields;
- author-side candidate/hit logs;
- source symbols that expose counters.

Output:

```text
history/internal_docs/goal4889_existing_work_count_inventory_2026-07-03.md
```

### Step 2: Source-Level Counter Map

Inspect RTDL and AuthorPatch source to identify where work counts are generated
or could be counted without changing product semantics.

Output:

```text
history/internal_docs/goal4889_counter_source_map_2026-07-03.md
```

### Step 3: Existing-Derived Work Ledger

If existing artifacts are enough, compute:

```text
history/internal_docs/goal4889_work_count_ledger_2026-07-03.json
history/internal_docs/goal4889_work_count_ledger_2026-07-03.md
```

If they are not enough, state exactly which counters are missing.

### Step 4: Decide Whether A Rerun/Instrumentation Is Needed

If missing counters are essential, propose the smallest safe measurement:

- external harness only if possible;
- source patch only if unavoidable, isolated as instrumentation, not product;
- no public claim;
- no runtime/API feature work.

Output:

```text
history/internal_docs/goal4889_measurement_gap_and_next_probe_2026-07-03.md
```

## Decision Labels

Goal4889 should end with one of:

- `work_count_available__rtdl_more_candidates__fusion_pushdown_supported`
- `work_count_available__same_candidates__kernel_tuning_supported`
- `work_count_mixed__needs_targeted_probe`
- `work_count_unavailable__instrumentation_required`
- `blocked_by_missing_author_or_rtdl_counter_access`

## Acceptance Criteria

Goal4889 succeeds if it produces:

1. a documented inventory of existing counter evidence;
2. a source-level counter map;
3. either a work-count ledger or a precise missing-counter report;
4. a decision label explaining whether next work should be fusion/compiler,
   native kernel tuning, or more instrumentation;
5. no RTDL core/native implementation changes.

## Goal-Level Decision Audit

1. **Am I being stupid?**

   The stupid path would be to infer "we need a fusion compiler" from timing
   alone without measuring whether RTDL is traversing more candidates.

2. **What action would make this stupid?**

   Starting Branch B implementation before candidate/test counts are known.

3. **Is there another path that avoids being stuck?**

   Yes. First inspect existing evidence and source. If counters are not
   available, design the smallest measurement-only probe.

4. **Can I start a better path now?**

   Yes. This goal is the better path: count work before optimizing work.

## Non-Authorization

This goal does not authorize:

- implementing prepared sessions;
- implementing row-buffer ABI;
- implementing Numba partner API;
- implementing native kernel changes;
- exposing callbacks;
- adding RayJoin-specific engine paths;
- changing public docs or release claims.
