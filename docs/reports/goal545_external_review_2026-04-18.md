# Goal 545: v0.9 HIPRT Plan — External Review

Date: 2026-04-18
Reviewer: Claude (claude-sonnet-4-6)
Verdict: **ACCEPT**

## Summary

The plan is honest, technically scoped, and suitable as the v0.9 goal ladder for
making HIPRT a first-class RTDL backend. Key reasons:

### Strengths

1. **Honest baseline.** The plan states exactly what HIPRT currently supports
   (Ray3D/Triangle3D hit count only) and does not inflate the baseline to make
   the gap look smaller.

2. **Technical honesty constraint is structural, not advisory.** The three-class
   workload taxonomy (`native HIPRT traversal`, `HIPRT-managed GPU companion`,
   `not acceptable`) prevents any workload from silently falling back to CPU. The
   rule is in the plan text, the matrix, and the release rule — it cannot be
   bypassed at individual goal level without triggering a 3-AI consensus step.

3. **Risks are explicit and credible.** The plan names the three most serious
   risks before implementation starts:
   - 2D ray/triangle coplanarity after lifting (this is a real degenerate case
     in HIPRT triangle intersection and may require AABB proxies or full workload
     rejection for some 2D predicates);
   - graph and DB workloads may reduce to ordinary GPU compute under HIPRT,
     requiring reclassification;
   - the GTX 1070 has no RT cores, so performance results are valid timing
     evidence but cannot support RT-core speedup claims.

4. **Goal ladder is correctly staged.** Goals 546–547 establish the skeleton and
   harness before any implementation lands. Goals 548–551 expand one workload
   family at a time. Goals 552–554 close with cross-backend evidence and public
   docs. This order means every workload reaches the harness before it can be
   claimed as supported.

5. **3-AI consensus gates are placed at the right checkpoints.** Plan scope
   (Goal 545), any workload rejection or reclassification (Goals 549–550), and
   public release wording (Goals 553–554) all require 3-AI sign-off. Lower-stakes
   implementation goals require 2-AI minimum, which is proportionate.

### Caveats (do not block acceptance, but must be tracked)

- **2D geometry family (Group C) carries the highest rejection probability.**
  The plan correctly marks it as high difficulty and flags the coplanarity risk,
  but the feasibility is not resolved at this stage. Goals 549 and the matrix
  entry for `ray_triangle_hit_count` 2D both flag this. If lifting is
  geometrically degenerate for all 2D ray/triangle predicates, a substantial
  fraction of Group C may end up in `not acceptable` — which is the right
  outcome, but the plan should expect that outcome openly rather than treating
  it as a surprising edge case.

- **AMD GPU gap.** The plan acknowledges that AMD validation is unavailable. This
  is honest, but v0.9 public docs should be explicit that HIPRT correctness and
  performance results are NVIDIA-only on a GTX 1070.

- **Graph and DB families may require reclassification at Goal 550/551.** The
  plan permits this with appropriate 3-AI gating. The risk is that those goals
  become primarily "honest documentation of HIPRT limits" rather than
  implementations. That is still a valid v0.9 outcome — but it changes the scope
  of Goals 553 (docs) and 554 (audit), which should be written conservatively.

### What would cause a BLOCK at a later goal

The following conditions, if they arise during execution, would require a plan
revision before the affected goal can close:

- Any workload passes review by claiming "HIPRT-managed GPU companion" support
  without an explicit consensus record.
- A v0.9 release candidate claims peer-backend parity for a workload that has
  not passed row-level correctness or has no performance data.
- The 2D coplanarity issue is resolved by adding a silent 2D→3D lifted fallback
  without a consensus reclassification step.

## Conclusion

ACCEPT for execution as the v0.9 goal ladder. The plan is technically honest,
risks are named before implementation starts, and the consensus gating structure
prevents dishonest release claims. The main execution risk is that Group C and
Groups D/E may produce more rejections than implementations — but the plan's
own release rule and reclassification protocol handle that case correctly.
