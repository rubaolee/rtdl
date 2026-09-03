# Goal5840 Formal Attempt 03 Engineering Failure

Date: 2026-09-03

## Classification

`INDEPENDENT_CHECKER_INLINE_SPECIALIZATION_RULE_ENGINEERING_FAILURE`

This was an independent-checker rule defect after a successful public-route
execution and successful raw evidence capture. It is not a scientific failure,
a lowering counterexample, a mutation-suite result, or accepted positive
Goal5840 evidence.

## Immutable Execution Identity

- Formal attempt number: `3`
- Source commit:
  `78610253c9650c3661f3f0107da373bf9f2ff549`
- Post-Attempt-02 repair-authority internal seal:
  `998f6d9ac8490b7bc70441678bd994a05ca3d784dde5887d4b871ccb20cff15c`
- Pod endpoint used: `root@213.173.108.100:12943`
- GPU: `NVIDIA RTX 2000 Ada Generation`
- GPU UUID: `GPU-f0ab2afa-0ec0-7da9-c951-01fc713ee1e9`
- Driver: `580.159.04`
- Compute capability: `8.9`
- OptiX SDK: `9.0.0`
- Native DSO path:
  `/workspace/goal5840-build-attempt03-7861025/librtdl_optix_goal5840.so`
- Native DSO SHA-256:
  `09aa9b432a2b55ccb7835306d591b8b6f0b2a1240c59f0e5534784cae3d3f660`
- Native build manifest path:
  `/workspace/goal5840-build-attempt03-7861025/NATIVE_BUILD.json`
- Native build manifest internal result seal:
  `23b11a79381757d29e21bb4624cb681a54bc95ad4bf116fe8ba3456c0de3aef5`
- Output directory:
  `/workspace/goal5840-evidence-attempt03-7861025`

The exact source checkout was clean before and after the failed runner.

## Published Failure Artifacts

The formal runner published exactly two files before stopping fail closed:

| Artifact | Bytes | File SHA-256 | UTC mtime |
|---|---:|---|---|
| `mode_01_capacity_fail_closed_collection_bundle.json` | 1,364,074 | `398e366efe3c7c156ef5c334ded4a258e360f55eded254eb5c7f491726296635` | `2026-09-03T09:59:24Z` |
| `mode_01_capacity_fail_closed_collection_independent_check.json` | 3,396 | `7aa16896c14e63664b486514b35713657b950a7e8e8a74709aa9816a0760c51a` | `2026-09-03T09:59:24Z` |

The bundle and report remain unaccepted failure evidence. They are identified
here by content hash; they are not copied into the Git tree and are not inputs
to a successor positive result.

## Observed Formal-Runner Sequence

1. Repository, frozen-core, preregistration, both prior incidents, both prior
   repair authorities, native build, exported-symbol, and machine preflight
   checks passed.
2. Frozen mode 1,
   `stable::bounded_relation::canonical_bounded_pair_collection::capacity_fail_closed_collection`,
   started.
3. The public route returned its exact frozen expected output:
   `((100, 10), (100, 30), (200, 20))`.
4. Raw target-evidence capture succeeded and published the exact bundle above.
5. The standalone checker returned `REJECT`: CP002 through CP005 passed, while
   CP001 failed with
   `TC001_COMPOSED_PTX_SYMBOL_ABSENT@any_hit` for
   `rtdl_v4_any_hit_54d76a4e128f6d78`.
6. The runner stopped before modes 2 through 4, runtime trust-root publication,
   mutation execution, or `RESULT.json` publication.

## Root-Cause Diagnosis

The CP001 rule incorrectly applied the linked-leaf-PTX symbol criterion to the
bounded route's `inline_cuda_wrapper` composition mode.

The production composer explicitly permits an inline leaf symbol to appear as
a definition, a call, or neither in optimized PTX after source compilation and
optimization. The Attempt-03 PTX retains the real
`__anyhit__rtdl_v4_bounded_relation` OptiX entry but legally eliminates the
unused exact leaf symbol. Therefore final-PTX symbol presence is not a valid
identity rule for this composition mode.

Offline inspection exposed a second, more important distinction. The bounded
route is an exact closed standard-callback specialization: its wrapper contains
the seven generated `__forceinline__` leaf definitions and binds their hashes,
but the executable entry programs use a hand-written partial evaluation of the
same closed callback rather than calling those definitions. The wrapper's
inherited `linked_role_symbols=true` default is consequently inaccurate.

The downloaded raw bundle independently supports the source-identity chain:

- all seven complete inline function definitions can be structurally extracted
  from the exact wrapper source;
- every extracted per-role SHA-256 equals its corresponding
  `identity_preimage.inline_cuda_leaves` value; and
- joining the seven extracted definitions in frozen leaf order yields
  `0de32f07a136319f502bab334d3154faf5b6a89995c74a4ebcbc038993ce8bd8`,
  exactly `identity_preimage.inline_cuda`.

The existing checker did not independently recompute those inline digests. It
also did not explicitly derive the role/effect facts from the actual
partial-evaluated wrapper. Merely removing the composed-PTX symbol requirement
would therefore weaken CP001 and is not an admissible repair.

## Offline Diagnostic Disclosure

After the formal rejection, the two published failure artifacts were downloaded
and inspected on the Mac. Structural parsing recomputed the seven leaf hashes
and aggregate inline-source hash stated above. Pod commands after failure only
listed, statted, and downloaded already-written files and checked Git status.
No additional route execution, OptiX launch, evidence capture, mutation, or
GPU diagnostic process occurred.

## Counts At Failure Boundary

Formal Attempt 03 alone:

- runner processes started: `1`
- frozen modes entered: `1`
- public route expected outputs returned: `1`
- published evidence bundles: `1`
- published independent property reports: `1`
- independently accepted reports: `0`
- published mutation applications: `0`
- accepted positive evidence rows: `0`

Cumulative through Attempts 01, 02, and 03:

- formal runner processes started: `3`
- frozen modes entered: `3`
- public route expected outputs returned: `3`
- published evidence bundles: `1`
- published independent property reports: `1`
- independently accepted reports: `0`
- published mutation applications: `0`
- accepted positive evidence rows: `0`

The two post-Attempt-02 diagnostic launches remain separately classified and
unaccepted. Attempt 03 added zero post-failure GPU diagnostic launches.

## Permitted Repair Boundary

A successor authority may permit only:

- marking the bounded wrapper as a closed partial evaluation rather than a
  direct role-symbol-linked wrapper;
- preserving the linked-PTX symbol rule for the two linked composition routes;
- structurally extracting and hashing every bounded inline definition from raw
  wrapper source, checking both per-role and aggregate preimage identities;
- independently deriving the bounded wrapper's actual role/effect facts from
  strict source entry-point and effect anchors;
- adding regressions that model optimized inline PTX without leaf symbols and
  reject inline-definition, aggregate-inline, or partial-evaluation drift;
- appending this incident and a third repair authority; and
- extending capture and verification to bind all three incidents and repair
  authorities under a new formal Attempt-04 schema.

It may not change routes, fixtures, expected outputs, declarations,
control-flow trust roots, properties, mutation selectors or replacements,
native engine code, or any Goal5838 frozen-core byte.

## Claim Boundary

- Accepted Goal5840 positive evidence: `0`
- Lowering/refinement preservation established: `false`
- General compiler soundness: `false`
- Application correctness: `false`
- Performance or speedup: `false`
- External review or consensus: `false`
