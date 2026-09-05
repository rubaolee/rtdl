# Goal5844 public execution parity engineering log

## Scope

This is an append-only successor record for Goal5844 after its first formal GPU
transaction. It does not rewrite the pre-pod compact-stamp packet or any
Goal5843 evidence. The scientific target is the same-contract steady public
triangle scalar path at no more than 1.25x the pinned PyOptiX public path.

## Immutable first transaction

- Source commit: `5e1518afe24230be677484f8e437e0a0da6bb30d`
- GPU: NVIDIA RTX 2000 Ada Generation, compute capability 8.9
- Driver: 580.159.04
- Samples: 1,024 per arm in eight balanced, alternating-order blocks
- RTDL public median: 273,457 ns
- PyOptiX public median: 129,368 ns
- Median within-block RTDL/PyOptiX: 2.1713906352x
- Outcome: `ADVERSE__CONTINUE_PERFORMANCE_ENGINEERING`
- Summary SHA-256:
  `4d6548238849c49e7aa89dcb663f08febb2815d83da924dd3a083db5549a94d3`
- Downloaded archive SHA-256:
  `d4d57100f77c74b1f43187d7c82e290fa6071524aa8478b8369f0925a6e93814`

This transaction is retained as a failed target result. It must not be pooled
with the successor transaction.

## Measured cause

The first transaction's layer medians were approximately 82.6 us for the
direct native v8 ABI, 141.6 us for the provider owner, 272.1 us for the public
path, and 2,770.7 us for explicit forensic receipt expansion. Profiling showed
that steady public execution repeatedly serialized, copied, revalidated, and
hashed the same compact proof and immutable executable identities at several
adjacent lifecycle boundaries.

## Successor design

1. Native launch facts are copied and validated eagerly into a factory-created
   immutable `ValidatedCompactTraversalReceipt`.
2. The canonical JSON receipt and its transport digest are generated lazily,
   only when an observer requests mapping contents.
3. The protocol checks exact provider, route, output, program bundle, ray count,
   and receipt type without materializing the transport document.
4. The family bridge uses a scalar fast envelope only for an exact factory
   receipt. External providers, non-scalar outputs, and ordinary receipt maps
   retain the original full canonicalization path.
5. Stable integer output digests, canonical SHA validation results, physical
   program-bundle IDs, and immutable executable/projection digests are boundedly
   memoized. Dynamic native stamp values remain validated on every execution.

The lifecycle memoization changes one Goal5838 frozen-core file only after that
prospective exam completed. The old seal remains authoritative at its exact Git
commit. The successor must not claim current-tree byte identity with that old
seal.

## Non-authoritative same-pod diagnostics

These values guided engineering only; they came from a deliberately dirty
diagnostic checkout and are not registered performance evidence.

| Stage | RTDL public median | Approx. ratio to first-transaction PyOptiX median |
|---|---:|---:|
| First formal transaction | 273.457 us | formal block ratio 2.171x |
| Lazy validated receipt and bridge fast envelope | 207.186 us | 1.601x |
| Plus immutable identity memoization | 178.875 us | 1.383x |
| Plus bundle/SHA/scalar-digest memoization | 131.824 us | 1.019x |
| Same code without frozen-core identity memoization | 170.080 us | 1.315x |

The diagnostic indicated that the target was plausible, but only a fresh clean
transaction could accept it.

## Clean successor transaction

- Source commit: `ee0237963bcd838d652a059f15ecc0d3f56dfd09`
- Same GPU UUID as attempt 1:
  `GPU-4b436f5f-bf8f-1d8c-0202-98e6e7b387e9`
- RTDL public median: 132,534 ns
- PyOptiX public median: 131,744 ns
- Median within-block RTDL/PyOptiX: 1.0456709696813038x
- Minimum/maximum block ratio: 0.9680755129797174x / 1.1543425587550877x
- RTDL-first stratified median: 1.0456709696813038x
- PyOptiX-first stratified median: 1.0456883372006447x
- Direct-native before/after medians: 82,757 ns / 82,592 ns
- Outcome: `PASS__INTERNAL_ENGINEERING_TARGET_MET`
- Summary SHA-256:
  `6229aeba61fa681cbcda37e0ca253f725269fe08c2dd5e85f91502e5ad0a3b03`
- Downloaded archive SHA-256:
  `4336526eb6084d18353812187b2bd6c57515a642d804313abbaa79b52b1b678d`

The successor reduced the RTDL public median by 2.0633x while the PyOptiX
median changed by only 1.0184x and direct native changed by 0.9980x. This
supports a protocol-overhead repair, not a changed RT workload explanation.

## Gates

- Run all focused functional, mutation, provenance, and harness tests.
- Commit and push the successor source: complete.
- Use a new create-only pod checkout and output directory: complete.
- Rebuild from that exact clean commit: complete.
- Run both worker-zero arms, then all eight balanced blocks: complete.
- Download and independently verify the complete result on the Mac: complete.
- Retain every outcome: complete; attempts are not pooled.
- External review remains unavailable and pending. No public or manuscript
  performance wording is authorized.
