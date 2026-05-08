## Review: Goal 1566 Output-Indexed Merge-Path Design

---

### Verdict

The partition conditions are **algorithmically correct** for the stated stable-merge semantics. The second merge-path lookup for the predecessor row is a **safe diagnostic choice**. The design is sound as a diagnostic-only kernel with the caveats listed below.

---

### Agreement

**Partition condition.** The two-sided condition

```
first_rows[i - 1] <= second_rows[j]   (non-strict)
second_rows[j - 1] < first_rows[i]    (strict)
```

is the standard merge-path invariant that encodes exactly this stable ordering: first-segment equal rows precede second-segment equal rows. The correspondence to `lower_bound`/`upper_bound` is exact:

- `lower_bound(second_rows, first_value)` returns the first `j` where `second_rows[j] >= first_value`, i.e. all prior second rows are `< first_value` — this is the strict condition.
- `upper_bound(first_rows, second_value)` returns the first `i` where `first_rows[i] > second_value`, i.e. all prior first rows are `<= second_value` — this is the non-strict condition.

The asymmetry (`<=` on the first side, `<` on the second) is not a typo; it is the discriminator that places equal first rows before equal second rows.

**Row-selection condition.** The output selection uses `first_value <= second_value` (non-strict), consistent with the partition's first-side `<=`. This must remain exactly consistent with the partition; any drift between the two would silently produce wrong rows without a sort-order violation.

**Second merge-path lookup for predecessor.** Computing `local_index - 1` via a second independent binary search is deterministic and operates only on read-only input arrays. There are no shared-memory races or ordering dependencies between the two lookups. It is the correct safe choice for a diagnostic where the goal is verified parity, not throughput.

---

### Caveats

1. **`local_index = 0` has no predecessor.** The mark comparison must be special-cased. The most defensible choice is to treat position 0 as always marking a new run (mark = 1), but this must match whatever convention the current mark kernel uses for the first output row of a pair.

2. **`i = 0` and `j = 0` must skip the respective `[i-1]`/`[j-1]` guards.** When the binary search lands at either boundary, those array accesses are out-of-range and the corresponding half of the invariant should be treated as unconditionally satisfied.

3. **Row-selection `<=` must be bit-for-bit identical to the partition's first condition.** If the comparison type or NaN/sign-bit treatment differs between the partition binary search and the final output selection, the selected row will disagree with the partition split — producing wrong rows silently in equal-value cases.

4. **The second merge-path lookup must use the same pair's input pointers.** Pair metadata (base pointers, `first_count`, `second_count`) must be available to each thread for both lookups. If pair descriptors are read from a table, both accesses must reference the same table entry without aliasing.

5. **Equal values crossing segment boundaries are the hardest correctness case.** A partition implemented with `<` where `<=` is required (or vice versa) will appear correct on inputs with no equal cross-segment values. The correctness case list in § Correctness Cases already names this; it must be the first hand-verified case before any block-size or timing variation is tested.

6. **Partial final blocks per pair.** `first_count + second_count` will rarely divide evenly by the CUDA block size. The shared-memory reduction for `block_counts[blockIdx.x]` must guard against out-of-range threads contributing to the reduction. This is the same guard the current mark kernel uses and must be replicated faithfully.

---

### Recommendation

Implement as the document describes: diagnostic-only, parity-first, no timing interpretation until correctness is established on the named small cases. Before any block-size sweep, hand-verify the partition at `i = 0`, `j = 0`, `local_index = 0`, and at least one equal-value cross-segment case with a small pair where the expected output can be checked by inspection. The document's own risk note and correctness coverage list are accurate and sufficient as the implementation checklist.
