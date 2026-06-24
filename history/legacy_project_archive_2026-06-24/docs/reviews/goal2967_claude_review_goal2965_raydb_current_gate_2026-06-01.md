# Review: Goal2965 RayDB Current-Commit Gate Refresh

Reviewer: Claude (independent read-only review)
Review goal: Goal2967
Subject: Goal2965
Date: 2026-06-01
Verdict: **accept-with-boundary**

---

## Scope

This review covers the Goal2965 refresh of the Goal2896 RayDB same-contract
performance decision gate and the 2M-row stress addition. Source commit under
review is `8baed4f0` (current HEAD); pod artifacts were recorded at
`28bcf380b078f6e3c0cbe55d9ed4ed78a9ac61e9`, which is the commit immediately
preceding the Goal2965 commit that adds the artifacts, report, and test.

Primary files examined:

- `docs/reports/goal2965_raydb_current_commit_gate_refresh_2026-06-01.md`
- `tests/goal2965_raydb_current_commit_gate_refresh_test.py`
- `docs/reports/goal2965_raydb_current_gate_pod/goal2965_raydb_same_contract_gate_current.json`
- `docs/reports/goal2965_raydb_current_gate_pod/goal2965_raydb_same_contract_raw_current.json`
- `scripts/goal2896_raydb_same_contract_performance_decision_gate.py`
- `src/rtdsl/v2_5_internal_readiness.py`

---

## Question-by-Question Findings

### Q1: Does the current-commit gate pass at 28bcf380 with no errors and all CPU-reference checks true?

**Yes, confirmed from artifact.**

`goal2965_raydb_same_contract_gate_current.json` records:

```json
"status": "pass",
"git_head": "28bcf380b078f6e3c0cbe55d9ed4ed78a9ac61e9",
"errors": [],
"all_correct": true
```

All 18 cases in the raw artifact carry `"matches_cpu_reference": true`, covering
all three row counts (250K, 1M, 2M) across all three backends and both modes.
The gate script (`scripts/goal2896_raydb_same_contract_performance_decision_gate.py`,
lines 106–108) enforces CPU-reference equality per case as an error condition;
the empty errors list confirms no case failed.

Note on commit identity: the pod was checked out at `28bcf380` (the commit
immediately before `8baed4f0`). The test at line 15 of the test file hardcodes
`EXPECTED_COMMIT = "28bcf380b078f6e3c0cbe55d9ed4ed78a9ac61e9"` and the gate
artifact's `git_head` field matches exactly. This is the expected pattern: the
pod runs the gate at the most recent pushed commit, then `8baed4f0` lands the
artifacts, report, and test.

### Q2: Do the formal 250K/1M acceptance rows still clear the Goal2896 thresholds for both count and sum?

**Yes. All four comparisons pass with large margins.**

Thresholds (from `scripts/goal2896_raydb_same_contract_performance_decision_gate.py`,
lines 21–28):

- `count`: hit-stream slowdown ≥ 10x  
- `sum`: hit-stream slowdown ≥ 50x

Actuals from `goal2965_raydb_same_contract_gate_current.json`:

| Rows    | Mode  | Primitive-first (s) | Hit-stream (s) | Slowdown   | Required | Margin |
| ------: | ----- | ------------------: | -------------: | ---------: | -------: | -----: |
| 250 000 | count | 0.000430            | 0.012945       | **30.14x** | ≥ 10x    | 3.0×   |
| 250 000 | sum   | 0.001913            | 0.257141       | **134.4x** | ≥ 50x    | 2.7×   |
| 1 000 000 | count | 0.000459          | 0.014525       | **31.62x** | ≥ 10x    | 3.2×   |
| 1 000 000 | sum   | 0.002162          | 0.308346       | **142.6x** | ≥ 50x    | 2.9×   |

Independently recomputed from the raw artifact medians: results match the gate
artifact to six significant figures. All four `"pass": true` entries in
`comparisons` are source-backed.

The old-paper diagnostic speedups also clear their thresholds
(≥ 20× for count, ≥ 5× for sum), reaching 1581× / 931× at 250K and
5274× / 1689× at 1M.

### Q3: Do the 2M stress rows support the same direction without being overpromoted?

**Yes on direction; correctly excluded from the formal gate.**

2M row medians from the raw artifact (cases at rows 1769–2648):

| Rows      | Mode  | Primitive-first (s) | Hit-stream (s) | Slowdown   | Old-paper speedup |
| --------: | ----- | ------------------: | -------------: | ---------: | ----------------: |
| 2 000 000 | count | 0.000456            | 0.015960       | **34.96x** | 10 148×           |
| 2 000 000 | sum   | 0.002334            | 0.252584       | **108.2x** | 2 435×            |

Numbers match the report table. The test
(`tests/goal2965_raydb_current_commit_gate_refresh_test.py`, lines 60–61)
applies non-threshold informal floor checks (> 30× for count, > 100× for sum)
and confirms `matches_cpu_reference: true` for all three backends at 2M.

The gate script at line 14 (`REQUIRED_ROW_COUNTS = (250000, 1000000)`) is
definitive: 2M rows are not in the formal acceptance set. The report states
explicitly: "The 2M rows reinforce the direction but are not part of the formal
Goal2896 threshold gate." No promotion has occurred.

The raw artifact carries `"status": "ok"` with 18 total cases (3 backends ×
3 row counts × 2 modes), matching the test assertion at line 45
(`self.assertEqual(18, len(raw["cases"]))`).

### Q4: Is the planner conclusion still sound?

**Yes.**

The gate artifact's `decision` block records:

