## Verdict

**ACCEPTED** as local prepared host-output exact-bounds stress evidence for COLLECT_K_BOUNDED. No blockers found within the stated scope.

---

## Findings

**Script (`goal1614_v1_6_4_collect_k_bounds_stress.py`)**

- 9 cases cover the complete boundary surface: zero-capacity, exact-fit with unsorted duplicates, duplicate compression, `k+1` overflow, zero-capacity overflow, row widths 1/2/3, width-mismatch rejection, and negative-capacity rejection.
- `_FakeCollectKBoundedI64Symbol` correctly implements the expected contract via ctypes: dedup via `sorted(set(...))`, capacity check, fail-closed overflow (returns count but writes nothing and sets the overflow flag).
- Overflow path verifies `overflow_fail_closed=True`, `partial_result_returned=False`, `output_buffer_preserved=True` — the sentinel (`-777777777`) approach makes buffer-write detection meaningful.
- `validate_package` enforces all 6 authorization flags are `False` and that the claim boundary contains every required phrase. This is a hard gate, not advisory.
- Only `fake_native` is required; real-hardware backends (`embree`, `optix`) gracefully skip — appropriate for local-only bounds stress.

**Test file (`goal1614_v1_6_4_collect_k_bounds_stress_test.py`)**

- 5 test methods with substantive assertions: package acceptance, overflow fail-closed invariants (2 overflow cases each checked), `ValueError` propagation for invalid shapes, all 6 flag assertions, and end-to-end artifact generation including markdown content checks.
- No superficial smoke tests; each method targets a distinct behavioral guarantee.

**Reports**

- JSON: all 9 records `status: pass`, all 6 flags `false`, `accepted: true`, `status: "accepted_local_bounds_stress"`. Consistent with script output.
- Markdown: claim boundary present verbatim; "Timing is not performance evidence" noted explicitly.
- Git commit `645a33ea` matches the most recent commit in the working tree.

---

## Claim Boundary

This package is scoped exactly as stated. It does **not** authorize:

| Claim | Authorized |
|---|---|
| Stable `COLLECT_K_BOUNDED` promotion | No |
| Public speedup wording | No |
| True zero-copy wording | No |
| Whole-app or RTX/GPU speedup claims | No |
| Broad RTX wording | No |
| Release tag or release action | No |

The package directly satisfies the `v1_6_x_collect_k_exact_bounds_stress_artifact` evidence item identified as missing in the Goal1613 promotion gate, and nothing more.

---

## Recommendation

Accept as-is. The package is internally consistent, the fake backend faithfully models the C ABI contract, the authorization firewall is machine-enforced rather than advisory, and the claim boundary is explicit throughout. No changes needed before recording this as the bounds-stress evidence item. Stable promotion, performance benchmarking, and RTX-hardware evidence remain separate future steps.
