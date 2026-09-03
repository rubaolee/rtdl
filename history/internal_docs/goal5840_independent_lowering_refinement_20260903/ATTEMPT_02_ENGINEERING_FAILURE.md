# Goal5840 Formal Attempt 02 Engineering Failure

Date: 2026-09-03

## Classification

`EVIDENCE_EXECUTABLE_IDENTITY_CANONICALIZATION_ENGINEERING_FAILURE`

This was an evidence-capture infrastructure failure after a successful public
route execution. It is not a scientific failure, a lowering counterexample, a
mutation-suite result, or accepted positive Goal5840 evidence.

## Immutable Execution Identity

- Formal attempt number: `2`
- Source commit:
  `3dcd92e3c2ebc71faffbcae0783b747b9820d71e`
- Prior repair authority internal seal:
  `d872df15c5ede9a13080d24dd7aca1fedbcc217eb3a27399a42ab2ebccf3511c`
- Pod endpoint used: `root@213.173.108.100:12943`
- GPU: `NVIDIA RTX 2000 Ada Generation`
- GPU UUID: `GPU-f0ab2afa-0ec0-7da9-c951-01fc713ee1e9`
- Driver: `580.159.04`
- Compute capability: `8.9`
- OptiX SDK: `9.0.0`
- Native DSO bytes: `7181936`
- Native DSO SHA-256:
  `1d64a81a1065497fe7a941df5766606e7f166f07fcb4a3cd39f3706633b6068a`
- Native build manifest bytes: `13963`
- Native build manifest file SHA-256:
  `144745a6320ccc80e9bab41940428c7b42b870da8ef928fb83c0e29f8dc53f6e`
- Native build manifest internal result seal:
  `120075acafcfd1ad3c64348519570c21d9b2b249d64f47495f74fc1006f4559a`
- Output directory:
  `/workspace/goal5840-evidence-attempt02-3dcd92e`
- Output-directory creation/last-write time before diagnostics:
  `2026-09-03T09:35:19Z`

The exact source checkout was clean before and after the failed runner. The
output directory exists and contains zero entries.

## Observed Formal-Runner Sequence

1. Repository, frozen-core, preregistration, prior repair-authority, native
   build, exported-symbol, and machine preflight checks passed.
2. Frozen mode 1,
   `stable::bounded_relation::canonical_bounded_pair_collection::capacity_fail_closed_collection`,
   started.
3. The public route returned its exact frozen expected output:
   `((100, 10), (100, 30), (200, 20))`.
4. Evidence capture rejected the executable identity preimage before writing a
   bundle:

```text
TargetEvidenceBundleError:
TE045_EXECUTABLE_PREIMAGE_DRIFT@executable.executable_sha256:
e24485755acf0b28280a7ae658c198b2766228f8e68f46fa8404f32e68a42eb1
```

5. No evidence bundle, independent property report, runtime trust-root file,
   mutation report, or `RESULT.json` was published.

## Root-Cause Diagnosis

The bounded-relation compiler stores `inline_cuda_leaf_sha256` roles as
`CallbackRole`, a `str`-derived enum. Canonical JSON encoding of the enum itself
uses its value, for example `"bounds"`. The evidence capture reconstructed the
same preimage by first applying `str(role)`, which instead produced
`"CallbackRole.BOUNDS"`.

On the exact Attempt-02 commit, DSO, target, toolchain, and frozen mode:

- compiler executable identity:
  `e24485755acf0b28280a7ae658c198b2766228f8e68f46fa8404f32e68a42eb1`
- independently reconstructed compiler-record digest:
  `e24485755acf0b28280a7ae658c198b2766228f8e68f46fa8404f32e68a42eb1`
- value-preserving capture-record digest:
  `e24485755acf0b28280a7ae658c198b2766228f8e68f46fa8404f32e68a42eb1`
- production capture's enum-stringified record digest:
  `23311d9448a22bb9723a0c0c42dbb0c0681ad13b96bea0ceb0a84776dbe3f2a6`

All record fields except the representation type of `inline_cuda_leaves` and
`options` were Python-equal. Their canonical JSON is intentionally equivalent
when tuples/lists and the original `str`-derived enum values are preserved.
Only the premature `str(enum)` conversion changes semantic bytes.

The initial hypothesis that raw and composed wrapper-PTX hashes differed was
tested and rejected: all three observed wrapper hashes were the same
`f59fc1a989bd31962ea5422440fc77cfb1e35a05d6e4f1956fe85863ae18a042`.

## Diagnostic Execution Disclosure

After the formal runner failed, two temporary, stdin-fed, uncommitted
diagnostic processes each executed only the same frozen mode 1 on the same
commit and DSO. Both returned the frozen expected output. The first compared
two manually reconstructed preimages; the second also invoked the production
capture and intercepted its in-memory preimage digest. Neither diagnostic
wrote a repository file or evidence-output file. The temporary local script
was deleted after diagnosis.

These two diagnostic launches are engineering observations only. They are not
formal attempts, independent checks, accepted bundles, mutation applications,
application correctness evidence, or performance evidence.

## Counts At Failure And Diagnosis Boundary

Formal Attempt 02 alone:

- runner processes started: `1`
- frozen modes entered: `1`
- public route expected outputs returned: `1`
- published evidence bundles: `0`
- published independent property reports: `0`
- published mutation applications: `0`
- accepted positive evidence rows: `0`

Cumulative through Attempts 01 and 02, before diagnostics:

- formal runner processes started: `2`
- frozen modes entered: `2`
- public route expected outputs returned: `2`
- published evidence bundles: `0`
- published independent property reports: `0`
- published mutation applications: `0`
- accepted positive evidence rows: `0`

Additional post-failure diagnostics:

- diagnostic processes: `2`
- diagnostic mode executions: `2`
- diagnostic expected outputs returned: `2`
- diagnostic evidence files published: `0`
- accepted positive evidence rows: `0`

## Permitted Repair Boundary

A successor authority may permit only:

- preserving enum string values while reconstructing the executable identity
  preimage;
- adding a regression that fails on `"CallbackRole.BOUNDS"` and accepts the
  exact compiler preimage;
- appending this incident and a second repair authority;
- extending capture and independent verification to bind both incidents and
  both repair authorities under a new formal Attempt 03 schema.

It may not change routes, declarations, control-flow roots, fixtures, expected
outputs, properties, mutation units, native engine code, or any Goal5838
frozen-core byte.

## Claim Boundary

- Accepted Goal5840 positive evidence: `0`
- Lowering/refinement preservation established: `false`
- General compiler soundness: `false`
- Application correctness: `false`
- Performance or speedup: `false`
- External review or consensus: `false`
