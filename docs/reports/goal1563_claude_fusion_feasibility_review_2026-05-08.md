---

## Technical Review: Goal 1563 OptiX collect-k fusion feasibility

### Verdict

The hazard analysis is technically correct, the proposed safe shape is sound, and the next diagnostic implementation has several correctness obligations the report does not spell out.

---

### Agreement

**Hazard claim — correct.**
The race condition is real. `__syncthreads()` only synchronizes threads within one CTA; it provides no ordering guarantee across blocks. Since the long-case path assigns multiple blocks per pair (confirmed by the report), thread A in block N can reach the `mark` read of `merged_rows[output_index - 1]` before thread B in block M has written to that slot. `cooperative_groups::grid_group::sync()` would remove the hazard, but it requires cooperative-kernel launch and imposes an SM-count ceiling on the block count — likely incompatible with the measured long-case problem sizes. The two-kernel split is therefore not incidental; it is load-bearing.

**Safe fusion shape — plausible.**
The predecessor derivation from the two sorted input segments is correct for a stable merge. For a first-segment row at `first_index` with value `v`:

- `less_second = lower_bound(second_rows, v)` places the row at `output_index = first_index + less_second`
- The unique predecessor is `max(first_rows[first_index−1], second_rows[less_second−1])`

For a second-segment row at `second_index` with value `v`:

- `le_first = upper_bound(first_rows, v)` places the row at `output_index = second_index + le_first`
- The unique predecessor is `max(second_rows[second_index−1], first_rows[le_first−1])`

Both reads are into the *input* segments, which are read-only during the launch, so there is no intra-launch RAW hazard. This is a correct observation.

---

### Caveats the diagnostic must handle

**1. Boundary conditions — both must be checked independently.**
When `first_index == 0` AND `less_second == 0`, `output_index == 0`; there is no predecessor. The implementation must guard both index bounds before dereferencing, not just one, and must mark those rows as new output rows. The report's "if any" gloss is insufficient as implementation guidance.

**2. Equal-valued candidates across segments.**
The "lexicographic max" shorthand is valid for deduplication comparison (value equality is all that matters, not element identity), but the implementation must be explicit: if `first_rows[first_index−1] == second_rows[less_second−1]`, neither is "greater"; either value gives the same `mark` result. Code that returns a pointer to the max candidate rather than just a value will need a tie-breaking rule consistent with the merge order (first-segment wins on equal values, given the lower_bound/upper_bound asymmetry).

**3. Work distribution must be input-row-indexed, not output-row-indexed.**
Each thread must own an input-segment row so it can compute its output index via binary search independently. A layout that assigns threads by output index would require knowing which input row maps to each output position — which reintroduces the global materialization dependency the fusion is trying to remove.

**4. Block-count accumulation alignment.**
Accumulating `block_counts` in shared memory requires a `__syncthreads()` before the block-level write. For pairs whose row count is not a multiple of the block size, the final block is partial; the reduction must zero-initialize unused lanes or clamp the summation to avoid stale shared-memory contributions inflating the count.

**5. Binary-search cost on short pairs.**
Each fused thread now performs one binary search on the *other* segment. On pairs with a large size disparity (short second, long first, or vice versa), the additional search work may exceed the launch-overhead saving. The diagnostic must measure across the full distribution of pair sizes, not only the 65537 and 131072 long-tail cases, to characterize where the tradeoff inverts.

---

### Recommendation

The report's next-action plan is correctly scoped: diagnostic-only, parity-validated against the four-kernel block, measured before any production flag. Before writing the kernel, explicitly codify the five caveats above as test-case invariants (boundary row, equal-value crossing, odd-sized pair, last-block partial count, short-segment pair). Parity failures on those cases are the most likely source of silent correctness regressions in the fused path.
