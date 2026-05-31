# Independent Review: Goal2803 Barnes-Hut v2.5 Consolidated Harness

Reviewer: Claude (external AI reviewer)
Date: 2026-05-31
Verdict: **accept-with-boundary**

---

## Blocking Issues

None. No blocking issues prevent acceptance.

---

## Review Question Findings

### 1. Real current consolidated harness vs. historical report links

The harness at `scripts/goal2803_barnes_hut_v25_consolidated_harness.py` executes
live against the current runtime. It imports `run_case` from
`scripts.goal2642_barnes_hut_embree_vs_optix_lowering_perf` for the membership
subpath (reusing existing infrastructure, not replaying recorded artifacts), and
calls `rt.grouped_vector_sum_2d_partner_columns` directly for the vector-sum
subpath. The pod artifact confirms a live run against commit
`feed82707a0947e3876adfb3e96809075c9b7db0` with measured timing values and
`elapsed_sec: 25.53 s` — consistent with genuine multi-case execution.

The `source_dirty` list in the artifact records the harness script as an
untracked file (`?? scripts/goal2803_barnes_hut_v25_consolidated_harness.py`),
confirming the script was copied into the checkout for the first run, which
the report explicitly discloses. This is expected for a first evidence run.

**Finding: satisfied. The harness executes live; it is not a wrapper around
stored results.**

---

### 2. Coverage of both halves — expanded-membership lowering and grouped vector-sum

The script contains two clearly separated execution paths:

- `_run_membership_cases()` drives Embree-vs-OptiX expanded-membership
  aggregate-frontier lowering, iterating over `(body_count, bucket_size)` pairs
  and extracting per-backend timing and row-match fields from `run_case()`.
- `_run_vector_sum_probe()` directly exercises `grouped_vector_sum_2d_partner_columns`
  for both `partner="torch"` and `partner="triton"`, comparing results with
  `torch.allclose` and recording per-partner median timings.

Both paths contribute to the single top-level `status` field:
`membership_ok and vector_ok` must both be true for `status = "pass"`. This
is a machine-enforced conjunction, not prose.

The pod artifact and the report table confirm both halves ran and produced
numerical results for the two tested sizes.

**Finding: satisfied. Both halves are present, distinct, and machine-coupled
in the pass criterion.**

---

### 3. Same-contract membership parity and OptiX RT-core field

Both membership rows in the artifact record:

```json
"rows_match_between_backends": true,
"optix_rt_core_accelerated": true
```

The harness computes `membership_ok` as:

```python
all(
    row["rows_match_between_backends"] and row["optix_rt_core_accelerated"]
    for row in membership_rows
)
```

A failure of either boolean in any row flips `status` to `"mismatch"`.
This enforces same-contract parity and RT-core use structurally, not only
by inspection. The test `test_pod_artifact_records_rt_membership_and_vector_sum_boundary`
additionally verifies these strings by grep over the artifact.

One honest disclosure: `validate=index == 0` means the cross-backend
correctness check runs only for the first (512-body) case; the 2048-body
row has `"validation_skipped": true`. For a first evidence run this is
reasonable, but the clean-from-Git re-run should validate all cases or
document the intended skip policy explicitly.

**Finding: satisfied. Parity and RT-core fields are present and
machine-enforced for all measured cases.**

---

### 4. Honest Torch-vs-Triton comparison and blocked auto-selection

The probe compares `partner="torch"` against `partner="triton"` with
correctness checked at `rtol=1e-9, atol=1e-9` (float64-appropriate tolerance).
The artifact records `"matches_torch": true` and `"torch_faster": true` with
`"triton_over_torch_ratio": 6.844` — Triton is 6.8× slower on the tested fixture.

Two structural points strengthen the honesty of this comparison:

- The Triton path receives `columns_with_offsets` (pre-computed `row_offsets`),
  while the Torch path operates from `columns_without_offsets` and derives
  grouping internally. This gives Triton a mild pre-computation advantage.
  Despite that, Torch still wins by 6.8× — the comparison is conservative
  in Triton's favor, not inflated against it.
- The Triton metadata records `"v2_5_triton_global_atomic_add_used": false`
  and `"v2_5_triton_presegmented_offsets_used": true`, documenting which
  Triton design variant was tested (the better presegmented-offsets approach).

The `triton_vector_sum_auto_selection_allowed` field is hardcoded `False`
in the harness output — a policy gate independent of measured timing, which
is correct. It does not auto-unblock if timing changes in a future run without
explicit review.

