# Call For Review: Goal4953 RayJoin Binary Overlay Operator Contract

Date: 2026-07-04

Review target:

- `history/internal_docs/goal4953_rayjoin_binary_overlay_operator_contract_2026-07-04.md`

Requested verdict:

`approve_goal4953_binary_overlay_operator_contract`

or:

`block_goal4953_binary_overlay_contract_until_amended`

## Context

The previous post-4952 direction was a plain writer fine-grained audit.

The owner identified a more important framing:

> RayJoin overlay, in a real SQL/dataflow pipeline, is an intermediate operator.
> It should produce binary/columnar output consumed by the next operator. The
> author-compatible text writer is a sink cost and should not be treated as the
> main measure of RTDL's RT/dataflow value.

Goal4953 therefore proposes a revised next goal:

- define the binary/columnar overlay operator contract;
- measure the public sample with the paper text writer isolated or bypassed;
- classify which costs are real operator costs versus sink/text-output costs;
- decide whether the next implementation should be device-resident
  reprojection/sort/binary-row construction.

No implementation is authorized in Goal4953.

## Review Questions

1. Is this revised Goal4953 the right correction after the realization that the
   paper writer is a sink workload rather than the core RTDL operator workload?

2. Does the goal correctly separate two lines:
   - paper reproduction text-output path;
   - RTDL binary intermediate operator path?

3. Does the proposed binary overlay contract avoid putting RayJoin paper text
   semantics into RTDL core?

4. Are the required measurements sufficient to answer whether current Layer 1/2
   infrastructure can help the real operator path?

5. Does the goal avoid overclaiming that a binary operator is already optimized?

6. Is it correct that this goal should supersede or pause the writer-only audit
   as the next main step?

7. Are the exit labels complete and decision-forcing?

8. Should review approve this goal with:

   `approve_goal4953_binary_overlay_operator_contract`

## Non-Authorization Boundary

Approval authorizes only Goal4953 contract/measurement work.

It does not authorize:

- native writer implementation;
- device writer implementation;
- device-resident reprojection/sort implementation;
- public API exposure;
- performance claims;
- hidden RayJoin-specific RTDL core logic;
- removal or weakening of the paper-reproduction correctness path.
