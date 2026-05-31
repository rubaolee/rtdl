# Goal2782 Partner-Selection Guidance — Independent Review

Reviewer: Claude (claude-sonnet-4-6)
Date: 2026-05-31

**Verdict: `accept`**

---

## Files Reviewed

- `src/rtdsl/v2_5_partner_selection_guidance.py`
- `src/rtdsl/__init__.py` (lines 215–219 for the new exports)
- `tests/goal2782_v2_5_partner_selection_guidance_test.py`
- `docs/reports/goal2782_v2_5_partner_selection_guidance_2026-05-31.md`
- `docs/reports/goal2780_topk_adapter_triton_grouped_topk_2026-05-31.md`
- `docs/reports/goal2781_grouped_vector_sum_adapter_2026-05-31.md`
- `docs/reports/goal2780_pod_artifacts/goal2780_topk_adapter_triton_pod_69_30_85_171_2026-05-31.json`
- `docs/reports/goal2781_pod_artifacts/goal2781_grouped_vector_sum_adapter_pod_69_30_85_171_2026-05-31.json`

---

## Question-by-Question Findings

### 1. Does Goal2782 correctly encode the Goal2780/Goal2781 lesson that preview kernel availability is not partner-selection authorization?

**Yes, correctly encoded.**

The lesson is embedded at three independent layers:

- **Guidance dict field**: `preview_kernel_available_does_not_imply_auto_select: True` is a required field in the `v2_5_partner_selection_guidance()` output.
- **Validator**: `validate_v2_5_partner_selection_guidance` checks this field is `True` and raises an error if absent or false.
- **Per-row dataclass**: `V25PartnerSelectionGuidanceRow.__post_init__` unconditionally raises `ValueError` if `auto_select_measured_partner_allowed` is true — meaning the lesson cannot be bypassed by constructing a guidance row directly.
- **Report text**: The Goal2782 report header states verbatim: "preview kernel available is not the same as selected partner."

The lesson is not advisory text in a comment; it is a structural invariant enforced at construction time.

### 2. Are the top-k and vector-sum slower-ratio ranges faithful to the artifacts?

**Yes, within displayed precision.**

**grouped_topk_f64 (Goal2780 artifact):**

| Row | Artifact ratio | Guidance field | Match |
|-----|---------------|---------------|-------|
| query=2, k=2 | 47.283123… | min_ratio = 47.28 | ✓ |
| query=256, k=8 | 150.901406… | max_ratio = 150.90 | ✓ |
| query=512, k=8 | 143.495653… | (within range) | ✓ |

**grouped_vector_sum_f64x2 (Goal2781 artifact):**

| Row | Artifact ratio | Guidance field | Match |
|-----|---------------|---------------|-------|
| rows=1,048,576, groups=8,192 | 4.093361… | min_ratio = 4.09 | ✓ |
| rows=262,144, groups=4,096 | 6.722556… | (within range) | ✓ |
| rows=8,192, groups=512 | 16.585575… | max_ratio = 16.59 | ✓ |

Both ranges are the correct observed minimum and maximum from the three-row pod runs. The guidance picks the observed boundaries, not rounded-down conservative values, which is the right approach for negative guidance.

### 3. Does the guidance remain advisory only, preserving explicit app/user partner choice and no forced partner?

**Yes, enforced at every layer.**

- `planner_policy` is set to `"advisory_only_explicit_app_partner_choice"` in the top-level dict.
- `no_partner_forced: True` is asserted in the top-level dict.
- `auto_select_measured_partner_allowed: False` is enforced per-row in `__post_init__`.
- `plan_v2_5_partner_selection()` returns `auto_select_partner_allowed: False` in both code paths — the matched path (`measured_negative_preview_guidance`) and the unmatched fallback (`no_measured_guidance`). There is no code path that returns `True` for auto-select.
- The fallback explicitly recommends "Require explicit app/user partner choice and same-contract evidence."

No code path allows a planner to infer an authorized auto-selection from these guidance rows.

### 4. Are public speedup, RT-core, true-zero-copy, whole-app, and release claims all blocked?

**Substantially yes; one enumeration gap noted but not a functional gap.**

Named blocking fields present in both the guidance dict and per-row metadata:

| Claim | Named field blocked | Validator checks |
|-------|-------------------|-----------------|
| Public speedup | `public_speedup_claim_authorized: False` | ✓ |
| True zero-copy | `true_zero_copy_claim_authorized: False` | ✓ |
| Release readiness | `release_readiness_authorized: False` | ✓ |
| Performance path promotion | `promoted_performance_path: False` | ✓ |

