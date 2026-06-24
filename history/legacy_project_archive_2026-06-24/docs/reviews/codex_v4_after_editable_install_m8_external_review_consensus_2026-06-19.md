# RTDL V4.0 After Editable Install M8 External Review Consensus

Date: 2026-06-19

Status: accepted 2-AI next-step consensus, not release approval.

## Context

Current head `7ab5a9a87a16147f090452b84fc577104203c2fe` records the V4
package/runtime hygiene addendum after the M8 packet:

- `v4_release_candidate`: 73 tests, pass locally and on Linux;
- source-tree runtime preflight: pass on `192.168.1.20`;
- editable source-tree install hygiene probe: pass on `192.168.1.20`;
- current front-door claim scan: pass;
- current release remains `v3.0.2`;
- `release_candidate_ready` remains false.

The editable-install probe is deliberately narrow. It validates fresh temporary
editable source-tree import/runtime hygiene from outside the repository with
`PYTHONPATH` unset, then runs one V4 M1 CuPy smoke against checkout
`build/librtdl_optix.so`. It does not authorize package install, PyPI, wheel,
stable SDK, generated binding package, V4 current release, public true-zero-copy,
async completion, public speedup, RTX speedup, full partner surfaces, or
multi-GPU claims.

## Reviewer Inputs

Bohr recommendation:

- seek external M8 release review next;
- do not expand routes, RTX perf, package flow, or true-zero-copy/async/full
  partner surfaces before reviewers attack the current promise;
- use the M8 packet, external review request, blocker manifest, source-tree
  runtime preflight, and editable-install probe as the review packet.

Averroes recommendation:

- submit the existing M8 packet for external critical review and wait for a
  verdict before any front-door switch or feature expansion;
- request an accept / accept-with-blockers / reject verdict, P0 blockers,
  forbidden wording, missing evidence, and one next engineering step;
- if external review is blocked, run only a fresh no-expansion validation pass
  and keep `release_candidate_ready` false.

## Consensus Decision

Both reviewers agree: the next highest-value V4 action is external M8 critical
review, not more implementation.

The current V4.0 evidence is now coherent enough to be attacked as an
experimental source-tree candidate. Expanding the implementation before that
review would increase surface area without first answering the key release
question: whether the exact fixed-radius M1 Python GPU operator candidate is
honest, useful, reproducible, and sufficiently bounded.

## Required Next Action

Send the current review request:

`docs/reviews/codex_v4_m8_external_review_request_2026-06-19.md`

The reviewer should answer:

1. accept baseline, accept with blockers, or reject;
2. P0 blockers;
3. P1 risks;
4. forbidden wording;
5. missing evidence;
6. whether the fixed-radius M1 route is enough as the V4 experimental headline;
7. the single next engineering step after review.

## Do Not Do Next

Do not pursue these before the external review verdict unless a reviewer or the
maintainer explicitly redirects:

- another route;
- broader PyTorch, Numba, or DLPack partner surfaces;
- async completion;
- public true-zero-copy wording;
- RTX/RT-core speedup claims;
- PyPI, wheel, stable SDK, or generated bindings;
- public multi-language C ABI promotion;
- front-door docs switch.

## Fallback If Review Is Blocked

If external review cannot be obtained, perform a fresh no-expansion validation
pass on the current head:

```bash
PYTHONPATH=src:. python3 scripts/run_test_matrix.py --group v4_release_candidate
PYTHONPATH=src:. python3 scripts/v4_0_source_tree_runtime_preflight.py --require-v4-gpu-runtime
python3 scripts/v4_0_editable_install_runtime_probe.py --system-site-packages --run-v4-smoke
python3 scripts/v4_0_current_front_door_claim_boundary_scan.py
git diff --check
```

Then keep `release_candidate_ready` false and document that review remains the
blocking gate.