```json
"selected_design_rule": "primitive_first_for_exact_fused_generic_grouped_reductions",
"hit_stream_triton_reserved_for": "continuations_not_expressible_as_fused_generic_rtdl_reductions",
"triton_front_door_promoted_for_scalar_grouped_reductions": false,
"auto_triton_promotion_authorized": false
```

Every primitive-first case records `"v2_5_selected_path": "prepared_fused_generic_grouped_reduction"`,
`"partner_continuation_required": false`, and `"typed_hit_stream_forced": false`
in both the gate and raw artifacts, for all three row counts. The gate script
enforces these as hard errors at lines 111–116.

The report states all four planner rules correctly:

1. Use fused generic RTDL primitive when it exactly expresses the grouped reduction.
2. Keep typed hit-stream + partner continuation for non-primitive-expressible continuations.
3. Do not promote Triton merely to say Triton was used.
4. Keep v3.0 user-defined shader injection out of the v2.5 release lane.

No rule has been altered from the Goal2896 baseline.

### Q5: Does the report avoid overclaiming and preserve all blocked release/public claim categories?

**Yes. All blocked categories are preserved.**

The gate artifact's `claim_boundary` block:

```json
"internal_decision_gate_only": true,
"release_authorized": false,
"public_speedup_claim_authorized": false,
"whole_app_speedup_claim_authorized": false,
"broad_rt_core_speedup_claim_authorized": false,
"true_zero_copy_authorized": false,
"paper_reproduction_claim_authorized": false
```

Every individual case in the raw artifact carries its own claim boundary string
with explicit negations of the same blocked claims. No case sets any `_authorized`
field to `true`.

The readiness packet (`src/rtdsl/v2_5_internal_readiness.py`, line 373–382)
hardcodes `v2_5_release_authorized: False` and all other authorization fields to
`False`. Test line 80 asserts this. The report's Boundary section explicitly lists
all nine blocked categories and does not use public speedup wording, whole-app
wording, zero-copy wording, or release-tag language.

The `V2_5_INTERNAL_READINESS_REQUIRED_REPORTS` tuple at line 146 of
`v2_5_internal_readiness.py` correctly includes
`docs/reports/goal2965_raydb_current_commit_gate_refresh_2026-06-01.md`,
integrating Goal2965 into the readiness index without altering its boundaries.

### Q6: Are there remaining fairness or release-gate cautions?

**Yes — two open cautions, both pre-existing and tracked.**

**Single GPU, single architecture.** Every measurement in both artifacts was
produced on one pod (`NVIDIA RTX A5000, 570.211.01, 24564 MiB`). The readiness
packet at lines 254–256 of `v2_5_internal_readiness.py` explicitly carries:

```python
"track_goal2897_compiler_flag_alignment_before_release_packet",
"track_goal2897_multivendor_or_second_arch_perf_check_before_release_packet",
```

in `V2_5_INTERNAL_READINESS_ALLOWED_NEXT_ACTIONS`. These are not new findings;
they were opened by the Goal2897 review and remain unresolved.

**Compiler flag alignment.** The toolchain metadata enforces
`compiler_fairness_claim_authorized: false` and `multivendor_claim_authorized: false`
(`v2_5_internal_readiness.py`, lines 470–473). The speedup figures produced under
the current nvcc/OptiX build configuration are not portable across compiler flags,
vendors, or second GPU architectures.

Neither caution invalidates the gate for its stated purpose (internal planning
decision for a single same-contract fused-primitive planner rule), but both must
be resolved before any release or public claim is authorized.

---

## Source / Test / Artifact Consistency

| Check | Source | Result |
| ----- | ------ | ------ |
| Gate status | `gate_current.json` → `"status": "pass"` | ✓ |
| Git head in artifact matches hardcoded test constant | both `= 28bcf380b078f6e3c0cbe55d9ed4ed78a9ac61e9` | ✓ |
| all_correct | `gate_current.json` and `raw_current.json` | ✓ true |
| errors list | `gate_current.json` | ✓ empty |
| Case count | `raw_current.json` → 18 cases; test asserts 18 | ✓ |
| Formal row counts | gate script line 14 → `(250000, 1000000)`; gate has 4 comparisons | ✓ |
| 2M excluded from gate comparisons | gate comparisons list has 4 entries only | ✓ |
| Threshold margins | recomputed from medians | ✓ all pass |
| Report required phrases | test lines 67–74 check six phrases | ✓ |
| Readiness packet includes report | `v2_5_internal_readiness.py` line 146 | ✓ |
| Release not authorized in packet | `claim_authorization["v2_5_release_authorized"] = False` | ✓ |

---

## Boundary Preservation

The following release and claim categories remain blocked by this review and
are not altered:

- v2.5 release or release tag action
- Public speedup wording
- Broad RT-core speedup wording
- Whole-app speedup wording
- True zero-copy wording
- Package-install wording
- Triton preview auto-selection
- Paper reproduction claims
- App-specific native engine customization

Goal2965 is internal planning and stress evidence only.

---

## Verdict

**accept-with-boundary**

The refreshed gate evidence at commit `28bcf380` is sound: the formal 250K/1M
acceptance rows exceed the Goal2896 thresholds with 2.7–3.2× margin, all 18
CPU-reference checks pass, the 2M stress rows corroborate the direction without
being promoted into the formal threshold set, and the planner conclusion is
unchanged. The report does not overclaim, and all blocked categories are
preserved in both the artifact and the readiness packet.

Acceptance is bounded by two pre-existing open items that must be resolved
before any release or public claim is authorized: (1) compiler flag alignment
has not been checked, and (2) no second-architecture or multi-vendor performance
check has been performed. Both are tracked in the readiness packet's
`allowed_next_actions` list.