**Gap:** `rt_core_speedup_claim_authorized` and `whole_app_speedup_claim_authorized` do not appear as named fields in the guidance module or its validator. These fields are present in the pod artifacts themselves (where they read `false`), but the guidance module covers them only via `promoted_performance_path: False` and the claim boundary string ("does not … promote a performance path"). This is adequate for the scope of a planner metadata layer, but weaker than having named fields for each claim type.

The claim boundary string is: *"v2.5 partner-selection guidance records measured preview evidence and planner cautions only. It does not force a partner, promote a performance path, authorize public speedup wording, authorize true zero-copy wording, or authorize release readiness."* This is correct but does not call out RT-core or whole-app explicitly by name.

Since this goal is a planner advisory layer (not a claim authority layer), and the pod artifacts that are its evidence already carry the explicit RT-core and whole-app blocks, this is not a rejection issue. However future guidance additions that carry performance evidence should add these as explicit named fields.

### 5. Does the validator fail closed enough for this narrow metadata/planner step?

**Yes, the validator fails closed.**

The validator (`validate_v2_5_partner_selection_guidance`) returns `"reject"` on any error and `"accept"` only when all checks pass. It verifies:

1. Version string identity
2. `row_count` matches actual row count
3. `preview_kernel_available_does_not_imply_auto_select` is exactly `True`
4. Four claim fields are exactly `False`
5. Per row: operation is in the allowed set, `measured_partner` matches `V2_5_PRIMARY_PARTNER`, `auto_select_measured_partner_allowed` is exactly `False`, `promoted_performance_path` is exactly `False`
6. Per row: artifact file exists on disk at the declared path

The artifact file existence check is important — it means the validator cannot accept guidance that points to a nonexistent evidence record. This is the right behavior for a metadata layer that is supposed to be grounded in real measurements.

One minor observation: the validator does not explicitly re-check `no_partner_forced` as a top-level field, only the per-row `auto_select_measured_partner_allowed`. This is not a gap because `auto_select_measured_partner_allowed` is the operational expression of "no partner forced" and is enforced both per-row and at construction time. The two checks are equivalent.

### 6. Is it correct that no new pod timing is required for this goal?

**Yes, correct.**

Goal2782 is a registry/metadata goal. It encodes the already-recorded evidence from Goals 2780 and 2781 into a machine-readable guidance structure. It does not produce new kernel measurements, new adapter calls, or new CUDA execution. The validator's artifact-file-exists check confirms that the referenced artifacts are present on disk and serve as the grounding evidence. Recording new pod timing for a metadata encoding step would add noise without adding information.

---

## Additional Observations

**`__init__.py` integration** is clean. The new symbols (`V25PartnerSelectionGuidanceRow`, `V2_5_PARTNER_SELECTION_GUIDANCE_VERSION`, `plan_v2_5_partner_selection`, `v2_5_partner_selection_guidance`, `validate_v2_5_partner_selection_guidance`) are all imported. The test confirms they are accessible via `rt.*` but excluded from `rt.__all__`, consistent with experimental status.

**Defense-in-depth structure** is good. `__post_init__` blocks invalid rows at construction time; the validator catches tampered dicts at query time; `plan_v2_5_partner_selection` always returns `auto_select_partner_allowed: False` at the planner API level. Three independent enforcement layers.

**Test coverage** is appropriate for the scope. The four test cases cover: full validation + claim blocking, machine-readable negative guidance + ratio floor checks + artifact existence, unknown-operation fallback behavior, and symbol availability + export exclusion. The test also checks the report file contains the key lesson phrases from the design lesson, which prevents a future refactor from silently removing them.

**Ratio encoding choice**: using `min_ratio` and `max_ratio` (observed boundaries) rather than a single point estimate or mean is the correct representation for evidence drawn from a three-row sweep. The range communicates that the slowdown is not constant and depends on workload shape (which it does — top-k ranges from 47x to 151x depending on problem size).

---

## Summary

Goal2782 correctly captures the design lesson from Goals 2780 and 2781. The ratio ranges match the pod artifacts. Advisory-only constraint is enforced at construction, validation, and query layers. The blocked-claims coverage is complete for the named fields, with RT-core and whole-app covered implicitly via `promoted_performance_path`. The validator fails closed with artifact existence as a grounding check. No new pod timing is warranted for a metadata encoding goal.

**Verdict: `accept`**
