# External Review (Verified): Goal5095 Amended RT-DBSCAN Component-Partition Gate

Date: 2026-07-07
Reviewer: external review (Claude)
Amendment response reviewed: `history/internal_docs/goal5095_review_amendment_response_2026-07-07.md`

## Verdict

```text
approve_goal5095_amended_component_partition_gate
```

Blocking findings: none.
Required amendments: none.

The prior strict-review blocking finding (BF-1) is resolved substantively, not
cosmetically. The gate now performs a label-renaming-invariant partition
comparison, requires it as a hard conjunct of `matched`, and is protected by a
regression test that reproduces the exact border-swap failure mode the original
review identified. Live POD evidence shows the partition check passing on both
fixtures.

## What the prior review required

- RA-1 (mandatory): remove the "covers border assignment" overclaim, because the
  signature `{core_count, sorted(component_sizes), noise_count}` is invariant to a
  border point moving between components of complementary sizes.
- RA-2 (strong): add a partition-equivalence comparison using the author's
  available per-point labels, independent of the author's representative label IDs.

## Verification performed (against real files)

1. Gate now uses the label-producing generic route.
   `run_authorofficial_component_signature_gate.py` line 152 calls
   `radius_graph_components_3d_optix_numba_prepared_grouped_stream_partner_columns`
   (not the count-only `_component_signature_` route) and reads per-point
   `component_labels` (line 162). The OptiX+Numba route now emits per-point labels.

2. `matched` hard-requires partition equality.
   Line 292: `matched = bool(signature_matched and component_partition_matched and
   (core_flags_matched is not False))`. Both the author-side and RTDL-side per-point
   labels are canonicalized by first-occurrence relabeling with `-1` preserved
   (`_canonical_partition_labels`), and the author labels are cross-checked against
   the author signature fields (raises on inconsistency).

3. Regression test reproduces the exact reported counterexample.
   `test_canonical_partition_detects_border_swap_that_signature_misses`
   (goal5094 test, lines 81-92):
   - `expected      = [0,0,0,0,0,0,1,1,1,1,1,-1]`
   - `border_swapped = [1,0,0,0,0,0,1,1,1,1,1,-1]`
   - `assertEqual(expected_signature, swapped_signature)` proves the signature is
     blind to the swap (sizes [6,5] and [5,6] both sort to [5,6]).
   - `assertNotEqual(canonical_partition(expected), canonical_partition(border_swapped))`
     proves the canonical partition detects it.

4. Live POD evidence upgraded.
   `authorofficial_component_signature_border_noise_pod_optix_summary.json`
   (schema `rtdl.paper_reproduction.rt_dbscan.authorofficial_component_partition_gate.v2`):
   `signature_matched=true`, `component_partition_matched=true`,
   `core_flags_matched=true`, `matched=true`. Author and RTDL
   `canonical_component_labels` are both `[0,0,0,0,0,0,1,1,1,1,1,-1]`, so the border
   point (index 0) is verified to be in the same component in both author and RTDL,
   with `core_flags=[0,1,1,1,1,1,1,1,1,1,1,0]`. This closes the per-point
   border-assignment agreement that the original signature-only gate could not.

## Non-blocking notes

- The `core_flags_matched is not False` clause allows graceful degradation when the
  author payload omits core_flags; `signature_matched` and
  `component_partition_matched` remain hard-required as True. On this POD run all
  three are True, so no effect.
- The border/noise POD summary file is truncated at its tail in the review sandbox
  (`stdout_tail` control characters plus a sync artifact), so full JSON parsing
  failed there; the top-level fields above were confirmed by direct reads/greps of
  the real file. The `Ran 8 tests OK` suite was not re-executed locally.

## Answers to the amended review questions

1. Yes. The border/noise fixture includes a border point (index 0) and a distant
   noise point (index 11), verified from the CSV geometry.
2. The border ordering rationale (border before its core neighbor; author call-2
   `xID > primID`) is an app-level fixture-construction detail; it justifies why the
   fixture exercises the author border path. Border-assignment agreement is now
   validated by the partition check, not merely asserted.
3. Yes. POD author raw sizes [6,5] normalize to [5,6]; core_count=10; noise_count=1;
   RTDL signature and partition both match; `matched=true`.
4. Now correct. The gate uses label-renaming-invariant partition equivalence, which
   is stronger than the signature and independent of exact author label IDs. This is
   the right middle level between exact-ID parity (too strict) and signature-only
   (too weak).
5. Yes. The RTDL route stays generic
   (`radius_graph_components_3d_optix_numba_prepared_grouped_stream_partner_columns`);
   no RT-DBSCAN core primitive was added. DBSCAN appears in core only in the app
   support matrix, which itself disclaims per-point core-flag / full DBSCAN clustering.
6. Yes. Full DBSCAN label parity, exact paper input reproduction, and performance are
   all unauthorized; the previous border-assignment overclaim is removed.
7. Yes. The tests now protect border/noise semantics: partition equality is required,
   and the border-swap regression proves the check catches the exact signature-blind
   failure mode.
8. Acceptable. Goals5093-5095 may be sent as a consolidated RT-DBSCAN bounded-line
   packet, carrying the bounded component-partition scope (not full DBSCAN parity).

## Conclusion

BF-1 is genuinely resolved: partition equivalence is now a required, ID-independent
check that catches the border-swap counterexample and passes end-to-end on live POD.
Goal5095 is approved under its bounded component-partition claim boundary.
