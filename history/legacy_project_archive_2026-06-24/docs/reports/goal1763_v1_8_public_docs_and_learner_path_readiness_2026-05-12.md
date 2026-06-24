# Goal1763 v1.8 Public Docs And Learner Path Readiness

Date: 2026-05-12

## Verdict

`v1_8_public_docs_and_learner_path_ready_pending_release_authorization`

The front-door documentation has been refreshed for the v1.8 source-tree
Python+RTDL release boundary. The docs now teach the release design directly:
Python owns application logic, RTDL owns the RT-shaped kernel contract, and the
native engine boundary stays app-agnostic.

This report does not authorize a tag, version bump, push, package upload, or
release.

## Updated Public Entry Points

| Entry point | Release-prep role |
| --- | --- |
| `README.md` | front-page project promise, start commands, v1.8 design split |
| `docs/README.md` | docs index and v1.8 learner rule |
| `docs/quick_tutorial.md` | first-run tutorial plus Python app / generic engine explanation |
| `examples/README.md` | example inventory plus how to read app examples under v1.8 |
| `docs/public_documentation_map.md` | learner questions and public doc layering |
| `docs/current_architecture.md` | current-main architecture lens after Goal1758/Goal1762 |
| `docs/capability_boundaries.md` | current public release plus v1.8 candidate boundary |
| `docs/current_main_support_matrix.md` | support matrix wording after v1.8 prep consensus |
| `docs/performance_model.md` | performance boundary after v1.8 prep consensus |
| `docs/rtdl/ir_and_lowering.md` | generic native boundary after v1.8 cleanup |

## Learner Contract

A GitHub learner should be able to answer:

1. How do I run RTDL from the source tree?
2. What does `input -> traverse -> refine -> emit` mean?
3. Which parts of my program stay in Python?
4. Which parts belong to the RTDL engine?
5. Why can examples have app names while native engine symbols stay generic?
6. Why is `--backend optix` not automatically a public speedup claim?
7. Why is v1.8 source-tree Python+RTDL, not package-install or
   Python+partner+RTDL?

## Public Claim Boundary

The docs continue to block:

- package-install support
- broad speedup wording
- whole-application acceleration
- universal backend support
- Python+partner+RTDL completion
- PyTorch/CuPy integration
- true zero-copy support
- backend-flag-only RTX claims

## Release Boundary

The docs are ready for the v1.8 release-candidate state, but they still say
that v1.8 is not tagged or released until the user authorizes release action.
That is intentional.
