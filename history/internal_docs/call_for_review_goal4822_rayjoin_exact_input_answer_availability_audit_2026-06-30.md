# Call For Review: Goal4822 RayJoin Exact Input/Answer Availability Audit

Date: 2026-06-30

Requested reviewer: Antigravity

Requested verdict label:

`approve_goal4822_close_expansion_until_exact_inputs_answers_available`

## Packet To Review

Please review:

`history/internal_docs/goal4822_rayjoin_section57_exact_input_answer_availability_audit_2026-06-30.md`

## Context

Goal4820 repaired two real RTDL product/core issues exposed by RayJoin:

- directed-segment point-location SoS reported-distance tie-break for OptiX;
- per-map midpoint face storage for overlay continuation.

Goal4821 then produced a bounded public-sample performance smoke:

- public County x Soil sample only;
- author clean-compat binary and repaired RTDL both byte-equal to the author
  answer on 3/3 runs;
- bounded ratio: `1.7076431181058986x`;
- no full Section 5.7 or broad performance claim.

Antigravity approved Goal4821 and required that any expansion to additional
Section 5.7 pairs happen only if exact author inputs and answer files are
available.

Goal4822 performs that availability audit.

## Questions

Please answer each question explicitly:

1. Does Goal4822 correctly distinguish the author public County x Soil sample
   from the paper Section 5.7 eight-pair overlay matrix?
2. Does the evidence support the claim that the author repo currently contains
   only the public County x Soil answer under `test/dataset`?
3. Does the evidence support the claim that the current POD lacks the author
   `DATASET_ROOT` and the old `/workspace/rayjoin_section57_data` exact root?
4. Is it correct to classify current County x Zipcode as `input_without_answer`
   rather than runnable exact paper reproduction evidence?
5. Does the packet preserve Goal4380 correctly as bounded 2/8 historical
   count-match/process-wall evidence, not byte-equal output-chain proof?
6. Is it correct to block additional Section 5.7 performance runs until exact
   inputs and author answer files are restored?
7. Is the recommended next step, Goal4823 closure packet, the right next move
   if no additional exact inputs/answers are available?
8. Does the packet avoid overclaiming full RayJoin paper reproduction, full
   eight-pair coverage, or broad RTDL performance?

## Non-Authorization Block

This review must not authorize:

- full Section 5.7 eight-pair paper reproduction claims;
- performance runs on pairs without exact author answer files;
- treating historical `Count Match=True` as byte-equal output-chain equality;
- Embree work;
- edits to public docs/tutorials/release surface;
- broad RTDL performance claims.

## Expected Output

Please write a review result with:

- a verdict label;
- answers to the eight questions;
- any blocking findings;
- explicit non-authorization boundaries.
