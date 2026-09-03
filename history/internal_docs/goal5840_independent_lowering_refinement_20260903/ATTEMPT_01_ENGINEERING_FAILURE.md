# Goal5840 Attempt 01 engineering failure

Observed at: 2026-09-03T09:13:43Z

Status:
`ENGINEERING_FAILURE_AFTER_FIRST_MODE_EXECUTION_BEFORE_EVIDENCE_PUBLICATION`

This is an append-only incident record. It does not alter or replace
`PRE_POD_INPUT_AUTHORITY.json`.

## Exact execution identity

- Source commit: `91a8309d9ee234f0315b6640a8dde1db29abe7e9`
- Pre-pod authority seal:
  `785529613e79a806937b5cc56b041e671de90a164e7434d6772de9b7f4989d91`
- Native DSO SHA-256:
  `cbc2e6641cf3d74a76467afa7aacdd7958d71fa79f213401836329df102de74e`
- GPU: NVIDIA RTX 2000 Ada Generation,
  UUID `GPU-f0ab2afa-0ec0-7da9-c951-01fc713ee1e9`, CC 8.9
- Driver: 580.159.04
- Repository clean before and after the failed capture process: true

## Observed sequence

The Goal5840 runner passed repository, frozen-core, pre-pod-authority, native
build, 17-symbol ABI, GPU identity, and toolchain preflight. It then started
the frozen bounded-relation mode and returned the frozen expected output from
the public generic `compile -> materialize -> prepare -> execute -> close`
path. While constructing the target evidence bundle, recursive JSON
serialization of `result.traversal_receipt` failed before any bundle was
written.

The exact exception was:

```text
TypeError: Object of type mappingproxy is not JSON serializable

rtdsl.v4_target_evidence_capture.TargetEvidenceCaptureError:
result.traversal_receipt: Object of type mappingproxy is not JSON serializable
```

The output directory existed but was empty. Therefore:

- runner processes started: 1
- frozen modes entered: 1
- public route executions returned expected output: 1
- Goal5840 evidence bundles published: 0
- independent property reports published: 0
- mutation applications published: 0
- accepted Goal5840 positive evidence rows: 0

The execution is not silently discarded, but it is not counted as positive
evidence because the preregistered evidence object was never published.

## Classification and bounded repair

This is an evidence-transport defect: the traversal receipt contains a nested
read-only `mappingproxy`, while the local synthetic tests used ordinary
`dict`. It is not a language, lowering, native ABI, output-correctness, or
frozen-property counterexample.

The only admissible repair is to canonicalize arbitrary `Mapping` instances
recursively into plain JSON objects, add a regression with a nested
`MappingProxyType`, and extend the runner/verifier authority chain so the
original zero-run seal remains immutable and this failed attempt remains
visible. The repair may not change any route, fixture, expected output,
declaration, control-flow root, property, mutation selector, native engine, or
Goal5838 frozen-core byte.

No scientific failure, Goal5840 pass, performance result, external review,
consensus, or CGO claim is authorized by this incident.
