I have enough to write the full review. Let me compile findings into the final verdict.

---

## Goal 127 Technical Honesty Review

### Verdict

**CONDITIONALLY HONEST — accepted with two medium findings and one low finding.**

The core claim — that `segment_polygon_anyhit_rows` is now a real workload family wired across the RTDL surface — is supported by the code. Every claimed insertion point (predicate, lowering, Python reference, C++ oracle, Embree, OptiX, Vulkan, baseline contracts, evaluation matrix, schema, codegen, tests, user example) is genuinely present and structurally correct. The boundary statement ("local closure evidence is strongest on lowering, schema, Python reference, authored tests") is honest. No inflation of results.

However there are specific accuracy gaps and one omission:

---

### Findings by Severity

#### MEDIUM-1: OptiX and Vulkan dispatch to CPU fallbacks, undisclosed

**What the report says:** "oracle/native runtime support for: CPU oracle, Embree, OptiX, Vulkan"

**What the code does:**
- `rtdl_optix.cpp:1916` — `run_seg_poly_anyhit_rows_optix_host_indexed` is a pure CPU bucket-index loop. No CUDA, no ray-tracing.
- `rtdl_vulkan.cpp:2833` — `run_segment_polygon_anyhit_rows_vulkan` is a pure CPU bucket-index loop. No Vulkan RT pipeline, no compute shader dispatch. (Compare: the `point_nearest_segment` Vulkan path actually dispatches a real compute shader.)

The report omits that neither OptiX nor Vulkan provide GPU execution for this workload. The functions are wired and will return correct rows, but the word "support" without qualification overstates what is actually delivered for those two backends.

**Mitigating factor:** This is consistent with the existing `segment_polygon_hitcount` family (same pattern: `run_seg_poly_hitcount_optix_host_indexed`, same CPU Vulkan loop). Goal 127 faithfully replicates the existing hitcount backend depth — it is not regressing from a higher bar. Still, if a reader checks only Goal 127's report, they receive a misleading picture of what OptiX and Vulkan actually run.

#### MEDIUM-2: Embree backend does not use Embree BVH

**What is claimed:** "strong Python/oracle/Embree code-surface integration"

**What the code does:** `rtdl_embree.cpp:1379` — `rtdl_embree_run_segment_polygon_anyhit_rows` builds a CPU bucket index and loops. It does not stage geometry into Embree's acceleration structure. The function lives in `rtdl_embree.cpp` but shares no Embree API calls.

Again consistent with `segment_polygon_hitcount` in the same file. The "Embree" label for this family refers to backend dispatch location, not BVH use. Not wrong, but "Embree integration" is slightly misleading phrasing.

#### LOW: Goal doc title says "Goal 127" but `evaluation_matrix.py:185` writes the provenance as "Hand-authored Goal **126** segment/polygon row-materializing example"

`evaluation_matrix.py:185`:
```python
provenance="Hand-authored Goal 126 segment/polygon row-materializing example stored in baseline_runner.",
```

Goal 126 selected the workload family; Goal 127 implements it. The provenance line conflates selection with implementation. Minor, but the evaluation matrix is a referenced artifact.

---

### Checks That Pass

| Claim | Evidence | Status |
|---|---|---|
| Predicate `segment_polygon_anyhit_rows` added | `api.py:140-141` | PASS |
| Python reference kernel in `GOAL10_KERNELS` | `rtdl_goal10_reference.py:16-21, 79` | PASS |
| `segment_polygon_anyhit_rows_cpu` correct | `reference.py:167-183` (row per hit pair, not per segment) | PASS |
| `runtime.py` dispatches new predicate | `runtime.py:118-119` | PASS |
| Oracle C++ has real implementation | `rtdl_oracle.cpp:1081-1078` (bucket + `segment_hits_polygon`) | PASS |
| Embree C++ has real implementation | `rtdl_embree.cpp:1379-1451` (same algorithm) | PASS |
| Baseline contract registered | `baseline_contracts.py:208-240` | PASS |
| `infer_workload` mapping updated | `baseline_runner.py:51` | PASS |
| `_load_segment_polygon_case` routes new workload | `baseline_runner.py:73` | PASS |
| `baseline_runner.py` main dispatch updated | `baseline_runner.py:537-538` | PASS |
| Evaluation matrix has 3 entries | `evaluation_matrix.py:179-208` | PASS |
| Codegen placeholder added | `codegen.py:564-600` | PASS |
| Schema enum updated | `schemas/rtdl_plan.schema.json:39,48` | PASS |
| Lowering wired | `lowering.py:64-65, 487-504` | PASS |
| `__init__.py` exports both new symbols | `__init__.py:12, 133, 362, 367` | PASS |
| User example is clean and runnable | `examples/rtdl_segment_polygon_anyhit_rows.py` | PASS |
| Test with expected row values | `goal10_workloads_test.py:40-51` | PASS |
| Language test includes new kernel | `rtdsl_language_test.py:50` | PASS |
| Predicate options test | `test_core_quality.py:270-273` | PASS |
| Baseline contract validation test | `baseline_contracts_test.py:46-47` | PASS |
| Test count claim (105 OK, 1 skip) | Plausible from test structure; cannot verify without run | UNVERIFIED |

---

### Package-Level Summary

Goal 127 does what it says: `segment_polygon_anyhit_rows` is a real workload family, not a roadmap entry. The predicate, Python reference, C++ oracle, lowering, schema, baseline, evaluation matrix, and tests are all genuinely present and internally consistent. The user-facing example runs and produces the claimed rows.

The two medium findings are accuracy gaps rather than fabrications: the OptiX and Vulkan "support" is real in the sense that the dispatch chain is wired and returns correct rows, but both execute as CPU loops with no GPU involvement — a fact not stated in the report. This is consistent with the existing `segment_polygon_hitcount` depth, so the family closure matches its peer. The low finding (evaluation matrix provenance saying "Goal 126") is a copy-paste error, not a substantive issue.

No test inflation is visible: the Embree-parity test (`goal10_workloads_test.py:40-51`) asserts specific expected row values, not just `assertIsNotNone`. The boundary statement in both docs is honest and appropriately scoped.