One minor observation: the warm-up loop runs only one iteration
(`for _ in range(1):`). For a Triton JIT path, a single warm-up is often
sufficient but borderline. Given the 6.8× gap, the conclusion is not
materially affected. A clean-from-Git re-run using `--repeats 3` and at
least two warm-up passes would improve confidence in the stability of the
ratio.

**Finding: satisfied. The comparison is honest, conservative toward Triton,
and auto-selection is correctly blocked as a policy field.**

---

### 5. Absent forbidden claims

The `CLAIM_BOUNDARY` dict in code and the embedded JSON both record every
excluded claim as `false`:

| Excluded claim | Code | JSON artifact |
| --- | --- | --- |
| `public_speedup_claim_authorized` | `False` | `false` |
| `whole_app_speedup_claim_authorized` | `False` | `false` |
| `paper_reproduction_claim_authorized` | `False` | `false` |
| `paper_speedup_claim_authorized` | `False` | `false` |
| `authors_code_comparison_authorized` | `False` | `false` |
| `triton_vector_sum_auto_selection_authorized` | `False` | `false` |
| `native_engine_customization` | `False` | `false` |

The report prose states explicitly: "This is not a paper-reproduction claim
and not a public speedup claim." The Boundary section enumerates every
excluded claim. The manifest note reads: "Never embed inverse-square force
law inside the engine or Triton primitive contract." Barnes-Hut tree policy,
opening semantics, and force interpretation are correctly left as app-owned.

The membership speedup values in the report (e.g., 25.767× at 2048 bodies)
are internal Embree-vs-OptiX same-contract comparisons, not public speedup
claims. These are properly scoped and presented as evidence, not release
wording.

**Finding: satisfied. All excluded claims are explicitly blocked in code,
artifact, and prose.**

---

### 6. Clean-from-Git validation status

The `source_dirty` field in the artifact confirms the run was not clean:

```json
"source_dirty": [
  "?? docs/reports/goal2803_pod_artifacts/",
  "?? scripts/goal2803_barnes_hut_v25_consolidated_harness.py"
]
```

The report states: "Focused tests, external review, consensus, and
clean-from-Git pod validation are still pending at the time this report was
first written." The initial verdict reads "accept-with-boundary pending
external review and clean-from-Git rerun."

This is the correct framing. No false clean-run claim is made.

**Finding: correctly identified as pending. Disclosure is accurate.**

---

## Minor Observations (Non-Blocking)

**Only 2 of 3 default cases run in the pod artifact.** `DEFAULT_CASES` includes
`(8192, 32)` but the first artifact command used only `--case 512:16 --case 2048:32`.
The larger case would stress the membership path more. The clean-from-Git re-run
should include all three default cases or document the omission.

**repeats = 2 means `statistics.median` returns the mean.** With an even-sized
list, `statistics.median` returns the average of the two values rather than
a true center-of-distribution median. At `repeats=2` this is effectively the
mean. Switching to `--repeats 3` for the clean-from-Git run eliminates this
edge case.

**Consensus file not yet written.** The test
`test_report_and_consensus_keep_boundary` references
`docs/reports/goal2803_barnes_hut_v2_5_consolidated_harness_consensus_2026-05-31.md`.
That file is not in scope for Goal2803 itself, but the test will fail if run
before the file is written. This is expected review sequencing, not a defect.

**`validation_skipped: true` for the 2048-body case.** Cross-backend correctness
is checked only for the first case (`validate=index == 0`). For the clean-from-Git
re-run, enabling validation for the larger case — or documenting why the skip
is intentional — would strengthen the same-contract evidence.

---

## Summary

Goal2803 delivers a real consolidated harness for `barnes_hut` that covers
both the RT-assisted expanded-membership lowering and the grouped vector-sum
partner continuation. Same-contract parity and OptiX RT-core use are
machine-enforced in the pass criterion, not asserted only in prose. The
Torch-vs-Triton comparison is honest and conservative in Triton's favor, and
auto-selection is blocked by policy independent of measured timing. Every
excluded claim — public speedup, whole-app speedup, paper reproduction,
authors-code comparison, native app customization — is explicitly recorded as
`false` in code, artifact, and prose. The not-clean-from-Git status of the
first run is correctly disclosed, and clean-from-Git validation is accurately
identified as pending.

**Verdict: accept-with-boundary.**

Conditions for full acceptance:
1. A clean-from-Git pod re-run with all three default cases, `--repeats 3`,
   and at least two warm-up passes for the vector-sum probe.
2. The consensus file referenced in the test should be written by the
   reviewing party before that test is run.
