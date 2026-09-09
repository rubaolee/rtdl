# Particle `110dee7aa` durable data handoff

Date: 2026-09-09

## Location and verification

The post-formal durability handoff is on the producing Pod's RunPod network
volume:

`/workspace/rtdl-particle-110dee7aa-durable`

- Approximate allocated payload size: `8.7 GiB` as reported by `du`.
- Registered payload files: 45.
- `SHA256SUMS` SHA-256:
  `d2859cdea49c239aed34381a989b757232e8cb06237c61d83b5e347ce815ea48`.
- `FILE_SIZES.tsv` SHA-256:
  `78bc5fa0ae5006e7f03e21196a6d9ce240226e5f8f707fb8dfcec22dc55e9ff9`.
- Handoff `README.md` SHA-256:
  `2605eec8653bae2d154621c273c42fecb52d3e2bbcf6cd98f60fbb926a346368`.
- Exact source archive SHA-256:
  `fddb4a480cfcd087153b8a0a28c429099e44de6e769bc4bb3b8fd70a34a74eb7`.

The standalone `tools/verify_durable_particle_110dee7aa.py` imports NumPy but
not RTDL. It rehashed all 45 registered files, checked array shapes and dtypes,
then compared the observed output against the independent adjacency oracle in
one-million-row chunks after the public `(2,0,1)` column transformation. Its
result was:

```text
PASS durable Particle handoff: 45 files; output=6c4ec71524be3d7b241c3d66c4cd06a5aa7089b3948bf1d8dd8aab550f0dec89
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

## Boundary

This handoff does not modify the original formal archive or performance
statistics. `observed_output_u32.npy` is actual output from a later untimed
replay, not output retained from an original timed worker. No replay timing is
pooled. The original timed workers' full receipts remain unavailable.

The network volume is more durable than `/tmp` and `/dev/shm`, but it is not
Git or archival-publication custody. These bytes remain available only while
the owner retains the underlying RunPod network volume. The repository keeps
this identity and verification record, not the multi-gigabyte payload itself.
