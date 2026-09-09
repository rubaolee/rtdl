# Particle `110dee7aa` durable data handoff

Date: 2026-09-09

## Location and verification

The post-formal durability handoff is on the producing Pod's RunPod network
volume:

`/workspace/rtdl-particle-110dee7aa-durable`

- Approximate allocated payload size: `8.7 GiB` as reported by `du`.
- Registered payload files: 47.
- `SHA256SUMS` SHA-256:
  `43e0bc33cd0eb9a702a35619ddc71f9a1a8d66fc7a2cd9df95b3e95dbf3645c5`.
- `FILE_SIZES.tsv` SHA-256:
  `cc2ac779e58d45b6f4ffe9ff8ffcb6a9e9da251a06aec335cfbafe3e7a603eed`.
- Handoff `README.md` SHA-256:
  `6b1375a051181c965d8a0459a75e72c4b78f09ba1fa79c17c7afd83e7528cabb`.
- Exact source archive SHA-256:
  `fddb4a480cfcd087153b8a0a28c429099e44de6e769bc4bb3b8fd70a34a74eb7`.

The standalone `tools/verify_durable_particle_110dee7aa.py` imports NumPy but
not RTDL. It rehashed all 47 registered files, checked array shapes and dtypes,
then compared the observed output against the independent adjacency oracle in
one-million-row chunks after the public `(2,0,1)` column transformation. Its
result was:

```text
PASS durable Particle handoff: 47 files; output=6c4ec71524be3d7b241c3d66c4cd06a5aa7089b3948bf1d8dd8aab550f0dec89
```

## Large data identities

| Member | Bytes | File SHA-256 |
| --- | ---: | --- |
| `data/transition_ensemble/queries_f32.npy` | 4,480,000,128 | `a2e613084c03cb717f6f86b8444d015737a23369b57367fe063b89e35c3a52fd` |
| `data/transition_ensemble/query_cells_u32.npy` | 640,000,128 | `7cbe1c2a80c1ead88137cc31e0dd7fd96e303d66abe8d4291a64622a5039f359` |
| `data/transition_ensemble/expected_u32.npy` | 1,920,000,128 | `f24c68beb656ba9f20c0fefc392d50653ede07b101f914f077349d63fcced038` |
| `data/observed_output_u32.npy` | 1,920,000,128 | `387fec59337c0246647fb31b957669f81b9ae26a7875bbc86c7a1875557ae43d` |

The observed output's canonical array digest is
`6c4ec71524be3d7b241c3d66c4cd06a5aa7089b3948bf1d8dd8aab550f0dec89`,
equal to the formal registered output digest and the transformed oracle.

## Included replay material

- Complete query ensemble, query-cell rows and independent oracle.
- Real Particle base mesh and base fixture arrays.
- Complete actual output from a post-formal untimed 160M replay.
- Measured RTDL native DSO and public-PyOptiX PTX with build records.
- Immutable original formal archive, preregistration and recount.
- Exact `110dee7aa` source-tree Git archive.
- Thirteen reconstructed RTDL compiler artifacts and one full replay receipt.
- The exact original post-formal replay script and command.
- A second replay command that reads durable data/artifact paths and accepts an
  exact clean Git checkout through `SOURCE_ROOT`.
- Producing environment and Python package records.
- The exact descriptive peak-memory diagnostic tool and its raw JSON result.

The diagnostic tool is
`tools/particle_peak_memory_diagnostic_110dee7aa.py`, SHA-256
`192b12ce24db902c0f164670ca0addc93f825e281955df6e49872f3c13f8f446`.
An exact repository copy is `PEAK_MEMORY_DIAGNOSTIC_TOOL.py`.
Its raw result is `PEAK_MEMORY_DIAGNOSTIC.json`, SHA-256
`0c3ee2df8d9411f3a6ef4e6e344cc802abe4b97bbba3d94b5e8eba20099ce49e`.

## Boundary

This handoff does not modify the original formal archive or performance
statistics. `observed_output_u32.npy` is actual output from a later untimed
replay, not output retained from an original timed worker. No replay timing is
pooled. The original timed workers' full receipts remain unavailable.

The network volume is more durable than `/tmp` and `/dev/shm`, but it is not
Git or archival-publication custody. These bytes remain available only while
the owner retains the underlying RunPod network volume. The repository keeps
this identity and verification record, not the multi-gigabyte payload itself.
