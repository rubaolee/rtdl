# Goal685 External Review — Engine Feature Support Contract

Reviewer: Claude (external review)
Date: 2026-04-21
Verdict: **ACCEPT**

---

## Checklist

### Every public feature has a status for every engine

Pass. The matrix covers 20 features × 5 engines (embree, optix, vulkan, hiprt, apple_rt) with no gaps.
`test_every_public_feature_has_status_for_every_engine` enforces this at runtime, including a `>=20` floor
and strict set-equality against `rt.RTDL_ENGINES` for every feature row.

### Statuses are limited to the four allowed values

Pass. `ENGINE_SUPPORT_STATUSES = ("native", "native_assisted", "compatibility_fallback", "unsupported_explicit")`
is the single source of truth. Every matrix entry is asserted against this tuple by the test.
All 100 entries in the current matrix use only `native`, `native_assisted`, or `compatibility_fallback`;
`unsupported_explicit` is reserved for future use and wired into `assert_engine_feature_supported`.

### Docs forbid blank cells and silent CPU fallback

Pass. The public doc (`docs/features/engine_support_matrix.md`) states explicitly:
"Silent CPU fallback is not allowed for a feature advertised as an RT engine feature."
`test_doc_records_no_blank_or_silent_cpu_fallback_policy` asserts the presence of all four status
strings plus that phrase in the doc text.

### Matrix does not overclaim performance or hardware acceleration

Pass. Notes throughout are deliberately qualified:
- No broad speedup claim appears anywhere in the matrix or docs.
- `compatibility_fallback` entries (Embree `prepared_scalar_visibility_count_2d`; HIPRT DB/graph;
  all-engine `reduce_rows`) are accompanied by notes explicitly disclaiming acceleration.
- `native_assisted` entries for Apple RT carry "not a broad speedup claim" or equivalent language.
- The boundary section in the report and the doc both repeat the non-claim list verbatim.

### Apple RT, HIPRT, DB/graph, and `reduce_rows` honesty boundaries preserved

Pass on all four:

| Boundary | Status | Notes |
|---|---|---|
| Apple RT 2D features | `native_assisted` | Exact 2D acceptance enforced outside pure MPS RT traversal API |
| Apple RT 3D RT features | `native` | MPS RT traversal is used directly; appropriate |
| Apple RT DB/graph | `native_assisted` | Note explicitly: "not Apple MPS RT traversal; Metal compute/native-assisted path" |
| HIPRT DB/graph | `compatibility_fallback` | Note explicitly: "no AMD GPU performance claim" |
| `reduce_rows` (all engines) | `compatibility_fallback` | "Python standard-library helper over emitted rows; not a backend-native reduction" |

The doc's Important Boundaries section restates each of these in prose, and `test_doc_table_matches_machine_readable_matrix_statuses`
machine-verifies that the rendered Markdown table matches the Python dict exactly.

---

## Issues Found

None. No missing cells, no invalid statuses, no overclaims, no silent fallback, all honesty
boundaries intact.

---

## Verdict

**ACCEPT**
