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

The diagnostic indicates that the target is plausible, but only a fresh clean
transaction can accept it.

## Gates

- Run all focused functional, mutation, provenance, and harness tests.
- Commit and push the successor source.
- Use a new create-only pod checkout and output directory.
- Rebuild from that exact clean commit.
- Run both worker-zero arms, then all eight balanced blocks.
- Download and independently verify the complete result on the Mac.
- Retain every outcome. Do not claim success from the dirty diagnostics.
- External review remains unavailable and pending. No public or manuscript
  performance wording is authorized.
