# Goal5840 Formal Attempt 04 Engineering Failure

Date: 2026-09-03

## Classification

`INDEPENDENT_CHECKER_TRIANGLE_STATUS_FLOW_RULE_ENGINEERING_FAILURE`

This was an independent-checker rule defect after two successful public-route
executions and two successful raw evidence captures. It is not a scientific
failure, a lowering counterexample, a mutation-suite result, or an accepted
complete Goal5840 result.

The first frozen mode did receive an independently accepted five-property
report. That per-mode acceptance is preserved below and must not be erased or
inflated: the formal runner stopped during the second mode, so no complete
four-mode Goal5840 result exists.

## Immutable Execution Identity

- Formal attempt number: `4`
- Source commit:
  `4f2a5d7f4d0f2c4a74756d7456180c8520742a47`
- Post-Attempt-03 repair-authority internal seal:
  `c9be840758e696afec003055c93876b3f54fb02b5aaf93eb19fa4d4a9c3e2cc1`
- Pod endpoint used: `root@213.173.108.100:12943`
- GPU: `NVIDIA RTX 2000 Ada Generation`
- GPU UUID: `GPU-f0ab2afa-0ec0-7da9-c951-01fc713ee1e9`
- Driver: `580.159.04`
- Compute capability: `8.9`
- CUDA toolkit: `12.8`
- OptiX SDK: `9.0.0`
- Native DSO path:
  `/workspace/goal5840-build-attempt04-4f2a5d7/librtdl_optix_goal5840.so`
- Native DSO bytes: `7,181,936`
- Native DSO SHA-256:
  `f27d72c8adce4a7c3ed9144ed3d1b10a6ebee357d96c9d4e22047b3b792e9112`
- Native build manifest path:
  `/workspace/goal5840-build-attempt04-4f2a5d7/NATIVE_BUILD.json`
- Native build manifest file SHA-256:
  `d402e94a99c13031943bf27fcbf67d383c878dd6492437476f5e28ff79e0818d`
- Native build manifest internal result seal:
  `3d82a0bab752981c1f5d0fada80da31aebf72af7d873e13d5763c099882fc3af`
- Output directory:
  `/workspace/goal5840-evidence-attempt04-4f2a5d7`

The exact detached source checkout was clean before the native build, after the
failed runner, and during the post-failure artifact inventory.

## Published Failure Artifacts

The formal runner published exactly four files before stopping fail closed:

| Artifact | Bytes | File SHA-256 | UTC mtime |
|---|---:|---|---|
| `mode_01_capacity_fail_closed_collection_bundle.json` | 1,364,069 | `785b0b9906368eabfecb190b0f6afc0d0768c2bcad00144cd018e5636c0f1d76` | `2026-09-03T10:33:52Z` |
| `mode_01_capacity_fail_closed_collection_independent_check.json` | 3,967 | `0c007fea0a8ab28e1ba3fe2f04752126aef28cd6bd181a9213d31de5c3f69876` | `2026-09-03T10:33:53Z` |
| `mode_02_all_hit_count_bundle.json` | 806,032 | `03e869e83164e3c8dac830111d7dbf17ae97ad0f69e00d3c5cb2f6bca7084739` | `2026-09-03T10:33:57Z` |
| `mode_02_all_hit_count_independent_check.json` | 3,616 | `02fbbf9a788b2d8589a6911ce20f07fec0e8e71fec5871e456c898d9888a6b90` | `2026-09-03T10:33:57Z` |

The mode-1 report's internal verdict is `ACCEPT`, with five passes and zero
rejects. Its internal report seal is
`e6ba773f84ff97a6b89f9d8c7466399313e43791a4f970e5cfe0b063c41bbc36`.
The mode-2 report's internal verdict is `REJECT`, with four passes and one
reject. Its internal report seal is
`8bcf240740aa1b5826e2f40ca480a321f7d34bbd25a27db4decaee59e8c9a70d`.

These files remain Attempt04 evidence. They are identified here by content
hash; they are not copied into the Git tree and are not substituted into a
successor result.

## Observed Formal-Runner Sequence

1. Repository, frozen-core, preregistration, three prior incidents, three prior
   repair authorities, native build, exported-symbol, and machine preflight
   checks passed.
2. Frozen mode 1,
   `stable::bounded_relation::canonical_bounded_pair_collection::capacity_fail_closed_collection`,
   returned its frozen expected output and published a raw bundle whose
   execution receipt reports two successful true-OptiX launches, complete
   output, status before output, and no partial result.
