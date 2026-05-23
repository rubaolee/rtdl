I now have everything needed. Here is the review.

---

## Verdict: ACCEPT (internal bounded engineering) / REVISE (before any public use)

---

### Evidence fact-check

Every number in the claim packet is traceable to the raw artifacts:

| Packet figure | Raw source | Verified |
|---|---|---|
| Goal2547 resident min 0.509 ms | JSON `resident_kernel_min: 0.508575975894928` | ✓ |
| Authors force phase 6.616 ms | Raw txt "32768 repeat 1: RT Cores Force Calculations time: 0.006616 seconds" | ✓ |
| Goal2544 subtree float64 3.971 ms | JSON `resident_kernel_min: 3.9711039066314697` | ✓ |
| Goal2545 resident repeated 3.565 ms | JSON `resident_event_min: 3.565279960632324` | ✓ |
| Goal2546 float32 0.473 ms | JSON `resident_kernel_min: 0.47276800870895386` | ✓ |
| Correctness deltas (visited 0, contributions 0, max rel err 4.3e-5) | Goal2547 JSON `deltas` block | ✓ |
| Same pod, same device, same driver | Both reports: 203.57.40.169:10297, RTX A5000, 565.57.01 | ✓ |
| `same_tree_contract_as_authors: false`, `public_speedup_claim_authorized: false` | Goal2547 JSON metadata | ✓ |

---

### Defensible claims (can be stated internally)

1. **The 0.509 ms kernel number** — `resident_kernel_min` (best of 5 warm launches), force kernel only, prepared state pre-loaded. The number is accurate and the metric is correctly labeled.
2. **The 6.616 ms authors number** — the authors' binary's own "RT Cores Force Calculations time" output from the same pod. Accurately quoted.
3. **Same dimensionality and scalar inverse-square force shape** — Goal2547 metadata `same_dimension_as_authors: true`, `same_scalar_inverse_square_force_shape_as_authors: true`. These are contract-level facts (same mathematical function), defensible.
4. **Authors-generated input file** — `/root/rtbarneshut_32768_repeat_1.txt` was produced by the authors' code on the same pod. Accurate.
5. **Correctness pass** — visited-node delta 0, contribution-row delta 0, max scalar relative error 4.3e-5 against RTDL's own 3-D Python reference. Clean result.
6. **Not same tree contract** — the claim states "narrower RTDL generic-tree contract" and the metadata confirms `same_tree_contract_as_authors: false`. Accurately bounded.
7. **The "Not Authorized" list** — complete and correct: no 13x public claim, no paper reproduction, no same-contract claim, no native OptiX claim, no whole-app speedup.

---

### Claims that must remain blocked

These remain blocked and the packet correctly blocks them; listing them explicitly as a guard:

1. **"RTDL is 13x faster than RT-BarnesHut"** — the ratio 6.616/0.509 ≈ 13x is implicit in the side-by-side sentence. It must never appear publicly. The contracts differ, the tree traversal differs, and the authors' binary was recompiled at a non-published body count.
2. **Paper reproduction** — RTDL has not reproduced the authors' outputs. Correctness is validated only against RTDL's own Python reference, not against the authors' per-body force values.
3. **Same-contract claim** — tree construction (subtree-containment vs. OWL/OptiX triangle/autorope traversal) differs. Blocked.
4. **Native OptiX claim** — Goal2547 is a Torch/CUDA partner prototype. The RTDL native OptiX path does not yet implement this. Blocked.
5. **Whole-application speedup** — the 0.509 ms figure excludes `tree_prepare_cpu` (330.8 ms) and `tensor_prepare_host_to_device` (199.4 ms). The authors' 6.616 ms excludes their "Preprocessing Time" (19.4 ms). Both are kernel-phase-only figures. Any claim about end-to-end or "wall-clock application" time is blocked.
6. **Direct numeric force-output match with authors** — correctness is against RTDL's own reference. No cross-system force-value comparison has been performed.

---

### Required wording changes

Three changes are needed even for the internal version; all three are mandatory before any public use:

**1. Correctness provenance — add parenthetical**

Current:

> RTDL's Goal2547 3-D scalar CUDA diagnostic path computes the same 3-D scalar inverse-square force shape as the RT-BarnesHut artifact

"Computes the same force shape" means the same mathematical function is implemented, not that outputs are numerically matched against the authors. Correctness was validated against RTDL's own 3-D Python reference only. A reader can misread this as "produces the same numbers as the authors' code." Fix:

> RTDL's Goal2547 3-D scalar CUDA diagnostic path implements the same 3-D scalar inverse-square force-sum contract as the RT-BarnesHut artifact **(correctness validated against RTDL's own 3-D Python reference, not the authors' output)**

**2. Authors' artifact body-count recompile — must be disclosed**

The authors' artifact hardcodes `constexpr int NUM_POINTS = 100000000`. The 6.616 ms time comes from a recompile at `NUM_POINTS = 32768`. The device ordinal was also patched from `1` to `0`. These are non-algorithmic environment patches, but a reader of the claim sentence alone cannot know this. The 100M-body published configuration is a materially different workload. Fix:

> …while the authors' OWL/OptiX artifact **(recompiled at NUM_POINTS=32768 for size-matched comparison; device ordinal patched from 1→0 for pod compatibility)** measured force phase reaches `6.616 ms`

**3. Public-facing use: decouple the two numbers**

The current claim sentence places 0.509 ms and 6.616 ms in the same clause. Any reader who skips the guard sentence at the end will compute ~13x and share it. If this claim ever appears in a public context (blog post, conference abstract, partner slide), the two figures must be in separate sentences with different framing, or one of them must be removed. The guard sentence alone is not sufficient for public use — it needs structural separation, not just a trailing disclaimer.

Suggested public-safe rewording of the entire paragraph:

> On an RTX A5000 pod, RTDL's Goal2547 3-D scalar CUDA diagnostic kernel reached a `0.509 ms` resident minimum at 32,768 bodies on an authors-generated input file, under the `generic_aggregate_frontier_inverse_square_scalar_sum_3d_v1` contract (correctness validated against RTDL's own 3-D Python reference). For engineering orientation: the authors' OWL/OptiX artifact, recompiled at 32,768 bodies on the same pod, reported a `6.616 ms` force phase under a different OWL/OptiX traversal contract. No speedup ratio should be inferred; the tree construction and traversal contracts differ, and this is a diagnostic kernel-phase comparison only, not a paper reproduction or whole-application claim.

---

### Summary

The packet is internally disciplined and the numbers are clean. The "Strongest Currently Defensible Claim" is **acceptable for internal engineering use as-is**, with the correctness-provenance and recompile-disclosure additions strongly recommended. It is **not acceptable for public-facing use** without structural decoupling of the two timing figures and explicit no-ratio language; the current single-sentence side-by-side will be read as a ~13x speedup claim regardless of the trailing guard. The "Not Authorized" section and `next gate` section are well-structured and should be retained verbatim in any derivative document.
