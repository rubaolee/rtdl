## Review: Phoenix V3 Phase A Performance-Source No-Go

### Evidence Assessment

**Barnes-Hut (Goal 0):**
Goal 0 verdict confirmed trunk existence (runtime executes, residency held, no host materialization, parity passes) and correctly classified Barnes-Hut as backend-bound — the remaining gap to V2.14 lives in the shared RT traversal kernel, which V3 cannot accelerate. The 0.844→0.953x movement is regression recovery, not a gain. Verdict: trunk pass, near-parity control row. No further tuning permitted. This finding is sound and complete.

**Anti-Avoidance Lock (RTNN):**
The lock correctly filed (a)–(d) before execution: family name, dominant phase measured (runner-after-input-pack = 0.677 of delta on uniform), concrete >=1.20x hypothesis (prepared-session runner removes repeated prepare overhead), and why V2.14 lacks it. The lock also explicitly stated its own kill condition: if the focused scorecard-bound RTNN run misses >=1.20x with parity → Phase H, no third search. This is the correct procedure.

**RTNN Focused Run (summary.json):**
All checks pass (0 failed). The trunk executes end-to-end, residency is internal, no host materialization, and runner-vs-legacy parity is exact (all checksum and distance deltas are 0.000).

The measured speedups against the frozen scorecard row (OptiX, clustered, 262144):

| Metric | Measured | Bar | Pass? |
|---|---|---|---|
| hot speedup (runner vs legacy) | 0.9956x | >=1.20x | **NO** |
| runner-wall speedup | 1.0386x | >=1.20x | **NO** |
| projected hot (scorecard row) | 0.9934x | >=1.20x | **NO** |
| projected runner-wall (scorecard row) | 1.0362x | >=1.20x | **NO** |
| cold+query speedup | 1.5809x | n/a (submetric) | — |

`runtime_sourced_material_gain_candidate: false` — set by the runner itself.

The cold+query 1.58x figure is real but is not the release metric. Substituting it for the scorecard-bound runner-wall row would repeat the exact error the anti-avoidance lock was written to prevent: replacing the release metric with a narrower internal submetric.

Named blockers moved to bar: **0 of ≥2 required.** `win_source` is not recorded. Phase A exit gate is not met.

### Is Any Rejection Basis Legitimate?

**Could a different RTNN distribution (uniform, shell) show >=1.20x?** No. The lock authorized one focused scorecard-bound run. Running additional distributions to find a winner is metric shopping — the kill condition in the lock document is explicit: "no third search." The distribution tested (clustered, 262144) is the frozen scorecard shape.

**Is evidence incomplete?** No. The run was repeat=50, warmup=3, at the frozen scorecard shape, with full phase accounting, residency audit, parity checksum, and scorecard projection. Nothing is missing.

**Is 1.039x a near-miss warranting one more bounded attempt?** No. It is 14 percentage points below the >=1.20x bar — not a near-miss, and the lock has no "near-miss remediation" clause. It has only a kill condition.

---

## Verdict

```
accept_phase_a_no_go_enter_phase_h_capability_quality
```

**Basis:**

1. Barnes-Hut closed as trunk proof/control. No performance source found there; backend-bound by construction. Correct classification, no further tuning.
2. RTNN was the only authorized reselected candidate. The kill condition in the anti-avoidance lock is unambiguously triggered: >=1.20x runtime-sourced with parity was the bar; the result is 1.036x runner-wall on the frozen scorecard row with full parity. The runner itself records `runtime_sourced_material_gain_candidate: false`.
3. No third search is authorized by the lock. No family, scorecard row, dominant phase, or >=1.20x hypothesis exists that was not already accounted for in the lock selection process (RayJoin and RTDBSCAN have prior no-go evidence; RayDB and Triangle are Set-B/control rows).
4. The cold+query 1.58x submetric cannot be promoted. Doing so would be the internal-metric-substitution error the entire A-H roadmap was designed to stop.

**Phase H entry confirmed.** V3 proceeds to capability/quality release planning with no broad V3-over-V2 speedup claim, no all-app benchmark, no public speedup wording, no V4/embedding/C-ABI, and no further Phase A candidate search.