3. The standalone checker independently accepted all five properties for mode
   1.
4. Frozen mode 2,
   `stable::triangle_reduction::checked_u64_reduction::all_hit_count`, returned
   its frozen expected output and published a raw bundle whose execution
   receipt reports one successful true-OptiX launch, complete output, status
   before output, and no partial result.
5. The standalone checker passed CP001, CP002, CP003, and CP005, but rejected
   CP004 with reason `TC004_STATUS_SOURCE_ANCHOR_MISSING` and detail
   `('first_error_claimed != 0u', 'const unsigned long long result')`.
6. The runner stopped before modes 3 and 4, runtime trust-root publication,
   mutation execution, or `RESULT.json` publication.

## Root-Cause Diagnosis

The CP004 rule reused stale route-table text anchors from an earlier synthetic
triangle wrapper instead of validating the actual control-flow shape of the
captured production wrapper.

The real triangle wrapper uses `final_value`, not `result`. Its fast raygen
performs `optixTrace`, checks
`params.fast_control->error_code != 0u`, computes
`const unsigned long long final_value`, and only then commits
`params.per_ray_u64[query] = final_value`. Its diagnostic raygen has both a fast
branch with the same status-before-output gate and a non-fast branch that checks
`params.status[query].first_error_claimed != 0u`, calls the status finalizer,
and commits the per-ray value only afterward.

The captured wrapper therefore contains the required status-gated continuation
behavior, but the generic two-string checker searched for the nonexistent
declaration `const unsigned long long result`. The pre-pod test fixture repeated
that stale synthetic spelling and consequently failed to exercise the real
wrapper shape.

This is a checker/test-model defect. The production wrapper, frozen routes,
fixtures, expected outputs, native engine, runtime, and frozen semantic core do
not require modification.

## Post-Failure Diagnostic Disclosure

After rejection, the four published files were downloaded to the Mac and
parsed offline. The exact production wrapper sources were extracted from the
mode-2 bundle to identify the status-flow mismatch. Pod commands after failure
only listed, statted, and hashed already-written files, printed the build
manifest, and checked Git status. No additional route execution, OptiX launch,
evidence capture, mutation application, or GPU diagnostic process occurred.

## Counts At Failure Boundary

Formal Attempt04 alone:

- runner processes started: `1`
- frozen modes entered: `2`
- public route expected outputs returned: `2`
- published evidence bundles: `2`
- published independent property reports: `2`
- independently accepted per-mode reports: `1`
- published mutation applications: `0`
- accepted complete Goal5840 results: `0`

Cumulative through Attempts 01, 02, 03, and 04:

- formal runner processes started: `4`
- frozen modes entered: `5`
- public route expected outputs returned: `5`
- published evidence bundles: `3`
- published independent property reports: `3`
- independently accepted per-mode reports: `1`
- published mutation applications: `0`
- accepted complete Goal5840 results: `0`

The two post-Attempt-02 diagnostic launches remain separately classified and
unaccepted. Attempt04 added zero post-failure GPU diagnostic launches.

## Permitted Repair Boundary

A successor authority may permit only:

- replacing the stale generic two-string CP004 wrapper test with
  route-specific structural status-flow checks over the exact captured wrapper;
- requiring ordered triangle fast and diagnostic status gates before their
  corresponding per-ray output commits;
- preserving the bounded fail-closed and sphere status-flow checks at their
  actual route-specific shapes;
- replacing the stale triangle synthetic wrapper with a faithful minimal model
  of the real dual-path wrapper;
- adding hostile regressions that remove, move, or comment-spoof a required
  triangle status gate or output order;
- appending this incident and a fourth repair authority; and
- extending capture and verification to bind all four incidents and repair
  authorities under a new formal Attempt05 schema.

It may not change routes, fixtures, expected outputs, declarations,
control-flow trust roots, properties, mutation selectors or replacements,
native engine code, runtime code, or any Goal5838 frozen-core byte.

## Claim Boundary

- Independently accepted Attempt04 per-mode reports: `1`
- Accepted complete Goal5840 result: `false`
- Four-mode lowering/refinement preservation established: `false`
- General compiler soundness: `false`
- Application correctness: `false`
- Performance or speedup: `false`
- External review or consensus: `false`
