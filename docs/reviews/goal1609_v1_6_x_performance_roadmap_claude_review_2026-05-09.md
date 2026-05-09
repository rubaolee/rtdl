**VERDICT: ACCEPT**

Reviewed against the four criteria — clarity, sequencing safety, claim safety, and practicality — with focused attention on `COLLECT_K_BOUNDED`, reduced-copy vs. zero-copy, pod usage, and public speedup wording.

---

## Summary Findings

### Clarity

The table structure (goal, deliverable, acceptance gate, hardware need) is unambiguous at every version slot. The workstreams map onto the version table without contradiction. Claim rules name specific blocked phrases rather than vague prohibitions. The "planning slots, not mandatory tags" disclaimer removes the implicit pressure to tag everything. **Clear.**

### Sequencing Safety

The dependency chain is sound:

- v1.6.1 (measurement) is unconditionally first. No version claims performance before a phase/copy instrumentation baseline exists.
- v1.6.2–v1.6.3 convert prior accepted evidence (Goal1455, Goal1465) into benchmarkable paths before any new optimization is attempted.
- v1.6.4 (COLLECT_K_BOUNDED promotion attempt) is placed before v1.6.5 (OptiX packing reduction). This is defensible: v1.6.4 is a **correctness/stability gate** with an explicit fail path ("documented rejection/defer with exact blockers"), not a performance gate. If OptiX pod evidence is unavailable, the roadmap's "keep it internal, continue with v1.6.11+" escape hatch is sufficient.
- v1.6.8 (same-contract benchmark package) is correctly placed after all preparation work (v1.6.1–v1.6.7). Requiring pod runs only after local readiness is established.
- v1.6.9 (public claim audit) precedes v1.6.10 (package publication). The audit gate cannot be bypassed.

**Sequenced safely.**

### Claim Safety

This is the roadmap's strongest dimension.

- `COLLECT_K_BOUNDED`: explicitly blocked from stable promotion until a separate evidence gate with named fields (`capacity`, `valid_count`, overflow flag, deterministic validation, Embree/OptiX parity, 3-AI review) passes. The binary outcome structure ("stable-promotion OR documented rejection") is correct — no middle state where it silently stays experimental without a decision.
- Reduced-copy vs. true zero-copy: the distinction is preserved everywhere. Workstreams B and C exit criteria both state "no true zero-copy wording unless a later device-resident/shareable memory gate proves it." The roadmap does not call its host-buffer approach zero-copy anywhere.
- OptiX/RTX speedup wording: blocked until same-contract reviewed comparison at v1.6.8. Slow OptiX results are explicitly allowed to produce "OptiX still slower with reason" packages — no requirement to suppress negative results.
- Public speedup wording template is appropriately narrow: named subpath, named workload, named backend, named contract, excluded phases listed.

The blocked-wording list (10 items, including `--backend optix` implies NVIDIA RT-core speedup, package-install usage, Vulkan/HIPRT/Apple as active targets) is comprehensive and covers the common over-claim patterns.

**Claim-safe.**

### Practicality

- v1.6.1–v1.6.3 build on already-accepted evidence (Goal1438, Goal1455, Goal1465). They are not greenfield.
- v1.6.8 workload list is specific: DB compact summary, graph visibility/prepared rays, polygon overlap/Jaccard, Hausdorff threshold, robot prepared flags/counts, one positive control. Concrete enough to audit.
- Pod policy prerequisites (local pass, scripted commands, artifact paths known, positive controls present) eliminate speculative pod spending.
- The 10-slot plan with a v1.6.11+ escape hatch avoids forcing weak evidence through to hit a slot count.

**Practical.**

---

## Non-Blocking Notes

1. **v1.6.4 OptiX path is pre-optimization**: COLLECT_K_BOUNDED OptiX parity evidence collected at v1.6.4 will be on unoptimized OptiX paths (v1.6.5 hasn't run yet). This is fine because v1.6.4 is a correctness/stability gate — but the final performance evidence for COLLECT_K_BOUNDED on OptiX should probably be re-sampled at v1.6.8, not re-used from v1.6.4. Consider noting this in the v1.6.4 acceptance gate.

2. **v1.6.6 acceptance gate is API-only**: The gate checks contract correctness and failure modes but does not require copy-count or timing measurements. This leaves v1.6.6's prepared session API without a performance baseline until v1.6.8. That is acceptable, but the v1.6.8 gate should explicitly require that v1.6.6 session paths are among the measured paths, not just any prepared path.

3. **"Positive control" is undefined**: v1.6.8 lists six workloads plus "one positive control" without defining what constitutes a valid positive control. Recommend adding a one-sentence definition (e.g., "a workload where OptiX is already known to be faster than Embree under the same contract, used to confirm the measurement harness is functioning").

4. **v1.6.7 thin views and v1.6.6 session API ordering**: v1.6.7 (thin result views) follows v1.6.6 (session API) but has no stated dependency on it. If thin views are orthogonal to sessions, they could proceed in parallel; if they are expected to compose, the dependency should be stated.

None of these require changes before proceeding. They are observations for the implementers to address in individual goal docs (Goal1610–Goal1614).

---

**ACCEPT.** The roadmap is clear, conservatively sequenced, claim-safe, and grounded in prior accepted evidence. No blocking issues identified.
