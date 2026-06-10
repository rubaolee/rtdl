# Goal4270 v2.10 Milestone Release 3-AI Consensus

Date: 2026-06-10
Status: release consensus for `v2.10` source-tree milestone

## Decision

Codex accepts the v2.10 milestone release packet after fresh Claude and Gemini
review.

The permitted release action is narrow:

```text
Create and push the `v2.10` source-tree milestone tag.
```

The release action does not authorize package-install wording, broad speedup
wording, whole-app acceleration wording, broad RT-core wording,
RTDL-beats-RayJoin wording, paper-reproduction wording, true-zero-copy wording,
automatic backend/partner selection wording, AMD/HIPRT performance wording,
Embree+Numba CPU partner wording, app-specific native-engine logic, or
universal CuPy-vs-Numba winner wording.

## Inputs

| Role | File | Verdict |
| --- | --- | --- |
| Codex packet | `docs/reports/goal4267_v2_10_milestone_release_packet_2026-06-10.md` | accept for final consensus |
| Claude | `docs/reviews/goal4268_claude_review_goal4267_v2_10_milestone_release_packet_2026-06-10.md` | `accept` |
| Gemini | `docs/reviews/goal4269_gemini_review_goal4267_v2_10_milestone_release_packet_2026-06-10.md` | `accept` |

This satisfies the project rule that key release decisions require Codex plus
two distinct external AI reviewers.

## Evidence Synthesis

The consensus accepts these facts:

1. Goal4267 is the final v2.10 milestone packet.
2. The user explicitly requested the milestone release on 2026-06-10:

   ```text
   Then go! Make this one a milestone version.
   ```

3. The last runtime/performance commit before the packet is `0c842eb0`
   (`Goal4266 publish large-scale partner timing evidence`).
4. Goal4266 adds decision-grade same-contract RTX 3090 evidence for the two
   partner-needed custom-continuation families:
   - RayDB-style unfused grouped count/sum/min/max and average-as-sum-plus-count;
   - Triangle/RayJoin-style compact-mask continuation.
5. The learner docs now explain the partner choice clearly:
   - use RTDL primitives first when they exactly answer;
   - use CuPy for current performance on the measured large-scale custom
     continuations;
   - use Numba when no-RawKernel Python-source reference code matters;
   - do not treat primitive-only rows as partner-choice rows.
6. Both external reviewers found no required content fix before consensus.

## Validation

Codex ran the focused local release gate after Goal4267:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal4267_v2_10_milestone_release_packet_test tests.goal4265_partner_guidance_user_facing_cleanup_test tests.goal4266_large_scale_partner_comparison_test tests.goal4257_v2_10_release_candidate_packet_draft_test tests.goal4254_v2_10_public_claim_wording_candidate_test tests.goal4258_public_claim_wording_repair_closure_test
```

Observed result:

```text
Ran 20 tests in 1.167s
OK
```

Codex also attempted to reach the last known Goal4266 CUDA pod endpoint:

```text
root@213.192.2.91 -p 40030
```

The endpoint refused the SSH connection. Therefore this consensus does not
claim a fresh pod run at the final documentation/governance commit. This is
acceptable for this milestone because the final delta after `0c842eb0` is
learner documentation, release packet, review, and consensus material only; no
runtime/performance code was changed after the Goal4266 evidence commit.

## Final Boundaries

Allowed wording:

```text
v2.10 is a source-tree milestone for Python + RTDL + explicit partner
continuations over a generic app-agnostic native engine.
```

Allowed wording:

```text
For the measured Goal4266 RTX 3090 partner-continuation contracts, CuPy is
currently faster than the Numba reference implementation; Numba remains useful
for users who want no-RawKernel Python-source custom continuation code.
```

Blocked wording:

```text
RTDL v2.10 is package-install ready, universally faster, a broad RT-core
speedup guarantee, a full paper reproduction, a true-zero-copy product, an
automatic partner selector, an AMD/HIPRT performance release, or proof that
CuPy is always faster than Numba.
```

## Verdict

`accept`

Codex may create, push, and publish the `v2.10` source-tree milestone tag after
the focused local gate passes on the exact commit being tagged.
