# V4 Post-Remediation Tutorial/App Reaudit And Closure

Date: 2026-06-27

This is an internal record for the follow-up audit after the first tutorial/app
gap remediation pass.

## Reaudit Method

Two read-only sub-agents rechecked the current public path:

- Application-side learner: studied benchmark apps, paper-reproduction
  wrappers, tutorial app-lowering programs, and public app documentation.
- Tutorial-side learner: studied only the public learning path and did not
  inspect archived harness internals.

## Reaudit Findings

The tutorial-side learner concluded that the public learning path is now strong
enough to understand all 10 benchmark apps at the
relation/operator/partner/continuation level. Remaining partials were:

- Triangle counting: graph witness flow was clear, but graph-derived
  ray/triangle columns were not visible enough.
- LibRTS spatial index: the AABB all-ops program still felt like a prepared
  runner call around a tiny fixture.
- Contact manifold: bounded witnesses were taught, but the broadphase-to-contact
  path was split across separate examples.
- Paper wrappers: wrapper purpose was covered, but default scripts still
  forwarded directly to the full runner.

The application-side learner agreed that the remediation substantially closed
the gap, but still marked several full-route or paper-route areas as partial:

- RTNN because `ranked_summary` appeared in recipes as a non-release planner
  surface.
- Contact manifold because full broadphase-to-witness construction was not one
  public teaching flow.
- Spatial RayJoin and RT-BarnesHut paper wrappers because they forwarded to the
  full runner by default.

## Second Remediation Pass

The following changes were made:

| Residual issue | Fix |
| --- | --- |
| RTNN recipe showed `ranked_summary` as a planner surface with no V4.0 release surface. | `benchmark_app_recipes.py` now describes ranked summary as an app-owned continuation after the V4 nearest-witness relation. |
| Triangle counting lacked visible graph-derived ray/triangle columns. | `triangle_counting_graph_lowering.py` now emits `ray_rows` and `triangle_primitive_rows` before witness rows and grouped counts. |
| LibRTS AABB learning path was too runner-shaped. | Added `aabb_spatial_index_predicates.py` to teach point containment, range containment, and range intersection manually. |
| Contact manifold learning path was split. | Added `contact_manifold_lowering.py` to teach shape bounds -> broadphase rows -> witness candidates -> bounded witnesses -> overflow validation. |
| Paper wrappers forwarded to the full runner by default. | `rt_barneshut.py` and `rayjoin.py` now default to a clean route explanation or `--json`; full runner execution requires `--run-harness`. |

## Verification

The following checks passed after the second remediation pass:

- modified tutorial scripts and paper wrappers run locally;
- paper wrappers still forward to full runners when explicitly invoked with
  `--run-harness`;
- public forbidden-language scan returned no findings;
- `tests.v4_goal4640_public_docs_cleanup_test` passed;
- release packaging/staging/clean-checkout unit tests passed;
- strict universe audit and final tag gate must be rerun after this record is
  staged.

## Closure Interpretation

After this pass, the public tutorial path should be considered sufficient for
users to understand and begin implementing the benchmark app logic from current
V4 materials before opening the full app source.

The remaining distinction is intentional: full serious benchmark execution is a
runner protocol, not the first tutorial layer. The public docs now teach that
boundary directly instead of hiding it.
