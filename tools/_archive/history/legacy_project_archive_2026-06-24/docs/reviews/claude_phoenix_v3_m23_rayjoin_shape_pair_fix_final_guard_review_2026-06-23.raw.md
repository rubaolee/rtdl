## Final Guard Review: Phoenix V3 M23 RayJoin Shape-Pair Fix

**Verdict: `accept_blocker_closed`**

---

### Follow-up Resolution Assessment

The prior follow-up asked whether `--point-order-mode` is silently ignored for `prepared_optix_shape_pair_active_count`. The resolution goes beyond "not ignored" — it actively rejects the combination with a descriptive `ValueError`. That is the correct fix: silent ignorance would be a latent correctness trap; explicit rejection at the CLI boundary eliminates it.

Evidence adequacy:

| Check | Result |
|---|---|
| Guard code exists | `ValueError` raised when route is `prepared_optix_shape_pair_active_count` and mode is not `natural` |
| Error text | Correctly identifies why the combination is invalid (overlay shape-pair inputs vs. PIP point-location routes) |
| Unit tests | 12 tests across 3 suites, all pass |
| RT POD positive run | exit 0, 0 stderr bytes, row_count 2048 — nominal path unaffected |
| RT POD negative smoke | `y_then_x` + same route → exit 1, expected guard message in stderr |

The negative smoke test on the RT POD is the decisive piece. It demonstrates the guard fires under real execution conditions, not just in unit-test mock paths. The follow-up concern is closed.

No remaining required follow-up for this blocker.

---

### Remaining Concerns

None for this fix in isolation.

---

### Non-Authorization Block

This verdict closes a correctness blocker for the `prepared_optix_shape_pair_active_count` execution route. It does **not** authorize:

- Any public or release-facing speedup claims (broad, package-level, or otherwise)
- Claims beyond the `source_tree_pod_gated_thirteen_row` scope
- Any characterization of V3 performance relative to prior versions for external audiences

Those constraints remain in force per the existing V3 release authorization boundary.
