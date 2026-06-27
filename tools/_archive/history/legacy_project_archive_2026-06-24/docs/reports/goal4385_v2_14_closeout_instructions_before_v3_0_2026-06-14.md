# Goal4385 v2.14 Closeout Instructions Before V3.0

Date: 2026-06-14

Status: maintainer instruction packet.

## Directive

End V2.X by closing v2.14 as the final cleanup/evidence release before V3.0. Do not start V3.0 implementation until every required v2.14 closeout action below is complete.

## Required Actions Before v2.14 Ends

| Order | Action | Required output |
| ---: | --- | --- |
| 1 | Freeze the promoted benchmark-app inventory. | One release matrix naming included rows and marking excluded/internal rows. |
| 2 | Finalize the RTDL OptiX-vs-Embree same-contract table. | A public/internal table with backend, hardware, partner, dataset, contract, phase explanation, and caveat per row. |
| 3 | Lock public wording boundaries. | No broad "all apps accelerated", no whole-app claim without phase proof, no paper claim without exact dataset/author timing basis. |
| 4 | Mark RayJoin overlay with an explicit Section 5.7 boundary. | Superseded by maintainer decision: the available 2/8 exact CDB subset is public-review-ready; full 8/8 Section 5.7 wording remains blocked. |
| 5 | Keep RTDBSCAN wording narrow. | State that Embree fairness was fixed, but full-app speedup is continuation-dominated. |
| 6 | Keep synthetic large rows honest. | Triangle, Barnes-Hut, Hausdorff, contact, and robot rows must say large synthetic or paper-like, not paper-exact. |
| 7 | Preserve app-agnostic primitive language. | No benchmark app may promote app-specific native engine names. |
| 8 | Confirm partner usage per row. | If a partner is used, name it; if no partner is needed, say primitive-first. |
| 9 | Run final local gates. | Focused unittest set for v2.14 release docs, cross-audit, reports, and touched apps. |
| 10 | Run final pod gates. | Same focused gates on the pod with OptiX and Embree env vars set. |
| 11 | Write the v2.14 final closeout report. | A concise report saying what is public-ready, internal-only, and deferred to V3.0. |
| 12 | Get release-packet review if public wording changes. | Claude/Gemini review over exact v2.14 public wording before publication. |

## Explicit Non-Actions

- Do not write V3.0 implementation code.
- Do not introduce V3.0 planner APIs.
- Do not rename V2.X primitives into V3.0 concepts.
- Do not claim RT cores universally beat Embree.
- Do not claim RTDL matches author hot C++/CUDA/OptiX paths.
- Do not move or relabel published tags without explicit maintainer decision.

## v2.14 Minimum Final Table

The v2.14 final report must include at least these rows:

| Row | Required stance |
| --- | --- |
| RTNN | Strong large RTNN-shaped prepared aggregate row; no paper-dataset claim. |
| RTDBSCAN | Fairer after Embree compact threshold route; continuation-dominated full-app result. |
| RayJoin LSI | Good row-scoped primitive claim; not full paper reproduction. |
| RayJoin PIP | Narrow claim only; CDB closest-hit face-id route deferred. |
| RayJoin Overlay | Public-review-ready for the available 2/8 exact CDB subset; full 8/8 Section 5.7 and author-hot-compute parity remain blocked. |
| LibRTS AABB | Strong prepared hot-query primitive row; cold total and exact paper reproduction separate. |
| Triangle Counting | Strong synthetic RT-Graph-shaped primitive row; no paper dataset claim. |
| Barnes-Hut | Node-coverage traversal only; no full force-solver claim. |
| Hausdorff | Threshold decision only; no exact witness-distance claim. |
| Robot Collision | Discrete sampled grouped-segment any-hit flags only. |
| Contact Manifold | AABB broadphase/contact-witness primitive only; no full physics solver claim. |
| RayDB-style | Strong grouped primitive evidence; label generated/paper-shaped data honestly. |

## Exit Criteria

v2.14 is closed only when:

- final local gates pass;
- final pod gates pass;
- the v2.14 release packet names every public row and every internal-only row;
- the public wording packet has no claim that contradicts the cross-audit;
- the final closeout report says V3.0 is next but still blocked until v2.14 closure is recorded.

After these conditions are met, the project may begin V3.0 M1 design work. V3.0 implementation remains blocked until the M1 IR design document is frozen.
