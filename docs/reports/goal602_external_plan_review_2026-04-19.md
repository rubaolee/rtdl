# Goal602: v0.9.3 Full Apple RT Native Coverage Plan — External Review

Date: 2026-04-19

Reviewer: External AI (Claude Sonnet 4.6)

Decision: **ACCEPT**

---

## Summary

The v0.9.3 plan honestly and feasibly scopes moving all remaining `run_apple_rt`
compatibility workloads to Apple Metal/MPS RT hardware-backed candidate discovery.
The plan earns ACCEPT on the following grounds.

---

## What The Plan Gets Right

### Hardware-backed definition is explicit and enforceable

The five-point definition (§ "Definition Of Hardware-Backed") is precise enough to
be tested in code. The three disqualifying conditions (direct call to
`_run_cpu_python_reference_from_normalized`, trivial probe-only use, dummy MPS
operation) close the most common loopholes for inflating a native-coverage claim.
The requirement that `run_apple_rt(..., native_only=True)` succeeds is a
machine-checkable gate, not a documentation assertion.

### Difficulty ratings are calibrated honestly

The plan does not flatten risk. Geometry workloads are rated low-to-medium;
KNN completeness and graph/DB lowering are rated high. Calling KNN candidate
completeness "the hard part" and acknowledging that exact overlap area stays on
CPU for polygon-pair workloads shows awareness of the real engineering boundary,
not wishful thinking.

### Phased ordering reduces false-coverage risk

Geometry first, nearest-neighbor second, graph and DB last is the correct order.
The geometry workloads have the most direct MPS mapping; building and validating
that infrastructure before attempting point-primitive encoding for KNN or CSR-to-
geometry encoding for BFS/triangle-match significantly reduces the risk of
prematurely labeling an incomplete lowering as hardware-backed.

### CPU postprocessing scope is correctly bounded

The plan allows CPU refinement, sorting, dedupe, grouping, and aggregation after
MPS candidate discovery, and explicitly states that this is acceptable if
documented. This matches the RTDL contract for exact semantics and avoids the
trap of claiming MPS must do all work to qualify as hardware-backed.

### Non-negotiable honesty boundaries are load-bearing

The four prohibitions in § "Risks And Non-Negotiable Honesty Boundaries" are the
right constraints:

- Workloads that cannot be lowered without missing true results must remain
  unsupported in `native_only=True`. This prevents shipping incomplete coverage
  under a passing label.
- CPU-reference compatibility must not be called Apple RT hardware.
- Apple RT must not be claimed as a DBMS, graph database, ANN index, or general
  GPU compute framework.

These are not aspirational; they are enforced by the `native_only=True` gate and
by the correctness tests required at every goal.

### Consensus and gate structure is appropriate

Goal603 (contract) requires 3-AI planning consensus before implementation.
Goal610 (pre-release gate) requires 3-AI final release consensus. Individual
implementation goals require 2-AI finish consensus. The escalation structure
correctly places the highest bar at the definition and release endpoints.

---

## Risks Acknowledged But Acceptable

**KNN candidate completeness.** The plan acknowledges that encoding points as
tiny triangles or degenerate boxes is speculative and that missing true neighbors
is the failure mode. The mitigation — adversarial completeness tests required
before Goal605 closes — is the correct control. If the lowering cannot be made
complete, the workload correctly remains unsupported in `native_only=True`.

**Graph workloads.** BFS and triangle-match are not naturally geometric. The plan
is honest that the difficulty is high and that v0.6's RT-style traversal model
is the reference, not a proven Apple RT implementation. Requiring deterministic
parity tests before Goal606 closes is adequate.

**DB workloads.** The plan explicitly limits scope to bounded integer/text-like
test cases and forbids claiming arbitrary SQL or a DBMS. Setup/query timing is
required in the performance report. This is an honest bounded-form claim.

**Performance.** The plan explicitly states that performance may be worse than
Embree and that correctness and native candidate discovery come first. Speed
claims require separate evidence. This is the correct priority ordering.

---

## No Blocking Issues Found

The plan does not inflate claims, does not blur the CPU-reference fallback into
the hardware-backed definition, and does not attempt to scope v0.9.3 as a
complete native solution for workloads where the lowering is unproven. Every
workload group has correctness gates before it can close.

---

## Recommendation

Proceed with Goal603 (contract and support-matrix definition) as the first
implementation step, per the plan's own recommended order. Do not open Goal604
until the `apple_rt_support_matrix()` schema, the `native_only=True` test
harness, and the v0.9.3 native-coverage semantics report are merged and
consensus-approved.
